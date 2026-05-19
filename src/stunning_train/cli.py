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
        max_y, max_x = stdscr.getmaxyx()
        start_y = (max_y - num_files) // 2
        if start_y < 0:
            start_y = 0
        for idx in range(num_files):
            filename = files[idx]
            if idx == selected:
                prefix = "> "
            else:
                prefix = "  "
            line = prefix + filename
            line_len = len(line)
            diff_x = max_x - line_len
            x = diff_x // 2
            if x < 0:
                x = 0
            y = start_y + idx
            stdscr.addstr(y, x, line)

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
    curses.curs_set(0)
    filename = choose_file(stdscr)
    if filename is None:
        return
    f = open(filename, 'r')
    text = f.read()
    f.close()
    r = reader(text)
    words_read = 0
    while r.has_next() == True:
        stdscr.clear()
        word = r.next_word()
        words_read = words_read + 1
        history_list, current_word, lookahead_list = r.nearby_words()
        
        history_str = ""
        for h_word in history_list:
            history_str = history_str + h_word + " "
            
        lookahead_str = ""
        for l_word in lookahead_list:
            lookahead_str = lookahead_str + " " + l_word
            
        max_y, max_x = stdscr.getmaxyx()
        y = max_y // 2
        word_len = len(word)
        diff_x = max_x - word_len
        x = diff_x // 2
        if x < 0:
            x = 0
            
        hx = x - len(history_str)
        if hx < 0:
            slice_start = len(history_str) - x
            history_str = history_str[slice_start:]
            hx = 0
            
        lx = x + word_len
        if lx < max_x:
            space_left = max_x - lx
            lookahead_str = lookahead_str[:space_left]
            
        if len(history_str) > 0:
            stdscr.addstr(y, hx, history_str, curses.A_DIM)
            
        stdscr.addstr(y, x, word)
        
        if lx < max_x:
            if len(lookahead_str) > 0:
                stdscr.addstr(y, lx, lookahead_str, curses.A_DIM)

        
        pct = words_read / r.size
        bar_width = 20
        filled = int(pct * bar_width)
        empty = bar_width - filled
        bar_str = "["
        for _ in range(filled):
            bar_str = bar_str + "#"
        for _ in range(empty):
            bar_str = bar_str + " "
        bar_str = bar_str + "]"
        percent_num = int(pct * 100)
        percent_str = " " + str(percent_num) + "%"
        full_str = bar_str + percent_str
        bar_len = len(full_str)
        bar_x = (max_x - bar_len) // 2
        if bar_x < 0:
            bar_x = 0
        bar_y = max_y - 2
        if bar_y > y:
            stdscr.addstr(bar_y, bar_x, full_str)
            
        stdscr.refresh()
        delay = r.get_delay()
        time.sleep(delay)



if __name__ == "__main__":
    curses.wrapper(main)

