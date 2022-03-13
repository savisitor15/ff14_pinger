import json
import logging
import asyncio
import aioping
import curses
import typing

DCfilename = "server_list.json"
#Setup logging
logging.basicConfig(level=logging.INFO)

class DataCenter():
    def __init__(self,name:str='',ip:str=''):
        self.name = name
        self.ip = ip
        self.delay = 0

    def update_delay(self, new_delay:int=0):
        self.delay = new_delay

    def __eq__(self, other : 'DataCenter'):
        return isinstance(other, DataCenter) and (self.name == other.name or self.ip == other.ip)

    def __hash__(self):
        return hash(f"{self.name:20}{self.ip:16}")
    
    def __str__(self):
        return f"name: {self.name:20}    ip: {self.ip:16}    delay: {self.delay:10}"

async def DC_ping(DC: DataCenter=None):
    while True:
        try:
            logging.debug(f"Running ping for {DC.name}")
            delay = await aioping.ping(DC.ip) * 1000
            delay = round(delay)
            logging.debug(f"Ping response from DC {DC.name} took {delay} ms")
            DC.update_delay(delay)
        except Exception as e:
            logging.warning(f"Ping time out with {DC.name}")
            logging.debug(e)
            DC.update_delay(-1)
        await asyncio.sleep(4)

async def DC_update(DCArray : set):
        output = await asyncio.gather(*[
            DC_ping(_DC) for _DC in DCArray
        ])
        logging.debug(output)

async def main():
    DataCenters = set()
    # get the raw datacenter data
    with open(DCfilename, 'r') as fp:
        DCRaw = json.load(fp)
    for k in DCRaw.keys():
        DC = DataCenter(k, (DCRaw.get(k).get('ip') or '127.0.0.1'))
        DataCenters.add(DC)
    asyncio.create_task(DC_update(DataCenters),name="DCUpdate")
    while True:
    # at this point we should have the data centers loaded
        await asyncio.sleep(5)
        logging.info("="*30)
        for i in DataCenters:
            logging.info(i)
        logging.info("="*30)


if __name__ == "__main__":

    asyncio.run(main())
    # at this point we should have the data centers loaded
    #main_ev_loop.run_until_complete(DC_update(DataCenters))