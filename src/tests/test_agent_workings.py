import logging
from pathlib import Path

from listener.agent import ListenerAgent, _log

from testing.volttron import TestServer


def test_agent():
    with open("/tmp/cfg.json", 'w') as fp:
        fp.write("{}")

    try:
        la = ListenerAgent(config_path="/tmp/cfg.json")
        ts = TestServer()
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
        Path("/tmp/cfg.json").unlink(missing_ok=True)


def test_agent_pubsub():
    try:
        with open("/tmp/cfg.json", 'w') as fp:
            fp.write("{}")

        la = ListenerAgent(config_path="/tmp/cfg.json")
        ts = TestServer()
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
