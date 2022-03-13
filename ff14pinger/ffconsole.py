import logging
import curses


class ff14_console():
    def __init__(self):
        # Create the main window
        self.stdscr = curses.initscr()
        # Setup curses
        curses.noecho() # No echo mode (No Frame buffering!)
        curses.cbreak() # Input mode
        self.stdscr.nodelay(1) # non-blocking input handling


    def get_scr(self):
        return self.stdscr
    
    def blstr(self, strin:str) -> str:
        return f'{strin} \n'

    def is_array(self, obj:object)->bool:
        try:
            getattr(obj,'__class_getitem__')
        except:
            return False
        else:
            return True
    
    def Exit(self):
        self.output("Exiting...")

    def output(self, Arr : object = None):
        blstr = self.blstr
        if not self.stdscr:
            logging.warning("No Terminal screen provided")
            return
        if not Arr:
            logging.warning("No DataCenter data provided")
            return
        self.stdscr.clear()
        self.stdscr.addstr(blstr(f"{'=':=<20}{'*':*^20}{'=':=>20}"))
        if self.is_array(Arr):
            for i in Arr:
                self.stdscr.addstr(blstr(i))
        else:
            self.stdscr.addstr(blstr(Arr))
        self.stdscr.addstr(blstr(f"{'=':=<20}{'*':*^20}{'=':=>20}"))
        self.stdscr.refresh()

    def __del__(self):
        curses.echo()
        curses.nocbreak()
        curses.endwin()