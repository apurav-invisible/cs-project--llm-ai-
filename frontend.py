import tkinter as tk
from tkinter import messagebox, scrolledtext
import threading
import requests
import subprocess
import time, sys
import ctypes

BACKEND_URL = "http://127.0.0.1:8000"



def start_backend():
    try:
        # Start FastAPI using uvicorn as a subprocess
        subprocess.Popen([sys.executable, "-m", "uvicorn", "main:app", "--host", "127.0.0.1", "--port", "8000"])
        time.sleep(3)  # wait for server to start
        print(" FastAPI backend started on port 8000")
    except Exception as e:
        print(f"Failed to start backend: {e}")

# Start FastAPI in background thread before Tkinter loads
threading.Thread(target=start_backend, daemon=True).start()

#  LOGIN PAGE
class LoginPage:
    def __init__(self, root):
        self.root = root
        self.render()

    def render(self):
        self.clear()
        self.root.title("NeuraAI Login")
        self.root.geometry("600x800")
        self.root.configure(bg="#000000")

        tk.Label(self.root, text="🔐 NeuraAI Login", bg="#0f0f0f", fg="#00ffcc",
                 font=("Segoe UI", 18, "bold")).pack(pady=30)

        self.email = self.create_entry("Email")
        self.password = self.create_entry("Password", show="*")

        tk.Button(self.root, text="Login", command=self.login, bg="#00ffcc", fg="#000",
                  font=("Segoe UI", 11, "bold")).pack(pady=10)
        tk.Button(self.root, text="Sign Up", command=self.open_signup,
                  bg="#444", fg="#fff", font=("Segoe UI", 10)).pack()

    def clear(self):
        for widget in self.root.winfo_children():
            widget.destroy()

    def create_entry(self, label, show=None):
        tk.Label(self.root, text=label, bg="#0f0f0f", fg="white",
                 font=("Segoe UI", 12)).pack(pady=(10, 5))
        entry = tk.Entry(self.root, width=30, show=show, font=("Segoe UI", 12),
                         bg="#1e1e1e", fg="white", insertbackground="white")
        entry.pack()
        return entry

    def login(self):
        email = self.email.get().strip().lower()
        password = self.password.get().strip()

        if not email or not password:
            messagebox.showwarning("Missing Info", "Please enter both email and password.")
            return

        try:
            res = requests.post(f"{BACKEND_URL}/login", json={"email": email, "password": password})
            if res.status_code == 200:
                session_token = res.json()["session_token"]
                messagebox.showinfo("Welcome", f"Welcome back, {email}!")
                ChatPage(self.root, email, session_token)
            else:
                messagebox.showerror("Login Failed", res.json().get("detail", "Invalid credentials."))
        except Exception as e:
            messagebox.showerror("Error", f"Login failed: {e}")

    def open_signup(self):
        SignupPage(self.root)


# SIGNUP PAGE
class SignupPage:
    def __init__(self, root):
        self.root = root
        self.render()

    def render(self):
        self.clear()
        self.root.title("NeuraAI Signup")
        self.root.geometry("600x800")
        self.root.configure(bg="#0f0f0f")

        tk.Label(self.root, text=" Create Your NeuraAI Account", bg="#0f0f0f", fg="#00ffcc",
                 font=("Segoe UI", 18, "bold")).pack(pady=30)

        self.email = self.create_entry("Email")
        self.password = self.create_entry("Password", show="*")

        tk.Button(self.root, text="Create Account", command=self.signup, bg="#00ffcc", fg="#000",
                  font=("Segoe UI", 11, "bold")).pack(pady=10)
        tk.Button(self.root, text="Back to Login", command=self.back_to_login,
                  bg="#444", fg="#fff", font=("Segoe UI", 10)).pack()

    def clear(self):
        for widget in self.root.winfo_children():
            widget.destroy()

    def create_entry(self, label, show=None):
        tk.Label(self.root, text=label, bg="#0f0f0f", fg="white",
                 font=("Segoe UI", 12)).pack(pady=(10, 5))
        entry = tk.Entry(self.root, width=30, show=show, font=("Segoe UI", 12),
                         bg="#1e1e1e", fg="white", insertbackground="white")
        entry.pack()
        return entry

    def signup(self):
        email = self.email.get().strip().lower()
        password = self.password.get().strip()

        if not email or not password:
            messagebox.showwarning("Missing Info", "Please enter both email and password.")
            return

        try:
            res = requests.post(f"{BACKEND_URL}/signup", json={"email": email, "password": password})
            if res.status_code == 200:
                session_token = res.json()["session_token"]
                messagebox.showinfo("Success", f"Account created for {email}!")
                ChatPage(self.root, email, session_token)
            else:
                messagebox.showerror("Signup Failed", res.json().get("detail", "Something went wrong."))
        except Exception as e:
            messagebox.showerror("Error", f"Signup failed: {e}")

    def back_to_login(self):
        LoginPage(self.root)


