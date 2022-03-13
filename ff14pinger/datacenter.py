import logging
import asyncio
import aioping
import os.path
import console
import json

class DataCenter():
    def __init__(self,name:str='',ip:str='')->'DataCenter':
        self.name = name
        self.ip = ip
        self.delay = 0

    def update_delay(self, new_delay:int=0)->None:
        self.delay = new_delay

    def __eq__(self, other : 'DataCenter')->bool:
        return isinstance(other, DataCenter) and (self.name == other.name or self.ip == other.ip)

    def __lt__(self, other: 'DataCenter')->bool:
        return isinstance(other, DataCenter) and (self.name < other.name)

    def __hash__(self)->int:
        return hash(f"{self.name:20}{self.ip:16}")
    
    def __str__(self)->str:
        output = f"name: {self.name}"
        output = f"{output:<20}"
        output = f"{output} ip: {self.ip:>16}"
        output = f"{output} delay: {self.delay:>10} ms"
        return output


def DCLoad(fname:str)->'DCHandler':
    DataCenters = set()
    if os.path.exists(fname):
        # get the raw datacenter data
        with open(fname, 'r') as fp:
            DCRaw = json.load(fp)
        for k in DCRaw.keys():
            DC = DataCenter(k, (DCRaw.get(k).get('ip') or '127.0.0.1'))
            DataCenters.add(DC)
    return DCHandler(DataCenters)



class DCHandler():
    def __init__(self, DCArrIN)->'DCHandler':
        DCArrIN = sorted(DCArrIN)
        self.DataCenters : list[DataCenter]= DCArrIN

    def pretty_print(self):
        output = list()
        defcol = console.fg.default
        green = console.fg.green
        yellow = console.fg.yellow
        red = console.fg.red
        for i in self.DataCenters:
            color = ""
            tmp = ""
            if i.delay > 200 and i.delay < 300:
                # Orange
                color = yellow
            elif i.delay > 300:
                # Red
                color = red
            else:
                #green
                color = green
            tmp = f"name: {console.fg.cyan}{i.name}{defcol}"
            tmp = f"{tmp:<20}"
            tmp = f"{tmp} ip: {i.ip:>16}"
            tmp = f"{tmp} {color}delay: {i.delay:>10} ms{defcol}"
            output.append(tmp)
            
        return output

    async def start(self)->None:
        asyncio.create_task(self.DC_update(),name="DCUpdate")

    async def DC_ping(self, DC: DataCenter=None)->None:
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

    async def DC_update(self)->None:
            output = await asyncio.gather(*[
                self.DC_ping(_DC) for _DC in self.DataCenters
            ])
            logging.debug(output)