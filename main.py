from source import app
from uvicorn import Config, Server
import asyncio


if __name__ == "__main__":
    config = Config(
        app=app,
        host="0.0.0.0",
        port=8080
    )
    server = Server(config)
    loop = asyncio.get_event_loop()
    loop.run_until_complete(server.serve())
