import tkinter as tk
from tkinter import ttk, messagebox
from auth import AuthManager
import json
import os
from datetime import datetime

class GradeManagementView:
    def __init__(self, parent, username=None):
        self.parent = parent
        self.auth_manager = AuthManager()
        self.crypto = self.auth_manager.crypto
        self.grades_file = "data/grades.json"
        self.username = username
        
        self.window = tk.Toplevel(parent)
        self.window.title("Добавление оценки")
        self.window.geometry("600x500")
        
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
        
        self.load_students()
        
    def create_form(self):
        student_frame = ttk.Frame(self.main_frame)
        student_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(student_frame, text="Ученик:").pack(side=tk.LEFT, padx=(0, 10))
        self.student_var = tk.StringVar()
        self.student_combo = ttk.Combobox(student_frame, textvariable=self.student_var, state="readonly")
        self.student_combo.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
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
        
        type_frame = ttk.Frame(self.main_frame)
        type_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(type_frame, text="Тип:").pack(side=tk.LEFT, padx=(0, 10))
        self.type_var = tk.StringVar()
        self.type_combo = ttk.Combobox(type_frame, textvariable=self.type_var, state="readonly")
        self.type_combo["values"] = ["Урок", "Домашнее задание"]
        self.type_combo.pack(side=tk.LEFT, fill=tk.X, expand=True)
        self.type_combo.bind("<<ComboboxSelected>>", self.on_type_change)
        
        # Выбор ДЗ (только если тип - ДЗ)
        self.homework_frame = ttk.Frame(self.main_frame)
        ttk.Label(self.homework_frame, text="Домашнее задание:").pack(side=tk.LEFT, padx=(0, 10))
        self.homework_var = tk.StringVar()
        self.homework_combo = ttk.Combobox(self.homework_frame, textvariable=self.homework_var, state="readonly")
        self.homework_combo.pack(side=tk.LEFT, fill=tk.X, expand=True)
        self.homework_frame.pack(fill=tk.X, pady=(0, 10))
        self.homework_frame.pack_forget()
        
        # Оценка
        grade_frame = ttk.Frame(self.main_frame)
        grade_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(grade_frame, text="Оценка:").pack(side=tk.LEFT, padx=(0, 10))
        self.grade_var = tk.StringVar()
        self.grade_combo = ttk.Combobox(grade_frame, textvariable=self.grade_var, state="readonly")
        self.grade_combo["values"] = ["2", "3", "4", "5"]
        self.grade_combo.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        comments_frame = ttk.Frame(self.main_frame)
        comments_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        ttk.Label(comments_frame, text="Комментарий (необязательно):").pack(anchor=tk.W)
        self.comments_text = tk.Text(comments_frame, height=3)
        self.comments_text.pack(fill=tk.BOTH, expand=True)
        
        ttk.Button(self.main_frame, text="Добавить оценку", command=self.add_grade).pack(fill=tk.X)
        
    def load_students(self):
        try:
            users = self.crypto.load_encrypted_file("data/users.json")
            if not users:
                return
            
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
            
    def load_homework(self):
        try:
            homework_data = self.crypto.load_encrypted_file("data/homework.json")
            if not homework_data:
                return
            
            student = self.student_var.get()
            if not student:
                return
            
            users = self.crypto.load_encrypted_file("data/users.json")
            if not users or student not in users:
                return
            
            group = users[student].get("group", "")
            if not group or group not in homework_data:
                return
            
            subject = self.subject_var.get()
            if not subject or subject not in homework_data[group]:
                return
            
            homework_entries = []
            for entry in homework_data[group][subject]:
                homework_entries.append(f"{entry['date']}: {entry['text']}")
            
            self.homework_combo["values"] = homework_entries
            if homework_entries:
                self.homework_combo.set(homework_entries[0])
            
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось загрузить домашнее задание: {str(e)}")
            
    def on_type_change(self, event=None): 
        if self.type_var.get() == "Homework":
            self.homework_frame.pack(fill=tk.X, pady=(0, 10))
            self.load_homework()
        else:
            self.homework_frame.pack_forget()
            
    def on_student_change(self, *args):
        if self.type_var.get() == "Homework":
            self.load_homework()
            
    def add_grade(self):
        try:
            student = self.student_var.get()
            subject = self.subject_var.get()
            grade_type = self.type_var.get()
            grade = self.grade_var.get()
            comments = self.comments_text.get("1.0", tk.END).strip()
            
            if not student:
                messagebox.showerror("Ошибка", "Пожалуйста, выберите ученика.")
                return
            if not subject:
                messagebox.showerror("Ошибка", "Пожалуйста, выберите предмет.")
                return
            if not grade_type:
                messagebox.showerror("Ошибка", "Пожалуйста, выберите тип оценки.")
                return
            if not grade:
                messagebox.showerror("Ошибка", "Пожалуйста, выберите оценку.")
                return
            
            grades_data = self.crypto.load_encrypted_file(self.grades_file)
            if not grades_data:
                grades_data = {}
            
            if student not in grades_data:
                grades_data[student] = {}
            
            if subject not in grades_data[student]:
                grades_data[student][subject] = []
            
            grade_entry = {
                "date": datetime.now().strftime("%Y-%m-%d %H:%M"),
                "type": grade_type,
                "grade": grade,
                "comments": comments if comments else None,
                "teacher": self.username
            }
            
            if grade_type == "Homework":
                homework = self.homework_var.get()
                if not homework:
                    messagebox.showerror("Ошибка", "Пожалуйста, выберите домашнее задание.")
                    return
                grade_entry["homework"] = homework
            
            grades_data[student][subject].append(grade_entry)
            
            self.crypto.save_encrypted_file(self.grades_file, grades_data)
            
            self.comments_text.delete("1.0", tk.END)
            
            messagebox.showinfo("Успешно", "Оценка успешно добавлена!")
            
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось добавить оценку: {str(e)}") 