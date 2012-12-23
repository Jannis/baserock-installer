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


class DownloadReleasesPage(Page):

    def __init__(self, assistant):
        Page.__init__(self, assistant)

        configdir = GLib.get_user_config_dir()
        self.repositories = os.path.join(
                configdir, 'baserock-installer', 'repos')

        label, box = self.start_section('Downloading Releases')

        self.download_text = self.create_text('')
        box.pack_start(self.download_text, False, False, 0)

        self.progress = Gtk.ProgressBar()
        self.progress.set_show_text(True)
        self.progress.show()
        box.pack_start(self.progress, False, False, 0)
        
        self.error_label = self.create_text('')
        self.error_label.set_selectable(True)
        box.pack_start(self.error_label, False, False, 0)

    def set_error(self, text):
        self.download_succeeded = False
        self.progress.set_text('Failed')
        self.error_label.set_markup('<b>Error: %s</b>' % text)
        self.error_label.show()

    def prepare(self, results):
        self.cancel()

        self.progress.set_text('')
        self.error_label.hide()
        self.releases = []
        self.download_succeeded = False

        self.repository = results['welcome']
        self.quoted_repository = utils.urls.quote_url(self.repository)

        self.download_text.set_markup(
                'Downloading releases from\n'
                '\n'
                '<tt>%s</tt>' % self.repository)

        if not os.path.isdir(self.repositories):
            os.makedirs(self.repositories)

        self.repodir = os.path.join(self.repositories, self.quoted_repository)

        self.worker = threading.Thread(target = self.clone_repository)
        self.worker.start()

    def clone_repository(self):
        try:
            if os.path.isdir(self.repodir):
                with gdk.lock:
                    self.progress.set_text('Pulling %s...' %
                                           os.path.basename(self.repository))
                subprocess.check_output(['git', 'remote', 'set-url', 'origin',
                                         self.repository], cwd=self.repodir,
                                        stderr=subprocess.STDOUT)
                with gdk.lock:
                    self.progress.set_fraction(1/3.0)
                subprocess.check_output(['git', 'pull', '--rebase', 'origin'],
                                        cwd=self.repodir,
                                        stderr=subprocess.STDOUT)
                with gdk.lock:
                    self.progress.set_fraction(2/3.0)
            else:
                with gdk.lock:
                    self.progress.set_text('Cloning %s...' %
                                           os.path.basename(self.repository))
                subprocess.check_output(['git', 'clone', self.repository,
                                        self.repodir],
                                        stderr=subprocess.STDOUT)
                with gdk.lock:
                    self.progress.set_fraction(2/3.0)
            self.download_succeeded = True
        except subprocess.CalledProcessError, err:
            with gdk.lock:
                self.set_error(err.output)
            return

        with gdk.lock:
            self.progress.set_text('Loading releases...')

        try:
            # Parse the releases found in the repository
            for dirname, dirs, filenames in os.walk(self.repodir):
                dirs[:] = [x for x in dirs if not x.startswith('.')]
                filenames[:] = [x for x in filenames if x.endswith('.yaml')]
                filenames[:] = [os.path.join(dirname, x) for x in filenames]
                for filename in filenames:
                    with open(filename) as f:
                        data = yaml.load(f)
                        release = Release(filename, data)
                        self.releases.append(release)
        except Exception, err:
            with gdk.lock:
                self.set_error('%s' % err)
                self.progress.set_fraction(0.0)
                return

        with gdk.lock:
            self.progress.set_text('Finished')
            self.progress.set_fraction(1.0)
            self.notify_complete()

    def is_complete(self):
        return self.download_succeeded and self.releases

    def result(self):
        return {
            'repodir': self.repodir,
            'releases': self.releases
        }
