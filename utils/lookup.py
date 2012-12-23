# vi:set sw=4 sts=4 ts=4 et nocindent:
#
# Copyright (C) 2006, 2012 Jannis Pohlmann <jannis.pohlmann@codethink.co.uk>
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
import sys


class Lookup:

    def __init__(self):
        self.paths = set()
        self.paths.add(".")
        for path in sys.path:
            self.paths.add(path)

    def icon(self, name):
        return self.lookup(os.path.join('data', 'icons', name))

    def ui(self, name):
        return self.lookup(os.path.join('data', 'ui', name))

    def data(self, file):
        return self.lookup(os.path.join('data', name))

    def lookup(self, relpath):
        for dirname in self.paths:
            fullpath = os.path.join(dirname, "baserock-installer", relpath)
            if os.path.isfile(fullpath):
                return fullpath
            fullpath = os.path.join(dirname, relpath)
            if os.path.isfile(fullpath):
                return fullpath
        return name
