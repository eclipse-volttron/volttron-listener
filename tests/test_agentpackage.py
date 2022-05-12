from listener.agent import ListenerAgent

from testing.volttron import TestServer


def test_agent():
    with open("/tmp/cfg.json", 'w') as fp:
        fp.write("{}")

    la = ListenerAgent(config_path="/tmp/cfg.json")
    ts = TestServer()
    ts.connect_agent(agent=la)
    assert ts
    resp = ts.trigger_setup_event('')
    assert resp.response is None
    assert resp.called_method == 'onsetup'
