import curses
import time
import os
from core import reader

def choose_file(stdscr):
    all_items = os.listdir('.')
    files = []
    for f in all_items:
        if os.path.isfile(f):
            files.append(f)
    if len(files) == 0:
        return None
    selected = 0
    num_files = len(files)
    while True:
        stdscr.clear()
        for idx in range(num_files):
            filename = files[idx]
            if idx == selected:
                prefix = "> "
            else:
                prefix = "  "
            stdscr.addstr(idx, 0, prefix + filename)
        stdscr.refresh()
        key = stdscr.getch()
        if key == curses.KEY_UP:
            selected = selected - 1
            if selected < 0:
                selected = num_files - 1
        elif key == curses.KEY_DOWN:
            selected = selected + 1
            if selected >= num_files:
                selected = 0
        elif key == 10 or key == 13:
            chosen_file = files[selected]
            return chosen_file

def main(stdscr):
    filename = choose_file(stdscr)
    if filename is None:
        return
    f = open(filename, 'r')
    text = f.read()
    f.close()
    r = reader(text)
    while r.has_next() == True:
        stdscr.clear()
        word = r.next_word()
        stdscr.addstr(0, 0, word)
        stdscr.refresh()
        delay = r.get_delay()
        time.sleep(delay)

if __name__ == "__main__":
    curses.wrapper(main)

