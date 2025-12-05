import os
import tkinter as tk
from tkinter import ttk, messagebox, font, PhotoImage
from auth_controller import AuthController
from dashboard_view import DashboardView
from datetime import datetime


C_HEADER    = "#3F5F91"
C_ACCENT    = "#2C3E50"
C_BODY_BG   = "#EBF0F5"
C_CARD_BG   = "#FFFFFF"
TEXT_COLOR  = "#1f2937"

FONT = ('Segoe UI', 10)
TITLE_FONT = ('Segoe UI', 14, 'bold')
SUBTITLE_FONT = ('Segoe UI', 10)

IMAGE_PATH = os.path.join('Image', 'cuenta.png')

class LoginView(tk.Tk):
    def __init__(self, auth_ctrl: AuthController = None):
        super().__init__()
        self.auth = auth_ctrl or AuthController()
        self.title('Login - Gestor Kanban')
        self.configure(bg=C_BODY_BG)
        self.geometry('520x420')
        self.minsize(420, 320)

        default = font.nametofont("TkDefaultFont")
        default.configure(family=FONT[0], size=FONT[1])

        header = tk.Frame(self, bg=C_HEADER, height=64)
        header.pack(fill='x', side='top')
        header.pack_propagate(False)
        lbl_title = tk.Label(header, text='Gestor de Proyectos (Kanban)', bg=C_HEADER, fg='white', font=TITLE_FONT)
        lbl_title.pack(side='left', padx=16, pady=12)
        lbl_info = tk.Label(header, text=f'{datetime.now().strftime("%Y-%m-%d")}', bg=C_HEADER, fg='white', font=SUBTITLE_FONT)
        lbl_info.pack(side='right', padx=12)

        container = tk.Frame(self, bg=C_BODY_BG)
        container.pack(fill='both', expand=True, padx=20, pady=14)

        card = tk.Frame(container, bg=C_CARD_BG, bd=0, relief='flat', padx=16, pady=12)
        card.configure(highlightthickness=1, highlightbackground='#D0D5DD')
        card.pack(pady=(6,10), ipadx=4, ipady=4)

        top = tk.Frame(card, bg=C_CARD_BG)
        top.pack(fill='x', pady=(0,8))
        title_frame = tk.Frame(top, bg=C_CARD_BG)
        title_frame.pack(side='left', fill='x', expand=True)
        lbl_card_title = tk.Label(title_frame, text='Iniciar sesión', bg=C_CARD_BG, fg=TEXT_COLOR, font=('Segoe UI',12,'bold'))
        lbl_card_title.pack(anchor='w')
        sub_lbl = tk.Label(title_frame, text='Ingrese usuario y contraseña', bg=C_CARD_BG, fg='#6b7280', font=('Segoe UI',9))
        sub_lbl.pack(anchor='w', pady=(2,0))

        self.logo_img = None
        if os.path.exists(IMAGE_PATH):
            try:
                img = PhotoImage(file=IMAGE_PATH)
                try:
                    w, h = img.width(), img.height()
                    max_dim = 64
                    if w > max_dim or h > max_dim:
                        factor = max(1, int(max(w / max_dim, h / max_dim)))
                        img = img.subsample(factor, factor)
                except Exception: pass
                self.logo_img = img
                logo_lbl = tk.Label(top, image=self.logo_img, bg=C_CARD_BG)
                logo_lbl.pack(side='right', padx=(8,0))
            except Exception: self.logo_img = None

        form = tk.Frame(card, bg=C_CARD_BG)
        form.pack(fill='x', pady=(4,6))
        label_opts = {'bg': C_CARD_BG, 'fg': TEXT_COLOR, 'font': FONT}
        
        tk.Label(form, text='Usuario', **label_opts).grid(row=0, column=0, sticky='w', padx=(0,6), pady=(6,8))
        self.ent_user = ttk.Entry(form, width=36)
        self.ent_user.grid(row=0, column=1, pady=(6,8), sticky='w')

        tk.Label(form, text='Contraseña', **label_opts).grid(row=1, column=0, sticky='w', padx=(0,6), pady=(2,8))
        pass_frame = tk.Frame(form, bg=C_CARD_BG)
        pass_frame.grid(row=1, column=1, sticky='w', pady=(2,8))

        self.ent_pass = ttk.Entry(pass_frame, show='*', width=30)
        self.ent_pass.pack(side='left', padx=(0,8))
        self.show_var = tk.BooleanVar(value=False)
        chk_show = ttk.Checkbutton(pass_frame, text='Mostrar', variable=self.show_var, command=self._toggle_pass)
        chk_show.pack(side='left')

        self.msg_var = tk.StringVar(value='Ingrese sus credenciales')
        msg_lbl = tk.Label(card, textvariable=self.msg_var, bg=C_CARD_BG, fg='#6b7280', anchor='w', font=('Segoe UI',9))
        msg_lbl.pack(fill='x', pady=(4,6))

        btns = tk.Frame(container, bg=C_BODY_BG)
        btns.pack(pady=(0,8))
        btn_login = tk.Button(btns, text='Entrar', command=self.on_login, bg=C_HEADER, fg='white', padx=14, pady=8)
        btn_login.pack(side='left', padx=(0,10))
        btn_quit = tk.Button(btns, text='Salir', command=self._on_quit, bg=C_CARD_BG, fg=TEXT_COLOR, padx=12, pady=8, relief='groove')
        btn_quit.pack(side='left')

        self.status = tk.Label(self, text='Estado: esperando credenciales', bg=C_BODY_BG, fg=TEXT_COLOR, anchor='w')
        self.status.pack(fill='x', padx=12, pady=(6,10))
        self.after(80, lambda: self.ent_user.focus_set())
        self.bind('<Return>', lambda e: self.on_login())
        self._after_open_id = None

    def _toggle_pass(self):
        if self.show_var.get(): self.ent_pass.config(show='')
        else: self.ent_pass.config(show='*')

    def on_login(self):
        user = self.ent_user.get().strip()
        pwd = self.ent_pass.get().strip()
        if not user or not pwd:
            messagebox.showwarning('Datos faltantes', 'Ingrese usuario y contraseña.')
            return
        ok, doc, msg = self.auth.authenticate(user, pwd)
        if not ok:
            messagebox.showerror('Error de autenticación', msg)
            self.msg_var.set(msg)
            self.status.config(text=f'Estado: {msg}')
            return

        self.msg_var.set(f'Autenticado como {doc.get("usuario")}')
        self.status.config(text=f'Autenticado como {doc.get("usuario")} ({doc.get("rol")})')
        
        self.ent_user.delete(0, tk.END)
        self.ent_pass.delete(0, tk.END)
        # -------------------------------------

        if self._after_open_id:
            try: self.after_cancel(self._after_open_id)
            except: pass
        self._after_open_id = self.after(150, lambda: self.open_dashboard(doc))

    def open_dashboard(self, user_doc):
        self._after_open_id = None
        if not self.winfo_exists(): return
        try: self.withdraw()
        except tk.TclError: return
        
        dash = DashboardView(self, user_doc)
        try: dash.wait_window()
        except Exception: pass
        
        if self.winfo_exists():
            try: self.deiconify()
            except tk.TclError: pass

    def _on_quit(self):
        if self._after_open_id:
            try: self.after_cancel(self._after_open_id)
            except: pass
            self._after_open_id = None
        self.destroy()

if __name__ == '__main__':
    LoginView().mainloop()