#!/usr/bin/env python3

import curses
import json
import os
import random
import time

CONFIG_FILE = os.path.expanduser("~/.bounty_scout_config.json")

# ============================================================
# COLORS
# ============================================================

COLORS = {
    "black": curses.COLOR_BLACK,
    "red": curses.COLOR_RED,
    "green": curses.COLOR_GREEN,
    "yellow": curses.COLOR_YELLOW,
    "blue": curses.COLOR_BLUE,
    "magenta": curses.COLOR_MAGENTA,
    "cyan": curses.COLOR_CYAN,
    "white": curses.COLOR_WHITE,
}

COLOR_NAMES = list(COLORS.keys())


# ============================================================
# 50 THEMES
# ============================================================

THEMES = [
    {"name": "Classic", "fg": "white", "bg": "black", "accent": "cyan"},
    {"name": "Matrix", "fg": "green", "bg": "black", "accent": "green"},
    {"name": "Red Alert", "fg": "red", "bg": "black", "accent": "yellow"},
    {"name": "Blue Ocean", "fg": "cyan", "bg": "blue", "accent": "white"},
    {"name": "Cyber Purple", "fg": "magenta", "bg": "black", "accent": "cyan"},
    {"name": "Golden", "fg": "yellow", "bg": "black", "accent": "white"},
    {"name": "Dark Blue", "fg": "white", "bg": "blue", "accent": "cyan"},
    {"name": "Dark Red", "fg": "white", "bg": "red", "accent": "yellow"},
    {"name": "Forest", "fg": "green", "bg": "black", "accent": "white"},
    {"name": "Purple Night", "fg": "white", "bg": "magenta", "accent": "cyan"},

    {"name": "Ice", "fg": "cyan", "bg": "black", "accent": "white"},
    {"name": "Fire", "fg": "yellow", "bg": "red", "accent": "white"},
    {"name": "Toxic", "fg": "green", "bg": "yellow", "accent": "black"},
    {"name": "Ocean", "fg": "blue", "bg": "cyan", "accent": "white"},
    {"name": "Violet", "fg": "magenta", "bg": "blue", "accent": "white"},
    {"name": "Terminal", "fg": "green", "bg": "black", "accent": "white"},
    {"name": "Stealth", "fg": "white", "bg": "black", "accent": "white"},
    {"name": "Whiteout", "fg": "black", "bg": "white", "accent": "blue"},
    {"name": "Ruby", "fg": "red", "bg": "magenta", "accent": "white"},
    {"name": "Emerald", "fg": "green", "bg": "black", "accent": "yellow"},

    {"name": "Cyber Blue", "fg": "blue", "bg": "black", "accent": "cyan"},
    {"name": "Cyber Red", "fg": "red", "bg": "black", "accent": "white"},
    {"name": "Cyber Green", "fg": "green", "bg": "black", "accent": "yellow"},
    {"name": "Cyber Gold", "fg": "yellow", "bg": "black", "accent": "red"},
    {"name": "Cyber White", "fg": "white", "bg": "black", "accent": "blue"},
    {"name": "Night Sky", "fg": "blue", "bg": "black", "accent": "white"},
    {"name": "Blood Moon", "fg": "red", "bg": "black", "accent": "magenta"},
    {"name": "Neon Green", "fg": "green", "bg": "black", "accent": "cyan"},
    {"name": "Neon Cyan", "fg": "cyan", "bg": "black", "accent": "green"},
    {"name": "Neon Pink", "fg": "magenta", "bg": "black", "accent": "white"},

    {"name": "Royal", "fg": "white", "bg": "blue", "accent": "yellow"},
    {"name": "Crimson", "fg": "white", "bg": "red", "accent": "cyan"},
    {"name": "Amethyst", "fg": "white", "bg": "magenta", "accent": "yellow"},
    {"name": "Lime", "fg": "green", "bg": "yellow", "accent": "black"},
    {"name": "Storm", "fg": "white", "bg": "blue", "accent": "green"},
    {"name": "Deep Sea", "fg": "cyan", "bg": "blue", "accent": "white"},
    {"name": "Dark Forest", "fg": "green", "bg": "black", "accent": "red"},
    {"name": "Solar", "fg": "yellow", "bg": "red", "accent": "black"},
    {"name": "Arctic", "fg": "white", "bg": "cyan", "accent": "blue"},
    {"name": "Galaxy", "fg": "magenta", "bg": "blue", "accent": "cyan"},

    {"name": "Hacker", "fg": "green", "bg": "black", "accent": "green"},
    {"name": "Ghost", "fg": "white", "bg": "black", "accent": "cyan"},
    {"name": "Shadow", "fg": "black", "bg": "white", "accent": "black"},
    {"name": "Inferno", "fg": "red", "bg": "yellow", "accent": "white"},
    {"name": "Cyberpunk", "fg": "magenta", "bg": "black", "accent": "yellow"},
    {"name": "Digital", "fg": "cyan", "bg": "black", "accent": "green"},
    {"name": "Terminal Red", "fg": "red", "bg": "black", "accent": "red"},
    {"name": "Terminal Blue", "fg": "blue", "bg": "black", "accent": "blue"},
    {"name": "Terminal Gold", "fg": "yellow", "bg": "black", "accent": "yellow"},
    {"name": "Ultimate", "fg": "white", "bg": "black", "accent": "red"},
]


