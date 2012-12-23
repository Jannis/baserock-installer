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


from gi.repository import Gdk, Gtk

from utils.lookup import Lookup


class Header(Gtk.Frame):

    def __init__(self):
        Gtk.Frame.__init__(self)

        self.set_shadow_type(Gtk.ShadowType.NONE)

        box = Gtk.EventBox()
        box.modify_bg(Gtk.StateType.NORMAL, Gdk.color_parse('#333'))
        box.show()
        self.add(box)

        alignment = Gtk.Alignment()
        alignment.set_padding(20, 20, 20, 20)
        alignment.show()
        box.add(alignment)

        image = Gtk.Image.new_from_file(Lookup().icon('baserock-logo.png'))
        image.show()
        alignment.add(image)


class Page(Gtk.VBox):

    def __init__(self, assistant):
        Gtk.VBox.__init__(self)

        self.assistant = assistant
        
        header = Header()
        header.show()
        self.pack_start(header, False, False, 0)

        alignment = Gtk.Alignment()
        alignment.set_padding(10, 0, 0, 0)
        alignment.show()
        self.pack_start(alignment, False, False, 0)

        self.vbox = Gtk.VBox(False, 12)
        self.vbox.show()
        alignment.add(self.vbox)

    def start_section(self, title):
        alignment = Gtk.Alignment()
        alignment.set_padding(20, 0, 0, 0)
        alignment.show()
        self.vbox.pack_start(alignment, False, False, 0)

        vbox = Gtk.VBox(False, 12)
        vbox.show()
        alignment.add(vbox)

        label = Gtk.Label()
        label.set_alignment(0.0, 0.0)
        label.set_markup('<span size="large">%s</span>' % title)
        label.show()
        vbox.pack_start(label, False, False, 0)

        box = Gtk.VBox(False, 12)
        box.show()
        vbox.pack_start(box, False, False, 0)

        return label, box

    def create_text(self, text):
        label = Gtk.Label()
        label.set_alignment(0.0, 0.0)
        label.set_line_wrap(True)
        label.set_markup(text)
        label.show()
        return label

    def is_complete(self):
        return True

    def result(self):
        return None

    def prepare(self, results):
        pass

    def notify_complete(self):
        self.assistant.child_notify(self, 'complete')

    def cancel(self):
        pass
