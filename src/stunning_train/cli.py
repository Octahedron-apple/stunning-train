#!/usr/bin/env python3
import time
import os
import argparse
import sys
import select
import termios
import tty

from rich.console import Console
from rich.text import Text
from rich.panel import Panel
from rich.layout import Layout
from rich.live import Live
from rich.align import Align
from rich.table import Table

try:
    from stunning_train.core import reader
    from stunning_train.pdf import pdf_reader
except ImportError:
    from core import reader
    from pdf import pdf_reader

console = Console()

class TerminalInput:
    def __init__(self):
        self.fd = sys.stdin.fileno()
        
    def __enter__(self):
        self.old_settings = termios.tcgetattr(self.fd)
        tty.setcbreak(self.fd)
        new_settings = termios.tcgetattr(self.fd)
        new_settings[3] = new_settings[3] & ~termios.ECHO
        termios.tcsetattr(self.fd, termios.TCSANOW, new_settings)
        return self
        
    def __exit__(self, exc_type, exc_val, exc_tb):
        termios.tcsetattr(self.fd, termios.TCSADRAIN, self.old_settings)

    def get_key(self):
        if select.select([self.fd], [], [], 0)[0]:
            ch = os.read(self.fd, 1).decode('utf-8', 'ignore')
            if ch == '\x1b':
                if select.select([self.fd], [], [], 0.05)[0]:
                    ch2 = os.read(self.fd, 1).decode('utf-8', 'ignore')
                    if ch2 in ('[', 'O'):
                        if select.select([self.fd], [], [], 0.05)[0]:
                            ch3 = os.read(self.fd, 1).decode('utf-8', 'ignore')
                            if ch3 == 'A': return 'UP'
                            if ch3 == 'B': return 'DOWN'
                            if ch3 == 'C': return 'RIGHT'
                            if ch3 == 'D': return 'LEFT'
            return ch
        return None

def generate_menu(files, selected):
    text = Text("Choose a file (Arrow keys to navigate, Enter to select, 'q' to quit):\n\n", justify="center", style="bold magenta")
    for idx, f in enumerate(files):
        if idx == selected:
            text.append(f"> {f}\n", style="bold green")
        else:
            text.append(f"  {f}\n", style="white")
            
    layout = Layout()
    layout.split_column(
        Layout(Align.center(text, vertical="middle"), ratio=1)
    )
    return layout

def choose_file(kb):
    all_items = os.listdir('.')
    files = [f for f in all_items if os.path.isfile(f)]
    if not files:
        return None
    selected = 0
    with Live(generate_menu(files, selected), screen=True, refresh_per_second=30) as live:
        while True:
            key = None
            while key is None:
                key = kb.get_key()
                time.sleep(0.01)
                
            if key == 'UP' or key == 'k':
                selected = (selected - 1) % len(files)
            elif key == 'DOWN' or key == 'j':
                selected = (selected + 1) % len(files)
            elif key == '\n' or key == '\r':
                return files[selected]
            elif key == 'q':
                return None
            live.update(generate_menu(files, selected))

def generate_renderable(r, paused):
    history, current, lookahead = r.nearby_words()
    
    if current is None:
        return Panel(Text("Done.", justify="center"))
        
    orp_idx = r.get_orp(current)
    
    left_word = current[:orp_idx]
    orp_char = current[orp_idx:orp_idx+1]
    right_word = current[orp_idx+1:]
    
    center_text = Text()
    center_text.append(left_word, style="white")
    center_text.append(orp_char, style="bold red")
    center_text.append(right_word, style="white")
    
    history_str = " ".join(history)
    lookahead_str = " ".join(lookahead)

    term_width = console.size.width
    side_width = max(10, (term_width - len(current) - 4) // 2)

    if len(history_str) > side_width:
        history_str = "..." + history_str[-(side_width-3):]
    if len(lookahead_str) > side_width:
        lookahead_str = lookahead_str[:side_width-3] + "..."
    
    table = Table(show_header=False, show_edge=False, box=None, padding=(0, 1), expand=True)
    table.add_column(justify="right", ratio=1, no_wrap=True)
    table.add_column(justify="center", no_wrap=True)
    table.add_column(justify="left", ratio=1, no_wrap=True)
    
    table.add_row(
        Text(history_str, style="dim", no_wrap=True),
        center_text,
        Text(lookahead_str, style="dim", no_wrap=True)
    )
    
    if getattr(r, 'is_pdf', False):
        pct = (r.current_page / r.size) if r.size > 0 else 1.0
    else:
        pct = (r.chars_read / r.size) if r.size > 0 else 1.0
    if pct > 1.0: pct = 1.0
    
    bar_width = 20
    filled = int(pct * bar_width)
    empty = bar_width - filled
    bar_str = "[" + "-"*filled + " "*empty + "]"
    progress_str = f"{bar_str} {int(pct*100)}%"
    
    if paused:
        progress_str += " [PAUSED]"
        
    layout = Layout()
    layout.split_column(
        Layout(Align.center(table, vertical="middle"), ratio=1),
        Layout(Align.center(Text(progress_str, style="bold blue")), size=1)
    )
    return layout

def main(args, kb):
    if args.string is not None:
        r = reader(args.string, wpm=args.wpm)
    elif args.file is not None:
        if args.file.lower().endswith('.pdf'):
            f = pdf_reader(args.file)
        else:
            f = open(args.file, 'r')
        r = reader(f, wpm=args.wpm)
    else:
        filename = choose_file(kb)
        if filename is None:
            return
        if filename.lower().endswith('.pdf'):
            f = pdf_reader(filename)
        else:
            f = open(filename, 'r')
        r = reader(f, wpm=args.wpm)
        
    if r.has_next():
        r.next_word()
        
    last_time = time.time()
    paused = False
    
    with Live(generate_renderable(r, paused), refresh_per_second=60, screen=True) as live:
        while r.has_next() or r.current is not None:
            if r.current is None:
                if r.has_next():
                    r.next_word()
                    last_time = time.time()
                else:
                    break
                
            now = time.time()
            elapsed = now - last_time
            remaining = r.get_delay() - elapsed
            
            if paused:
                remaining = 0.1
                
            end_time = now + max(0, remaining)
            key = None
            while time.time() < end_time:
                key = kb.get_key()
                if key is not None:
                    break
                time.sleep(0.01)
                
            if key == 'RIGHT':
                steps = max(1, int((r.size / 6) * 0.02))
                r.skip_forward(steps)
                last_time = time.time()
            elif key == 'LEFT':
                steps = max(1, int((r.size / 6) * 0.02))
                for _ in range(steps):
                    r.go_backward()
                last_time = time.time()
            elif key == ' ':
                paused = not paused
                last_time = time.time()
            elif key == 'q':
                break
            else:
                if not paused:
                    if time.time() >= end_time:
                        if r.has_next():
                            r.next_word()
                            last_time = time.time()
                        else:
                            break
                else:
                    last_time = time.time()
                    
            live.update(generate_renderable(r, paused))

def run():
    parser = argparse.ArgumentParser(description="Terminal-based Fast Screen Reader")
    parser.add_argument('-f', '--file', type=str, help="File Path (needed if file is outside the cwd)")
    parser.add_argument('-s', '--string', type=str, help="Input String")
    parser.add_argument('-w', '--wpm', type=int, default=300, help="SET WPM (default: 300)")
    args = parser.parse_args()
    
    with TerminalInput() as kb:
        main(args, kb)

if __name__ == "__main__":
    run()
