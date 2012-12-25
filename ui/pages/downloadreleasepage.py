#!/usr/bin/env python
# -
# vi:set sw=4 sts=4 ts=4 et nocindent:
#
# Copyright (C) 2012 Jannis Pohlmann <jannis.pohlmann@codethink.co.uk>
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


import glib
import glob
import gtk
import os
import subprocess
import threading
import yaml

import utils.urls

from ui.pages.page import Page
from utils.release import Release
from utils.download import DownloadItem, FileDownload


class DownloadReleasePage(Page):

    def __init__(self, assistant):
        Page.__init__(self, assistant)

        config_dir = glib.get_user_config_dir()
        self.repositories = os.path.join(
                config_dir, 'baserock-installer', 'repos')

        self.worker = None
        self.idle_id = 0
        self.download_completed = False

        self.title, box = self.start_section('Downloading Release')
        text = self.create_text(
                'Depending on your internet connection, this may take '
                'some time. You will, however, get a Baserock system that '
                'provides a traceable and controlled runtime or development '
                'environment. Among many other things, this helps in '
                'spotting, diagnosing and fixing problems as at any time '
                'it is clear how exactly the system is configured.')
        box.pack_start(text, False, False, 0)

        progress_box = gtk.VBox(False, 6)
        progress_box.show()
        box.pack_start(progress_box, False, True, 0)

        label = gtk.Label('Current File:')
        label.set_alignment(0.0, 0.5)
        label.show()
        progress_box.pack_start(label, False, False, 0)

        self.item_progress = gtk.ProgressBar()
        self.item_progress.show()
        progress_box.pack_start(self.item_progress, False, False, 0)

        label = gtk.Label('Total:')
        label.set_alignment(0.0, 0.5)
        label.show()
        progress_box.pack_start(label, False, False, 0)

        self.total_progress = gtk.ProgressBar()
        self.total_progress.show()
        progress_box.pack_start(self.total_progress, False, False, 0)

        self.numbers_label = gtk.Label()
        self.numbers_label.set_alignment(0.0, 0.5)
        self.numbers_label.show()
        progress_box.pack_start(self.numbers_label, False, False, 0)

        self.downloader = FileDownload()
        self.downloader.connect('download-error', self.download_error)
        self.downloader.connect('download-progress', self.download_progress)
        self.downloader.connect('download-finished', self.download_finished)
        self.downloader.excluded_mime_types.add('text/html')

        self.reset()

    def download_error(self, downloader, handle):
        print 'Downloading %s failed' % handle

    def download_progress(self, downloader, handle):
        self.item_bytes = handle.info.size
        self.item_bytes_read = handle.bytes_read
        self.total_bytes = downloader.total_bytes
        self.total_bytes_read = downloader.total_bytes_read

    def download_finished(self, downloader):
        self.download_completed = True
        self.emit('complete')

    def update_progress_bars(self):
        if self.downloader.is_terminated() or self.download_completed:
            return False
        
        if self.item_bytes == 0:
            self.item_progress.set_fraction(0.0)
        else:
            fraction = self.item_bytes_read / float(self.item_bytes)
            self.item_progress.set_fraction(fraction)

        if self.total_bytes == 0:
            self.total_progress.set_fraction(0.0)
            self.numbers_label.set_text('Connecting...')
        else:
            fraction = self.total_bytes_read / float(self.total_bytes)
            self.total_progress.set_fraction(fraction)

            text = '%.1f of %.1f MB' % (
                self.total_bytes_read / 1000 / 1000.0,
                self.total_bytes / 1000 / 1000.0
            )
            self.numbers_label.set_text(text)

        return True

    def reset(self):
        if self.idle_id != 0:
            glib.source_remove(self.idle_id)
        self.idle_id = glib.idle_add(self.update_progress_bars)

        self.download_completed = False

        self.total_bytes = 0
        self.total_bytes_read = 0
        self.item_bytes = 0
        self.item_bytes_read = 0
        self.item_name = ''

        self.item_progress.set_text('')
        self.total_progress.set_text('')

    def prepare(self, results):
        self.cancel()

        configdir = glib.get_user_config_dir()
        self.dirname = os.path.join(
                configdir, 'baserock-installer', 'files',
                os.path.basename(results['download-releases']['repodir']))

        if not os.path.isdir(self.dirname):
            os.makedirs(self.dirname)

        release = results['select-release']
        self.download_items = []
        for url in release.files():
            basename = os.path.basename(url)
            destination = os.path.join(self.dirname, basename)
            self.download_items.append(
                    DownloadItem(basename, url, destination))

        self.worker = self.downloader.download(self.download_items)

    def is_complete(self):
        return self.download_completed

    def result(self):
        return self.download_items

    def cancel(self):
        self.reset()
        if self.worker:
            self.downloader.terminate()
            self.worker.join()
