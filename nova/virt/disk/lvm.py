# vim: tabstop=4 shiftwidth=4 softtabstop=4

# Copyright 2011 Red Hat, Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.
"""Support for mounting lvm imagese"""

import os

from nova import utils
from nova.openstack.common import cfg
from nova.openstack.common import jsonutils
from nova.openstack.common import log as logging
from nova.virt.disk import mount
LOG = logging.getLogger(__name__)

class Mount(mount.Mount):
    """mount support for raw lvm images."""
    mode = 'lvm'
    device_id_string = mode

    def map_dev(self):
        """Map partitions of the device to the file system namespace."""
        assert(os.path.exists(self.image))
        vg = FLAGS.libvirt_images_volume_group
        automapped_path = '/dev/%sp%s' % (os.path.basename(self.image),
                                              self.partition)
        if self.partition == -1:
            self.error = _('partition search unsupported with %s') % self.mode
        elif self.partition and not os.path.exists(automapped_path):
            mapper_name = os.path.basename(self.image).split('-')
            map_path = '/dev/mapper/%s-%s--%s%s' % (vg, mapper_name[0],
                                                   mapper_name[1],
                                                   self.partition)
            assert(not os.path.exists(map_path))

            # Note kpartx can output warnings to stderr and succeed
            # Also it can output failures to stderr and "succeed"
            # So we just go on the existence of the mapped device
            _out, err = utils.trycmd('kpartx', '-a', self.image,
                                     run_as_root=True, discard_warnings=True)


            # Note kpartx does nothing when presented with a raw image,
            # so given we only use it when we expect a partitioned image, fail
            if not os.path.exists(map_path):
                if not err:
                    err = _('partition %s not found') % self.partition
                self.error = _('Failed to map partitions: %s') % err
            else:
                self.mapped_device = map_path
                self.mapped = True
        elif self.partition and os.path.exists(automapped_path):
            self.mapped_device = automapped_path
            self.mapped = True
            self.automapped = True
        else:
            self.mapped_device = self.image
            self.mapped = True

        return self.mapped

    def unmap_dev(self):
        """Remove partitions of the device from the file system namespace."""
        if not self.mapped:
            return
        if self.partition and not self.automapped:
            utils.execute('kpartx', '-d', self.image, run_as_root=True)
        
        self.mapped = False
        self.automapped = False
