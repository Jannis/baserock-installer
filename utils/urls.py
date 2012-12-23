# vi:set sw=4 sts=4 ts=4 et nocindent:
#
# Copyright (C) 2012 Codethink Limited
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


import string


def quote_url(url):
    ''' Convert URIs to strings that only contain digits, letters, % and _. '''
    valid_chars = string.digits + string.letters + '%_'
    transl = lambda x: x if x in valid_chars else '_'
    return ''.join([transl(x) for x in url])
