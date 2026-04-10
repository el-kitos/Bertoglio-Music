import customtkinter as ctk
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
    return ctk.CTkButton(root, text=text, font=font, fg_color=bg, text_color=fg, width=width, height=height, command=command)

def aplicar_botones(boton, x, y):
    boton.place(relx=x, rely=y)

#-------Funciones para interfaz--------
def cuadros_pag_principal(root):
    global lista_canciones

    panel_izq = ctk.CTkFrame(root, width=350, height=768, fg_color="#2b2b2b", corner_radius=15)
    panel_izq.place(x=0, y=0)

    titulo = ctk.CTkLabel(panel_izq, text="🎵 Canciones", font=ctk.CTkFont(size=20, weight="bold"), text_color="#ffffff")
    titulo.pack(pady=0)

    lista_canciones = ctk.CTkScrollableFrame(panel_izq, width=320, height=650, fg_color="#1f1f1f", corner_radius=10)
    lista_canciones.pack(pady=70, padx=15)

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
            cancion_btn = ctk.CTkButton(lista_canciones, text=f"🎶 {nombre}", command=lambda n=nombre: reproducir_cancion_por_nombre(n), fg_color="#3a3a3a", hover_color="#4a4a4a", corner_radius=8)
            cancion_btn.pack(pady=5, fill="x", padx=10)

    guardar_canciones()

def reproducir_cancion_por_nombre(nombre):
    ruta_cancion = os.path.join(MUSICA_DIR, nombre)
    if os.path.exists(ruta_cancion):
        try:
            pygame.mixer.music.stop()
            pygame.mixer.music.load(ruta_cancion)
            pygame.mixer.music.play()
        except Exception:
            pass

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
            cancion_btn = ctk.CTkButton(lista_canciones, text=f"🎶 {nombre}", command=lambda n=nombre: reproducir_cancion_por_nombre(n), fg_color="#3a3a3a", hover_color="#4a4a4a", corner_radius=8)
            cancion_btn.pack(pady=5, fill="x", padx=10)
    



