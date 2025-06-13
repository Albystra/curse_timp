import tkinter as tk
from tkinter import ttk, messagebox
from auth import AuthManager
import json
import os
from datetime import datetime

class HomeworkManagementView:
    def __init__(self, parent, username=None):
        self.parent = parent
        self.auth_manager = AuthManager()
        self.crypto = self.auth_manager.crypto
        self.homework_file = "data/homework.json"
        self.username = username
        
        self.window = tk.Toplevel(parent)
        self.window.title("Добавить домашнее задание")
        self.window.geometry("600x400")
        
        self.main_frame = ttk.Frame(self.window, padding="10")
        self.main_frame.pack(fill=tk.BOTH, expand=True)
        
        self.user_role = None
        self.user_subject = None
        if username:
            try:
                users = self.crypto.load_encrypted_file("data/users.json")
                if users and username in users:
                    self.user_role = users[username]["role"]
                    self.user_subject = users[username].get("subject", "")
            except Exception as e:
                messagebox.showerror("Ошибка", f"Не удалось загрузить данные пользователя: {str(e)}")
        
        self.create_form()
        
        self.load_groups()
        
    def create_form(self):
        group_frame = ttk.Frame(self.main_frame)
        group_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(group_frame, text="Класс:").pack(side=tk.LEFT, padx=(0, 10))
        self.group_var = tk.StringVar()
        self.group_combo = ttk.Combobox(group_frame, textvariable=self.group_var, state="readonly")
        self.group_combo.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        subject_frame = ttk.Frame(self.main_frame)
        subject_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(subject_frame, text="Предмет:").pack(side=tk.LEFT, padx=(0, 10))
        self.subject_var = tk.StringVar()
        if self.user_role == "admin":
            self.subject_combo = ttk.Combobox(subject_frame, textvariable=self.subject_var, state="readonly")
            self.subject_combo.pack(side=tk.LEFT, fill=tk.X, expand=True)
            self.load_subjects()
        else:
            ttk.Label(subject_frame, text=self.user_subject).pack(side=tk.LEFT)
            self.subject_var.set(self.user_subject)
        
        homework_frame = ttk.Frame(self.main_frame)
        homework_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        ttk.Label(homework_frame, text="Домашнее задание:").pack(anchor=tk.W)
        self.homework_text = tk.Text(homework_frame, height=5)
        self.homework_text.pack(fill=tk.BOTH, expand=True)
        
        details_frame = ttk.Frame(self.main_frame)
        details_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        ttk.Label(details_frame, text="Подробности (необязательно):").pack(anchor=tk.W)
        self.details_text = tk.Text(details_frame, height=3)
        self.details_text.pack(fill=tk.BOTH, expand=True)
        
        ttk.Button(self.main_frame, text="Добавить домашнее задание", command=self.add_homework).pack(fill=tk.X)
        
    def load_groups(self):
        try:
            groups = self.crypto.load_encrypted_file("data/groups.json")
            if not groups:
                groups = {}
            
            self.group_combo["values"] = sorted(groups.keys())
            if self.group_combo["values"]:
                self.group_combo.set(self.group_combo["values"][0])
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось загрузить классы: {str(e)}")
            
    def load_subjects(self):
        try:
            with open("data/subjects.json", "r", encoding="utf-8") as f:
                data = json.load(f)
                if isinstance(data, dict) and "subjects" in data:
                    subjects = data["subjects"]
                    if isinstance(subjects, list):
                        self.subject_combo["values"] = subjects
                        if subjects:
                            self.subject_combo.set(subjects[0])
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось загрузить предметы: {str(e)}")
            
    def add_homework(self):
        try:
            group = self.group_var.get()
            subject = self.subject_var.get()
            homework = self.homework_text.get("1.0", tk.END).strip()
            details = self.details_text.get("1.0", tk.END).strip()
            
            if not group:
                messagebox.showerror("Ошибка", "Пожалуйста, выберите класс.")
                return
            if not subject:
                messagebox.showerror("Ошибка", "Пожалуйста, выберите предмет.")
                return
            if not homework:
                messagebox.showerror("Ошибка", "Пожалуйста, введите домашнее задание.")
                return
            
            homework_data = self.crypto.load_encrypted_file(self.homework_file)
            if not homework_data:
                homework_data = {}
            
            if group not in homework_data:
                homework_data[group] = {}
            
            if subject not in homework_data[group]:
                homework_data[group][subject] = []
            
            homework_entry = {
                "date": datetime.now().strftime("%Y-%m-%d %H:%M"),
                "text": homework,
                "details": details if details else None,
                "teacher": self.username
            }
            
            homework_data[group][subject].append(homework_entry)
            
            self.crypto.save_encrypted_file(self.homework_file, homework_data)
            
            self.homework_text.delete("1.0", tk.END)
            self.details_text.delete("1.0", tk.END)
            
            messagebox.showinfo("Успешно", "Домашнее задание успешно добавлено!")
            
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось добавить домашнее задание: {str(e)}") 