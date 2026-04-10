import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk
from tkinter import filedialog
import os
import shutil
import json
import pygame

pygame.mixer.init()



rutas = []
lista_canciones = None


def cargar_imagen(ruta, ancho=None, alto=None):
    img = Image.open(ruta)
    if ancho and alto:
        img = img.resize((ancho, alto))
    return ImageTk.PhotoImage(img)


#---------Funciones para crear botones---------
def botones(root, text, font, bg, fg, width, height, command):
    return tk.Button(root, text=text, font=font, bg=bg, fg=fg, width=width, height=height, command=command)


def aplicar_botones(boton, x, y):
    boton.place(x=x, y=y)


#-------Funciones para interfaz--------
def cuadros_pag_principal(root):
    global lista_canciones

    style = ttk.Style()
    style.configure('SinBorde.TLabelframe', background='#000000')
    style.configure('SinBorde.TLabelframe.Label', font='arial 14 bold', background='#000000', foreground='#ffffff')

    panel_izq = ttk.LabelFrame(root, text="Canciones", style="SinBorde.TLabelframe")
    panel_izq.place(x=0, y=0, width=300, height=768)

    lista_canciones = tk.Listbox(panel_izq, bg="#111111", fg="#ffffff", font=("Arial", 12), selectbackground="#444444")
    lista_canciones.place(x=10, y=80, width=280, height=720)
    lista_canciones.bind("<Double-Button-1>", reproducir_cancion)
    return lista_canciones


#-------Funciones para reproducir canciones---------
def reproducir_cancion(event=None):
    if lista_canciones is None:
        return

    seleccion = lista_canciones.curselection()
    if not seleccion:
        return

    nombre = lista_canciones.get(seleccion[0])
    ruta_cancion = os.path.join(MUSICA_DIR, nombre)

    if os.path.exists(ruta_cancion):
        try:
            pygame.mixer.music.stop()
            pygame.mixer.music.load(ruta_cancion)
            pygame.mixer.music.play()
        except Exception:
            pass


#-------Funciones para agregar una cancion---------

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MUSICA_DIR = os.path.join(BASE_DIR, "musica")
DATABASE_PATH = os.path.join(BASE_DIR, "BaseDeDatos.json")

def agregar_canciones():
    archivos = filedialog.askopenfilenames(
        title="Seleccionar canción",
        filetypes=[("Archivos MP3", "*.mp3")]
    )

    if not archivos:
        return

    os.makedirs(MUSICA_DIR, exist_ok=True)

    for archivo in archivos:
        nombre = os.path.basename(archivo)
        destino = os.path.join(MUSICA_DIR, nombre)

        if not os.path.exists(destino):
            shutil.copy(archivo, destino)

        if nombre not in rutas:
            rutas.append(nombre)
            if lista_canciones is not None:
                lista_canciones.insert(tk.END, nombre)

    guardar_canciones()


def guardar_canciones():
    os.makedirs(MUSICA_DIR, exist_ok=True)
    with open(DATABASE_PATH, "w", encoding="utf-8") as f:
        json.dump(rutas, f, ensure_ascii=False, indent=2)


def cargar_canciones():
    if not os.path.exists(DATABASE_PATH):
        return

    try:
        with open(DATABASE_PATH, "r", encoding="utf-8") as f:
            datos = json.load(f)
    except (json.JSONDecodeError, ValueError):
        return

    for nombre in datos:
        if nombre not in rutas:
            rutas.append(nombre)
            if lista_canciones is not None:
                lista_canciones.insert(tk.END, nombre)
    



