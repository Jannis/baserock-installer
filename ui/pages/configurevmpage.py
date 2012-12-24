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


import pkgutil
import os

from gi.repository import Gtk

from ui.pages.page import Page


class ConfigureVMPage(Page):

    def __init__(self, assistant):
        Page.__init__(self, assistant)

        title, box = self.start_section('Configure Virtual Machine')

        grid = Gtk.Grid()
        grid.set_column_spacing(12)
        grid.set_row_spacing(6)
        grid.show()
        box.pack_start(grid, False, False, 0)

        label = Gtk.Label('Virtualization:')
        label.set_halign(Gtk.Align.START)
        label.show()
        grid.attach(label, 0, 1, 1, 1)

        self.model = Gtk.ListStore(str, object)
        self.combo = Gtk.ComboBox(model=self.model)
        self.combo.connect('changed', self.virtualization_changed)
        renderer = Gtk.CellRendererText()
        self.combo.pack_start(renderer, True)
        self.combo.add_attribute(renderer, 'text', 0)
        self.combo.show()
        grid.attach(self.combo, 1, 1, 1, 1)

        label = Gtk.Label('VM Name:')
        label.set_halign(Gtk.Align.START)
        label.show()
        grid.attach(label, 0, 2, 1, 1)

        self.vm_name = Gtk.Entry()
        self.vm_name.set_halign(Gtk.Align.FILL)
        self.vm_name.set_hexpand(True)
        self.vm_name.show()
        grid.attach(self.vm_name, 1, 2, 4, 1)

        label = Gtk.Label('SSH Forward Port:')
        label.set_halign(Gtk.Align.START)
        label.show()
        grid.attach(label, 0, 3, 1, 1)

        self.ssh_port = Gtk.SpinButton()
        self.ssh_port.set_range(1, 9999)
        self.ssh_port.set_value(2222)
        self.ssh_port.show()
        grid.attach(self.ssh_port, 1, 3, 1, 1)

    def prepare(self, results):
        self.release = results['select-release']
        self.downloads = results['download-release']

        self.vm_name.set_text(self.release.title)

        self.model.clear()

        import vm
        for importer, modname, ispkg in pkgutil.iter_modules(vm.__path__):
            module = __import__('vm.%s' % modname,
                                fromlist='Implementation')
            if hasattr(module, 'Implementation'):
                instance = module.Implementation()
                self.model.append([instance.name(), instance])

        self.combo.set_active(0)

    def virtualization_changed(self, combo):
        self.notify_complete()

    def is_complete(self):
        return self.vm_name.get_text() and self.ssh_port.get_value()

    def result(self):
        model_iter = self.combo.get_active_iter()
        name, virtualization = self.model.get(model_iter, 0, 1)
        return {
            'virtualization': virtualization,
            'vm-name': self.vm_name.get_text(),
            'ssh-port': self.ssh_port.get_value()
        }
