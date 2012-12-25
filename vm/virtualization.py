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


import subprocess


class VMExistsError(RuntimeError):

    def __init__(self, vm):
        RuntimeError.__init__(self, 'Virtual machine "%s" already exists' % vm)


class VMConfigurationError(RuntimeError):

    def __init__(self, vm, msg):
        RuntimeError.__init__(
                self, 'Failed to configure virtual machine "%s": %s' (vm, msg))


class VMStartError(RuntimeError):

    def __init__(self, vm):
        RuntimeError.__init__(
                self, 'Failed to start virtual machine "%s"' % vm)


class Virtualization(object):

    def __init__(self):
        pass

    def name(self):
        return NotImplemented

    def create(self, vm):
        return NotImplemented

    def setup_port_forwarding(self, vm, host_port, client_port):
        return NotImplemented

    def prepare_disk(self, vm, image):
        return NotImplemented

    def attach_disk(self, vm, index, disk):
        return NotImplemented

    def start(self, vm):
        return NotImplemented
