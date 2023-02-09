from aiohttp import web
import random
import asyncio
import re
import string

routes = web.RouteTableDef()


async def izbroj_rijeci(data):
    words = re.sub(f"[{string.punctuation}]", "", data).split()
    return len(words)


async def random_sleep(min_time, max_time):
    wait_time = random.uniform(min_time, max_time)
    await asyncio.sleep(wait_time)


@routes.get("/")
async def function(request):
    try:
        await random_sleep(0.1, 0.3)

        data = await request.json()
        result = await izbroj_rijeci(data["data"])

        await random_sleep(0.1, 0.3)

        return web.json_response({"name": "WORKER", "status": "OK", "RijeciBr": result}, status=200)
    except Exception as e:
        return web.json_response({"name": "WORKER", "error": str(e)}, status=500)

app = web.Application()
app.router.add_routes(routes)
web.run_app(app, port=8083)
