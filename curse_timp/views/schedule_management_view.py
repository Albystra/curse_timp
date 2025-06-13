import tkinter as tk
from tkinter import ttk, messagebox
from auth import AuthManager
import json
import os
from datetime import datetime, timedelta

class ScheduleManagementView:
    def __init__(self, parent):
        self.parent = parent
        self.auth_manager = AuthManager()
        self.crypto = self.auth_manager.crypto
        self.schedule_file = "data/schedule.json"
        self.unsaved_changes = False
        
        self.window = tk.Toplevel(parent)
        self.window.title("Управление расписанием")
        self.window.geometry("1200x800")
        
        self.main_frame = ttk.Frame(self.window, padding="10")
        self.main_frame.pack(fill=tk.BOTH, expand=True)
        
        self.left_panel = ttk.Frame(self.main_frame, width=200)
        self.left_panel.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 10))
        
        ttk.Label(self.left_panel, text="Выберите класс:").pack(fill=tk.X, pady=(0, 5))
        self.group_var = tk.StringVar()
        self.group_combo = ttk.Combobox(self.left_panel, textvariable=self.group_var, state="readonly")
        self.group_combo.pack(fill=tk.X, pady=(0, 10))
        self.group_var.trace("w", self.on_group_change)
        
        self.save_button = ttk.Button(self.left_panel, text="Сохранить изменения", command=self.save_schedule, state="disabled")
        self.save_button.pack(fill=tk.X, pady=(0, 10))
        
        self.schedule_frame = ttk.Frame(self.main_frame)
        self.schedule_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        self.time_slots = [
            "8:00 - 8:40",
            "8:50 - 9:30",
            "9:40 - 10:20",
            "10:40 - 11:20",  # Между 3 и 4 уроком - 20 минут перерыв на обед
            "11:30 - 12:10",
            "12:20 - 13:00"
        ]
        
        self.create_schedule_grid()
        
        self.load_groups()
        self.load_schedule()

        self.window.protocol("WM_DELETE_WINDOW", self.on_close)

    def create_schedule_grid(self):
        header_frame = ttk.Frame(self.schedule_frame)
        header_frame.pack(fill=tk.X)
        
        ttk.Label(header_frame, text="Время", width=15).pack(side=tk.LEFT)
        
        self.days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"]
        for day in self.days:
            frame = ttk.Frame(header_frame)
            frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
            ttk.Label(frame, text=day, anchor="center").pack(fill=tk.X)
        
        self.slot_combos = []
        for time in self.time_slots:
            frame = ttk.Frame(self.schedule_frame)
            frame.pack(fill=tk.X, pady=2)
            
            ttk.Label(frame, text=time, width=15).pack(side=tk.LEFT)
            
            day_slots = []
            for i in range(len(self.days)):
                combo = ttk.Combobox(frame, state="readonly")
                combo.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=2)
                combo.bind("<<ComboboxSelected>>", lambda e, day=day, time=time: self.on_subject_selected(day, time))
                day_slots.append(combo)
            self.slot_combos.append(day_slots)

    def load_groups(self):
        try:
            groups = self.crypto.load_encrypted_file("data/groups.json")
            if not groups:
                groups = {}
            
            self.group_combo["values"] = sorted(groups.keys())
            if self.group_combo["values"]:
                self.group_combo.set(self.group_combo["values"][0])
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось загрузить группы: {str(e)}")

    def _get_subjects(self):
        try:
            with open("data/subjects.json", "r", encoding="utf-8") as f:
                data = json.load(f)
                if isinstance(data, dict) and "subjects" in data:
                    subjects = data["subjects"]
                    if isinstance(subjects, list):
                        return [""] + subjects
            return [""]
        except FileNotFoundError:
            messagebox.showwarning("Предупреждение", "Файл subjects.json не найден.")
            return [""]
        except json.JSONDecodeError:
            messagebox.showwarning("Предупреждение", "Неверный формат файла subjects.json.")
            return [""]
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось загрузить предметы: {str(e)}")
            return [""]

    def load_schedule(self):
        try:
            schedule = self.crypto.load_encrypted_file(self.schedule_file)
            if not schedule:
                schedule = self._create_default_schedule()
            
            group = self.group_var.get()
            if not group:
                return
            
            if group not in schedule:
                schedule[group] = self._create_default_schedule()[group]
            
            subjects = self._get_subjects()
            for i, day in enumerate(self.days):
                for j, time in enumerate(self.time_slots):
                    combo = self.slot_combos[j][i]
                    combo["values"] = subjects
                    subject = schedule[group][day].get(time, "")
                    combo.set(subject)
            
            self.unsaved_changes = False
            self.save_button.configure(state="disabled")
                    
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось загрузить расписание: {str(e)}")

    def _create_default_schedule(self):
        schedule = {}
        try:
            groups = self.crypto.load_encrypted_file("data/groups.json")
            if not groups:
                groups = {}
            
            for group in groups:
                schedule[group] = {}
                for day in self.days:
                    schedule[group][day] = {}
                    for time in self.time_slots:
                        schedule[group][day][time] = ""
            
            self.crypto.save_encrypted_file(self.schedule_file, schedule)
            
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось создать расписание: {str(e)}")
        
        return schedule

    def on_group_change(self, *args):
        if self.unsaved_changes:
            if messagebox.askyesno("Несохранённые изменения", "У вас есть несохраненные изменения. Вы хотите сохранить перед переключением класса?"):
                self.save_schedule()
            else:
                self.unsaved_changes = False
                self.save_button.configure(state="disabled")
        self.load_schedule()

    def on_subject_selected(self, day, time):
        self.unsaved_changes = True
        self.save_button.configure(state="normal")

    def save_schedule(self):
        try:
            schedule = self.crypto.load_encrypted_file(self.schedule_file)
            if not schedule:
                schedule = self._create_default_schedule()
            
            group = self.group_var.get()
            if not group:
                return
            
            if group not in schedule:
                schedule[group] = self._create_default_schedule()[group]
            
            for i, day in enumerate(self.days):
                for j, time in enumerate(self.time_slots):
                    combo = self.slot_combos[j][i]
                    schedule[group][day][time] = combo.get()
            
            self.crypto.save_encrypted_file(self.schedule_file, schedule)
            
            self.unsaved_changes = False
            self.save_button.configure(state="disabled")
            
            messagebox.showinfo("Успешно", "Расписание успешно сохранено!")
            
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось сохранить расписание: {str(e)}")

    def on_close(self):
        if self.unsaved_changes:
            if messagebox.askyesno("Несохранённые изменения", "У вас есть несохраненные изменения. Вы хотите сохранить перед закрытием?"):
                self.save_schedule()
        self.window.destroy() 