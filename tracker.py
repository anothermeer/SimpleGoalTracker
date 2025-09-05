# tracker.py
# Made by Anothermeer <https://github.com/anothermeer>
# Version 1.1

# This script is licenced under GPU Public License,
# You can get a copy of the license at
# https://www.gnu.org/licenses/gpl-3.0.en.html

import curses
import json
import os

SAVE_FILE = "goal.json"

def load_data():
    if os.path.exists(SAVE_FILE):
        with open(SAVE_FILE, "r") as f:
            data = json.load(f)
            if "appsett" not in data:
                data["appsett"] = {"currency": "$"}
            if "active" not in data:
                data["active"] = 0
            return data
    # Default with this goal
    return {"appsett": {"currency": "$"}, "goals": [{"name": "Placeholder", "target": 230.0, "current": 150.0}], "active": 0}

def save_data(data):
    with open(SAVE_FILE, "w") as f:
        json.dump(data, f, indent=4)

def draw_box(stdscr, width=45, height=9):
    for y in range(height):
        for x in range(width):
            if y == 0 or y == height - 1:
                if 0 < x < width -1:
                    stdscr.addstr(y, x, "-")
            elif x == 0 or x == width - 1:
                stdscr.addstr(y, x, "|")

def draw_progress(stdscr, data, highlight):
    stdscr.clear()
    draw_box(stdscr, 45, 9)

    appsett = data["appsett"]
    goal = data["goals"][data["active"]]

    stdscr.addstr(0, 2, "Simple Goal Tracker V1.1")
    stdscr.addstr(2, 2, f"Goal: {goal['name']}")
    stdscr.addstr(3, 2, f"Target: {appsett['currency']} {goal['target']:.2f}")
    stdscr.addstr(4, 2, f"Current: {appsett['currency']} {goal['current']:.2f}")

    # Progress bar
    progress = min(goal['current'] / goal['target'], 1.0)
    bar_width = 30
    filled = int(bar_width * progress)
    percent = f"{progress*100:.2f}%"
    bar = "[" + "="*filled + "-"*(bar_width-filled) + f"] {percent}"
    stdscr.addstr(5, 2, bar)

    options = ["[Settings]", "[Switch Goal]", "[Quit]"]
    for i, opt in enumerate(options):
        if i == highlight:
            stdscr.addstr(7, 2 + i*15, opt, curses.A_REVERSE)
        else:
            stdscr.addstr(7, 2 + i*15, opt)

    stdscr.refresh()

def draw_settings(stdscr, goal, appsett, highlight):
    stdscr.clear()
    draw_box(stdscr, 45, 14)

    stdscr.addstr(0, 2, "Simple Goal Tracker V1.1 - Settings")
    stdscr.addstr(2, 2, f"[Goal Settings]")

    stdscr.addstr(3, 2, "G", curses.A_BOLD)
    stdscr.addstr(3, 3, "oal: " + goal["name"])

    stdscr.addstr(4, 2, "T", curses.A_BOLD)
    stdscr.addstr(4, 3, f"arget: {appsett['currency']} {goal['target']:.2f}")

    stdscr.addstr(5, 2, "C", curses.A_BOLD)
    stdscr.addstr(5, 3, f"urrent: {appsett['currency']} {goal['current']:.2f}")

    stdscr.addstr(7, 2, f"[App Settings]")
    stdscr.addstr(8, 2, "C")
    stdscr.addstr(8, 3, "u", curses.A_BOLD)
    stdscr.addstr(8 ,4, "rrency: " + appsett['currency'])

    options = ["[Save]", "[Discard (Back)]"]
    for i, opt in enumerate(options):
        if i == highlight:
            stdscr.addstr(10+i, 2, opt, curses.A_REVERSE)
        else:
            stdscr.addstr(10+i, 2, opt)

    stdscr.refresh()

def main(stdscr):
    curses.curs_set(0)
    data = load_data()
    highlight = 0
    in_settings = False
    while True:
        appsett = data["appsett"]
        goal = data["goals"][data["active"]]
        if in_settings:
            draw_settings(stdscr, goal, appsett, highlight)
        else:
            draw_progress(stdscr, data, highlight)

        key = stdscr.getch()

        if key == curses.KEY_UP:
            highlight = (highlight - 1) % 2 if in_settings else (highlight - 1) % 3
        elif key == curses.KEY_DOWN:
            highlight = (highlight + 1) % 2 if in_settings else (highlight + 1) % 3
        elif key == curses.KEY_RIGHT or key == 10:  # Enter
            if not in_settings:
                if highlight == 0:  # Settings
                    in_settings = True
                    highlight = 0
                elif highlight == 1:  # Switch Goal
                    data["active"] = (data["active"] + 1) % len(data["goals"])
                elif highlight == 2:  # Quit
                    break
            else:
                if highlight == 0:  # Save
                    save_data(data)
                    in_settings = False
                elif highlight == 1:  # Discard
                    data = load_data()
                    in_settings = False
        elif in_settings and key == ord('t'):  # Edit target
            curses.echo()
            stdscr.move(13, 2)
            stdscr.clrtoeol()
            stdscr.addstr(13, 2, f"New Target: {appsett['currency']} ")
            target = stdscr.getstr().decode()
            if target.lower() == "q" or target.strip() == "":
                continue
            try:
                goal['target'] = float(target)
            except ValueError:
                pass
            curses.noecho()
        elif in_settings and key == ord('c'):  # Edit current
            curses.echo()
            stdscr.move(13, 2)
            stdscr.clrtoeol()
            stdscr.addstr(13, 2, f"New Current: {appsett['currency']} ")
            current = stdscr.getstr().decode()
            if current.lower() == "q" or current.strip() == "":
                continue
            try:
                goal['current'] = float(current)
            except ValueError:
                pass
            curses.noecho()
        elif in_settings and key == ord('u'):  # Edit currency
            curses.echo()
            stdscr.move(13, 2)
            stdscr.clrtoeol()
            stdscr.addstr(13, 2, f"New Currency:  ")
            currency = stdscr.getstr().decode()
            if currency.lower() == "q" or currency.strip() == "":
                continue
            try:
                appsett['currency'] = str(currency)
            except ValueError:
                pass
            curses.noecho()
        elif in_settings and key == ord('g'):  # Change goal name
            curses.echo()
            stdscr.move(13, 2)
            stdscr.clrtoeol()
            stdscr.addstr(13, 2, "New Goal Name: ")
            name = stdscr.getstr().decode()
            if name.lower() == "q" or name.strip() == "":
                continue
            if name:
                goal['name'] = name
            curses.noecho()

curses.wrapper(main)
