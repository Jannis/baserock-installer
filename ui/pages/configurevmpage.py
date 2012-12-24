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

    def prepare(self, results):
        self.release = results['select-release']
        self.downloads = results['download-release']

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
        return True
