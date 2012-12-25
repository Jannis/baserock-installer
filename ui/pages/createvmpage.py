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


import os
import threading

from gi.repository import GLib, GObject, Gtk

from ui.pages.page import Page
from utils import gdk
from utils.task import Task


class SetupWorker(Task):

    def __init__(self, release, downloads, virtualization):
        Task.__init__(self)

        self.release = release
        self.downloads = downloads
        self.virt = virtualization['virtualization']
        self.vm = virtualization['vm-name']
        self.ssh_port = virtualization['ssh-port']

    def run(self):
        if self.cancellable.set_error_if_cancelled():
            return

        self.emit('started')

        if self.cancellable.set_error_if_cancelled():
            return

        self.emit('progress', 0.0, 'Creating virtual machine...')
        self.virt.create(self.vm)

        if self.cancellable.set_error_if_cancelled():
            return

        self.emit('progress', 0.1, 'Setting up SSH port forwarding...')
        self.virt.setup_port_forwarding(self.vm, self.ssh_port, 22)

        if self.cancellable.set_error_if_cancelled():
            return

        disk = None
        self.emit('progress', 0.2, 'Preparing disk...')
        image = self.downloads[0]
        disk = self.virt.prepare_disk(self.vm, image.target)

        if self.cancellable.set_error_if_cancelled():
            return

        self.emit('progress', 0.8, 'Attaching disk...')
        self.virt.attach_disk(self.vm, 0, disk)

        if self.cancellable.set_error_if_cancelled():
            return

        self.emit('progress', 1.0, 'Completed')
        self.emit('finished')

class CreateVMPage(Page):

    def __init__(self, assistant):
        Page.__init__(self, assistant)

        title, box = self.start_section('Create Virtual Machine')
        text = self.create_text(
                'This step automatically sets up your Baserock virtual '
                'machine. This involves converting the downloaded release '
                'into a format that the virtualization technology '
                'understands, creating the virtual machine and copying '
                'other downloaded files into it.')
        box.pack_start(text, False, False, 0)

        self.progress_bar = Gtk.ProgressBar()
        self.progress_bar.show()
        box.pack_start(self.progress_bar, False, False, 0)

        self.status_label = Gtk.Label('Initialising...')
        self.status_label.set_line_wrap(True)
        self.status_label.set_alignment(0.0, 0.0)
        self.status_label.show()
        box.pack_start(self.status_label, False, False, 0)

    def prepare(self, results):
        release = results['select-release']
        downloads = results['download-release']
        virtualization = results['configure-vm']

        self.worker = SetupWorker(release, downloads, virtualization)
        self.worker.connect('progress', self.progress)
        self.worker.connect('error', self.error)
        self.worker.connect('finished', self.finished)
        self.worker.start()

        self.setup_completed = False
        self.percent = 0.0
        self.status_label_text = ''

        GLib.idle_add(self.update_progress_bar)

    def progress(self, worker, percent, text):
        self.percent = percent
        self.status_label_text = text
        GLib.idle_add(self.update_progress_bar)

    def error(self, worker, error):
        self.status_label_text = '<b>Error: %s</b>' % error
        GLib.idle_add(self.update_progress_bar)

    def finished(self, worker):
        GLib.idle_add(self.update_progress_bar)
        self.setup_completed = True
        self.notify_complete()

    def update_progress_bar(self):
        self.progress_bar.set_fraction(self.percent)
        self.status_label.set_markup(self.status_label_text)
        return False

    def cancel(self):
        self.worker.cancel()

    def is_complete(self):
        return self.setup_completed
