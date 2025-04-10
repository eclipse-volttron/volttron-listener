# -*- coding: utf-8 -*- {{{
# ===----------------------------------------------------------------------===
#
#                 Installable Component of Eclipse VOLTTRON
#
# ===----------------------------------------------------------------------===
#
# Copyright 2022 Battelle Memorial Institute
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may not
# use this file except in compliance with the License. You may obtain a copy
# of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.
#
# ===----------------------------------------------------------------------===
# }}}

import time
from pathlib import Path
from unittest.mock import MagicMock

import gevent
from cattrs.fns import identity
from volttrontesting import PlatformWrapper
from volttron.client.known_identities import CONTROL

from volttrontesting.platformwrapper import InstallAgentOptions


def test_startup_instance(volttron_instance: PlatformWrapper):
    assert volttron_instance.is_running()

    # Agent install path based upon root of this repository
    agent_pth = Path(__file__).parent.parent.resolve().as_posix()

    vi = volttron_instance
    assert vi is not None
    assert vi.is_running()

    # agent identity should be
    auuid = vi.install_agent(agent_dir=agent_pth, install_options=InstallAgentOptions(start=False))
    assert auuid is not None
    time.sleep(1)
    started = vi.start_agent(auuid)

    assert started
    assert vi.is_agent_running(auuid)
    listening = vi.build_agent(identity="world")
    listening.callback = MagicMock(name="callback")
    listening.callback.reset_mock()

    assert listening.core.identity
    agent_identity = listening.vip.rpc.call(CONTROL, 'agent_vip_identity', auuid).get(timeout=10)
    listening.vip.pubsub.subscribe(peer='pubsub',
                                   prefix='heartbeat/{}'.format(agent_identity),
                                   callback=listening.callback)

    # default heartbeat for core listener is 5 seconds.
    # sleep for 10 just in case we miss one.
    gevent.sleep(10)

    assert listening.callback.called
    call_args = listening.callback.call_args[0]
    # peer, sender, bus, topic, headers, message
    assert call_args[0] == 'pubsub'
    assert call_args[1] == agent_identity
    assert call_args[2] == ''
    assert call_args[3].startswith(f'heartbeat/{agent_identity}')
    assert 'max_compatible_version' in call_args[4]
    assert 'min_compatible_version' in call_args[4]
    assert 'TimeStamp' in call_args[4]
    assert 'GOOD' in call_args[5]

    # TODO: Setup test in platform testing to deal with the stop issue.
    # stopped = vi.stop_agent(auuid)
    # print('STOPPED: ', stopped)
    # removed = vi.remove_agent(auuid)
    # print('REMOVED: ', removed)
    # listening.core.stop()
