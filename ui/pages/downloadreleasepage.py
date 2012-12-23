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


import glob
import os
import subprocess
import threading
import yaml

from gi.repository import Gdk, GLib, Gtk

import utils.urls

from ui.pages.page import Page
from utils.release import Release
from utils.download import DownloadItem, FileDownload


class DownloadReleasePage(Page):

    def __init__(self, assistant):
        Page.__init__(self, assistant)

        config_dir = GLib.get_user_config_dir()
        self.repositories = os.path.join(
                config_dir, 'baserock-installer', 'repos')

        self.title, box = self.start_section('Downloading Release')

        self.item_progress = Gtk.ProgressBar()
        self.item_progress.set_show_text(True)
        self.item_progress.show()
        box.pack_start(self.item_progress, False, False, 0)

        self.total_progress = Gtk.ProgressBar()
        self.total_progress.set_show_text(True)
        self.total_progress.show()
        box.pack_start(self.total_progress, False, False, 0)

        self.downloader = FileDownload()
        self.downloader.connect('download-error', self.download_error)
        self.downloader.connect('download-progress', self.download_progress)
        self.downloader.connect('download-finished', self.download_finished)
        self.downloader.excluded_mime_types.add('text/html')

    def download_error(self, downloader, handle):
        print 'Downloading %s failed' % handle

    def download_progress(self, downloader, handle):
        Gdk.threads_enter()
        try:
            self.total_bytes = downloader.total_bytes
            self.total_bytes_read = downloader.total_bytes_read
            self.item_bytes = handle.info.size
            self.item_bytes_read = handle.bytes_read
            self.item_name = handle.item.name
            self.update_progress_bars()
        finally:
            Gdk.threads_leave()

    def download_finished(self, downloader):
        self.notify_completed()

    def update_progress_bars(self):
        if self.downloader.terminated:
            return

        if self.total_bytes != 0:
            total_fraction = \
                    float(self.total_bytes_read) / float(self.total_bytes)
            total_percent = total_fraction * 100
            
            total_text = \
                    'Total: %(percent)d%% (%(bytes).1f/%(total).1f MB)' % {
                'percent': total_percent,
                'bytes': self.total_bytes_read / 1000 / 1000.0, 
                'total': self.total_bytes / 1000 / 1000.0
            }

            self.total_progress.set_fraction(total_fraction)
            self.total_progress.set_text(total_text)
        else:
            self.total_progress.set_text('Total')

        if self.item_bytes != 0:
            item_fraction = float(self.item_bytes_read) / float(self.item_bytes)
            item_percent = item_fraction * 100

            item_text = \
                    '%(name)s: %(percent)d%% (%(bytes).1f/%(total).1f MB)' % {
                'name': self.item_name, 
                'percent': item_percent,
                'bytes': self.item_bytes_read / 1000 / 1000.0,
                'total': self.item_bytes / 1000 / 1000.0
            }

            self.item_progress.set_fraction(item_fraction)
            self.item_progress.set_text(item_text)
        else:
            self.item_progress.set_text(self.item_name)

    def prepare(self, results):
        release = results['select-release']
        self.title.set_markup('<span size="large">Downloading %s</span>' %
                              release.title)

        self.total_bytes = 0
        self.total_bytes_read = 0
        self.item_bytes = 0
        self.item_bytes_read = 0
        self.item_name = ''

        configdir = GLib.get_user_config_dir()
        self.dirname = os.path.join(
                configdir, 'baserock-installer', 'files',
                os.path.basename(results['download-releases']['repodir']))

        if not os.path.isdir(self.dirname):
            os.makedirs(self.dirname)

        download_items = set()
        for url in release.files():
            basename = os.path.basename(url)
            destination = os.path.join(self.dirname, basename)
            download_items.add(DownloadItem(basename, url, destination))

        self.worker = self.downloader.download(download_items)

    def is_complete(self):
        return False

    def result(self):
        return None
