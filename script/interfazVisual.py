import tkinter as tk
from tkinter import ttk, messagebox
from PIL import Image, ImageTk
from tkinter import filedialog
import os

def cuadros_pag_principal(root):
    style = ttk.Style()
    style.configure('SinBorde.TLabelframe', background='#000000')
    style.configure('SinBorde.TLabelframe.Label', font='arial 14 bold', background='#000000', foreground='#ffffff')
    panel_izq = ttk.LabelFrame(root, text="Canciones", style="SinBorde.TLabelframe")
    panel_izq.place(x=0, y=0, width=300, height=768)



def cargar_imagen(ruta, ancho=None, alto=None):
    # Abrir la imagen
    img = Image.open(ruta)
    # Redimensionar si se pasan ancho y alto
    if ancho and alto:
        img = img.resize((ancho, alto))
    
    # Convertir para tkinter
    return ImageTk.PhotoImage(img)

def botones(root, text, font, bg, fg, width, height,):
    boton = tk.Button(root, text=text, font=font, bg=bg fg=fg, width=width, height=height)
    return boton

def aplicar_botones(boton, x, y):
    boton.place(x=x ,y= y)

root = tk.Tk()
play_boton = botones(root, "Play", (14, "Arial"), "#000000", "#ffffff", 30, 10)



