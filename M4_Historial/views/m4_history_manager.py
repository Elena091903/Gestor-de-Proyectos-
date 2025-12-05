# M4_Historial/views/m4_history_manager.py
import tkinter as tk
from tkinter import ttk, messagebox
from tkcalendar import DateEntry
from datetime import datetime, timedelta
from controllers.m4_history_controller import HistoryController
from bson import ObjectId

C_HEADER    = "#3F5F91"
C_ACCENT    = "#2C3E50"
C_BODY_BG   = "#EBF0F5"
C_CARD_BG   = "#FFFFFF"
TEXT_COLOR  = "#1f2937"
FONT = ("Segoe UI", 10)

# colores por tipo de acción
ACTION_COLORS = {
    "CREATE_PROJECT": "#2E7D32",
    "UPDATE_PROJECT": "#1E88E5",
    "DELETE_PROJECT": "#C62828",
    "CAMBIO_ESTADO": "#F59E0B",
    None: "#6B7280"
}

# etiquetas para los resúmenes
ACTION_LABELS_ES = {
    "CREATE_PROJECT": "Proyectos creados",
    "UPDATE_PROJECT": "Proyectos actualizados",
    "CAMBIO_ESTADO": "Cambios de estado",
    "DELETE_PROJECT": "Proyectos eliminados"
}


