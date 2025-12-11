import tkinter.font as tkfont
import tkinter as tk
import ctypes
import json
import os
import re

SAVE_FILE = "note_en.json"
SEPARATOR = "---------------------"

pages = [""]
current_page = 0
is_getting = False

# window
root = tk.Tk()
root.overrideredirect(True)

user32 = ctypes.windll.user32
screen_width = user32.GetSystemMetrics(0)
screen_height = user32.GetSystemMetrics(1)


def render_note(content):
    text.delete("1.0", "end")
    text.insert("1.0", content)

    red = r"x .*? x"
    orange = r"\[.*?\]"
    yellow = r"\(.*?\)"

    for match in re.finditer(red, content):
        start, end = match.span()
        text.tag_add("red", f"1.0+{start}c", f"1.0+{end}c")

    for match in re.finditer(orange, content):
        start, end = match.span()
        text.tag_add("orange", f"1.0+{start}c", f"1.0+{end}c")

    for match in re.finditer(yellow, content):
        start, end = match.span()
        text.tag_add("yellow", f"1.0+{start}c", f"1.0+{end}c")

    text.edit_reset()


def load_note():
    global pages, current_page
    if os.path.exists(SAVE_FILE):
        try:
            with open(SAVE_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
            pages = data.get("pages", pages)
        except:
            pages = [""]

    render_note(pages[current_page])
    close_btn.config(text="✕")
    text.edit_modified(False)


def save_note():
    pages[current_page] = text.get("1.0", "end-1c")

    end = max(get_last_valid_page(), current_page)
    cleaned_pages = pages[: end + 1]

    pages.clear()
    pages.extend(cleaned_pages)

    with open(SAVE_FILE, "w", encoding="utf-8") as f:
        json.dump(
            {"pages": pages},
            f,
            ensure_ascii=False,
            indent=2,
        )

    render_note(pages[current_page])
    close_btn.config(text="✕")
    text.edit_modified(False)


def get_last_valid_page():
    last = 0

    for i, content in enumerate(pages):
        if content.strip() != "":
            last = i

    return last


def switch_page(offset):
    global current_page, is_getting

    if is_getting:
        return

    pages[current_page] = text.get("1.0", "end-1c")
    last_page = get_last_valid_page()
    current_page += offset

    if current_page < 0:
        prev_btn.config(fg="#ff3300")
        current_page = 0

    if current_page < last_page:
        next_btn.config(text="〉")
    else:
        next_btn.config(text="》")

    if current_page >= len(pages):
        pages.append("")

    page_label.config(text=str(current_page + 1))
    render_note(pages[current_page])


def start_move(event):
    global drag_x, drag_y
    drag_x = event.x
    drag_y = event.y


def do_move(event):
    global drag_x, drag_y, is_getting

    if is_getting:
        return

    x = event.x_root - drag_x
    y = event.y_root - drag_y
    root.geometry(f"+{x}+{y}")


def move_to_bottom_right():
    save_note()
    w = root.winfo_width()
    h = root.winfo_height()
    x = screen_width - w
    y = screen_height - h - 48
    root.geometry(f"+{x}+{y}")


def auto_resize():
    global is_getting

    if is_getting:
        root.after(200, auto_resize)
        return

    pages[current_page] = text.get("1.0", "end-1c")

    def count_lines(text_value):
        lines = text_value.splitlines(keepends=True)

        if text_value.endswith("\n"):
            return len(lines) + 2
        else:
            return len(lines) + 1

    max_lines = max(count_lines(p) for p in pages)
    line_height = 20
    new_height = min(max(max_lines * line_height, 200) + 100, 550)

    root.geometry(f"200x{new_height}+{root.winfo_x()}+{root.winfo_y()}")
    root.after(200, auto_resize)


def auto_indent(event):
    current_line = text.get("insert linestart", "insert")
    if current_line.strip() == "-":
        text.delete("insert linestart", "insert lineend")
        return "break"
    elif (
        current_line.startswith("- ")
        or current_line.endswith(":")
        or current_line.endswith("：")
    ):
        text.insert("insert", "\n- ")
        return "break"
    else:
        return None


def on_text_change(event):
    global is_getting

    if is_getting:
        return

    ignore_keys = {"Control_L", "Control_R", "Shift_L", "Shift_R", "Alt_L", "Alt_R"}

    if event.keysym in ignore_keys:
        return

    if text.edit_modified():
        close_btn.config(text="●")
        text.edit_modified(False)


def on_enter(e):
    e.widget.config(fg="orange")


def on_leave(e):
    e.widget.config(fg="white")


def on_close():
    save_note()
    text.config(bg="white")
    root.after(50, root.destroy)


# title bar
titlebar = tk.Frame(root, bg="#1e1e1e", relief="raised", pady=5)
titlebar.pack(fill="x", side="top")

# title
title = tk.Label(
    titlebar,
    text="A Note",
    fg="white",
    bg="#1e1e1e",
    font=("Microsoft JhengHei", 14, "bold"),
)
title.pack(side="left", padx=10)

titlebar.bind("<Button-1>", start_move)
titlebar.bind("<B1-Motion>", do_move)
title.bind("<Button-1>", start_move)
title.bind("<B1-Motion>", do_move)

# page frame
mid_frame = tk.Frame(titlebar, bg="#1e1e1e")
mid_frame.pack(side="left", expand=True)

# <
prev_btn = tk.Label(
    mid_frame,
    text="〈",
    fg="white",
    bg="#1e1e1e",
    font=("Microsoft JhengHei", 11, "bold"),
)
prev_btn.pack(side="left", padx=0)
prev_btn.bind("<Enter>", on_enter)
prev_btn.bind("<Leave>", on_leave)
prev_btn.bind("<Button-1>", lambda e: switch_page(-1))

# page number
page_label = tk.Label(
    mid_frame,
    text="1",
    fg="white",
    bg="#1e1e1e",
    font=("Microsoft JhengHei", 11, "bold"),
)
page_label.pack(side="left", padx=0)

# >
next_btn = tk.Label(
    mid_frame,
    text="〉",
    fg="white",
    bg="#1e1e1e",
    font=("Microsoft JhengHei", 11, "bold"),
)
next_btn.pack(side="left", padx=0)
next_btn.bind("<Enter>", on_enter)
next_btn.bind("<Leave>", on_leave)
next_btn.bind("<Button-1>", lambda e: switch_page(1))


# ✕
close_btn = tk.Label(
    titlebar,
    text="✕",
    fg="white",
    bg="#1e1e1e",
    font=("Microsoft JhengHei", 12, "bold"),
)
close_btn.pack(side="right", padx=8)

close_btn.bind("<Enter>", on_enter)
close_btn.bind("<Leave>", on_leave)
close_btn.bind("<Button-1>", lambda e: on_close())

frame = tk.Frame(root, bg="#292929")
frame.pack(fill="both", expand=True)

scrollbar = tk.Scrollbar(frame, width=20, bg="#1e1e1e", activebackground="orange")
scrollbar.pack(side="right", fill="y")

text = tk.Text(
    frame,
    wrap="word",
    font=("Microsoft JhengHei", 12),
    padx=15,
    pady=15,
    bg="#292929",
    fg="white",
    insertbackground="white",
    selectbackground="#335980",
    relief="flat",
    bd=0,
    highlightthickness=0,
    yscrollcommand=scrollbar.set,
    undo=True,
)
bold_font = tkfont.Font(family="Microsoft JhengHei", size=12, weight="bold")

text.tag_config("red", foreground="#ff3300", font=bold_font)
text.tag_config("orange", foreground="#ffa500")
text.tag_config("yellow", foreground="#ffdd7e")

text.pack(fill="both", expand=True)
scrollbar.config(command=text.yview)

# key
root.bind("<Control-s>", lambda e: save_note())
root.bind("<Button-2>", lambda e: on_close())
root.bind("<Control-r>", lambda e: move_to_bottom_right())
text.bind("<Return>", auto_indent)
text.bind("<KeyRelease>", on_text_change)

# close
root.protocol("WM_DELETE_WINDOW", on_close)

# start
load_note()
auto_resize()
switch_page(0)
text.edit_reset()
root.after(10, move_to_bottom_right)
root.mainloop()
