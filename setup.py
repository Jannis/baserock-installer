#!/usr/bin/python
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


import info

from distutils.core import setup


setup(
    name = 'baserock-installer',
    version = info.version,
    description = 'Graphical installer for Baserock',
    author = 'Jannis Pohlmann',
    author_email = 'jannis.pohlmann@codethink.co.uk',
    url = 'http://github.com/jannis/baserock-installer',
    license = 'GNU GPLv2',
    packages = [
        'baserock-installer',
        'baserock-installer/ui',
        'baserock-installer/utils',
        'baserock-installer/standards',
        'baserock-installer/vm',
    ],
    package_dir = {
        'baserock-installer' : '.',
        'baserock-installer/ui' : 'ui',
        'baserock-installer/utils' : 'utils',
        'baserock-installer/standards' : 'standards',
        'baserock-installer/vm' : 'vm',
    },
    package_data = {
    },
    scripts = [
        'baserock-installer'
    ],
)
