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
import signal
import subprocess

from vm.virtualization import *


class VirtualBox(Virtualization):

    def __init__(self):
        pass

    def name(self):
        return 'VirtualBox'

    def create(self, vm):
        try:
            self.vboxmanage('createvm', '--name', vm, '--ostype', 'Linux26_64',
                            '--register')
        except:
            raise VMExistsError(vm)

        # TODO Make VM memory configurable
        try:
            self.vboxmanage('modifyvm', vm, '--ioapic', 'on')
        except:
            raise VMConfigurationError(
                    vm, 'hardware acceleration could not be enabled')

        try:
            self.vboxmanage('modifyvm', vm, '--memory', '1024')
        except:
            raise VMConfigurationError(vm, 'memory could not be set')

        try:
            self.vboxmanage('modifyvm', vm, '--nic1', 'nat')
        except:
            raise VMConfigurationError(
                    vm, 'NAT networking could not be enabled')

    def setup_port_forwarding(self, vm, host_port, client_port):
        try:
            self.vboxmanage('modifyvm', vm, '--natpf1',
                            'ssh,tcp,,%i,,%i' % (host_port, client_port))
        except:
            raise VMConfigurationError(
                    vm, 'SSH port forwarding could not be set up')

    def prepare_disk(self, vm, image):
        disk = '%s.vdi' % image

        try:
            if os.path.exists(disk):
                os.remove(disk)
        except:
            raise VMConfigurationError(vm, 'old disk could not be deleted')

        try:
            # FIXME Do not hard-code this. Define it as part of the
            # release information instead.
            size = 2147483648

            p1 = subprocess.Popen(['gzip', '-cd', image],
                                  stdout=subprocess.PIPE)
            p2 = subprocess.Popen(['VBoxManage', 'convertfromraw', 'stdin',
                                   disk, '%i' % size],
                                   stdin=p1.stdout, stdout=subprocess.PIPE)
            p1.stdout.close()
            p2.communicate()
        except:
            raise VMConfigurationError(vm, 'disk could not be created')

        return disk

    def attach_disk(self, vm, index, disk):
        try:
            self.vboxmanage('storagectl', vm, '--name', 'SATA Controller',
                            '--add', 'sata', '--bootable', 'on',
                            '--sataportcount', '2')
        except:
            pass
        try:
            self.vboxmanage('storageattach', vm,
                            '--storagectl', 'SATA Controller',
                            '--port', str(index), '--device', str(index),
                            '--type', 'hdd', '--medium', disk)
        except:
            raise VMConfigurationError(vm, 'disk could not be attached')

    def start(self, vm):
        try:
            self.vboxmanage('startvm', vm)
        except:
            raise VMStartError(vm)

    def vboxmanage(self, *args, **kwargs):
        args = ['VBoxManage'] + list(args)
        return subprocess.check_output(args, **kwargs)


Implementation = VirtualBox
