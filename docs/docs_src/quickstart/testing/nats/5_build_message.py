from propan.test.nats import build_message

from main import healthcheck

def test_publish(test_broker):
    msg = build_message("ping", "ping")
    assert (await healthcheck(msg)) == "pong"