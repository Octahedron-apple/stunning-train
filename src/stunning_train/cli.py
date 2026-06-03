#!/usr/bin/env python3
import curses
import time
import os
import argparse
try:
    from stunning_train.core import reader
    from stunning_train.pdf import pdf_reader
except ImportError:
    from core import reader
    from pdf import pdf_reader

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

def main(stdscr, args):
    curses.curs_set(0)
    stdscr.keypad(True)
    if args.string is not None:
        r = reader(args.string, wpm=args.wpm)
    elif args.file is not None:
        if args.file.lower().endswith('.pdf'):
            f = pdf_reader(args.file)
        else:
            f = open(args.file, 'r')
        r = reader(f, wpm=args.wpm)
    else:
        filename = choose_file(stdscr)
        if filename is None:
            return
        if filename.lower().endswith('.pdf'):
            f = pdf_reader(filename)
        else:
            f = open(filename, 'r')
        r = reader(f, wpm=args.wpm)
    last_time = time.time()
    paused = False
    while r.has_next() == True or r.current is not None:
        if r.current is None:
            r.next_word()
            last_time = time.time()
        stdscr.clear()
        word = r.current
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
        if getattr(r, 'is_pdf', False):
            pct = (r.current_page / r.size) if r.size > 0 else 1.0
        else:
            pct = (r.chars_read / r.size) if r.size > 0 else 1.0
        if pct > 1.0:
            pct = 1.0
        bar_width = 20
        filled = int(pct * bar_width)
        empty = bar_width - filled
        bar_str = "["
        for _ in range(filled):
            bar_str = bar_str + "-"
        for _ in range(empty):
            bar_str = bar_str + " "
        bar_str = bar_str + "]"
        percent_num = int(pct * 100)
        percent_str = " " + str(percent_num) + "%"
        full_str = bar_str + percent_str
        if paused:
            full_str += " [PAUSED]"
        bar_len = len(full_str)
        bar_x = (max_x - bar_len) // 2
        if bar_x < 0:
            bar_x = 0
        bar_y = max_y - 2
        if bar_y > y:
            stdscr.addstr(bar_y, bar_x, full_str)
        stdscr.refresh()
        now = time.time()
        elapsed = now - last_time
        remaining = r.get_delay() - elapsed
        if remaining < 0:
            remaining = 0
        delay_ms = int(remaining * 1000)
        stdscr.timeout(delay_ms)
        key = stdscr.getch()
        if key == curses.KEY_RIGHT:
            steps = int((r.size / 6) * 0.02)
            if steps < 1:
                steps = 1
            r.skip_forward(steps)
            last_time = time.time()
        elif key == curses.KEY_LEFT:
            steps = int((r.size / 6) * 0.02)
            if steps < 1:
                steps = 1
            for _ in range(steps):
                r.go_backward()
            last_time = time.time()
        elif key == ord(' '):
            paused = not paused
            last_time = time.time()
        elif key == -1:
            if not paused:
                if r.has_next() == True:
                    r.next_word()
                    last_time = time.time()
                else:
                    break
            else:
                last_time = time.time()

def run():
    parser = argparse.ArgumentParser(description="Terminal-based Fast Screen Reader ")
    parser.add_argument('-f', '--file', type=str, help="File Path(needed if file is outside the cwd)")
    parser.add_argument('-s', '--string', type=str, help="Input String")
    parser.add_argument('-w', '--wpm', type=int, default=300, help="SET WPM(default: 300)")
    args = parser.parse_args()
    curses.wrapper(main, args)

if __name__ == "__main__":
    run()
