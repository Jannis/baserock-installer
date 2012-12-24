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


class SetupWorker(GObject.GObject):

    __gsignals__ = {
        'started': (
            GObject.SIGNAL_RUN_LAST,
            GObject.TYPE_NONE,
            ()
        ),
        'finished': (
            GObject.SIGNAL_RUN_LAST,
            GObject.TYPE_NONE,
            ()
        ),
        'progress': (
            GObject.SIGNAL_RUN_LAST,
            GObject.TYPE_NONE,
            (float, str),
        ),
        'error': (
            GObject.SIGNAL_RUN_LAST,
            GObject.TYPE_NONE,
            (str, ),
        ),
    }

    def __init__(self, release, downloads, virtualization):
        GObject.GObject.__init__(self)

        self.release = release
        self.downloads = downloads
        self.virt = virtualization['virtualization']
        self.vm = virtualization['vm-name']
        self.ssh_port = virtualization['ssh-port']

        self.thread = threading.Thread(target=self.setup)

    def start(self):
        self.cancelled = False
        self.thread.start()

    def cancel(self):
        self.cancelled = True
        self.thread.join()

    def setup(self):
        self.emit('started')

        if not self.cancelled:
            self.emit('progress', 0.0, 'Creating virtual machine...')
            self.virt.create(self.vm)

        if not self.cancelled:
            self.emit('progress', 0.1, 'Setting up SSH port forwarding...')
            self.virt.setup_port_forwarding(self.vm, self.ssh_port, 22)

        disk = None
        if not self.cancelled:
            self.emit('progress', 0.2, 'Preparing disk...')
            image = self.downloads[0]
            disk = self.virt.prepare_disk(self.vm, image.target)

        if not self.cancelled:
            self.emit('progress', 0.8, 'Attaching disk...')
            self.virt.attach_disk(self.vm, 0, disk)

        if not self.cancelled:
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

        self.progress = Gtk.ProgressBar()
        self.progress.show()
        box.pack_start(self.progress, False, False, 0)

        self.info = Gtk.Label('Initialising...')
        self.info.set_alignment(0.0, 0.0)
        self.info.show()
        box.pack_start(self.info, False, False, 0)

    def prepare(self, results):
        release = results['select-release']
        downloads = results['download-release']
        virtualization = results['configure-vm']

        self.worker = SetupWorker(release, downloads, virtualization)
        self.worker.connect('progress', self.progress_reported)
        self.worker.connect('finished', self.finished)
        self.worker.start()

        self.setup_completed = False
        self.percent = 0.0
        self.info_text = ''

        GLib.idle_add(self.update_progress)

    def progress_reported(self, worker, percent, text):
        print 'progress reported: %f, %s' % (percent, text)
        self.percent = percent
        self.info_text = text

    def update_progress(self):
        self.progress.set_fraction(self.percent)
        self.info.set_text(self.info_text)
        return True

    def finished(self, worker):
        self.setup_completed = True
        self.notify_complete()

    def cancel(self):
        self.worker.cancel()

    def is_complete(self):
        return self.setup_completed
