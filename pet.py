import os
os.environ.setdefault("PYSTRAY_BACKEND", "xorg")

import tkinter as tk
from PIL import Image, ImageTk
import json
import time
import threading
from datetime import datetime, timedelta
import pystray

STATE_FILE = os.path.join(os.path.dirname(__file__), "pet_state.json")
SPRITE_DIR = os.path.join(os.path.dirname(__file__), "sprites")

DECAY_INTERVAL_SEC = 300
NO_CODING_PENALTY_HOURS = 24


def load_state():
    if not os.path.exists(STATE_FILE):
        return {"health": 80, "happiness": 80, "last_coding_time": time.time()}
    with open(STATE_FILE, "r") as f:
        return json.load(f)


def save_state(state):
    with open(STATE_FILE, "w") as f:
        json.dump(state, f)


def sprite_name(h, happy):
    if h > 70 and happy > 70:
        return "happy"
    elif h > 40 and happy > 40:
        return "okay"
    elif h > 20:
        return "sad"
    return "dead"


def status_text(h, happy):
    if h > 70 and happy > 70:
        return "Happy and healthy! Keep coding."
    elif h > 40 and happy > 40:
        return "Doing okay. Could use some clean code."
    elif h > 20:
        return "Not feeling great. Maybe close some tabs?"
    return "You've abandoned your pet (and your editor)."


class PetApp:
    def __init__(self, root):
        self.root = root
        self.root.title("CodePet")
        self.root.attributes("-topmost", True)
        self.root.resizable(False, False)
        self.root.protocol("WM_DELETE_WINDOW", self._hide)

        self.state = load_state()
        self._load_sprites()

        self.pet_label = tk.Label(root, image=self.sprites["happy"], bg="#ebebeb")
        self.pet_label.pack(pady=2)

        self.status_label = tk.Label(root, text="", font=("Arial", 8), wraplength=150, bg="#ebebeb")
        self.status_label.pack()

        self.health_label = tk.Label(root, text="", font=("Arial", 8), bg="#ebebeb")
        self.health_label.pack()

        root.configure(bg="#ebebeb")

        btn_frame = tk.Frame(root, bg="#ebebeb")
        btn_frame.pack(pady=2)

        tk.Button(btn_frame, text="I coded!", command=self.mark_coded).grid(row=0, column=0, padx=2)
        tk.Button(btn_frame, text="Too many tabs", command=self.too_many_tabs).grid(row=0, column=1, padx=2)
        tk.Button(btn_frame, text="Lint pass", command=self.lint_pass).grid(row=1, column=0, padx=2, pady=2)
        tk.Button(btn_frame, text="Lint fail", command=self.lint_fail).grid(row=1, column=1, padx=2, pady=2)

        self._start_tray()
        self.update_ui()
        self.schedule_decay()

    def _load_sprites(self):
        if not os.path.exists(os.path.join(SPRITE_DIR, "happy.png")):
            import sprites as sp
            sp.generate()
        self.sprites = {}
        self.pil_sprites = {}
        for name in ("happy", "okay", "sad", "dead"):
            img = Image.open(os.path.join(SPRITE_DIR, f"{name}.png"))
            self.pil_sprites[name] = img
            self.sprites[name] = ImageTk.PhotoImage(img)

    def _start_tray(self):
        h, happy = self.state["health"], self.state["happiness"]
        icon_img = self.pil_sprites[sprite_name(h, happy)]
        menu = pystray.Menu(
            pystray.MenuItem("Show / Hide", self._toggle, default=True),
            pystray.MenuItem("Quit", self._quit),
        )
        self.tray = pystray.Icon("CodePet", icon_img, "CodePet", menu)
        threading.Thread(target=self.tray.run, daemon=True).start()

    def _hide(self):
        self.root.withdraw()

    def _toggle(self, icon=None, item=None):
        if self.root.winfo_viewable():
            self.root.after(0, self.root.withdraw)
        else:
            self.root.after(0, self.root.deiconify)

    def _quit(self, icon=None, item=None):
        self.tray.stop()
        self.root.after(0, self.root.destroy)

    def mark_coded(self):
        self.state["last_coding_time"] = time.time()
        self.state["happiness"] = min(100, self.state["happiness"] + 10)
        self.state["health"] = min(100, self.state["health"] + 5)
        save_state(self.state)
        self.update_ui()

    def too_many_tabs(self):
        self.state["happiness"] = max(0, self.state["happiness"] - 15)
        self.state["health"] = max(0, self.state["health"] - 10)
        save_state(self.state)
        self.update_ui()

    def lint_pass(self):
        self.state["happiness"] = min(100, self.state["happiness"] + 8)
        self.state["health"] = min(100, self.state["health"] + 5)
        save_state(self.state)
        self.update_ui()

    def lint_fail(self):
        self.state["happiness"] = max(0, self.state["happiness"] - 5)
        save_state(self.state)
        self.update_ui()

    def schedule_decay(self):
        self.root.after(DECAY_INTERVAL_SEC * 1000, self.decay_tick)

    def decay_tick(self):
        if self._claude_running():
            self.state["happiness"] = min(100, self.state["happiness"] + 1)
            self.state["last_coding_time"] = time.time()
        else:
            self.state["happiness"] = max(0, self.state["happiness"] - 1)
            self.state["health"] = max(0, self.state["health"] - 1)

            last = datetime.fromtimestamp(self.state["last_coding_time"])
            if datetime.now() - last > timedelta(hours=NO_CODING_PENALTY_HOURS):
                self.state["happiness"] = max(0, self.state["happiness"] - 3)
                self.state["health"] = max(0, self.state["health"] - 2)

        save_state(self.state)
        self.update_ui()
        self.schedule_decay()

    def _claude_running(self):
        try:
            import psutil
            return any("claude" in p.name().lower() for p in psutil.process_iter(["name"]))
        except Exception:
            return False

    def update_ui(self):
        h = self.state["health"]
        happy = self.state["happiness"]
        sname = sprite_name(h, happy)

        self.pet_label.config(image=self.sprites[sname])
        self.status_label.config(text=status_text(h, happy))
        self.health_label.config(text=f"Health: {h} | Happiness: {happy}")

        # update tray icon to match current state
        if hasattr(self, "tray"):
            self.tray.icon = self.pil_sprites[sname]
            self.tray.title = f"CodePet — {h}hp {happy}☺"


def main():
    root = tk.Tk()
    PetApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
