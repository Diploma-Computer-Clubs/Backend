import asyncio


def run_async_task(coro):
    async def _run():
        from src.shared.configurations.database import engine

        try:
            return await coro
        finally:
            await engine.dispose()

    return asyncio.run(_run())
