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


class WelcomePage(Page):

    def __init__(self, assistant):
        Page.__init__(self, assistant)

        self.repository = None

        label, box = self.start_section('Welcome to the Baserock installer!')
        text = self.create_text(
                'This wizard will guide you through the installation of '
                'Baserock. You will be able to select a Baserock release '
                'and will be helped to set up your development or runtime '
                'environment step by step.\n'
                '\n'
                'If you encounter any problems during the installation or '
                'have any further questions, please join us in '
                '<tt>#baserock</tt> on the FreeNode IRC network.')
        box.pack_start(text, False, True, 0)

        label, box = self.start_section('Release Repository')
        text = self.create_text(
                'Please enter the URL of a Baserock release repository into '
                'the following field. This URL should be in a format that Git '
                'understands, e.g.\n'
                '\n'
                '<tt>ssh://user@host/path/to/repo.git</tt>\n'
                '<tt>git://host:path/to/repo.git</tt>')
        box.pack_start(text, False, True, 0)

        hbox = Gtk.HBox(False, 12)
        hbox.show()
        box.pack_start(hbox, False, True, 0)

        label = Gtk.Label('Repository:')
        label.show()
        hbox.pack_start(label, False, True, 0)

        entry = Gtk.Entry()
        entry.set_activates_default(True)
        entry.connect('changed', self.repository_changed)
        entry.connect('activate', self.repository_changed)
        entry.set_placeholder_text(
                'git://trove.baserock.org/baserock/baserock/releases.git')
        entry.show()
        hbox.add(entry)

    def repository_changed(self, entry):
        self.repository = entry.get_text()
        self.notify_complete()

    def is_complete(self):
        return self.repository and len(self.repository) > 0

    def result(self):
        return self.repository
