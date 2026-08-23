#!/usr/bin/env python3
# color_buttons.py - أداة تعرض 50 زراً (أرقام 1-50) مع خلفية وأمامية قابلة للتغيير، وتحفظ الإعدادات.

import curses
import json
import os
import sys

CONFIG_FILE = os.path.expanduser("~/.color_buttons_config.json")

# قائمة الألوان المتاحة (أسماء ومقابلاتها في curses)
COLORS = {
    'black':   curses.COLOR_BLACK,
    'red':     curses.COLOR_RED,
    'green':   curses.COLOR_GREEN,
    'yellow':  curses.COLOR_YELLOW,
    'blue':    curses.COLOR_BLUE,
    'magenta': curses.COLOR_MAGENTA,
    'cyan':    curses.COLOR_CYAN,
    'white':   curses.COLOR_WHITE,
}
COLOR_NAMES = list(COLORS.keys())

# الإعدادات الافتراضية لكل زر (فهرسة من 0 إلى 49)
DEFAULT_CONFIG = {
    "fg": ["white"] * 50,
    "bg": ["black"] * 50
}

def load_config():
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, 'r') as f:
                data = json.load(f)
                if "fg" in data and "bg" in data and len(data["fg"]) == 50 and len(data["bg"]) == 50:
                    return data
        except:
            pass
    return DEFAULT_CONFIG.copy()

def save_config(cfg):
    with open(CONFIG_FILE, 'w') as f:
        json.dump(cfg, f, indent=2)

def draw_buttons(stdscr, config, selected_idx, message):
    stdscr.clear()
    height, width = stdscr.getmaxyx()
    cols = 10
    rows = 5
    total_width = cols * 6
    start_x = (width - total_width) // 2
    start_y = 2

    for i in range(50):
        row = i // cols
        col = i % cols
        y = start_y + row
        x = start_x + col * 6
        if y >= height or x >= width:
            continue
        fg_name = config["fg"][i]
        bg_name = config["bg"][i]
        fg = COLORS.get(fg_name, curses.COLOR_WHITE)
        bg = COLORS.get(bg_name, curses.COLOR_BLACK)
        try:
            curses.init_pair(i+1, fg, bg)
        except:
            curses.init_pair(i+1, curses.COLOR_WHITE, curses.COLOR_BLACK)
        color_pair = curses.color_pair(i+1)
        if i == selected_idx:
            label = f"*{i+1:2d}*"
            stdscr.attron(curses.A_REVERSE)
            stdscr.addstr(y, x, label, color_pair)
            stdscr.attroff(curses.A_REVERSE)
        else:
            label = f" {i+1:2d} "
            stdscr.addstr(y, x, label, color_pair)

    help_text = f"←↑↓→ تحريك | (f) تغيير الأمامية | (b) تغيير الخلفية | (s) حفظ | (q) خروج | {message}"
    if len(help_text) < width:
        stdscr.addstr(height-2, (width-len(help_text))//2, help_text)
    else:
        stdscr.addstr(height-2, 0, help_text[:width-1])
    stdscr.refresh()

def main(stdscr):
    curses.curs_set(0)
    curses.start_color()
    curses.use_default_colors()
    
    # التحقق من دعم الألوان بعد تهيئة curses
    if not curses.has_colors():
        stdscr.addstr(0, 0, "خطأ: المحطة لا تدعم الألوان.")
        stdscr.refresh()
        stdscr.getch()
        return

    config = load_config()
    selected = 0
    message = ""

    while True:
        draw_buttons(stdscr, config, selected, message)
        key = stdscr.getch()

        if key == ord('q') or key == ord('Q'):
            break
        elif key == ord('s') or key == ord('S'):
            save_config(config)
            message = "تم الحفظ!"
        elif key == curses.KEY_UP:
            if selected >= 10:
                selected -= 10
        elif key == curses.KEY_DOWN:
            if selected < 40:
                selected += 10
        elif key == curses.KEY_LEFT:
            if selected % 10 > 0:
                selected -= 1
        elif key == curses.KEY_RIGHT:
            if selected % 10 < 9:
                selected += 1
        elif key == ord('f') or key == ord('F'):
            current = config["fg"][selected]
            idx = COLOR_NAMES.index(current) if current in COLOR_NAMES else 0
            new_idx = (idx + 1) % len(COLOR_NAMES)
            config["fg"][selected] = COLOR_NAMES[new_idx]
            message = f"الزر {selected+1} -> أمامية: {COLOR_NAMES[new_idx]}"
        elif key == ord('b') or key == ord('B'):
            current = config["bg"][selected]
            idx = COLOR_NAMES.index(current) if current in COLOR_NAMES else 0
            new_idx = (idx + 1) % len(COLOR_NAMES)
            config["bg"][selected] = COLOR_NAMES[new_idx]
            message = f"الزر {selected+1} -> خلفية: {COLOR_NAMES[new_idx]}"
        else:
            message = f"ضغطت: {key} (غير معروف)"

    save_config(config)
    stdscr.clear()
    stdscr.addstr(0, 0, "تم الخروج، الإعدادات محفوظة.")
    stdscr.refresh()
    stdscr.getch()

if __name__ == "__main__":
    curses.wrapper(main)
