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


class Installer(Gtk.Assistant):

    def __init__(self):
        super(Gtk.Assistant, self).__init__()
        self.connect('cancel', self.cancelled)
        self.connect('delete-event', self.cancelled)
    
    def cancelled(self, *args):
        self.quit()

    def quit(self):
        Gtk.main_quit()

    def run(self):
        self.show()
        Gtk.main()
