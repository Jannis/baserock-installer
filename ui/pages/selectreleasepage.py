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
import subprocess
import threading

from gi.repository import Gdk, GLib, Gtk

import utils.urls

from ui.pages.page import Page


class SelectReleasePage(Page):

    def __init__(self, assistant):
        Page.__init__(self, assistant)

        label, box = self.start_section('Select Release')
        text = self.create_text(
                'In order to set up a Baserock development or runtime '
                'environment, please select one of the releases below.')
        box.pack_start(text, False, False, 0)

        self.model = Gtk.ListStore(str, object)
        self.combo = Gtk.ComboBox.new_with_model(self.model)
        self.combo.connect('changed', self.selection_changed)
        renderer = Gtk.CellRendererText()
        self.combo.pack_start(renderer, True)
        self.combo.add_attribute(renderer, 'text', 0)
        self.combo.show()
        box.pack_start(self.combo, False, False, 0)

    def selection_changed(self, combo):
        self.notify_complete()

    def prepare(self, results):
        self.model.clear()
        releases = results['download-releases']
        for release in releases:
            self.model.append([release.title, release])
        self.combo.set_active(0)

    def is_complete(self):
        return True

    def result(self):
        title, release = self.model.get(self.combo.get_active_iter(), 0, 1)
        return release
