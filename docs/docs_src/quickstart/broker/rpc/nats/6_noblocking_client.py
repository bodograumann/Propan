import asyncio
from propan import NatsBroker

broker = NatsBroker("nats://localhost:4222")

@broker.handle("reply")
async def get_message(m: str):
    assert m == "pong!"  # <-- take the RPC response

async def main():
    await broker.start()

    await broker.publish(
        "hello", "ping",
        reply_to="reply"
    )

    try:
        await asyncio.Future()
    finally:
        await broker.close()

asyncio.run(main())