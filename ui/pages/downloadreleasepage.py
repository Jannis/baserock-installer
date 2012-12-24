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
from utils import gdk
from utils.release import Release
from utils.download import DownloadItem, FileDownload


class DownloadReleasePage(Page):

    def __init__(self, assistant):
        Page.__init__(self, assistant)

        config_dir = GLib.get_user_config_dir()
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

        grid = Gtk.Grid()
        grid.set_column_spacing(12)
        grid.set_row_spacing(6)
        grid.show()
        box.pack_start(grid, False, True, 0)

        label = Gtk.Label('Current File:')
        label.set_halign(Gtk.Align.START)
        label.show()
        grid.attach(label, 0, 1, 1, 1)

        self.item_progress = Gtk.ProgressBar()
        self.item_progress.set_show_text(True)
        self.item_progress.set_hexpand(True)
        self.item_progress.show()
        grid.attach(self.item_progress, 1, 1, 1, 1)

        label = Gtk.Label('Total:')
        label.set_halign(Gtk.Align.START)
        label.show()
        grid.attach(label, 0, 2, 1, 1)

        self.total_progress = Gtk.ProgressBar()
        self.total_progress.set_show_text(True)
        self.total_progress.show()
        grid.attach(self.total_progress, 1, 2, 1, 1)

        self.downloader = FileDownload()
        self.downloader.connect('download-error', self.download_error)
        self.downloader.connect('download-progress', self.download_progress)
        self.downloader.connect('download-finished', self.download_finished)
        self.downloader.excluded_mime_types.add('text/html')

        self.reset()

    def download_error(self, downloader, handle):
        print 'Downloading %s failed' % handle

    def download_progress(self, downloader, handle):
        self.total_bytes = downloader.total_bytes
        self.total_bytes_read = downloader.total_bytes_read
        self.item_bytes = handle.info.size
        self.item_bytes_read = handle.bytes_read
        self.item_name = handle.item.name

    def download_finished(self, downloader):
        self.download_completed = True
        self.notify_complete()

    def update_progress_bars(self):
        if self.downloader.is_terminated() or self.download_completed:
            return False
        
        if self.item_bytes == 0:
            self.item_progress.set_text(self.item_name)
        else:
            fraction = self.item_bytes_read / float(self.item_bytes)
            self.item_progress.set_fraction(fraction)

            text = '%.1f of %.1f MB' % (
                self.item_bytes_read / 1000 / 1000.0,
                self.item_bytes / 1000 / 1000.0
            )
            self.item_progress.set_text(text)

        if self.total_bytes == 0:
            self.total_progress.set_fraction(0.0)
            self.total_progress.set_text('Connecting...')
        else:
            fraction = self.total_bytes_read / float(self.total_bytes)
            self.total_progress.set_fraction(fraction)

            text = '%.1f of %.1f MB' % (
                self.total_bytes_read / 1000 / 1000.0,
                self.total_bytes / 1000 / 1000.0
            )
            self.total_progress.set_text(text)

        return True

    def reset(self):
        if self.idle_id != 0:
            GLib.source_remove(self.idle_id)
        self.idle_id = GLib.idle_add(self.update_progress_bars)

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

        release = results['select-release']
        self.title.set_markup('<span size="large">Downloading %s</span>' %
                              release.title)

        configdir = GLib.get_user_config_dir()
        self.dirname = os.path.join(
                configdir, 'baserock-installer', 'files',
                os.path.basename(results['download-releases']['repodir']))

        if not os.path.isdir(self.dirname):
            os.makedirs(self.dirname)

        self.download_items = set()
        for url in release.files():
            basename = os.path.basename(url)
            destination = os.path.join(self.dirname, basename)
            self.download_items.add(DownloadItem(basename, url, destination))

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
