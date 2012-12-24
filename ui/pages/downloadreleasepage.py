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


import collections
import glob
import os
import subprocess
import threading
import yaml

from gi.repository import Gdk, Gio, GLib, Gtk

import utils.urls

from ui.pages.page import Page
from utils import gdk
from utils.release import Release
from utils.download import DownloadItem, Downloader


class DownloadReleasePage(Page):

    def __init__(self, assistant):
        Page.__init__(self, assistant)

        config_dir = GLib.get_user_config_dir()
        self.repositories = os.path.join(
                config_dir, 'baserock-installer', 'repos')

        self.downloader = Downloader()
        self.downloader.connect('download-progress', self.download_progress)
        self.downloader.connect('download-finished', self.download_finished)

        self.title, box = self.start_section('Downloading Release')

        grid = Gtk.Grid()
        grid.set_row_spacing(6)
        grid.set_column_spacing(12)
        grid.show()
        self.add(grid)

        label = Gtk.Label('Current File:')
        label.set_halign(Gtk.Align.START)
        label.set_valign(Gtk.Align.CENTER)
        label.show()
        grid.attach(label, 0, 0, 1, 1)

        self.item_progress = Gtk.ProgressBar()
        self.item_progress.set_hexpand(True)
        self.item_progress.set_show_text(True)
        self.item_progress.show()
        grid.attach(self.item_progress, 1, 0, 1, 1)

        label = Gtk.Label('Total:')
        label.set_halign(Gtk.Align.START)
        label.set_valign(Gtk.Align.CENTER)
        label.show()
        grid.attach(label, 0, 1, 1, 1)

        self.total_progress = Gtk.ProgressBar()
        self.total_progress.set_hexpand(True)
        self.total_progress.set_show_text(True)
        self.total_progress.show()
        grid.attach(self.total_progress, 1, 1, 1, 1)

    def download_progress(self, downloader, item):
        self.total_bytes = downloader.total_bytes
        self.total_bytes_read = downloader.total_bytes_read
        self.item_bytes = downloader.item_bytes
        self.item_bytes_read = downloader.item_bytes_read
        self.update_progress_bars()

    def download_finished(self, downloader):
        self.notify_complete()

    def update_progress_bars(self):
        if self.item_bytes != 0:
            item_fraction = self.item_bytes_read / float(self.item_bytes)
            self.item_progress.set_fraction(item_fraction)

            item_text = '%(bytes).1f of %(total).1f MB' % {
                'bytes': self.item_bytes_read / 1000 / 1000.0,
                'total': self.item_bytes / 1000 / 1000.0
            }
            self.item_progress.set_text(item_text)
        else:
            self.item_progress.set_text('')

        if self.total_bytes != 0:
            total_fraction = self.total_bytes_read / float(self.total_bytes)
            self.total_progress.set_fraction(total_fraction)
            
            total_text = '%(bytes).1f of %(total).1f MB)' % {
                'bytes': self.total_bytes_read / 1000 / 1000.0, 
                'total': self.total_bytes / 1000 / 1000.0
            }
            self.total_progress.set_text(total_text)
        else:
            self.total_progress.set_text('')

    def reset(self):
        self.total_bytes = 0
        self.total_bytes_read = 0
        self.item_bytes = 0
        self.item_bytes_read = 0
        self.item_progress.set_text('')
        self.total_progress.set_text('')

    def prepare(self, results):
        #self.cancel()

        release = results['select-release']
        self.title.set_markup('<span size="large">Downloading %s</span>' %
                              release.title)

        configdir = GLib.get_user_config_dir()
        self.dirname = os.path.join(
                configdir, 'baserock-installer', 'files',
                os.path.basename(results['download-releases']['repodir']))

        if not os.path.isdir(self.dirname):
            os.makedirs(self.dirname)

        self.download_items = []
        for url in release.files():
            target = os.path.join(self.dirname, os.path.basename(url))
            self.download_items.append(DownloadItem(url, target))

        self.downloader.download(self.download_items)
    
    def is_complete(self):
        return False

    def result(self):
        return self.download_items

    def cancel(self):
        self.downloader.cancel()
