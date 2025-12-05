# M4_Historial/main_m4.py
import argparse
import sys
from views.m4_history_manager import HistoryManagerUI

def parse_args():
    p = argparse.ArgumentParser()
    p.add_argument("--user-id", default="", help="ID del usuario que abre el módulo")
    p.add_argument("--usuario", default="", help="nombre del usuario")
    p.add_argument("--rol", default="", help="rol del usuario")
    return p.parse_args()

def main():
    args = parse_args()
    current_user = {"_id": args.user_id, "usuario": args.usuario, "rol": args.rol}
    app = HistoryManagerUI(current_user=current_user)
    app.mainloop()

if __name__ == "__main__":
    main()
