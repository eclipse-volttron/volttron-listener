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

import logging
from pathlib import Path
import os

from volttron.types.agent_context import AgentOptions

from listener.agent import ListenerAgent, _log

from volttrontesting import TestServer
import shutil


def test_agent(monkeypatch):
    with open("/tmp/cfg.json", 'w') as fp:
        fp.write("{}")

    try:
        os.environ['AGENT_VIP_IDENTITY'] = 'brown.cow'
        ts = TestServer()

        la: ListenerAgent = ts.instantiate_agent(ListenerAgent, config_path="/tmp/cfg.json")

        assert la.core

        # la = ListenerAgent(config_path="/tmp/cfg.json")
        ts.connect_agent(agent=la, logger=_log)
        assert ts
        resp = ts.trigger_setup_event(identity_or_agent=la)
        assert resp.response is None
        assert resp.called_method == 'onsetup'

        resp = ts.trigger_start_event(identity_or_agent=la)
        assert resp.response is None
        assert resp.called_method == 'onstart'


        ts.publish("atestmessage", message="Woot we got this")
        assert len(ts.get_published_messages()) == 1

        for msg in ts.get_published_messages():
            assert "atestmessage" == msg.topic
            assert None is msg.headers
            assert '' == msg.bus
            assert "Woot we got this" == msg.message

        assert len(ts.get_server_log()) > 1

    finally:
        shutil.rmtree(TestServer.__volttron_home__)
        Path("/tmp/cfg.json").unlink(missing_ok=True)


def test_agent_pubsub():
    try:
        with open("/tmp/cfg.json", 'w') as fp:
            fp.write("{}")

        ts = TestServer()
        la = ts.instantiate_agent(ListenerAgent, config_path="/tmp/cfg.json")
        ts.connect_agent(agent=la, logger=_log)
        assert ts
        resp = ts.trigger_setup_event(la)
        assert resp.response is None
        assert 'onsetup' == resp.called_method
        resp = ts.trigger_start_event(la)

        ts.publish('foo')
        assert resp.response is None
        assert 'onstart' == resp.called_method
    finally:
        Path("/tmp/cfg.json").unlink(missing_ok=True)
