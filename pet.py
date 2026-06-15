import tkinter as tk
import json
import os
import time
from datetime import datetime, timedelta

STATE_FILE = os.path.join(os.path.dirname(__file__), "pet_state.json")

DECAY_INTERVAL_SEC = 60
NO_CODING_PENALTY_HOURS = 24


def load_state():
    if not os.path.exists(STATE_FILE):
        return {
            "health": 80,
            "happiness": 80,
            "last_coding_time": time.time(),
        }
    with open(STATE_FILE, "r") as f:
        return json.load(f)


def save_state(state):
    with open(STATE_FILE, "w") as f:
        json.dump(state, f)


class PetApp:
    def __init__(self, root):
        self.root = root
        self.root.title("CodePet")
        self.root.attributes("-topmost", True)
        self.root.resizable(False, False)

        self.state = load_state()

        self.pet_label = tk.Label(root, text="😺", font=("Arial", 40))
        self.pet_label.pack()

        self.status_label = tk.Label(root, text="", font=("Arial", 10), wraplength=200)
        self.status_label.pack()

        self.health_label = tk.Label(root, text="", font=("Arial", 10))
        self.health_label.pack()

        btn_frame = tk.Frame(root)
        btn_frame.pack(pady=5)

        tk.Button(btn_frame, text="I coded!", command=self.mark_coded).grid(row=0, column=0, padx=2)
        tk.Button(btn_frame, text="Too many tabs", command=self.too_many_tabs).grid(row=0, column=1, padx=2)
        tk.Button(btn_frame, text="Lint pass", command=self.lint_pass).grid(row=1, column=0, padx=2, pady=2)
        tk.Button(btn_frame, text="Lint fail", command=self.lint_fail).grid(row=1, column=1, padx=2, pady=2)

        self.update_ui()
        self.schedule_decay()

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
        self.state["happiness"] = max(0, self.state["happiness"] - 1)
        self.state["health"] = max(0, self.state["health"] - 1)

        last = datetime.fromtimestamp(self.state["last_coding_time"])
        if datetime.now() - last > timedelta(hours=NO_CODING_PENALTY_HOURS):
            self.state["happiness"] = max(0, self.state["happiness"] - 3)
            self.state["health"] = max(0, self.state["health"] - 2)

        save_state(self.state)
        self.update_ui()
        self.schedule_decay()

    def update_ui(self):
        h = self.state["health"]
        happy = self.state["happiness"]

        if h > 70 and happy > 70:
            pet, status = "😺", "Happy and healthy! Keep coding."
        elif h > 40 and happy > 40:
            pet, status = "😼", "Doing okay. Could use some clean code."
        elif h > 20:
            pet, status = "😿", "Not feeling great. Maybe close some tabs?"
        else:
            pet, status = "💀", "You've abandoned your pet (and your editor)."

        self.pet_label.config(text=pet)
        self.status_label.config(text=status)
        self.health_label.config(text=f"Health: {h} | Happiness: {happy}")


def main():
    root = tk.Tk()
    PetApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