class HistoryManagerUI(tk.Tk):
    def __init__(self, current_user=None):
        super().__init__()
        self.current_user = current_user or {}
        self.title("Historial y Logs")
        self.configure(bg=C_BODY_BG)
        self.geometry("1200x740")
        self.controller = HistoryController()

        self.per_page = 10000
        self.view_mode = "table"   
        self._proj_map = {}

        self._build_ui()
        self._load_filters()
        self.load_entries()

    def _build_ui(self):
        # cabecera
        header = tk.Frame(self, bg=C_HEADER, height=68)
        header.pack(fill="x", side="top")
        header.pack_propagate(False)
        tk.Label(header, text="Historial y Logs", bg=C_HEADER, fg="white", font=("Segoe UI", 16, "bold")).pack(side="left", padx=18)
        tk.Label(header, text=f"{self.current_user.get('usuario','-')} — {self.current_user.get('rol','-')}", bg=C_HEADER, fg="white").pack(side="right", padx=18)

        # toolbar (filtros)
        toolbar = tk.Frame(self, bg="white", padx=12, pady=10)
        toolbar.pack(fill="x", side="top")

        tk.Label(toolbar, text="Proyecto:", bg="white").pack(side="left", padx=(2,6))
        self.cb_proj = ttk.Combobox(toolbar, values=[], width=36, state="readonly")
        self.cb_proj.pack(side="left", padx=6)
        self.cb_proj.set("Todos los proyectos")

        tk.Label(toolbar, text="Acción:", bg="white").pack(side="left", padx=(8,6))
        self.cb_tipo = ttk.Combobox(toolbar, values=["","CREATE_PROJECT","UPDATE_PROJECT","DELETE_PROJECT","CAMBIO_ESTADO"], width=20, state="readonly")
        self.cb_tipo.pack(side="left", padx=6)
        self.cb_tipo.current(0)

        tk.Label(toolbar, text="Desde:", bg="white").pack(side="left", padx=(10,6))
        self.entry_from = DateEntry(toolbar, width=12, date_pattern="yyyy-mm-dd")
        self.entry_from.pack(side="left", padx=6)
        self.entry_from.set_date(datetime.utcnow() - timedelta(days=30))

        tk.Label(toolbar, text="Hasta:", bg="white").pack(side="left", padx=(8,6))
        self.entry_to = DateEntry(toolbar, width=12, date_pattern="yyyy-mm-dd")
        self.entry_to.pack(side="left", padx=6)
        self.entry_to.set_date(datetime.utcnow())

        tk.Button(toolbar, text="Aplicar filtros", bg=C_HEADER, fg="white", command=self.on_apply_filters).pack(side="right", padx=8)
        tk.Button(toolbar, text="Exportar CSV", command=self.on_export_csv).pack(side="right", padx=8)
        self.btn_toggle = tk.Button(toolbar, text="Ver como tarjetas", command=self._toggle_view)
        self.btn_toggle.pack(side="right", padx=8)

        # resumen con conteos
        self.summary_frame = tk.Frame(self, bg=C_BODY_BG, pady=6)
        self.summary_frame.pack(fill="x", padx=12)
        self._build_summary_cards()

        # panel principal: izquierda contenido, derecha detalle
        main_pane = ttk.Panedwindow(self, orient="horizontal")
        main_pane.pack(fill="both", expand=True, padx=12, pady=(6,12))

        left_container = tk.Frame(main_pane, bg=C_CARD_BG)
        left_container.configure(width=760)
        main_pane.add(left_container, weight=3)

        right_container = tk.Frame(main_pane, bg=C_CARD_BG, padx=12, pady=12)
        right_container.configure(width=360)
        main_pane.add(right_container, weight=1)

        # área con scroll donde se colocará la tabla o tarjetas
        self.left_canvas = tk.Canvas(left_container, bg=C_CARD_BG, highlightthickness=0)
        self.left_scroll = ttk.Scrollbar(left_container, orient="vertical", command=self.left_canvas.yview)
        self.left_frame = tk.Frame(self.left_canvas, bg=C_CARD_BG)
        self.left_frame.bind("<Configure>", lambda e: self.left_canvas.configure(scrollregion=self.left_canvas.bbox("all")))
        self.left_canvas.create_window((0,0), window=self.left_frame, anchor="nw")
        self.left_canvas.configure(yscrollcommand=self.left_scroll.set)
        self.left_canvas.pack(side="left", fill="both", expand=True)
        self.left_scroll.pack(side="right", fill="y")

        self._build_table_view(self.left_frame)

        # detalle a la derecha
        self.detail_card = tk.Frame(right_container, bg=C_CARD_BG)
        self.detail_card.pack(fill="both", expand=True)
        self._build_detail_card(self.detail_card)

    def _build_summary_cards(self):
        # limpiar
        for w in self.summary_frame.winfo_children():
            w.destroy()

        types = ["CREATE_PROJECT","UPDATE_PROJECT","CAMBIO_ESTADO","DELETE_PROJECT"]
        for t in types:
            color = ACTION_COLORS.get(t, "#6B7280")
            card = tk.Frame(self.summary_frame, bg=C_CARD_BG, bd=0, highlightthickness=1, highlightbackground="#E5E7EB", padx=12, pady=8)
            card.pack(side="left", padx=8, pady=4)
            label_text = ACTION_LABELS_ES.get(t, t.replace("_", " "))
            tk.Label(card, text=label_text, bg=C_CARD_BG, fg=C_ACCENT, font=("Segoe UI", 9, "bold")).pack(anchor="w")
            cnt = "-"
            try:
                q = self._build_query_from_ui()
                cnt = self.controller.count(project_id=q.get("project_id"), tipo=t, start_date=q.get("start_date"), end_date=q.get("end_date"))
            except Exception:
                try:
                    cnt = self.controller.model.collection.count_documents({"tipo_de_accion": t})
                except Exception:
                    cnt = "-"
            tk.Label(card, text=str(cnt), bg=C_CARD_BG, fg=color, font=("Segoe UI", 14, "bold")).pack(anchor="w")

    def _build_table_view(self, parent):
        for w in parent.winfo_children():
            w.destroy()
        columns = ("fecha","usuario","rol","tipo","campo","valor_ant","valor_nvo")
        self.tree = ttk.Treeview(parent, columns=columns, show="headings", height=18)
        for col, title in zip(columns, ["Fecha","Usuario","Rol","Acción","Campo","Valor anterior","Nuevo valor"]):
            self.tree.heading(col, text=title)
            if col == "fecha":
                self.tree.column(col, width=150, anchor="w")
            elif col in ("valor_ant","valor_nvo"):
                self.tree.column(col, width=220, anchor="w")
            else:
                self.tree.column(col, width=110, anchor="w")
        vsb = ttk.Scrollbar(parent, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=vsb.set)
        vsb.pack(side="right", fill="y")
        self.tree.pack(fill="both", expand=True, side="left")
        self.tree.bind("<<TreeviewSelect>>", lambda e: self.on_select_entry())
        self.tree.bind("<Double-1>", lambda e: self.on_row_double())

    def _build_detail_card(self, parent):
        for w in parent.winfo_children():
            w.destroy()
        hdr = tk.Frame(parent, bg=C_HEADER, height=40)
        hdr.pack(fill="x", side="top")
        hdr.pack_propagate(False)
        tk.Label(hdr, text="Detalle del registro", bg=C_HEADER, fg="white", font=("Segoe UI", 11, "bold")).pack(side="left", padx=10)

        body = tk.Frame(parent, bg=C_CARD_BG, padx=10, pady=10)
        body.pack(fill="both", expand=True)

        self._detail_widgets = {}
        rows = [
            ("Fecha", "fecha"),
            ("Usuario", "usuario_nombre"),
            ("Rol", "rol"),
            ("Tipo de acción", "tipo_de_accion"),
            ("Campo", "campo"),
            ("Valor anterior", "valor_anterior"),
            ("Nuevo valor", "nuevo_valor"),
            ("ID Proyecto", "id_proyecto"),
            ("ID Registro", "_id"),
        ]
        for i, (label, key) in enumerate(rows):
            tk.Label(body, text=label + ":", bg=C_CARD_BG, fg="#374151", font=("Segoe UI", 9, "bold")).grid(row=i, column=0, sticky="nw", pady=(6,0))
            v = tk.Label(body, text="-", bg=C_CARD_BG, fg=TEXT_COLOR, wraplength=300, justify="left")
            v.grid(row=i, column=1, sticky="nw", pady=(6,0), padx=(10,0))
            self._detail_widgets[key] = v

        btns = tk.Frame(parent, bg=C_CARD_BG)
        btns.pack(fill="x", pady=(6,0))

    def _load_filters(self):
        # llenar combobox de proyectos basado en ids únicos de la colección historial
        vals = ["Todos los proyectos"]
        self._proj_map = {"Todos los proyectos": None}

        try:
            from mongo_con import MongoConnection
            conn = MongoConnection()
            hist_coll = conn.get_collection("historial")
            proj_coll = conn.get_collection("proyectos")
        except Exception:
            self.cb_proj['values'] = vals
            try:
                self.cb_proj.current(0)
            except Exception:
                self.cb_proj.set(vals[0])
            return

        try:
            distinct_ids = hist_coll.distinct("id_proyecto") or []
        except Exception:
            distinct_ids = []

        from bson import ObjectId
        seen = set()
        for raw in distinct_ids:
            try:
                if raw is None:
                    continue
                oid = None
                if isinstance(raw, ObjectId):
                    oid = raw
                else:
                    try:
                        if isinstance(raw, str) and len(raw) == 24:
                            oid = ObjectId(raw)
                        else:
                            oid = raw
                    except Exception:
                        oid = raw

                key = str(oid)
                if key in seen:
                    continue
                seen.add(key)

                name = None
                try:
                    if isinstance(oid, ObjectId):
                        pdoc = proj_coll.find_one({"_id": oid})
                    else:
                        pdoc = proj_coll.find_one({"_id": key})
                    if pdoc:
                        name = pdoc.get("nombre") or key
                except Exception:
                    name = None

                display = f"{name} ({key[:6]})" if name else f"{key[:6]}"
                vals.append(display)
                self._proj_map[display] = key

            except Exception:
                continue

        if len(vals) == 1:
            try:
                for p in proj_coll.find().limit(200):
                    nid = str(p.get("_id"))
                    display = f"{p.get('nombre', nid)} ({nid[:6]})"
                    if display not in vals:
                        vals.append(display)
                        self._proj_map[display] = nid
            except Exception:
                pass

        try:
            self.cb_proj['values'] = vals
            self.cb_proj.current(0)
        except Exception:
            try:
                self.cb_proj.set(vals[0])
            except Exception:
                pass

    def _build_query_from_ui(self):
        # construir filtros (project_id, tipo, fechas)
        sel = self.cb_proj.get().strip() if hasattr(self, "cb_proj") else None
        proj = None
        if sel:
            proj = self._proj_map.get(sel)
        tipo = self.cb_tipo.get().strip() or None

        start = None; end = None
        try:
            v = self.entry_from.get_date()
            if v:
                from datetime import datetime as _dt
                start = _dt.combine(v, _dt.min.time())
        except Exception:
            start = None
        try:
            v = self.entry_to.get_date()
            if v:
                from datetime import datetime as _dt
                end = _dt.combine(v, _dt.max.time())
        except Exception:
            end = None

        return {
            "project_id": proj,
            "tipo": tipo,
            "start_date": start,
            "end_date": end,
            "per_page": self.per_page
        }

    def load_entries(self):
        q = self._build_query_from_ui()
        try:
            entries = self.controller.list(**q) or []
        except Exception:
            try:
                entries = self.controller.model.find_by_filters(**q)
            except Exception as ex:
                messagebox.showerror("Error", f"No se pudieron cargar los registros:\n{ex}")
                return

        try:
            self._build_summary_cards()
        except Exception:
            pass

        if self.view_mode == "table":
            try:
                self.tree.delete(*self.tree.get_children())
            except Exception:
                pass
            for e in entries:
                fecha = e.get("fecha")
                fecha_str = fecha.strftime("%Y-%m-%d %H:%M:%S") if hasattr(fecha, "strftime") else str(fecha)
                iid = str(e.get("_id"))
                tipo = e.get("tipo_de_accion") or "-"
                vals = (
                    fecha_str,
                    e.get("usuario_nombre") or "-",
                    e.get("rol") or "-",
                    tipo,
                    e.get("campo") or "-",
                    str(e.get("valor_anterior") or "-"),
                    str(e.get("nuevo_valor") or "-"),
                )
                self.tree.insert("", "end", iid=iid, values=vals, tags=(tipo,))
            try:
                self.left_canvas.yview_moveto(0)
            except Exception:
                pass
        else:
            self._render_cards_view(entries)

    def _render_cards_view(self, entries):
        for w in self.left_frame.winfo_children():
            w.destroy()
        cols = 2
        r = 0; c = 0
        padx = 8; pady = 8
        for e in entries:
            tipo = e.get("tipo_de_accion") or "-"
            color = ACTION_COLORS.get(tipo, ACTION_COLORS.get(None))
            card = tk.Frame(self.left_frame, bg="white", bd=1, relief="solid", highlightthickness=0, padx=10, pady=8)
            card.grid(row=r, column=c, padx=padx, pady=pady, sticky="nwes")
            strip = tk.Frame(card, bg=color, height=6)
            strip.pack(fill="x", side="top", pady=(0,8))
            fecha = e.get("fecha")
            fecha_str = fecha.strftime("%Y-%m-%d %H:%M:%S") if hasattr(fecha, "strftime") else str(fecha)
            label_text = ACTION_LABELS_ES.get(tipo, tipo.replace("_"," "))
            tk.Label(card, text=label_text, bg="white", fg=C_ACCENT, font=("Segoe UI", 10, "bold")).pack(anchor="w")
            tk.Label(card, text=f"{e.get('usuario_nombre','-')} • {e.get('rol','-')}", bg="white", fg="#6B7280", font=("Segoe UI", 9)).pack(anchor="w", pady=(2,0))
            tk.Label(card, text=fecha_str, bg="white", fg="#9CA3AF", font=("Segoe UI", 8)).pack(anchor="w", pady=(2,6))
            tk.Label(card, text=f"Campo: {e.get('campo','-')}", bg="white", fg=TEXT_COLOR, font=("Segoe UI", 9)).pack(anchor="w")
            tk.Label(card, text=f"Antes: {str(e.get('valor_anterior','-'))}", bg="white", fg="#374151", wraplength=300, justify="left").pack(anchor="w", pady=(4,0))
            tk.Label(card, text=f"Ahora: {str(e.get('nuevo_valor','-'))}", bg="white", fg="#111827", wraplength=300, justify="left").pack(anchor="w", pady=(2,0))
            card.bind("<Button-1>", lambda ev, id_=str(e.get("_id")): self._select_by_id(id_))
            for child in card.winfo_children():
                child.bind("<Button-1>", lambda ev, id_=str(e.get("_id")): self._select_by_id(id_))

            c += 1
            if c >= cols:
                c = 0; r += 1
        for i in range(cols):
            try: self.left_frame.grid_columnconfigure(i, weight=1)
            except Exception: pass
        self.left_canvas.yview_moveto(0)

    def _select_by_id(self, hid):
        try:
            from mongo_con import MongoConnection
            conn = MongoConnection()
            doc = conn.get_collection("historial").find_one({"_id": ObjectId(hid)})
        except Exception:
            doc = None
        if not doc:
            messagebox.showinfo("Detalle", "No se pudo cargar el detalle.")
            return
        self._show_detail(doc)
        try:
            self.tree.selection_set(hid)
            self.tree.focus(hid)
        except Exception:
            pass

    def on_select_entry(self):
        sel = self.tree.focus()
        if not sel:
            return
        hid = sel
        try:
            from mongo_con import MongoConnection
            conn = MongoConnection()
            doc = conn.get_collection("historial").find_one({"_id": ObjectId(hid)})
        except Exception:
            doc = None
        if not doc:
            messagebox.showinfo("Detalle", "No se pudo cargar el detalle.")
            return
        self._show_detail(doc)

    def _show_detail(self, doc):
        def fmt(v):
            if v is None: return "-"
            try:
                if isinstance(v, ObjectId): return str(v)
            except Exception: pass
            try:
                return v.strftime("%Y-%m-%d %H:%M:%S") if hasattr(v, "strftime") else str(v)
            except Exception:
                return str(v)
        self._detail_widgets.get("fecha").config(text=fmt(doc.get("fecha")))
        self._detail_widgets.get("usuario_nombre").config(text=fmt(doc.get("usuario_nombre")))
        self._detail_widgets.get("rol").config(text=fmt(doc.get("rol")))
        self._detail_widgets.get("tipo_de_accion").config(text=fmt(doc.get("tipo_de_accion")))
        self._detail_widgets.get("campo").config(text=fmt(doc.get("campo")))
        self._detail_widgets.get("valor_anterior").config(text=fmt(doc.get("valor_anterior")))
        self._detail_widgets.get("nuevo_valor").config(text=fmt(doc.get("nuevo_valor")))
        self._detail_widgets.get("id_proyecto").config(text=fmt(doc.get("id_proyecto")))
        self._detail_widgets.get("_id").config(text=fmt(doc.get("_id")))

    def on_row_double(self):
        sel = self.tree.focus()
        if not sel:
            return
        hid = sel
        try:
            from mongo_con import MongoConnection
            conn = MongoConnection()
            doc = conn.get_collection("historial").find_one({"_id": ObjectId(hid)})
        except Exception:
            doc = None
        if not doc:
            messagebox.showinfo("Detalle", "No se pudo cargar el detalle.")
            return
        d = tk.Toplevel(self)
        d.title("Detalle del log")
        txt = tk.Text(d, width=100, height=30)
        import json
        def conv(o):
            try:
                if isinstance(o, ObjectId): return str(o)
                if hasattr(o, "isoformat"): return o.isoformat()
            except Exception: pass
            return o
        serial = {k: conv(v) for k,v in (doc.items())}
        txt.insert("1.0", json.dumps(serial, indent=2, default=str))
        txt.pack(fill="both", expand=True, padx=10, pady=10)

    def _toggle_view(self):
        self.view_mode = "cards" if self.view_mode == "table" else "table"
        self.btn_toggle.config(text="Ver como tabla" if self.view_mode == "cards" else "Ver como tarjetas")
        if self.view_mode == "table":
            self._build_table_view(self.left_frame)
        else:
            for w in self.left_frame.winfo_children():
                w.destroy()
        self.load_entries()

    def on_apply_filters(self):
        self.load_entries()

    def on_export_csv(self):
        import csv, tkinter.filedialog as fd
        q = self._build_query_from_ui()
        try:
            all_entries = self.controller.model.find_by_filters(**{**q, "page":1, "per_page":10000})
        except Exception:
            try:
                all_entries = self.controller.list(**{**q, "page":1, "per_page":10000})
            except Exception:
                all_entries = []
        if not all_entries:
            messagebox.showinfo("Exportar CSV", "No hay registros para exportar.")
            return
        f = fd.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV files","*.csv")])
        if not f:
            return
        with open(f, "w", newline="", encoding="utf-8") as fh:
            writer = csv.writer(fh)
            writer.writerow(["fecha","usuario","rol","id_proyecto","tipo","campo","valor_anterior","nuevo_valor"])
            for e in all_entries:
                fecha = e.get("fecha")
                fecha_str = fecha.strftime("%Y-%m-%d %H:%M:%S") if hasattr(fecha, "strftime") else str(fecha)
                writer.writerow([fecha_str, e.get("usuario_nombre"), e.get("rol"), str(e.get("id_proyecto")), e.get("tipo_de_accion"), str(e.get("campo")), str(e.get("valor_anterior")), str(e.get("nuevo_valor"))])
        messagebox.showinfo("Exportar CSV", f"Exportado {len(all_entries)} registros a:\n{f}")
