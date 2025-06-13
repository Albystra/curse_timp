import tkinter as tk
from tkinter import ttk, messagebox
from auth import AuthManager
import json
import os

class HomeworkView:
    def __init__(self, parent, username=None):
        self.parent = parent
        self.auth_manager = AuthManager()
        self.crypto = self.auth_manager.crypto
        self.homework_file = "data/homework.json"
        self.username = username
        
        self.window = tk.Toplevel(parent)
        self.window.title("Просмотр домашнего задания")
        self.window.geometry("800x600")
        
        self.main_frame = ttk.Frame(self.window, padding="10")
        self.main_frame.pack(fill=tk.BOTH, expand=True)
        
        self.user_role = None
        self.user_group = None
        self.user_subject = None
        if username:
            try:
                users = self.crypto.load_encrypted_file("data/users.json")
                if users and username in users:
                    self.user_role = users[username]["role"]
                    self.user_group = users[username].get("group", "")
                    self.user_subject = users[username].get("subject", "")
            except Exception as e:
                messagebox.showerror("Ошибка", f"Не удалось загрузить данные пользователя: {str(e)}")
        
        self.left_panel = ttk.Frame(self.main_frame, width=200)
        self.left_panel.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 10))
        
        if self.user_role in ["teacher", "admin"]:
            ttk.Label(self.left_panel, text="Выберите класс:").pack(fill=tk.X, pady=(0, 5))
            self.group_var = tk.StringVar()
            self.group_combo = ttk.Combobox(self.left_panel, textvariable=self.group_var, state="readonly")
            self.group_combo.pack(fill=tk.X, pady=(0, 10))
            self.group_var.trace("w", self.on_group_change)
        else:
            ttk.Label(self.left_panel, text="Ваш класс:").pack(fill=tk.X, pady=(0, 5))
            ttk.Label(self.left_panel, text=self.user_group).pack(fill=tk.X, pady=(0, 10))
        
        self.create_homework_view()
        
        self.load_groups()
        self.load_homework()
        
    def create_homework_view(self):
        self.notebook = ttk.Notebook(self.main_frame)
        self.notebook.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
    def load_groups(self):
        try:
            groups = self.crypto.load_encrypted_file("data/groups.json")
            if not groups:
                groups = {}
            
            if self.user_role in ["teacher", "admin"]:
                self.group_combo["values"] = sorted(groups.keys())
                if self.user_group and self.user_role == "teacher":
                    self.group_combo.set(self.user_group)
                elif self.group_combo["values"]:
                    self.group_combo.set(self.group_combo["values"][0])
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось загрузить группы: {str(e)}")
            
    def load_homework(self):
        try:
            for tab in self.notebook.tabs():
                self.notebook.forget(tab)
            
            homework_data = self.crypto.load_encrypted_file(self.homework_file)
            if not homework_data:
                return
            
            group = None
            if self.user_role in ["teacher", "admin"]:
                group = self.group_var.get()
            else:
                group = self.user_group
            
            if not group or group not in homework_data:
                return
            
            # Вкладки на предметы
            for subject, entries in homework_data[group].items():
                # Пропуск предметов, не соответствующих учителю
                if self.user_role == "teacher" and subject != self.user_subject:
                    continue
                
                frame = ttk.Frame(self.notebook)
                self.notebook.add(frame, text=subject)
                
                # Создание дерева для записей ДЗ
                columns = ("Дата", "Домашнее задание", "Подробности", "Учитель")
                tree = ttk.Treeview(frame, columns=columns, show="headings")
                
                # Настройка столбцов
                tree.heading("Дата", text="Дата")
                tree.heading("Домашнее задание", text="Домашнее задание")
                tree.heading("Подробности", text="Подробности")
                tree.heading("Учитель", text="Учитель")
                
                tree.column("Дата", width=150)
                tree.column("Домашнее задание", width=200)
                tree.column("Подробности", width=200)
                tree.column("Учитель", width=100)
                
                scrollbar = ttk.Scrollbar(frame, orient=tk.VERTICAL, command=tree.yview)
                tree.configure(yscrollcommand=scrollbar.set)
                
                tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
                scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
                
                for entry in entries:
                    tree.insert("", tk.END, values=(
                        entry["date"],
                        entry["text"],
                        entry["details"] if entry["details"] else "",
                        entry["teacher"]
                    ))
                    
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось загрузить домашнее задание: {str(e)}")
            
    def on_group_change(self, *args):
        self.load_homework()