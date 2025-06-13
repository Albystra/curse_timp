import tkinter as tk
from tkinter import ttk, messagebox
import json
import os

class SubjectManagementView:
    def __init__(self, parent):
        self.parent = parent
        self.subjects_file = "data/subjects.json"
        
        self.window = tk.Toplevel(parent)
        self.window.title("Управление предметами")
        self.window.geometry("400x500")
        
        self.main_frame = ttk.Frame(self.window, padding="10")
        self.main_frame.pack(fill=tk.BOTH, expand=True)
        
        self.listbox_frame = ttk.Frame(self.main_frame)
        self.listbox_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        self.listbox = tk.Listbox(self.listbox_frame, font=('Helvetica', 10))
        self.listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        scrollbar = ttk.Scrollbar(self.listbox_frame, orient=tk.VERTICAL, command=self.listbox.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.listbox.configure(yscrollcommand=scrollbar.set)
        
        self.entry_frame = ttk.Frame(self.main_frame)
        self.entry_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.subject_entry = ttk.Entry(self.entry_frame)
        self.subject_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))
        
        self.button_frame = ttk.Frame(self.main_frame)
        self.button_frame.pack(fill=tk.X)
        
        ttk.Button(self.button_frame, text="Добавить предмет", command=self.add_subject).pack(side=tk.LEFT, padx=5)
        ttk.Button(self.button_frame, text="Удалить выбранный предмет", command=self.delete_subject).pack(side=tk.LEFT, padx=5)
        
        self.load_subjects()
        
        self.subject_entry.bind('<Return>', lambda e: self.add_subject())
        
        self.subject_entry.focus()

    def load_subjects(self):
        try:
            if not os.path.exists(self.subjects_file):
                self._create_default_subjects()
            
            with open(self.subjects_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                subjects = data.get('subjects', [])
            
            self.listbox.delete(0, tk.END)
            for subject in sorted(subjects):
                self.listbox.insert(tk.END, subject)
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось загрузить предметы: {str(e)}")

    def _create_default_subjects(self):
        default_subjects = {
            "subjects": [
                "Математика",
                "Русский язык",
                "Литература",
                "Физика",
                "Химия",
                "Биология",
                "История",
                "География",
                "Английский язык",
                "Информатика"
            ]
        }
        
        os.makedirs(os.path.dirname(self.subjects_file), exist_ok=True)
        with open(self.subjects_file, 'w', encoding='utf-8') as f:
            json.dump(default_subjects, f, ensure_ascii=False, indent=4)

    def add_subject(self):
        subject = self.subject_entry.get().strip()
        if not subject:
            messagebox.showwarning("Предупреждение", "Пожалуйста, введите название предмета.")
            return
        
        try:
            with open(self.subjects_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                subjects = data.get('subjects', [])
            
            if subject in subjects:
                messagebox.showwarning("Предупреждение", "Этот предмет уже существует.")
                return
            
            subjects.append(subject)
            subjects.sort()
            
            with open(self.subjects_file, 'w', encoding='utf-8') as f:
                json.dump({"subjects": subjects}, f, ensure_ascii=False, indent=4)
            
            self.load_subjects()
            
            self.subject_entry.delete(0, tk.END)
            
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось добавить предмет: {str(e)}")

    def delete_subject(self):
        selection = self.listbox.curselection()
        if not selection:
            messagebox.showwarning("Предупреждение", "Пожалуйста, выберите предмет для удаления.")
            return
        
        subject = self.listbox.get(selection[0])
        if messagebox.askyesno("Подтверждение", f"Вы уверены, что хотите удалить предмет: '{subject}'?"):
            try:
                with open(self.subjects_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    subjects = data.get('subjects', [])
                
                subjects.remove(subject)
                
                with open(self.subjects_file, 'w', encoding='utf-8') as f:
                    json.dump({"subjects": subjects}, f, ensure_ascii=False, indent=4)
                
                self.load_subjects()
                
            except Exception as e:
                messagebox.showerror("Ошибка", f"Не удалось удалить предмет: {str(e)}")

    def get_subjects(self):
        try:
            with open(self.subjects_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return sorted(data.get('subjects', []))
        except Exception:
            return [] 