# ============================================================
# CONFIG
# ============================================================

def load_config():
    default = {
        "theme": 0,
        "fg": ["white"] * 50,
        "bg": ["black"] * 50,
    }

    try:
        if os.path.exists(CONFIG_FILE):
            with open(CONFIG_FILE, "r") as f:
                data = json.load(f)

            if (
                isinstance(data, dict)
                and isinstance(data.get("theme"), int)
                and len(data.get("fg", [])) == 50
                and len(data.get("bg", [])) == 50
            ):
                return data

    except Exception:
        pass

    return default


def save_config(config):
    try:
        with open(CONFIG_FILE, "w") as f:
            json.dump(config, f, indent=2)
    except Exception:
        pass


# ============================================================
# SAFE TEXT
# ============================================================

def safe_addstr(stdscr, y, x, text, attr=0):
    height, width = stdscr.getmaxyx()

    if y < 0 or y >= height:
        return

    if x < 0:
        x = 0

    if x >= width:
        return

    text = str(text)
    text = text[:max(0, width - x - 1)]

    try:
        stdscr.addstr(y, x, text, attr)
    except curses.error:
        pass


def center_text(stdscr, y, text, attr=0):
    height, width = stdscr.getmaxyx()

    if y < 0 or y >= height:
        return

    x = max(0, (width - len(text)) // 2)

    safe_addstr(stdscr, y, x, text, attr)


# ============================================================
# THEME COLORS
# ============================================================

def init_theme(theme):
    fg = COLORS.get(theme["fg"], curses.COLOR_WHITE)
    bg = COLORS.get(theme["bg"], curses.COLOR_BLACK)
    accent = COLORS.get(theme["accent"], curses.COLOR_CYAN)

    try:
        curses.init_pair(1, fg, bg)
        curses.init_pair(2, accent, bg)
        curses.init_pair(3, bg, accent)
    except Exception:
        try:
            curses.init_pair(1, curses.COLOR_WHITE, curses.COLOR_BLACK)
            curses.init_pair(2, curses.COLOR_CYAN, curses.COLOR_BLACK)
            curses.init_pair(3, curses.COLOR_BLACK, curses.COLOR_WHITE)
        except Exception:
            pass


# ============================================================
# LOGIN
# ============================================================

def login_screen(stdscr, config):

    while True:

        theme_index = config["theme"]

        if not 0 <= theme_index < 50:
            theme_index = 0
            config["theme"] = 0

        theme = THEMES[theme_index]

        init_theme(theme)

        stdscr.clear()

        try:
            stdscr.bkgd(" ", curses.color_pair(1))
        except Exception:
            pass

        height, width = stdscr.getmaxyx()

        center_text(
            stdscr,
            max(1, height // 2 - 6),
            "================================",
            curses.color_pair(2) | curses.A_BOLD
        )

        center_text(
            stdscr,
            max(2, height // 2 - 5),
            "B O U N T Y   S C O U T",
            curses.color_pair(2) | curses.A_BOLD
        )

        center_text(
            stdscr,
            max(3, height // 2 - 4),
            "50 THEME TERMINAL",
            curses.color_pair(1)
        )

        center_text(
            stdscr,
            max(5, height // 2 - 2),
            "[ ENTER ]  START",
            curses.color_pair(3) | curses.A_BOLD
        )

        center_text(
            stdscr,
            max(6, height // 2 - 1),
            "[ T ]  THEMES",
            curses.color_pair(2)
        )

        center_text(
            stdscr,
            max(7, height // 2),
            "[ R ]  RANDOM THEME",
            curses.color_pair(2)
        )

        center_text(
            stdscr,
            max(8, height // 2 + 1),
            "[ Q ]  EXIT",
            curses.color_pair(2)
        )

        center_text(
            stdscr,
            max(10, height // 2 + 3),
            f"THEME {theme_index + 1}/50 : {theme['name']}",
            curses.color_pair(2) | curses.A_BOLD
        )

        center_text(
            stdscr,
            max(12, height // 2 + 5),
            "iSH / Alpine Linux",
            curses.color_pair(1)
        )

        stdscr.refresh()

        key = stdscr.getch()

        if key in (10, 13):
            button_program(stdscr, config)

        elif key in (ord("t"), ord("T")):
            theme_menu(stdscr, config)

        elif key in (ord("r"), ord("R")):
            config["theme"] = random.randint(0, 49)
            save_config(config)

            stdscr.clear()

            init_theme(THEMES[config["theme"]])

            center_text(
                stdscr,
                height // 2,
                "RANDOM THEME SELECTED",
                curses.color_pair(2) | curses.A_BOLD
            )

            stdscr.refresh()
            time.sleep(0.7)

        elif key in (ord("q"), ord("Q")):
            save_config(config)
            return


# ============================================================
# THEME PREVIEW
# ============================================================

def preview_theme(stdscr, index):

    theme = THEMES[index]

    init_theme(theme)

    stdscr.clear()

    try:
        stdscr.bkgd(" ", curses.color_pair(1))
    except Exception:
        pass

    height, width = stdscr.getmaxyx()

    center_text(
        stdscr,
        max(1, height // 2 - 6),
        "THEME PREVIEW",
        curses.color_pair(2) | curses.A_BOLD
    )

    center_text(
        stdscr,
        max(3, height // 2 - 4),
        f"{index + 1:02d} - {theme['name']}",
        curses.color_pair(2) | curses.A_BOLD
    )

    center_text(
        stdscr,
        max(5, height // 2 - 2),
        "+----------------------------+",
        curses.color_pair(2)
    )

    center_text(
        stdscr,
        max(6, height // 2 - 1),
        "|      BOUNTY SCOUT          |",
        curses.color_pair(2) | curses.A_BOLD
    )

    center_text(
        stdscr,
        max(7, height // 2),
        "|       [ 01 ] [ 02 ]        |",
        curses.color_pair(1)
    )

    center_text(
        stdscr,
        max(8, height // 2 + 1),
        "|       [ 03 ] [ 04 ]        |",
        curses.color_pair(1)
    )

    center_text(
        stdscr,
        max(9, height // 2 + 2),
        "+----------------------------+",
        curses.color_pair(2)
    )

    center_text(
        stdscr,
        max(11, height // 2 + 4),
        "ENTER = SELECT",
        curses.color_pair(3) | curses.A_BOLD
    )

    center_text(
        stdscr,
        max(12, height // 2 + 5),
        "Q = BACK",
        curses.color_pair(2)
    )

    stdscr.refresh()


# ============================================================
# THEME MENU
# ============================================================

def theme_menu(stdscr, config):

    selected = config["theme"]

    while True:

        theme = THEMES[selected]

        init_theme(theme)

        stdscr.clear()

        try:
            stdscr.bkgd(" ", curses.color_pair(1))
        except Exception:
            pass

        height, width = stdscr.getmaxyx()

        center_text(
            stdscr,
            0,
            "=== 50 THEMES ===",
            curses.color_pair(2) | curses.A_BOLD
        )

        # 10 columns x 5 rows
        for i in range(50):

            row = i // 10
            col = i % 10

            x = 1 + col * max(6, width // 10)
            y = 2 + row * 2

            if y >= height - 4:
                continue

            if i == selected:

                text = f"[{i + 1:02d}]"

                safe_addstr(
                    stdscr,
                    y,
                    x,
                    text,
                    curses.color_pair(3) | curses.A_BOLD
                )

            else:

                text = f" {i + 1:02d} "

                safe_addstr(
                    stdscr,
                    y,
                    x,
                    text,
                    curses.color_pair(1)
                )

        center_text(
            stdscr,
            max(13, height - 4),
            f"SELECTED: {selected + 1}/50 - {theme['name']}",
            curses.color_pair(2) | curses.A_BOLD
        )

        center_text(
            stdscr,
            max(14, height - 3),
            "W/S = UP/DOWN   A/D = LEFT/RIGHT",
            curses.color_pair(2)
        )

        center_text(
            stdscr,
            max(15, height - 2),
            "ENTER = PREVIEW   R = RANDOM   Q = BACK",
            curses.color_pair(2)
        )

        stdscr.refresh()

        key = stdscr.getch()

        # W = UP
        if key in (ord("w"), ord("W")):
            selected = (selected - 10) % 50

        # S = DOWN
        elif key in (ord("s"), ord("S")):
            selected = (selected + 10) % 50

        # A = LEFT
        elif key in (ord("a"), ord("A")):
            selected = (selected - 1) % 50

        # D = RIGHT
        elif key in (ord("d"), ord("D")):
            selected = (selected + 1) % 50

        # ENTER
        elif key in (10, 13):

            preview_theme(stdscr, selected)

            preview_key = stdscr.getch()

            if preview_key in (10, 13):

                config["theme"] = selected
                save_config(config)

                return

        # RANDOM
        elif key in (ord("r"), ord("R")):

            selected = random.randint(0, 49)

            preview_theme(stdscr, selected)

            preview_key = stdscr.getch()

            if preview_key in (10, 13):

                config["theme"] = selected
                save_config(config)

                return

        # BACK
        elif key in (ord("q"), ord("Q"), 27):
            return


# ============================================================
# MAIN 50 BUTTONS
# ============================================================

def button_program(stdscr, config):

    selected = 0
    message = ""

    while True:

        theme_index = config["theme"]

        if not 0 <= theme_index < 50:
            theme_index = 0
            config["theme"] = 0

        theme = THEMES[theme_index]

        init_theme(theme)

        stdscr.clear()

        try:
            stdscr.bkgd(" ", curses.color_pair(1))
        except Exception:
            pass

        height, width = stdscr.getmaxyx()

        center_text(
            stdscr,
            0,
            f"BOUNTY SCOUT | THEME {theme_index + 1}: {theme['name']}",
            curses.color_pair(2) | curses.A_BOLD
        )

        cols = 10

        # 50 buttons = 5 rows x 10 columns
        for i in range(50):

            row = i // cols
            col = i % cols

            y = 3 + row * 2
            x = max(1, (width - 60) // 2 + col * 6)

            if y >= height - 5:
                continue

            fg_name = config["fg"][i]
            bg_name = config["bg"][i]

            fg = COLORS.get(
                fg_name,
                curses.COLOR_WHITE
            )

            bg = COLORS.get(
                bg_name,
                curses.COLOR_BLACK
            )

            pair = 10 + i

            try:
                curses.init_pair(
                    pair,
                    fg,
                    bg
                )
            except Exception:
                pair = 1

            if i == selected:

                label = f"[{i + 1:02d}]"

                safe_addstr(
                    stdscr,
                    y,
                    x,
                    label,
                    curses.color_pair(pair)
                    | curses.A_REVERSE
                    | curses.A_BOLD
                )

            else:

                label = f" {i + 1:02d} "

                safe_addstr(
                    stdscr,
                    y,
                    x,
                    label,
                    curses.color_pair(pair)
                )

        center_text(
            stdscr,
            max(14, height - 4),
            "W/S = UP/DOWN    A/D = LEFT/RIGHT",
            curses.color_pair(2)
        )

        center_text(
            stdscr,
            max(15, height - 3),
            "F = FOREGROUND    B = BACKGROUND",
            curses.color_pair(2)
        )

        center_text(
            stdscr,
            max(16, height - 2),
            "T = THEMES    S = SAVE    Q = EXIT",
            curses.color_pair(2)
        )

        if message:

            center_text(
                stdscr,
                height - 1,
                message,
                curses.color_pair(2) | curses.A_BOLD
            )

        stdscr.refresh()

        key = stdscr.getch()

        message = ""

        # ====================================================
        # NAVIGATION
        # ====================================================

        # W = UP
        if key in (ord("w"), ord("W")):

            if selected >= 10:
                selected -= 10

        # S = DOWN
        elif key in (ord("s"), ord("S")):

            if selected < 40:
                selected += 10

        # A = LEFT
        elif key in (ord("a"), ord("A")):

            if selected % 10 != 0:
                selected -= 1

        # D = RIGHT
        elif key in (ord("d"), ord("D")):

            if selected % 10 != 9:
                selected += 1

        # ====================================================
        # FOREGROUND
        # ====================================================

        elif key in (ord("f"), ord("F")):

            current = config["fg"][selected]

            try:
                index = COLOR_NAMES.index(current)
            except ValueError:
                index = 0

            index = (index + 1) % len(COLOR_NAMES)

            config["fg"][selected] = COLOR_NAMES[index]

            save_config(config)

            message = (
                f"BUTTON {selected + 1}: "
                f"FG = {COLOR_NAMES[index]}"
            )

        # ====================================================
        # BACKGROUND
        # ====================================================

        elif key in (ord("b"), ord("B")):

            current = config["bg"][selected]

            try:
                index = COLOR_NAMES.index(current)
            except ValueError:
                index = 0

            index = (index + 1) % len(COLOR_NAMES)

            config["bg"][selected] = COLOR_NAMES[index]

            save_config(config)

            message = (
                f"BUTTON {selected + 1}: "
                f"BG = {COLOR_NAMES[index]}"
            )

        # ====================================================
        # THEMES
        # ====================================================

        elif key in (ord("t"), ord("T")):

            theme_menu(
                stdscr,
                config
            )

        # ====================================================
        # SAVE
        # ====================================================

        elif key in (ord("s"), ord("S")):

            save_config(config)

            message = "SAVED SUCCESSFULLY"

        # ====================================================
        # EXIT
        # ====================================================

        elif key in (ord("q"), ord("Q")):

            save_config(config)

            return


# ============================================================
# MAIN
# ============================================================

def main(stdscr):

    try:
        curses.curs_set(0)
    except Exception:
        pass

    try:
        curses.start_color()
    except Exception:
        pass

    try:
        curses.use_default_colors()
    except Exception:
        pass

    if not curses.has_colors():

        stdscr.clear()

        safe_addstr(
            stdscr,
            1,
            1,
            "Your terminal does not support colors."
        )

        safe_addstr(
            stdscr,
            2,
            1,
            "Press any key to exit."
        )

        stdscr.refresh()
        stdscr.getch()

        return

    config = load_config()

    login_screen(
        stdscr,
        config
    )


# ============================================================
# START
# ============================================================

if __name__ == "__main__":

    try:

        curses.wrapper(main)

    except KeyboardInterrupt:

        pass

    except Exception as error:

        print()
        print("Bounty Scout stopped.")
        print("Error:", error)
