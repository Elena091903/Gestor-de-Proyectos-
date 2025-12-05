import tkinter as tk
from controllers.m3_controller import TareaController

if __name__ == "__main__":
    root = tk.Tk()
    root.title("Módulo 3: Creación de Tareas")
    root.geometry("700x550")
    
    app = TareaController(root)
    
    root.mainloop()