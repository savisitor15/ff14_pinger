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

    def __lt__(self, other: 'DataCenter'):
        return isinstance(other, DataCenter) and (self.name < other.name)

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

def blstr(strin:str) -> str:
    return f'{strin} \n'

def output(stdscr = None, DCs : set = None):
    if not stdscr:
        logging.warning("No Terminal screen provided")
        return
    if not DCs:
        logging.warning("No DataCenter data provided")
        return
    stdscr.clear()
    stdscr.addstr(blstr("="*30))
    for i in DCs:
        stdscr.addstr(blstr(i))
    stdscr.addstr(blstr("="*30))
    stdscr.refresh()

async def main():
    DataCenters = set()
    running = True
    # Create terminal
    stdscr = curses.initscr()
    curses.noecho()
    curses.cbreak()
    #non blocking input
    stdscr.nodelay(1)
    # get the raw datacenter data
    with open(DCfilename, 'r') as fp:
        DCRaw = json.load(fp)
    for k in DCRaw.keys():
        DC = DataCenter(k, (DCRaw.get(k).get('ip') or '127.0.0.1'))
        DataCenters.add(DC)
    # order the list
    DataCenters = sorted(DataCenters)
    asyncio.create_task(DC_update(DataCenters),name="DCUpdate")
    try:
        while running:
            c = stdscr.getch()
            if c == ord('q'):
                running = False
            # at this point we should have the data centers loaded
            if running:
                await asyncio.sleep(5)
                output(stdscr, DataCenters)
            else:

                stdscr.clear()
                stdscr.addstr(blstr('Exiting...'))
                stdscr.refresh()
                # this won't show for more than a milisecond add a slight delay
                await asyncio.sleep(1)
                break
    finally:
        curses.echo()
        curses.nocbreak()
        curses.endwin()


if __name__ == "__main__":
    asyncio.run(main())