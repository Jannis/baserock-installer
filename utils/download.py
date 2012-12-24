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


import collections
import threading

from gi.repository import Gio, GLib, GObject


class DownloadItem(GObject.GObject):

    ''' Wraps information about a file being downloaded. '''

    def __init__(self, source, target):
        GObject.GObject.__init__(self)
        self.source = source
        self.target = target
        self.source_file = None
        self.target_file = None
        self.source_info = None
        self.target_info = None


class Downloader(GObject.GObject):

    ''' Download manager with cancellation and download queue capabilities. '''

    BLOCK_SIZE = 4096 * 4

    __gsignals__ = {
        'download-item-started': (
            GObject.SIGNAL_RUN_LAST,
            GObject.TYPE_BOOLEAN,
            (DownloadItem, )
        ),
        'download-item-finished': (
            GObject.SIGNAL_RUN_LAST,
            GObject.TYPE_BOOLEAN,
            (DownloadItem, )
        ),
        'download-error': (
            GObject.SIGNAL_RUN_LAST,
            GObject.TYPE_BOOLEAN,
            (DownloadItem, )
        ),
        'download-progress': (
            GObject.SIGNAL_RUN_LAST,
            GObject.TYPE_BOOLEAN,
            (DownloadItem, )
        ),
        'download-finished': (
            GObject.SIGNAL_RUN_LAST,
            GObject.TYPE_NONE,
            ()
        ),
    }

    def __init__(self):
        GObject.GObject.__init__(self)
        self.cancellable = Gio.Cancellable()
        self.worker = None

    def cancel(self):
        print 'cancel cancellable'
        self.cancellable.cancel()
        if self.worker:
            self.worker.join()
            self.worker = None
        print 'cancellable cancelled'

    def download(self, items):
        self.cancellable.reset()
        self.queue = collections.deque(items)
        if self.queue:
            self.step1_obtain_file_infos()

    def step1_obtain_file_infos(self):
        items = list(self.queue)

        def target_info_ready(target_file, result, item):
            print 'target info ready: %s' % item.target
            try:
                item.target_info = target_file.query_info_finish(result)
            except GLib.GError:
                pass
            if items:
                obtain_source_info(items.pop(0))
            else:
                self.step2_download_files()

        def obtain_target_info(item):
            print 'obtain target info: %s' % item.target
            item.target_file = Gio.File.new_for_commandline_arg(item.target)
            item.target_file.query_info_async(
                    '*', 0, GLib.PRIORITY_DEFAULT, self.cancellable,
                    target_info_ready, item)

        def source_info_ready(source_file, result, item):
            print 'source info read: %s' % item.source
            item.source_info = source_file.query_info_finish(result)
            obtain_target_info(item)

        def obtain_source_info(item):
            print 'obtain source info: %s' % item.source
            item.source_file = Gio.File.new_for_commandline_arg(item.source)
            item.source_file.query_info_async(
                    '*', 0, GLib.PRIORITY_DEFAULT, self.cancellable,
                    source_info_ready, item)

        obtain_source_info(items.pop(0))

    def step2_download_files(self):
        items = list(self.queue)

        self.item_bytes = 0
        self.item_bytes_read = 0
        self.total_bytes = 0
        self.total_bytes = sum([x.source_info.get_size() for x in items])
        self.total_bytes_read = 0

        def download_progress(item_bytes_read, item_bytes, item):
            print 'download progress: %d' % item_bytes_read
            self.item_bytes_read = item_bytes_read
            self.item_bytes = item_bytes
            self.emit('download-progress', item)

        def download_item(item):
            try:
                item.source_file.copy(
                        item.target_file,
                        Gio.FileCopyFlags.OVERWRITE,
                        self.cancellable,
                        download_progress,
                        item)
                print 'copied'
                import sys
                sys.stdout.flush()
            except Exception, err:
                print 'error: %s' % err
                import sys
                sys.stdout.flush()
                self.emit('download-error', item)
                return
            if items:
                print 'next'
                import sys
                sys.stdout.flush()
                download_next(items.pop(0))
            else:
                print 'finished'
                import sys
                sys.stdout.flush()
                self.emit('download-finished')

        def download_next(item):
            self.worker = threading.Thread(target=download_item, args=[item])
            self.worker.start()

        download_next(items.pop(0))
