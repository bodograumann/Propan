from uuid import uuid4

import pytest
import pytest_asyncio

from pydantic import BaseSettings

from propan.brokers import RabbitBroker, RabbitQueue
from propan.utils import context as global_context


class Settings(BaseSettings):
    url = "amqp://guest:guest@localhost:5672/"

    host = "localhost"
    port = 5672
    login = "guest"
    password = "guest"

    queue = "test_queue"


@pytest.fixture
def queue():
    name = str(uuid4())
    return RabbitQueue(name=name, declare=True)


@pytest.fixture(scope="session")
def settings():
    return Settings()


@pytest.fixture
def context():
    yield global_context
    global_context.clear()


@pytest_asyncio.fixture
async def broker(settings):
    broker = RabbitBroker(settings.url)
    yield broker
    await broker.close()