# 💬 CHAT PAGE
class ChatPage:
    def __init__(self, root, user_email, session_token):
        self.root = root
        self.user_email = user_email
        self.session_token = session_token
        self.render()

    def render(self):
        self.clear()
        self.root.title(f"NeuraAI Chat - {self.user_email}")
        self.root.geometry("700x600")
        self.root.configure(bg="#0f0f0f")

        tk.Label(self.root, text=f" NeuraAI ({self.user_email})", bg="#0f0f0f", fg="#00ffcc",
                 font=("Segoe UI", 16, "bold")).pack(pady=10)

        self.chat_box = scrolledtext.ScrolledText(self.root, wrap=tk.WORD, bg="#1e1e1e", fg="#ffffff",
                                                  font=("Segoe UI", 12), padx=10, pady=10)
        self.chat_box.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)
        self.chat_box.config(state=tk.DISABLED)

        entry_frame = tk.Frame(self.root, bg="#0f0f0f")
        entry_frame.pack(fill=tk.X, padx=10, pady=10)

        self.user_input = tk.Entry(entry_frame, font=("Segoe UI", 12),
                                   bg="#2b2b2b", fg="white", insertbackground="white")
        self.user_input.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))
        self.user_input.bind("<Return>", self.send_message)

        tk.Button(entry_frame, text="Send", command=self.send_message,
                  bg="#00ffcc", fg="#000", font=("Segoe UI", 11, "bold"), relief="flat").pack(side=tk.RIGHT)

        tk.Button(entry_frame, text="Logout", command=self.logout,
                  bg="#ff4444", fg="#fff", font=("Segoe UI", 10, "bold")).pack(side=tk.LEFT, padx=(0, 10))

        self.display_message("NeuraAI", f"Welcome, {self.user_email}! ")

    def clear(self):
        for widget in self.root.winfo_children():
            widget.destroy()

    def display_message(self, sender, message):
        self.chat_box.config(state=tk.NORMAL)
        tag = "user" if sender == "You" else "bot"
        self.chat_box.insert(tk.END, f"{sender}: {message}\n\n", tag)
        self.chat_box.tag_config("user", foreground="#00ffcc")
        self.chat_box.tag_config("bot", foreground="#ffffff")
        self.chat_box.config(state=tk.DISABLED)
        self.chat_box.yview(tk.END)

    def send_message(self, event=None):
        user_text = self.user_input.get().strip()
        if not user_text:
            return
        self.display_message("You", user_text)
        self.user_input.delete(0, tk.END)
        threading.Thread(target=self.get_ai_response, args=(user_text,)).start()

    def get_ai_response(self, user_text):
        try:
            res = requests.post(f"{BACKEND_URL}/chat",
                                json={"session_token": self.session_token, "message": user_text})
            data = res.json()
            reply = data.get("reply") or data.get("detail", " No response.")
        except Exception as e:
            reply = f" Error: {str(e)}"
        self.root.after(0, lambda: self.display_message("NeuraAI", reply))

    def logout(self):
        try:
            requests.post(f"{BACKEND_URL}/logout", json={"session_token": self.session_token})
        except:
            pass
        LoginPage(self.root)


# 🚀 Launch App
def run():
    root = tk.Tk()
    LoginPage(root)
    root.mainloop()


    try:
        ctypes.windll.user32.ShowWindow(ctypes.windll.kernel32.GetConsoleWindow(), 0)
    except:
        pass