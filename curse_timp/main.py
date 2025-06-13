import tkinter as tk
from tkinter import ttk, messagebox
from views.login_view import LoginView
from views.user_management_view import UserManagementView
from views.subject_management_view import SubjectManagementView
from views.group_management_view import GroupManagementView
from views.schedule_management_view import ScheduleManagementView
from views.schedule_view import ScheduleView
from views.homework_management_view import HomeworkManagementView
from views.homework_view import HomeworkView
from auth import AuthManager
from views.grade_management_view import GradeManagementView
from views.grade_view import GradeView

class SchoolJournal:
    def __init__(self):
        self.auth_manager = AuthManager()
        self.current_user = None
        self.current_role = None
        self.root = None

    def on_login_success(self, username, role):
        self.current_user = username
        self.current_role = role
        self.show_main_view()

    def show_main_view(self):
        self.root = tk.Tk()
        self.root.title(f"Журнал - {self.current_user} ({self.current_role})")
        self.root.geometry("800x600")
        
        # Меню
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
        
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Файл", menu=file_menu)
        file_menu.add_command(label="Сменить пароль", command=self.show_change_password)
        file_menu.add_separator()
        file_menu.add_command(label="Выход из аккаунта", command=self.logout)
        file_menu.add_command(label="Выход из программы", command=self.root.quit)
        
        # Основной контент
        self.content_frame = tk.Frame(self.root)
        self.content_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Show appropriate view based on role
        if self.current_role == "admin":
            self.show_admin_view()
        elif self.current_role == "teacher":
            self.show_teacher_view()
        else:  # student
            self.show_student_view()

    def show_admin_view(self):
        # Clear content frame
        for widget in self.content_frame.winfo_children():
            widget.destroy()
        
        # Create admin view content
        ttk.Label(self.content_frame, text="Добро пожаловать, админ!", font=('Helvetica', 16, 'bold')).pack(pady=20)
        
        # Add buttons for different admin functions
        functions = [
            ("Управление пользователями", self.manage_users),
            ("Управление предметами", self.manage_subjects),
            ("Управление классами", self.manage_groups),
            ("Управление расписанием", self.manage_schedule),
            ("Просмотр оценок", self.view_grades),
            ("Просмотр домашних заданий", self.view_homework)
        ]
        
        for text, command in functions:
            ttk.Button(self.content_frame, text=text, command=command).pack(pady=5)

    def show_teacher_view(self):
        # Clear content frame
        for widget in self.content_frame.winfo_children():
            widget.destroy()
        
        # Create teacher view content
        ttk.Label(self.content_frame, text="Добро пожаловать, учитель!", font=('Helvetica', 16, 'bold')).pack(pady=20)
        
        # Add buttons for different teacher functions
        functions = [
            ("Просмотр расписания", self.view_schedule),
            ("Добавление домашнего задания", self.add_homework),
            ("Добавление оценки", self.add_grade),
            ("Просмотр оценок", self.view_grades),
            ("Просмотр домашних заданий", self.view_homework)
        ]
        
        for text, command in functions:
            ttk.Button(self.content_frame, text=text, command=command).pack(pady=5)

    def show_student_view(self):
        # Clear content frame
        for widget in self.content_frame.winfo_children():
            widget.destroy()
        
        # Create student view content
        ttk.Label(self.content_frame, text="Добро пожаловать, ученик!", font=('Helvetica', 16, 'bold')).pack(pady=20)
        
        # Add buttons for different student functions
        functions = [
            ("Просмотр расписания", self.view_schedule),
            ("Просмотр оценок", self.view_grades),
            ("Просмотр домашних заданий", self.view_homework)
        ]
        
        for text, command in functions:
            ttk.Button(self.content_frame, text=text, command=command).pack(pady=5)

    def show_change_password(self):
        dialog = tk.Toplevel(self.root)
        dialog.title("Смена пароля")
        dialog.geometry("300x200")
        dialog.resizable(False, False)
        
        # Center the dialog
        dialog.update_idletasks()
        width = dialog.winfo_width()
        height = dialog.winfo_height()
        x = (dialog.winfo_screenwidth() // 2) - (width // 2)
        y = (dialog.winfo_screenheight() // 2) - (height // 2)
        dialog.geometry(f'{width}x{height}+{x}+{y}')
        
        # Create widgets
        ttk.Label(dialog, text="Смена пароля", font=('Helvetica', 12, 'bold')).pack(pady=10)
        
        old_password_frame = ttk.Frame(dialog)
        old_password_frame.pack(fill=tk.X, padx=20, pady=5)
        ttk.Label(old_password_frame, text="Старый пароль:").pack(side=tk.LEFT)
        old_password_entry = ttk.Entry(old_password_frame, show="*")
        old_password_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        new_password_frame = ttk.Frame(dialog)
        new_password_frame.pack(fill=tk.X, padx=20, pady=5)
        ttk.Label(new_password_frame, text="Новый пароль:").pack(side=tk.LEFT)
        new_password_entry = ttk.Entry(new_password_frame, show="*")
        new_password_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        confirm_password_frame = ttk.Frame(dialog)
        confirm_password_frame.pack(fill=tk.X, padx=20, pady=5)
        ttk.Label(confirm_password_frame, text="Подтвердите пароль:").pack(side=tk.LEFT)
        confirm_password_entry = ttk.Entry(confirm_password_frame, show="*")
        confirm_password_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        # Add change button
        ttk.Button(dialog, text="Сменить пароль", command=lambda: self.change_password(
            old_password_entry.get(),
            new_password_entry.get(),
            confirm_password_entry.get(),
            dialog
        )).pack(pady=10)

    def change_password(self, old_password, new_password, confirm_password, dialog):
        if not old_password or not new_password or not confirm_password:
            messagebox.showerror("Ошибка", "Пожалуйста, заполните все поля.")
            return
        
        if new_password != confirm_password:
            messagebox.showerror("Ошибка", "Новый пароль и подтверждение пароля не совпадают.")
            return
        
        success, message = self.auth_manager.change_password(
            self.current_user, old_password, new_password
        )
        
        if success:
            messagebox.showinfo("Успешно", message)
            dialog.destroy()
        else:
            messagebox.showerror("Ошибка", message)

    def logout(self):
        if self.root:
            self.root.destroy()
        self.current_user = None
        self.current_role = None
        self.show_login()

    def show_login(self):
        login_view = LoginView(self.on_login_success)
        login_view.run()

    # Placeholder methods for different functions
    def manage_users(self):
        UserManagementView(self.root)
    
    def manage_subjects(self):
        SubjectManagementView(self.root)
    
    def manage_groups(self):
        GroupManagementView(self.root)
    
    def manage_schedule(self):
        ScheduleManagementView(self.root)
    
    def view_schedule(self):
        ScheduleView(self.root, self.current_user)
    
    def add_homework(self):
        HomeworkManagementView(self.root, self.current_user)
    
    def add_grade(self):
        GradeManagementView(self.root, self.current_user)
    
    def view_grades(self):
        GradeView(self.root, self.current_user)
    
    def view_homework(self):
        HomeworkView(self.root, self.current_user)

    def run(self):
        self.show_login()

if __name__ == "__main__":
    app = SchoolJournal()
    app.run() 