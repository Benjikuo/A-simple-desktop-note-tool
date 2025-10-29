import tkinter as tk
import json
import os
import ctypes

SAVE_FILE = "note.json"

root = tk.Tk()
root.overrideredirect(True)

user32 = ctypes.windll.user32
screen_width = user32.GetSystemMetrics(0)
screen_height = user32.GetSystemMetrics(1)


def save_note():
    content = text.get("1.0", "end-1c")
    with open(SAVE_FILE, "w", encoding="utf-8") as f:
        json.dump({"content": content}, f, ensure_ascii=False, indent=2)
    close_btn.config(text="✕")


def load_note():
    if os.path.exists(SAVE_FILE):
        try:
            with open(SAVE_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
            text.insert("1.0", data.get("content", ""))
        except Exception:
            pass


def on_close():
    save_note()
    text.config(bg="white")
    root.after(50, root.destroy)


def start_move(event):
    global drag_x, drag_y
    drag_x = event.x
    drag_y = event.y


def do_move(event):
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
    lines = int(text.index("end-1c").split(".")[0])
    line_height = 20
    new_height = min(max(lines * line_height, 200) + 100, 550)
    root.geometry(f"200x{new_height}+{root.winfo_x()}+{root.winfo_y()}")
    root.after(200, auto_resize)


def on_text_change(event):
    if text.edit_modified():
        close_btn.config(text="●")
        text.edit_modified(False)


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


def on_enter(e):
    close_btn.config(fg="orange")


def on_leave(e):
    close_btn.config(fg="white")


titlebar = tk.Frame(root, bg="#1e1e1e", relief="raised", pady=5)
titlebar.pack(fill="x", side="top")

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
    selectbackground="orange",
    selectforeground="black",
    relief="flat",
    bd=0,
    highlightthickness=0,
    yscrollcommand=scrollbar.set,
    undo=True,
)
text.pack(fill="both", expand=True)
scrollbar.config(command=text.yview)

root.bind("<Button-2>", lambda e: on_close())
root.bind("<Control-s>", lambda e: save_note())
root.bind("<Control-r>", lambda e: move_to_bottom_right())
text.bind("<Return>", auto_indent)
text.bind("<KeyRelease>", on_text_change)

root.protocol("WM_DELETE_WINDOW", on_close)

load_note()
auto_resize()
text.edit_reset()
root.after(10, move_to_bottom_right)
root.mainloop()
