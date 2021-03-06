#!/usr/bin/env python
# vim: tabstop=4 shiftwidth=4 softtabstop=4
#
# Copyright (c) 2012 Rackspace Hosting
# All Rights Reserved.
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.

"""Starter script for Nova Cells Service."""

import sys

from oslo.config import cfg

from nova import config
from nova.openstack.common import log as logging
from nova import service
from nova import utils

CONF = cfg.CONF
CONF.import_opt('topic', 'nova.cells.opts', group='cells')
CONF.import_opt('manager', 'nova.cells.opts', group='cells')


def main():
    config.parse_args(sys.argv)
    logging.setup('nova')
    utils.monkey_patch()
    server = service.Service.create(binary='nova-cells',
                                    topic=CONF.cells.topic,
                                    manager=CONF.cells.manager)
    service.serve(server)
    service.wait()
