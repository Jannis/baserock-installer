# vi:set sw=4 sts=4 ts=4 et nocindent:
#
# Copyright (C) 2006, 2012 Jannis Pohlmann <jannis.pohlmann@codethink.co.uk>
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; version 2 of the License.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along
# with this program; if not, write to the Free Software Foundation, Inc.,
# 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.


import gobject
import httplib
import os
import socket
import tempfile
import time
import urllib
import urlparse
import shutil

from threading import Thread


class DownloadItem(object):

    ''' Wraps information about a file being downloaded. '''

    def __init__(self, name, source, target):
        self.name = name
        self.source = source
        self.target = target


class URLInfo(object):

    ''' Wrapper class for handle information. '''

    def __init__(self, handle_info):
        self.size = int(handle_info['Content-Length'])


class DownloadHandle(gobject.GObject):

    ''' Handle object for file downloads. '''

    def __init__(self, item, handle):
        gobject.GObject.__init__(self)
        self.item = item
        self.handle = handle
        self.info = URLInfo(handle.info())
        self.bytes_read = 0


class FileDownload(gobject.GObject):

    ''' Download manager with cancellation and download queue capabilities. '''

    BLOCK_SIZE = 8192

    __gsignals__ = {
        'download-item-started': (
            gobject.SIGNAL_RUN_LAST,
            gobject.TYPE_BOOLEAN,
            (DownloadHandle, )
        ),
        'download-item-finished': (
            gobject.SIGNAL_RUN_LAST,
            gobject.TYPE_BOOLEAN,
            (DownloadHandle, )
        ),
        'download-error': (
            gobject.SIGNAL_RUN_LAST,
            gobject.TYPE_BOOLEAN,
            (DownloadHandle, )
        ),
        'download-progress': (
            gobject.SIGNAL_RUN_LAST,
            gobject.TYPE_BOOLEAN,
            (DownloadHandle, )
        ),
        'download-finished': (
            gobject.SIGNAL_RUN_LAST,
            gobject.TYPE_BOOLEAN,
            ()
        ),
    }

    def __init__(self):
        gobject.GObject.__init__(self)
        self.excluded_mime_types = set()
        self._reset()
    
    def _reset(self):
        self.total_bytes = 0
        self.total_bytes_read = 0
        self.queue = list()
        self.terminated = False

    def terminate(self):
        ''' Abort download. '''
        self.terminated = True

    def is_terminated(self):
        ''' Determine whether the downloader was terminated or not. '''
        return self.terminated

    def _is_valid_header(self, data):
        if self.excluded_mime_types:
            for type in self.excluded_mime_types:
                if data.gettype() == type:
                    return False
        return True

    def download(self, items):
        ''' Download items in the passed item list.
        
        Other classes can hook into the download process by connecting
        to the various status signals listed at the bottom of this file.
        
        '''
        # Reset certain variables
        self._reset()

        self.items = items

        # Spawn worker thread
        worker = Thread(target = self._process)
        worker.start()

        # Return thread object
        return worker
        
    def _process(self):
        # Use FancyURLopener for accessing URLs
        opener = urllib.FancyURLopener()

        # Open URL handles and build download queue
        for item in self.items:
            # Open URL
            handle = opener.open(item.source)

            # Create download handle
            dl_handle = DownloadHandle(item, handle)
            
            # Check header (exclude mime-types)
            if not self._is_valid_header(handle.info()):
                self.emit('download-error', dl_handle)
                return
                
            # Append handle to queue
            self.queue.append(dl_handle)

        # Determine total bytes to retrieve
        for dl_handle in self.queue:
            self.total_bytes += dl_handle.info.size

        # Download items
        for dl_handle in self.queue:
            # Emit 'download-started' signal
            self.emit('download-item-started', dl_handle)

            # Create temporary file for writing the data to
            tmpfile_fd, tmpfile_path = tempfile.mkstemp(
                    '-download', 'baserock-',
                    dir=os.path.dirname(dl_handle.item.target))

            # Read data from the URL handle
            buf = dl_handle.handle.read(self.BLOCK_SIZE)
            while buf:
                # Abort download, if requested
                if self.terminated:
                    dl_handle.handle.close()
                    os.close(tmpfile_fd)
                    os.remove(tmpfile_path)
                    return
                
                # Write data to temp file
                os.write(tmpfile_fd, buf)

                # Keep track of the already retrieved bytes
                dl_handle.bytes_read += len(buf)
                self.total_bytes_read += len(buf)

                # Emit 'download-progress' signal
                self.emit('download-progress', dl_handle)

                # Read next block
                buf = dl_handle.handle.read(self.BLOCK_SIZE)

            # Close temporary file
            os.close(tmpfile_fd)

            # Move temporary file to destination
            shutil.move(tmpfile_path, dl_handle.item.target)

            # Remove temporary file if it still exists
            try:
                os.remove(tmpfile_path)
            except:
                pass

            # Close download file handle
            dl_handle.handle.close()

            # Emit 'download-item-finished' signal
            self.emit('download-item-finished', dl_handle)

        # Emit 'download-finished' signal
        self.emit('download-finished')
