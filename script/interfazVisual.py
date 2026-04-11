import customtkinter as ctk
from PIL import Image, ImageTk
from tkinter import filedialog, simpledialog, messagebox
import os
import shutil
import json
import pygame

pygame.mixer.init()

# Cambia 'rutas' por 'playlists' como diccionario: {"nombre_playlist": ["cancion1.mp3", "cancion2.mp3"]}
playlists = {}
playlist_actual = None  # Para rastrear la playlist seleccionada
playlists_frame = None  # Para recargar la interfaz

def cargar_imagen(ruta, ancho=None, alto=None):
    img = Image.open(ruta)
    if ancho and alto:
        img = img.resize((ancho, alto))
    return ImageTk.PhotoImage(img)

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
def cuadros_pag_principal(root, update_callback):
    global playlists, playlists_frame

    panel_izq = ctk.CTkFrame(root, width=350, height=768, fg_color="#2b2b2b", corner_radius=15)
    panel_izq.place(x=0, y=0)

    titulo = ctk.CTkLabel(panel_izq, text="🎵 Playlists", font=ctk.CTkFont(size=20, weight="bold"), text_color="#ffffff")
    titulo.pack(pady=10)

    # Frame para listas de playlists y canciones
    playlists_frame = ctk.CTkScrollableFrame(panel_izq, width=320, height=600, fg_color="#1f1f1f", corner_radius=10)
    playlists_frame.pack(pady=70, padx=15)

    # Cargar playlists existentes
    cargar_playlists(playlists_frame, update_callback)

    return playlists_frame

def cargar_playlists(frame, update_callback):
    # Limpiar el frame
    for widget in frame.winfo_children():
        widget.destroy()

    # Mostrar cada playlist como un botón
    for nombre_playlist in playlists:
        btn_playlist = ctk.CTkButton(frame, text=f"📁 {nombre_playlist}", command=lambda n=nombre_playlist: seleccionar_playlist(n, frame, update_callback), fg_color="#3a3a3a", hover_color="#4a4a4a", corner_radius=8)
        btn_playlist.pack(pady=5, fill="x", padx=10)

    update_callback(playlist_actual)

def volver_a_playlists(frame, update_callback):
    global playlist_actual
    playlist_actual = None
    cargar_playlists(frame, update_callback)

def seleccionar_playlist(nombre_playlist, frame, update_callback):
    global playlist_actual
    playlist_actual = nombre_playlist

    # Limpiar y mostrar canciones de la playlist seleccionada
    for widget in frame.winfo_children():
        widget.destroy()

    # Botón para volver a la lista de playlists
    btn_volver = ctk.CTkButton(frame, text="⬅ Volver a Playlists", command=lambda: volver_a_playlists(frame, update_callback), fg_color="#4a4a4a", hover_color="#5a5a5a", corner_radius=8)
    btn_volver.pack(pady=5, fill="x", padx=10)

    # Mostrar canciones de la playlist
    for cancion in playlists[nombre_playlist]:
        cancion_btn = ctk.CTkButton(frame, text=f"🎶 {cancion}", command=lambda c=cancion: reproducir_cancion_por_nombre(c), fg_color="#3a3a3a", hover_color="#4a4a4a", corner_radius=8)
        cancion_btn.pack(pady=5, fill="x", padx=10)

    update_callback(playlist_actual)

#-------Funciones para reproducir canciones---------
def reproducir_cancion_por_nombre(nombre):
    if playlist_actual and nombre in playlists[playlist_actual]:
        ruta_cancion = os.path.join(MUSICA_DIR, nombre)
        if os.path.exists(ruta_cancion):
            try:
                pygame.mixer.music.stop()
                pygame.mixer.music.load(ruta_cancion)
                pygame.mixer.music.play()
            except Exception:
                pass

#-------Funciones para agregar una canción---------
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MUSICA_DIR = os.path.join(BASE_DIR, "musica")
DATABASE_PATH = os.path.join(BASE_DIR, "BaseDeDatos.json")

def agregar_canciones():
    if not playlist_actual:
        messagebox.showerror("Error", "Selecciona una playlist primero.")
        return

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

        if nombre not in playlists[playlist_actual]:
            playlists[playlist_actual].append(nombre)

    guardar_playlists()

def crear_playlist():
    nombre = simpledialog.askstring("Nueva Playlist", "Ingresa el nombre de la playlist:")
    if nombre and nombre not in playlists:
        playlists[nombre] = []
        guardar_playlists()
        if playlists_frame:
            cargar_playlists(playlists_frame)

def guardar_playlists():
    with open(DATABASE_PATH, "w", encoding="utf-8") as f:
        json.dump(playlists, f, ensure_ascii=False, indent=2)

def cargar_canciones():
    global playlists
    if not os.path.exists(DATABASE_PATH):
        return

    try:
        with open(DATABASE_PATH, "r", encoding="utf-8") as f:
            datos = json.load(f)
            if isinstance(datos, list):
                # Migrar de lista antigua a dict con playlist por defecto
                playlists = {"Canciones": datos}
            else:
                playlists = datos
    except (json.JSONDecodeError, ValueError):
        playlists = {}




