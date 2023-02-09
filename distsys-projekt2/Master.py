from aiohttp import web
import random
import aiohttp
import logging
import asyncio


routes = web.RouteTableDef()

primljeni_zahtjevi = odg_zahtjev = poslani_zahtjev = zavrseno_zahtjeva = 0
zahtjevi_max = 10000
sample_size = 1000

logging.basicConfig(format='%(asctime)s - %(message)s',
                    datefmt='%H:%M:%S %d/%m/%Y ', level=logging.INFO)


N = random.randint(5, 10)
workers = {f"WorkerBr{i}": [] for i in range(1, N + 1)}
print("Trenutni:", workers)


@routes.get('/')
async def function(request):
    global N, workers, sample_size, primljeni_zahtjevi, odg_zahtjev, poslani_zahtjev, zavrseno_zahtjeva
    primljeni_zahtjevi = primljeni_zahtjevi + 1
    logging.info(
        f"Trenutni zahtjev: {primljeni_zahtjevi} od {zahtjevi_max}")

    try:
        data = await request.json()
        duljina = len(data['codes'])
        codes = '\n'.join(data['codes']).split("\n")
        data['codes'] = ["\n".join(codes[i:i+sample_size])
                         for i in range(0, len(codes), sample_size)]

        async with aiohttp.ClientSession(connector=aiohttp.TCPConnector(ssl=False)) as session:
            zad = []
            rez = []
            worker_trenutni = 1
            for i in range(len(data['codes'])):
                task = asyncio.create_task(
                    session.get(f"http://127.0.0.1:{8080 + worker_trenutni}/", json={
                                "id": data["client"], "data": data['codes'][i]})
                )
                poslani_zahtjev = poslani_zahtjev + 1
                logging.info(
                    f"Trenutni zahtjev: {poslani_zahtjev}, worker br. {worker_trenutni} obavlja zadatak.")
                zad.append(task)
                workers["WorkerBr" + str(worker_trenutni)].append(task)
                if worker_trenutni is N:
                    worker_trenutni = 1
                else:
                    worker_trenutni = worker_trenutni + 1

            rez = await asyncio.gather(*zad)
            zavrseno_zahtjeva += len(rez)
            logging.info(
                f"Trenutno: {zavrseno_zahtjeva}, {len(rez)} zadatka završena. ")
            rez = [await result.json() for result in rez]
            rez = [result["RijeciBr"] for result in rez]

        odg_zahtjev = odg_zahtjev + 1
        logging.info(
            f"Trenutni: {odg_zahtjev} / {zahtjevi_max}")
        return web.json_response({
            "name": "Master",
            "status": "Ok",
            "client": data["client"],
            "prosjekrijeci": round(sum(rez) / duljina, 2)
        }, status=200)
    except Exception as e:
        logging.exception("Error")
        return web.json_response({
            "name": "Master",
            "status": "Error",
            "message": str(e)
        }, status=500)


app = web.Application()

app.router.add_routes(routes)

web.run_app(app, port=8080, access_log=None)
