

import tkinter as tk
from tkinter import ttk, messagebox
import time
import threading
import math

class AptitudeTimer:
    def __init__(self, master):
        self.master = master
        master.title("Timer")
        master.attributes("-topmost", True)
        master.resizable(False, False)
        master.geometry("+200+120")


        self.total_seconds = 0
        self.interval_seconds = 0
        self.remaining = 0
        self.running = False
        self.next_alarm = None
        self.last_update_time = None


        frm = ttk.Frame(master, padding=8)
        frm.grid()


        ttk.Label(frm, text="Hours:").grid(row=0, column=0, sticky="w")
        self.hours_var = tk.StringVar(value="1")
        self.hours_entry = ttk.Entry(frm, width=5, textvariable=self.hours_var)
        self.hours_entry.grid(row=0, column=1, sticky="w", padx=(0,8))
        self.hours_entry.bind("<KeyRelease>", lambda e: self.on_input_change())

        ttk.Label(frm, text="Minutes:").grid(row=0, column=2, sticky="w")
        self.minutes_var = tk.StringVar(value="0")
        self.minutes_entry = ttk.Entry(frm, width=5, textvariable=self.minutes_var)
        self.minutes_entry.grid(row=0, column=3, sticky="w", padx=(0,8))
        self.minutes_entry.bind("<KeyRelease>", lambda e: self.on_input_change())

        ttk.Label(frm, text="Interval (min):").grid(row=0, column=4, sticky="w")
        self.interval_var = tk.StringVar(value="3")
        self.interval_entry = ttk.Entry(frm, width=5, textvariable=self.interval_var)
        self.interval_entry.grid(row=0, column=5, sticky="w")



        self.time_label = ttk.Label(frm, text="01:00:00", font=("Helvetica", 24))
        self.time_label.grid(row=1, column=0, columnspan=6, pady=(8,8))


        btn_frame = ttk.Frame(frm)
        btn_frame.grid(row=2, column=0, columnspan=6)

        self.start_btn = ttk.Button(btn_frame, text="Start", command=self.start)
        self.start_btn.grid(row=0, column=0, padx=4)
        self.pause_btn = ttk.Button(btn_frame, text="Pause", command=self.toggle_pause, state="disabled")
        self.pause_btn.grid(row=0, column=1, padx=4)
        self.reset_btn = ttk.Button(btn_frame, text="Reset", command=self.reset)
        self.reset_btn.grid(row=0, column=2, padx=4)

        self.status_label = ttk.Label(frm, text="Idle", font=("Helvetica", 9))
        self.status_label.grid(row=3, column=0, columnspan=6, pady=(6,0))


        self.on_input_change()


        master.bind("<Escape>", lambda e: master.destroy())


    def parse_hours_minutes(self):

        try:
            h = float(self.hours_var.get()) if self.hours_var.get().strip() != "" else 0.0
        except Exception:
            h = None
        try:
            m = float(self.minutes_var.get()) if self.minutes_var.get().strip() != "" else 0.0
        except Exception:
            m = None
        return h, m

    def on_input_change(self):

        h, m = self.parse_hours_minutes()
        if h is None or m is None or h < 0 or m < 0:

            self.time_label.config(text="--:--:--")
            return
        total = int(h * 3600 + m * 60)
        self.update_time_label(total)

    def update_time_label(self, seconds):

        if seconds < 0:
            seconds = 0
        if seconds >= 3600:
            hh = seconds // 3600
            mm = (seconds % 3600) // 60
            ss = seconds % 60
            self.time_label.config(text=f"{int(hh):02d}:{int(mm):02d}:{int(ss):02d}")
        else:
            mm = seconds // 60
            ss = seconds % 60
            self.time_label.config(text=f"{int(mm):02d}:{int(ss):02d}")


    def start(self):
        if self.running:
            return

        h, m = self.parse_hours_minutes()
        if h is None or m is None or h < 0 or m < 0:
            messagebox.showerror("Input error", "Please enter valid non-negative numbers for hours and minutes.")
            return
        try:
            interval_min = float(self.interval_var.get())
        except Exception:
            messagebox.showerror("Input error", "Please enter a valid interval in minutes.")
            return
        if interval_min <= 0:
            messagebox.showerror("Input error", "Interval must be positive.")
            return

        self.total_seconds = int(h * 3600 + m * 60)
        if self.total_seconds <= 0:
            messagebox.showerror("Input error", "Total time must be greater than zero.")
            return

        self.interval_seconds = int(interval_min * 60)
        self.remaining = self.total_seconds


        self.next_alarm = self.remaining - self.interval_seconds
        if self.next_alarm < 0:

            self.next_alarm = 0

        self.running = True
        self.last_update_time = time.time()
        self.set_ui_running(True)
        self.status_label.config(text="Running")
        self._tick()

    def toggle_pause(self):
        if not self.running:
            return

        if self.pause_btn.config('text')[-1] == 'Pause':

            self.running = False
            self.pause_btn.config(text="Resume")
            self.status_label.config(text="Paused")
        else:

            self.running = True
            self.last_update_time = time.time()
            self.pause_btn.config(text="Pause")
            self.status_label.config(text="Running")
            self._tick()

    def reset(self):
        self.running = False
        self.set_ui_running(False)

        h, m = self.parse_hours_minutes()
        if h is None or m is None or h < 0 or m < 0:
            self.remaining = 0
        else:
            self.remaining = int(h * 3600 + m * 60)
        self.update_time_label(self.remaining)
        self.status_label.config(text="Idle")
        self.pause_btn.config(text="Pause", state="disabled")

    def set_ui_running(self, running):
        if running:
            self.start_btn.config(state="disabled")
            self.pause_btn.config(state="normal")
            self.reset_btn.config(state="normal")
        else:
            self.start_btn.config(state="normal")
            self.pause_btn.config(state="disabled")


    def _tick(self):
        if not self.running:
            return
        now = time.time()
        elapsed = now - (self.last_update_time or now)

        dec = int(elapsed)
        if dec < 0:
            dec = 0
        if dec > 0:
            self.remaining -= dec
            self.last_update_time = now

        if self.remaining <= 0:
            self.remaining = 0
            self.update_time_label(0)
            self.status_label.config(text="Time's up!")

            threading.Thread(target=self.play_sound, daemon=True).start()
            self.running = False
            self.set_ui_running(False)
            return


        if self.next_alarm is not None and self.remaining <= self.next_alarm:

            threading.Thread(target=self.play_sound, daemon=True).start()

            self.next_alarm -= self.interval_seconds
            if self.next_alarm < 0:
                self.next_alarm = None


        self.update_time_label(self.remaining)


        self.master.after(300, self._tick)


    def play_sound(self):

        try:
            import simpleaudio as sa
            import numpy as np
            freq = 880  # Hz
            fs = 44100
            duration = 0.18
            t = np.linspace(0, duration, int(fs * duration), False)
            note = np.sin(freq * t * 2 * math.pi)
            audio = (note * (2**15 - 1)).astype(np.int16)
            sa.play_buffer(audio, 1, 2, fs)
            return
        except Exception:
            pass
        try:
            import winsound
            winsound.Beep(800, 200)
            return
        except Exception:
            pass
        try:
            self.master.bell()
            return
        except Exception:
            print("\a")

if __name__ == "__main__":
    window = tk.Tk()
    app = AptitudeTimer(window)
    window.config(bg="lightblue")
    window.mainloop()





