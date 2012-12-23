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


from gi.repository import Gtk

from ui.pages.page import Page


class FinishPage(Page):

    def __init__(self):
        Page.__init__(self)

        label, box = self.start_section('Thanks for installing Baserock!')
        text = self.create_text(
                'Your development or runtime environment should now be '
                'configured and ready to use. If this is not the case, '
                'please join us in <tt>#baserock</tt> on the FreeNode IRC '
                'network.')
        box.pack_start(text, False, True, 0)

        label, box = self.start_section('Start Baserock now?')
        text = self.create_text(
                'If you want to start Baserock now, simply press the '
                'button below.')
        box.pack_start(text, False, True, 0)

        button = Gtk.Button()
        image = Gtk.Image.new_from_stock(
                Gtk.STOCK_EXECUTE, Gtk.IconSize.BUTTON)
        button.set_image(image)
        button.set_label('Start Baserock')
        button.show()
        box.pack_start(button, False, False, 0)
