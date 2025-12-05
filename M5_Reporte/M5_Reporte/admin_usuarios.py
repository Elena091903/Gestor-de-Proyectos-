import tkinter as tk
from tkinter import ttk, messagebox
import re
import secrets
import string
import sys


try:
    from mongo_con import MongoConnection
except ImportError:
    messagebox.showerror("Error Crítico", "No se encontró el archivo 'mongo_con.py'")
    sys.exit(1)

C_PRIMARY    = "#3F5F91"  
C_BACKGROUND = "#F3F4F6"  
C_CARD       = "#FFFFFF"  
C_TEXT       = "#111827"
C_ERROR      = "#EF4444"
C_SUCCESS_BG = "#ECFDF5"
C_BORDER     = "#9CA3AF"  

class AdminUserCreator(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Administración de Usuarios")
        self.geometry("500x700")
        self.configure(bg=C_BACKGROUND)
        self.resizable(False, False)

        
        try:
            self.conn = MongoConnection()
            self.users = self.conn.get_collection('usuarios')
        except Exception as e:
            messagebox.showerror("Error", f"Error de conexión: {e}")
            self.destroy()
            return

        self._build_ui()

    def _build_ui(self):

       
        header = tk.Frame(self, bg=C_PRIMARY, height=75)
        header.pack(fill='x')
        header.pack_propagate(False)

        tk.Label(header, text="👤", bg=C_PRIMARY, fg="white", font=('Segoe UI', 22)).pack(side='left', padx=(25, 15))
        tk.Label(header, text="Crear Nuevo Usuario", bg=C_PRIMARY, fg="white", font=('Segoe UI', 15, 'bold')).pack(side='left')

        
        main_container = tk.Frame(self, bg=C_BACKGROUND)
        main_container.pack(fill='both', expand=True, padx=35, pady=25)

        
        self.card = tk.Frame(main_container, bg=C_CARD)
        self.card.config(highlightbackground=C_BORDER, highlightthickness=2, bd=0)
        self.card.pack(fill='both', expand=True)

        
        inner = tk.Frame(self.card, bg=C_CARD)
        inner.pack(fill='both', expand=True, padx=35, pady=30)

      
        tk.Label(inner, text="Nombre de Usuario", bg=C_CARD, fg=C_TEXT,
                 font=('Segoe UI', 10, 'bold')).pack(anchor='w', pady=(0, 8))

        self.user_var = tk.StringVar()
        self.user_var.trace_add("write", self._validate_input)

        self.ent_user = ttk.Entry(inner, textvariable=self.user_var, font=('Segoe UI', 11))
        self.ent_user.pack(fill='x', ipady=4)

      
        self.lbl_error = tk.Label(inner, text="", bg=C_CARD, fg=C_ERROR, font=('Segoe UI', 8, 'bold'))
        self.lbl_error.pack(anchor='w', pady=(4, 0))

        tk.Label(inner, text="* Solo letras y números. Iniciar con letra.",
                 bg=C_CARD, fg="#6B7280", font=('Segoe UI', 9)).pack(anchor='w', pady=(0, 20))

        
        tk.Label(inner, text="Rol del Sistema", bg=C_CARD, fg=C_TEXT,
                 font=('Segoe UI', 10, 'bold')).pack(anchor='w', pady=(5, 8))

        self.combo_rol = ttk.Combobox(inner, values=["Desarrollador", "Scrum Master"],
                                      state="readonly", font=('Segoe UI', 10))
        self.combo_rol.current(0)
        self.combo_rol.pack(fill='x', ipady=4, pady=(0, 25))

    
        self.btn_save = tk.Button(inner, text="💾  GENERAR USUARIO", command=self.save,
                                  bg=C_PRIMARY, fg="white",
                                  font=('Segoe UI', 10, 'bold'),
                                  relief='flat', cursor="hand2", pady=10)
        self.btn_save.pack(fill='x', pady=5)

        
        self.result_container = tk.Frame(inner, bg=C_CARD)
        self.result_container.pack(fill='x', pady=15)

       
        footer = tk.Frame(self, bg=C_BACKGROUND, height=50)
        footer.pack(fill='x', side='bottom', pady=10)

        tk.Button(footer, text="Cerrar", command=self.destroy,
                  bg="#E5E7EB", fg=C_TEXT, relief='groove',
                  font=('Segoe UI', 9), padx=20, pady=5).pack(side='bottom')

    def _validate_input(self, *args):
        text = self.user_var.get()
        self.lbl_error.config(text="")

        if text and not text[0].isalpha():
            self.lbl_error.config(text="⛔ Error: Debe iniciar con letra.")
        elif text and not re.match(r'^[a-zA-Z0-9]+$', text):
            self.lbl_error.config(text="⛔ Error: Sin símbolos ni espacios.")

    def save(self):
        for w in self.result_container.winfo_children():
            w.destroy()

        user = self.ent_user.get().strip()
        rol = self.combo_rol.get()

        if not user:
            messagebox.showwarning("Atención", "Ingrese un nombre de usuario.")
            return
        if self.lbl_error.cget("text") or not re.match(r'^[a-zA-Z][a-zA-Z0-9]*$', user):
            messagebox.showerror("Error", "Nombre de usuario inválido.")
            return

        try:
            if self.users.find_one({'usuario': user}):
                messagebox.showerror("Error", f"El usuario '{user}' ya existe.")
                return
        except Exception:
            return

        pwd = ''.join(secrets.choice(string.ascii_letters + string.digits) for _ in range(8))

        try:
            self.users.insert_one({
                "usuario": user,
                "contrasena": pwd,
                "rol": rol,
                "activo": True
            })
            self.ent_user.delete(0, 'end')
            self.mostrar_exito(user, pwd)
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def mostrar_exito(self, u, p):
        ticket = tk.Frame(self.result_container, bg=C_SUCCESS_BG,
                          highlightbackground="#34D399", highlightthickness=1)
        ticket.pack(fill='x', pady=5, ipadx=10, ipady=10)

        tk.Label(ticket, text="✅ Usuario Creado Exitosamente",
                 bg=C_SUCCESS_BG, fg="#065F46",
                 font=('Segoe UI', 10, 'bold')).pack(anchor='w', pady=(0, 5))

        info = tk.Frame(ticket, bg=C_SUCCESS_BG)
        info.pack(fill='x', pady=5)

        row_u = tk.Frame(info, bg=C_SUCCESS_BG)
        row_u.pack(fill='x', pady=2)
        tk.Label(row_u, text="Usuario:    ", bg=C_SUCCESS_BG,
                 font=('Segoe UI', 9, 'bold')).pack(side='left')
        tk.Label(row_u, text=u, bg=C_SUCCESS_BG, font=('Segoe UI', 10)).pack(side='left')

        row_p = tk.Frame(info, bg=C_SUCCESS_BG)
        row_p.pack(fill='x', pady=2)
        tk.Label(row_p, text="Contraseña: ", bg=C_SUCCESS_BG,
                 font=('Segoe UI', 9, 'bold')).pack(side='left')

        e = tk.Entry(row_p, width=14, font=('Consolas', 11),
                     justify='center', bg="white", bd=1, relief="solid")
        e.insert(0, p)
        e.config(state='readonly')
        e.pack(side='left')


if __name__ == "__main__":
    app = AdminUserCreator()
    app.mainloop()
