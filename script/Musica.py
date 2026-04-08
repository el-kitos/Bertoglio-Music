import tkinter as tk
from tkinter import ttk, messagebox

class Boton:
    def __init__(self, ventana, pos_x, pos_y, imagen, action):
        self.ventana = ventana
        self.pos_x = pos_x
        self.pos_y = pos_y
        self.imagen = imagen
        self.action = action
    
    def play(self):
        pass
    
    def pause():
        pass

    def stop():
        pass

    def next():
        pass

    def previous():
        pass

    def volume():
        pass

def cuadros(root):
    panel_izq = ttk.LabelFrame(root, text="Panel de Operaciones")
    panel_izq.place(x=10, y=10, width=300, height=680)