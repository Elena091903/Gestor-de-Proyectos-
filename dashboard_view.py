# dashboard_view.py
import os
import sys
import subprocess
import tkinter as tk
from tkinter import messagebox, PhotoImage
from datetime import datetime

C_HEADER    = "#3F5F91"
C_ACCENT    = "#2C3E50"
C_BODY_BG   = "#EBF0F5"
C_CARD_BG   = "#FFFFFF"
TEXT_COLOR  = "#1f2937"
FONT = ('Segoe UI', 10)

MODULES = {
    1: "Gestión Proyectos / Equipos",
    2: "Tablero Kanban (Vista Principal)",
    3: "Creación y Detalle de Tareas",
    4: "Historial y Logs",
    5: "Reporte de Velocidad"
}

ROLE_PERMISSIONS = {
    "Administrador": [1,2,4],
    "Scrum Master": [1,2,3,4,5],
    "Desarrollador": [2,3],
}

IMAGE_MAP = {
    1: os.path.join('Image', 'm1.png'),
    2: os.path.join('Image', 'm2.png'),
    3: os.path.join('Image', 'm3.png'),
    4: os.path.join('Image', 'm4.png'),
    5: os.path.join('Image', 'm5.png'),
}

class DashboardView(tk.Toplevel):
    def __init__(self, parent, user_doc):
        super().__init__(parent)
        self.parent = parent
        # guarda el usuario en current_user (uso en otros módulos)
        self.current_user = user_doc or {}
        self.title(f"Dashboard - {self.current_user.get('usuario')} ({self.current_user.get('rol')})")

        self.configure(bg=C_BODY_BG)
        self.geometry('920x560')
        self.minsize(720, 420)
        self._imgs = {}
        self.protocol("WM_DELETE_WINDOW", self.on_logout)

        header = tk.Frame(self, bg=C_HEADER, height=68)
        header.pack(fill='x', side='top')
        header.pack_propagate(False)
        lbl_title = tk.Label(header, text=f"Bienvenido, {self.current_user.get('usuario')}", bg=C_HEADER, fg='white',
                             font=('Segoe UI', 14, 'bold'))
        lbl_title.pack(side='left', padx=18)
        lbl_info = tk.Label(header, text=f"Rol: {self.current_user.get('rol')}   •   {datetime.now().strftime('%Y-%m-%d')}",
                            bg=C_HEADER, fg='white', font=('Segoe UI', 10))
        lbl_info.pack(side='right', padx=18)

        container = tk.Frame(self, bg=C_BODY_BG)
        container.pack(fill='both', expand=True, padx=16, pady=12)

        body = tk.Frame(container, bg=C_BODY_BG)
        body.pack(fill='both', expand=True)
        body.grid_rowconfigure(0, weight=1)
        for i in range(3):
            body.grid_columnconfigure(i, weight=1, uniform='col')

        allowed = ROLE_PERMISSIONS.get(self.current_user.get('rol'), [])
        if not allowed:
            tk.Label(body, text='No tiene módulos asignados para su rol.', bg=C_BODY_BG, fg=TEXT_COLOR, font=FONT).pack(pady=20)
        else:
            max_cols = 3
            r = 0; c = 0
            for mod_id in allowed:
                title = MODULES.get(mod_id, f'Módulo {mod_id}')
                card_w, card_h = 280, 160
                card = tk.Frame(body, bg=C_BODY_BG, width=card_w, height=card_h)
                card.grid(row=r, column=c, padx=12, pady=12, sticky='n')
                card.grid_propagate(False)

                visual = tk.Frame(card, bg=C_HEADER, width=card_w, height=92)
                visual.pack(fill='x', side='top')
                visual.pack_propagate(False)

                img_path = IMAGE_MAP.get(mod_id)
                if img_path and os.path.exists(img_path):
                    try:
                        img = PhotoImage(file=img_path)
                        try:
                            w, h = img.width(), img.height()
                            max_dim = 72
                            if w > max_dim or h > max_dim:
                                factor = max(1, int(max(w / max_dim, h / max_dim)))
                                img = img.subsample(factor, factor)
                        except Exception:
                            pass
                        self._imgs[f"m{mod_id}"] = img
                        img_lbl = tk.Label(visual, image=img, bg=C_HEADER)
                        img_lbl.pack(side='left', padx=10, pady=8)
                    except Exception:
                        pass

                title_frame = tk.Frame(visual, bg=C_HEADER)
                title_frame.pack(fill='both', expand=True, padx=(4,8), pady=8)
                lbl_mod = tk.Label(title_frame, text=title, bg=C_HEADER, fg='white', wraplength=170,
                                   justify='left', font=('Segoe UI', 10, 'bold'))
                lbl_mod.pack(anchor='w')

                footer = tk.Frame(card, bg=C_CARD_BG)
                footer.pack(fill='both', expand=True)
                footer.configure(highlightbackground="#D0D5DD", highlightthickness=1)

                desc = tk.Label(footer, text='', bg=C_CARD_BG, fg=TEXT_COLOR, font=('Segoe UI', 9))
                desc.pack(fill='both', expand=True, padx=10, pady=(6,0))

                btn = tk.Button(footer, text='Abrir', command=lambda m=mod_id: self.open_module(m),
                                bg=C_CARD_BG, fg=C_HEADER, relief='raised', padx=14, pady=6)
                btn.pack(side='right', padx=12, pady=10)

                c += 1
                if c >= max_cols:
                    c = 0; r += 1

        footer_bar = tk.Frame(self, bg=C_BODY_BG)
        footer_bar.pack(fill='x', side='bottom', padx=16, pady=(8,12))

        if self.current_user.get('rol') == "Administrador":
            tk.Button(footer_bar, text='➕ Crear Usuario', command=self.abrir_admin_usuarios,
                      bg='#2E7D32', fg='white', relief='raised', padx=12, pady=6).pack(side='left')

        tk.Button(footer_bar, text='Cerrar sesión', command=self.on_logout,
                  bg=C_CARD_BG, fg=TEXT_COLOR, relief='groove', padx=10, pady=6).pack(side='right')

    def abrir_admin_usuarios(self):
        """Abre la herramienta de creación de usuarios."""
        script_name = 'admin_usuarios.py'
        try:
            base_dir = os.path.abspath(os.path.dirname(__file__))
            script_path = os.path.join(base_dir, script_name)
            if not os.path.exists(script_path): script_path = os.path.abspath(script_name)
            if not os.path.exists(script_path):
                messagebox.showerror('Error', f'No se encuentra {script_name}')
                return
            python_exec = sys.executable or 'python'
            subprocess.Popen([python_exec, script_path], cwd=os.path.dirname(script_path))
        except Exception as e:
            messagebox.showerror('Error', str(e))

    def open_module(self, module_id: int):
        # Apertura de los módulos del sistema
        mod_name = MODULES.get(module_id, f'Módulo {module_id}')
        folder_prefix_map = {1: 'M1_Gestion', 2: 'M2_Tablero', 3: 'M3_Creacion', 4: 'M4_Historial', 5: 'M5_Reporte'}
        folder_name = folder_prefix_map.get(module_id)

        if not folder_name:
            messagebox.showerror('Error', f'ID de módulo no reconocido: {module_id}')
            return

        script_name = f'main_m{module_id}.py'
        base_dir = os.path.abspath(os.path.dirname(__file__))
        script_path = os.path.join(base_dir, folder_name, script_name)

        if not os.path.exists(script_path):
            messagebox.showerror('Error', f'No se encontró el archivo:\n{script_path}')
            return

        # preparar args (usar self.current_user)
        python_exec = sys.executable or 'python'
        uid = self.current_user.get('_id') or self.current_user.get('id') or ''
        usuario = self.current_user.get('usuario') or ''
        rol = self.current_user.get('rol') or ''
        cmd = [python_exec, script_path, '--user-id', str(uid), '--usuario', str(usuario), '--rol', str(rol)]

        try:
            subprocess.Popen(cmd, cwd=os.path.dirname(script_path))
        except Exception as e:
            messagebox.showerror('Error al abrir módulo', f'No se pudo abrir {mod_name}:\n{str(e)}')


    def on_logout(self):
        try:
            if self.parent:
                try:
                    if getattr(self.parent, 'winfo_exists', lambda: False)():
                        self.parent.deiconify()
                except Exception:
                    pass
        finally:
            try:
                self.destroy()
            except Exception:
                pass
