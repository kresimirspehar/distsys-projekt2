import asyncio
import aiohttp
import pandas as pd

zad = []
rez = []

IdKlijenti = list(range(1, 10001))
df = pd.read_json("./data.json", lines=True)

KlijentRd = int(len(df) / len(IdKlijenti))

klijenti = {}
for klijent_id in IdKlijenti:
    pocetni_index = (klijent_id - 1) * KlijentRd
    end_index = pocetni_index + KlijentRd
    codes = []
    for i, row in df.iloc[pocetni_index + 1:end_index + 1].iterrows():
        codes.append(row["content"])
    klijenti[klijent_id] = codes


print("Dataframe je učitan.")


async def send_data():
    global zad
    global rez

    async with aiohttp.ClientSession(connector=aiohttp.TCPConnector(limit=100, ssl=False)) as session:
        for klijent_id, codes in klijenti.items():
            zad.append(asyncio.create_task(session.get(
                "http://127.0.0.1:8080/", json={"client": klijent_id, "codes": codes})))

        print("Podaci uspješno poslani.")
        rez = await asyncio.gather(*zad)
        rez = [await response.json() for response in rez]

asyncio.get_event_loop().run_until_complete(send_data())


for rezultati in rez:
    print("Prosjecan broj slova koji sadrzi python kod od klijenta (",
          rezultati.get("client"), ") je", rezultati.get("prosjekrijeci"))
