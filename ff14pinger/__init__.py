from .datacenter import DataCenter, DCHandler, DCLoad
from .ffconsole import ff14_console
import asyncio

async def main(filename = "", pretty=False):
    # get details
    handler = DCLoad(filename)
    con_handler = ff14_console()
    running = True
    await handler.start()
    while running:
        c = con_handler.get_scr().getch()
        if c == ord('q'):
            running = False
        if running:
            if pretty:
                con_handler.output(handler.pretty_print())
            else:
                con_handler.output(handler.DataCenters)
            await asyncio.sleep(5)
        else:
            con_handler.Exit()
            await asyncio.sleep(1)
            break