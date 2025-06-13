import tkinter as tk
from tkinter import ttk, messagebox
from auth import AuthManager

class LoginView:
    def __init__(self, on_login_success):
        self.auth_manager = AuthManager()
        self.on_login_success = on_login_success
        
        self.root = tk.Tk()
        self.root.title("Журнал - Вход")
        self.root.geometry("400x300")
        self.root.resizable(False, False)
        
        # С Т И Л Ь
        self.root.eval('tk::PlaceWindow . center')
        
        style = ttk.Style()
        style.configure("TLabel", padding=5, font=('Helvetica', 10))
        style.configure("TButton", padding=5, font=('Helvetica', 10))
        style.configure("TEntry", padding=5, font=('Helvetica', 10))
        
        main_frame = ttk.Frame(self.root, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        title_label = ttk.Label(main_frame, text="Журнал", font=('Helvetica', 16, 'bold'))
        title_label.pack(pady=20)
        
        username_frame = ttk.Frame(main_frame)
        username_frame.pack(fill=tk.X, pady=5)
        ttk.Label(username_frame, text="Логин:").pack(side=tk.LEFT)
        self.username_entry = ttk.Entry(username_frame)
        self.username_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        password_frame = ttk.Frame(main_frame)
        password_frame.pack(fill=tk.X, pady=5)
        ttk.Label(password_frame, text="Пароль:").pack(side=tk.LEFT)
        self.password_entry = ttk.Entry(password_frame, show="*")
        self.password_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        login_button = ttk.Button(main_frame, text="Войти", command=self.login)
        login_button.pack(pady=20)
        
        self.root.bind('<Return>', lambda e: self.login())
        
        self.username_entry.focus()

    def login(self):
        username = self.username_entry.get()
        password = self.password_entry.get()
        
        if not username or not password:
            messagebox.showerror("Ошибка", "Пожалуйста, введите логин и пароль.")
            return
        
        success, role = self.auth_manager.authenticate(username, password)
        if success:
            self.root.destroy()
            self.on_login_success(username, role)
        else:
            messagebox.showerror("Ошибка", "Неверный логин или пароль.")
            self.password_entry.delete(0, tk.END)
            self.password_entry.focus()

    def run(self):
        self.root.mainloop() 