import tkinter as tk
from tkinter import ttk, messagebox
from auth import AuthManager
import json
import os

class ScheduleView:
    def __init__(self, parent, username=None):
        self.parent = parent
        self.auth_manager = AuthManager()
        self.crypto = self.auth_manager.crypto
        self.schedule_file = "data/schedule.json"
        self.username = username
        
        self.window = tk.Toplevel(parent)
        self.window.title("Расписание")
        self.window.geometry("1200x800")
        
        self.main_frame = ttk.Frame(self.window, padding="10")
        self.main_frame.pack(fill=tk.BOTH, expand=True)
        
        self.left_panel = ttk.Frame(self.main_frame, width=200)
        self.left_panel.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 10))
        
        self.user_role = None
        self.user_group = None
        if username:
            try:
                users = self.crypto.load_encrypted_file("data/users.json")
                if users and username in users:
                    self.user_role = users[username]["role"]
                    self.user_group = users[username].get("group", "")
            except Exception as e:
                messagebox.showerror("Ошибка", f"Не удалось загрузить данные пользователя: {str(e)}")
        
        if self.user_role in ["admin", "teacher"]:
            ttk.Label(self.left_panel, text="Выберите класс:").pack(fill=tk.X, pady=(0, 5))
            self.group_var = tk.StringVar()
            self.group_combo = ttk.Combobox(self.left_panel, textvariable=self.group_var, state="readonly")
            self.group_combo.pack(fill=tk.X, pady=(0, 10))
            self.group_var.trace("w", self.on_group_change)
        else:
            ttk.Label(self.left_panel, text="Ваш класс:").pack(fill=tk.X, pady=(0, 5))
            ttk.Label(self.left_panel, text=self.user_group).pack(fill=tk.X, pady=(0, 10))
        
        self.schedule_frame = ttk.Frame(self.main_frame)
        self.schedule_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        self.time_slots = [
            "8:00 - 8:40",
            "8:50 - 9:30",
            "9:40 - 10:20",
            "10:40 - 11:20",
            "11:30 - 12:10",
            "12:20 - 13:00"
        ]
        
        self.create_schedule_grid()
        
        self.load_groups()
        self.load_schedule()

    def create_schedule_grid(self):
        header_frame = ttk.Frame(self.schedule_frame)
        header_frame.pack(fill=tk.X)
        
        ttk.Label(header_frame, text="Время", width=15).pack(side=tk.LEFT)
        
        self.days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"]
        for day in self.days:
            frame = ttk.Frame(header_frame)
            frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
            ttk.Label(frame, text=day, anchor="center").pack(fill=tk.X)
        
        self.slot_labels = []
        for time in self.time_slots:
            frame = ttk.Frame(self.schedule_frame)
            frame.pack(fill=tk.X, pady=2)
            
            ttk.Label(frame, text=time, width=15).pack(side=tk.LEFT)
            
            day_slots = []
            for i in range(len(self.days)):
                label = ttk.Label(frame, text="", anchor="center")
                label.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=2)
                day_slots.append(label)
            self.slot_labels.append(day_slots)

    def load_groups(self):
        try:
            groups = self.crypto.load_encrypted_file("data/groups.json")
            if not groups:
                groups = {}
            
            if self.user_role in ["admin", "teacher"]:
                self.group_combo["values"] = sorted(groups.keys())
                if self.user_role == "teacher" and self.user_group:
                    self.group_combo.set(self.user_group)
                elif self.group_combo["values"]:
                    self.group_combo.set(self.group_combo["values"][0])
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось загрузить группы: {str(e)}")

    def load_schedule(self):
        try:
            schedule = self.crypto.load_encrypted_file(self.schedule_file)
            if not schedule:
                return
            
            group = None
            if self.user_role in ["admin", "teacher"]:
                group = self.group_var.get()
            else:
                group = self.user_group
            
            if not group or group not in schedule:
                return
            
            for i, day in enumerate(self.days):
                for j, time in enumerate(self.time_slots):
                    subject = schedule[group][day].get(time, "")
                    self.slot_labels[j][i].configure(text=subject)
                    
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось загрузить расписание: {str(e)}")

    def on_group_change(self, *args):
        self.load_schedule() 