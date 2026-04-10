import os
import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk
from interfazVisual import cuadros_pag_principal, aplicar_botones, botones, agregar_canciones, cargar_canciones, reproducir_cancion

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ASSET_PATH = os.path.join(ROOT_DIR, "assets", "background.png")

root = tk.Tk()
root.title("Reproductor de Musica")
root.geometry("1366x768")
root.iconbitmap("assets/icon.ico")

image = Image.open("assets/background.png")
bg_image = ImageTk.PhotoImage(image)

bg_label = tk.Label(root, image=bg_image)
bg_label.place(x=0, y=0, relwidth=1, relheight=1)


def main():
    cuadros_pag_principal(root)
    cargar_canciones()

    agregar_cancion_boton = botones(root, "Agregar Cancion", ("Arial", 14), "#000000", "#ffffff", 15, 2, command=agregar_canciones)
    aplicar_botones(agregar_cancion_boton, 60, 30)
    
    reproducir_cancion()
    


main()
root.mainloop()


















