import tkinter as tk
from tkinter import ttk, messagebox
from auth import AuthManager
import json
import os

class GroupManagementView:
    def __init__(self, parent):
        self.parent = parent
        self.auth_manager = AuthManager()
        self.crypto = self.auth_manager.crypto
        self.groups_file = "data/groups.json"
        
        self.window = tk.Toplevel(parent)
        self.window.title("Управление классами")
        self.window.geometry("800x600")
        
        self.main_frame = ttk.Frame(self.window, padding="10")
        self.main_frame.pack(fill=tk.BOTH, expand=True)
        
        self.listbox_frame = ttk.Frame(self.main_frame)
        self.listbox_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        self.listbox = tk.Listbox(self.listbox_frame, font=('Helvetica', 10))
        self.listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        scrollbar = ttk.Scrollbar(self.listbox_frame, orient=tk.VERTICAL, command=self.listbox.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.listbox.bind('<<ListboxSelect>>', self.on_group_select)
        
        self.entry_frame = ttk.Frame(self.main_frame)
        self.entry_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(self.entry_frame, text="Название класса:").pack(side=tk.LEFT, padx=5)
        self.group_entry = ttk.Entry(self.entry_frame)
        self.group_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        
        self.button_frame = ttk.Frame(self.main_frame)
        self.button_frame.pack(fill=tk.X)
        
        ttk.Button(self.button_frame, text="Добавить класс", command=self.add_group).pack(side=tk.LEFT, padx=5)
        ttk.Button(self.button_frame, text="Удалить выбранный класс", command=self.delete_group).pack(side=tk.LEFT, padx=5)
        
        self.students_frame = ttk.LabelFrame(self.main_frame, text="Ученики в классе", padding="10")
        self.students_frame.pack(fill=tk.BOTH, expand=True, pady=(10, 0))
        
        self.students_tree = ttk.Treeview(self.students_frame, columns=("Логин", "Имя", "Фамилия", "Отчество"), show="headings")
        self.students_tree.pack(fill=tk.BOTH, expand=True)

        self.students_tree.heading("Логин", text="Логин")
        self.students_tree.heading("Имя", text="Имя")
        self.students_tree.heading("Фамилия", text="Фамилия")
        self.students_tree.heading("Отчество", text="Отчество")
        
        students_scrollbar = ttk.Scrollbar(self.students_frame, orient=tk.VERTICAL, command=self.students_tree.yview)
        students_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.students_tree.configure(yscrollcommand=students_scrollbar.set)
        
        self.load_groups()
        
        self.group_entry.bind('<Return>', lambda e: self.add_group())
        
        self.group_entry.focus()

    def load_groups(self):
        try:
            groups = self.crypto.load_encrypted_file(self.groups_file)
            if not groups:
                groups = {}
            
            self.listbox.delete(0, tk.END)
            for group in sorted(groups.keys()):
                self.listbox.insert(tk.END, group)
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось загрузить классы: {str(e)}")

    def add_group(self):
        group_name = self.group_entry.get().strip()
        if not group_name:
            messagebox.showwarning("Предупреждение", "Пожалуйста, введите название класса.")
            return
        
        try:
            groups = self.crypto.load_encrypted_file(self.groups_file)
            if not groups:
                groups = {}
            
            if group_name in groups:
                messagebox.showwarning("Предупреждение", "Этот класс уже существует.")
                return
            
            groups[group_name] = {
                "students": []
            }
            
            self.crypto.save_encrypted_file(self.groups_file, groups)
            
            self.load_groups()
            
            self.group_entry.delete(0, tk.END)
            
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось добавить класс: {str(e)}")

    def delete_group(self):
        selection = self.listbox.curselection()
        if not selection:
            messagebox.showwarning("Предупреждение", "Пожалуйста, выберите класс для удаления.")
            return
        
        group_name = self.listbox.get(selection[0])
        if messagebox.askyesno("Подтверждение", f"Вы уверены, что хотите удалить класс '{group_name}'?"):
            try:
                groups = self.crypto.load_encrypted_file(self.groups_file)
                if not groups or group_name not in groups:
                    return
                
                del groups[group_name]
                
                self.crypto.save_encrypted_file(self.groups_file, groups)
                
                self.load_groups()
                self.students_tree.delete(*self.students_tree.get_children())
                
            except Exception as e:
                messagebox.showerror("Ошибка", f"Не удалось удалить класс: {str(e)}")

    def on_group_select(self, event):
        selection = self.listbox.curselection()
        if not selection:
            return
        
        group_name = self.listbox.get(selection[0])
        
        try:
            groups = self.crypto.load_encrypted_file(self.groups_file)
            users = self.crypto.load_encrypted_file("data/users.json")
            
            if not groups or group_name not in groups:
                return
            
            self.students_tree.delete(*self.students_tree.get_children())
            
            for username in groups[group_name]["students"]:
                if username in users:
                    user_data = users[username]
                    self.students_tree.insert("", tk.END, values=(
                        username,
                        user_data.get("first_name", ""),
                        user_data.get("last_name", ""),
                        user_data.get("father_name", "")
                    ))
            
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось загрузить учеников класса: {str(e)}")

    def get_groups(self):
        try:
            groups = self.crypto.load_encrypted_file(self.groups_file)
            if not groups:
                return []
            return sorted(groups.keys())
        except Exception:
            return []

    def update_student_groups(self, username, old_group, new_group):
        try:
            groups = self.crypto.load_encrypted_file(self.groups_file)
            if not groups:
                groups = {}
            
            if old_group and old_group in groups:
                if username in groups[old_group]["students"]:
                    groups[old_group]["students"].remove(username)
            
            if new_group and new_group in groups:
                if username not in groups[new_group]["students"]:
                    groups[new_group]["students"].append(username)
            
            self.crypto.save_encrypted_file(self.groups_file, groups)
            
            selection = self.listbox.curselection()
            if selection and self.listbox.get(selection[0]) in [old_group, new_group]:
                self.on_group_select(None)
                
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось обновить группы учеников: {str(e)}") 