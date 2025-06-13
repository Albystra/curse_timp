import tkinter as tk
from tkinter import ttk, messagebox
from auth import AuthManager
from views.subject_management_view import SubjectManagementView
from views.group_management_view import GroupManagementView
import os

class UserManagementView:
    def __init__(self, parent):
        self.parent = parent
        self.auth_manager = AuthManager()
        self.crypto = self.auth_manager.crypto
        
        self.subject_view = SubjectManagementView(parent)
        self.subject_view.window.withdraw()
        
        self.group_view = GroupManagementView(parent)
        self.group_view.window.withdraw()
        
        self.window = tk.Toplevel(parent)
        self.window.title("Управление пользователями")
        self.window.geometry("1000x600")
        
        self.main_frame = ttk.Frame(self.window, padding="10")
        self.main_frame.pack(fill=tk.BOTH, expand=True)
        
        self.tree = ttk.Treeview(self.main_frame, columns=("Логин", "Роль", "Имя", "Фамилия", "Отчество", "Класс", "Предмет"), show="headings")
        self.tree.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        self.tree.heading("Логин", text="Логин")
        self.tree.heading("Роль", text="Роль")
        self.tree.heading("Имя", text="Имя")
        self.tree.heading("Фамилия", text="Фамилия")
        self.tree.heading("Отчество", text="Отчество")
        self.tree.heading("Класс", text="Класс")
        self.tree.heading("Предмет", text="Предмет")
        
        scrollbar = ttk.Scrollbar(self.main_frame, orient=tk.VERTICAL, command=self.tree.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        self.button_frame = ttk.Frame(self.main_frame)
        self.button_frame.pack(fill=tk.X)
        
        ttk.Button(self.button_frame, text="Добавить пользователя", command=self.add_user).pack(side=tk.LEFT, padx=5)
        ttk.Button(self.button_frame, text="Редактировать выбранного пользователя", command=self.edit_user).pack(side=tk.LEFT, padx=5)
        ttk.Button(self.button_frame, text="Удалить выбранного пользователя", command=self.delete_user).pack(side=tk.LEFT, padx=5)
        
        self.load_users()
        
        # Двойной клик на редактирование
        self.tree.bind('<Double-1>', lambda e: self.edit_user())

    def load_users(self):
        try:
            users = self.crypto.load_encrypted_file("data/users.json")
            if not users:
                return
            
            self.tree.delete(*self.tree.get_children())
            
            for username, data in users.items():
                if username == "admin": # Админа не показываем
                    continue
                self.tree.insert("", tk.END, values=(
                    username,
                    data.get("role", ""),
                    data.get("first_name", ""),
                    data.get("last_name", ""),
                    data.get("father_name", ""),
                    data.get("group", ""),
                    data.get("subject", "")
                ))
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось загрузить пользователей: {str(e)}")

    def add_user(self):
        self._show_user_dialog()

    def edit_user(self):
        selection = self.tree.selection()
        if not selection:
            messagebox.showwarning("Предупреждение", "Пожалуйста, выберите пользователя для редактирования.")
            return
        
        values = self.tree.item(selection[0])["values"]
        username = values[0]
        
        try:
            users = self.crypto.load_encrypted_file("data/users.json")
            if not users or username not in users:
                return
            
            self._show_user_dialog(users[username], username)
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось загрузить данные пользователя: {str(e)}")

    def delete_user(self):
        selection = self.tree.selection()
        if not selection:
            messagebox.showwarning("Предупреждение", "Пожалуйста, выберите пользователя для удаления.")
            return
        
        username = self.tree.item(selection[0])["values"][0]
        if messagebox.askyesno("Подтверждение", f"Вы уверены, что хотите удалить пользователя '{username}'?"):
            try:
                users = self.crypto.load_encrypted_file("data/users.json")
                if not users or username not in users:
                    return
                
                del users[username]
                
                self.crypto.save_encrypted_file("data/users.json", users)
                
                self.load_users()
                
            except Exception as e:
                messagebox.showerror("Ошибка", f"Не удалось удалить пользователя: {str(e)}")

    def _show_user_dialog(self, existing_user=None, username=None):
        dialog = tk.Toplevel(self.window)
        dialog.title("Добавить пользователя" if not existing_user else "Редактировать пользователя")
        dialog.geometry("400x500")
        dialog.transient(self.window)
        dialog.grab_set()
        
        main_frame = ttk.Frame(dialog, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        ttk.Label(main_frame, text="Логин:").pack(fill=tk.X, pady=(0, 5))
        username_entry = ttk.Entry(main_frame)
        username_entry.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(main_frame, text="Пароль:").pack(fill=tk.X, pady=(0, 5))
        password_entry = ttk.Entry(main_frame, show="*")
        password_entry.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(main_frame, text="Роль:").pack(fill=tk.X, pady=(0, 5))
        role_var = tk.StringVar()
        role_combo = ttk.Combobox(main_frame, textvariable=role_var, state="readonly")
        role_combo["values"] = ["admin", "teacher", "student"]
        role_combo.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(main_frame, text="Имя:").pack(fill=tk.X, pady=(0, 5))
        first_name_entry = ttk.Entry(main_frame)
        first_name_entry.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(main_frame, text="Фамилия:").pack(fill=tk.X, pady=(0, 5))
        last_name_entry = ttk.Entry(main_frame)
        last_name_entry.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(main_frame, text="Отчество:").pack(fill=tk.X, pady=(0, 5))
        father_name_entry = ttk.Entry(main_frame)
        father_name_entry.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(main_frame, text="Класс:").pack(fill=tk.X, pady=(0, 5))
        group_var = tk.StringVar()
        group_combo = ttk.Combobox(main_frame, textvariable=group_var, state="readonly")
        group_combo.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(main_frame, text="Предмет:").pack(fill=tk.X, pady=(0, 5))
        subject_var = tk.StringVar()
        subject_combo = ttk.Combobox(main_frame, textvariable=subject_var, state="readonly")
        subject_combo.pack(fill=tk.X, pady=(0, 10))
        
        def on_role_change(*args):
            role = role_var.get()
            if role == "teacher":
                subject_combo["values"] = self.subject_view.get_subjects()
                subject_combo.set("")
                subject_combo["state"] = "readonly"
                group_combo["values"] = self.group_view.get_groups()
                group_combo["state"] = "readonly"
            elif role == "student":
                group_combo["values"] = self.group_view.get_groups()
                group_combo.set("")
                group_combo["state"] = "readonly"
                subject_combo.set("")
                subject_combo["state"] = "disabled"
            else:  # admin
                group_combo.set("")
                subject_combo.set("")
                group_combo["state"] = "disabled"
                subject_combo["state"] = "disabled"
        
        role_var.trace("w", on_role_change)
        
        if existing_user:
            username_entry.insert(0, username)
            username_entry.configure(state="disabled")
            first_name_entry.insert(0, existing_user.get("first_name", ""))
            last_name_entry.insert(0, existing_user.get("last_name", ""))
            father_name_entry.insert(0, existing_user.get("father_name", ""))
            role_var.set(existing_user.get("role", ""))
            group_var.set(existing_user.get("group", ""))
            subject_var.set(existing_user.get("subject", ""))
            on_role_change()
        
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X, pady=(10, 0))
        
        def save():
            username = username_entry.get().strip()
            password = password_entry.get()
            role = role_var.get()
            first_name = first_name_entry.get().strip()
            last_name = last_name_entry.get().strip()
            father_name = father_name_entry.get().strip()
            group = group_var.get()
            subject = subject_var.get()
            
            if not all([username, role, first_name, last_name, father_name]):
                messagebox.showwarning("Предупреждение", "Пожалуйста, заполните все обязательные поля.")
                return
            
            if not existing_user and not password:
                messagebox.showwarning("Предупреждение", "Пожалуйста, введите пароль.")
                return
            
            if role == "teacher" and not subject:
                messagebox.showwarning("Предупреждение", "Пожалуйста, выберите предмет.")
                return
            
            if role == "student" and not group:
                messagebox.showwarning("Предупреждение", "Пожалуйста, выберите класс.")
                return
            
            try:
                users = self.crypto.load_encrypted_file("data/users.json")
                if not users:
                    users = {}
                
                if not existing_user and username in users:
                    messagebox.showwarning("Предупреждение", "Этот логин уже существует.")
                    return
                
                new_user_data = {
                    "role": role,
                    "first_name": first_name,
                    "last_name": last_name,
                    "father_name": father_name,
                    "group": group if role in ["student", "teacher"] else "",
                    "subject": subject if role == "teacher" else ""
                }
                
                if not existing_user or password:
                    new_user_data["password"] = self.auth_manager._hash_password(password)
                
                if role == "student":
                    old_group = existing_user.get("group", "") if existing_user else ""
                    self.group_view.update_student_groups(username, old_group, group)
                
                users[username] = new_user_data
                self.crypto.save_encrypted_file("data/users.json", users)

                self.load_users()
                
                dialog.destroy()
                
            except Exception as e:
                messagebox.showerror("Ошибка", f"Не удалось сохранить пользователя: {str(e)}")
        
        ttk.Button(button_frame, text="Сохранить", command=save).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Отмена", command=dialog.destroy).pack(side=tk.LEFT, padx=5)
        
        if not existing_user:
            username_entry.focus()
        else:
            first_name_entry.focus()