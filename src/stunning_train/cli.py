import curses
import time
from stunning_train.core import reader

def main(stdscr):
    r = reader(" test")
    while r.has_next():
        stdscr.clear()
        stdscr.addstr(0, 0, r.next_word())
        stdscr.refresh()
        time.sleep(r.get_delay())

if __name__ == "__main__":
    curses.wrapper(main)
