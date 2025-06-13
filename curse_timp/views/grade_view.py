import tkinter as tk
from tkinter import ttk, messagebox
from auth import AuthManager
import json
import os

class GradeView:
    def __init__(self, parent, username=None):
        self.parent = parent
        self.auth_manager = AuthManager()
        self.crypto = self.auth_manager.crypto
        self.grades_file = "data/grades.json"
        self.username = username
        
        self.window = tk.Toplevel(parent)
        self.window.title("Просмотр оценок")
        self.window.geometry("800x600")
        
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
        
        self.left_panel = ttk.Frame(self.main_frame, width=200)
        self.left_panel.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 10))
        
        # Раздел учителя/админа
        if self.user_role in ["teacher", "admin"]:
            ttk.Label(self.left_panel, text="Выберите ученика:").pack(fill=tk.X, pady=(0, 5))
            self.student_var = tk.StringVar()
            self.student_combo = ttk.Combobox(self.left_panel, textvariable=self.student_var, state="readonly")
            self.student_combo.pack(fill=tk.X, pady=(0, 10))
            self.student_var.trace("w", self.on_student_change)
        else:
            # Раздел ученика
            ttk.Label(self.left_panel, text="Ваши оценки:").pack(fill=tk.X, pady=(0, 5))
            ttk.Label(self.left_panel, text=username).pack(fill=tk.X, pady=(0, 10))
        
        self.create_grade_view()
        
        self.load_students()
        self.load_grades()
        
    def create_grade_view(self):
        self.notebook = ttk.Notebook(self.main_frame)
        self.notebook.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
    def load_students(self):
        try:
            users = self.crypto.load_encrypted_file("data/users.json")
            if not users:
                return
            
            if self.user_role in ["teacher", "admin"]:
                # Фильтр
                students = []
                for username, data in users.items():
                    if data["role"] == "student":
                        students.append(username)
                
                self.student_combo["values"] = sorted(students)
                if self.student_combo["values"]:
                    self.student_combo.set(self.student_combo["values"][0])
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось загрузить учеников: {str(e)}")
            
    def load_grades(self):
        try:
            # Очистка существующих вкладок
            for tab in self.notebook.tabs():
                self.notebook.forget(tab)
            
            grades_data = self.crypto.load_encrypted_file(self.grades_file)
            if not grades_data:
                return
            
            # Выбор ученика
            student = None
            if self.user_role in ["teacher", "admin"]:
                student = self.student_var.get()
            else:
                student = self.username
            
            if not student or student not in grades_data:
                return
            
            # Создание вкладок предметов
            for subject, entries in grades_data[student].items():
                # Пропуск предметов, не соответствующих учителю
                if self.user_role == "teacher" and subject != self.user_subject:
                    continue
                
                frame = ttk.Frame(self.notebook)
                self.notebook.add(frame, text=subject)
                
                columns = ("Дата", "Тип", "Оценка", "Домашнее задание", "Комментарий", "Учитель")
                tree = ttk.Treeview(frame, columns=columns, show="headings")
                
                tree.heading("Дата", text="Дата")
                tree.heading("Тип", text="Тип")
                tree.heading("Оценка", text="Оценка")
                tree.heading("Домашнее задание", text="Домашнее задание")
                tree.heading("Комментарий", text="Комментарий")
                tree.heading("Учитель", text="Учитель")
                
                tree.column("Дата", width=150)
                tree.column("Тип", width=100)
                tree.column("Оценка", width=50)
                tree.column("Домашнее задание", width=200)
                tree.column("Комментарий", width=200)
                tree.column("Учитель", width=100)
                
                scrollbar = ttk.Scrollbar(frame, orient=tk.VERTICAL, command=tree.yview)
                tree.configure(yscrollcommand=scrollbar.set)
                
                tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
                scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
                
                for entry in entries:
                    tree.insert("", tk.END, values=(
                        entry["date"],
                        entry["type"],
                        entry["grade"],
                        entry.get("homework", ""),
                        entry.get("comments", ""),
                        entry["teacher"]
                    ))
                    
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось загрузить оценки: {str(e)}")
            
    def on_student_change(self, *args):
        self.load_grades() 