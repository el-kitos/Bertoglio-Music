import customtkinter as ctk
from PIL import Image, ImageTk
from tkinter import filedialog, simpledialog, messagebox
import os
import shutil
import json
import pygame
from mutagen.mp3 import MP3
from mutagen.id3 import ID3, APIC
import io

pygame.mixer.init()

# Cambia 'rutas' por 'playlists' como diccionario: {"nombre_playlist": ["cancion1.mp3", "cancion2.mp3"]}
playlists = {}
playlist_actual = None  # Para rastrear la playlist seleccionada
cancion_seleccionada = None  # Para rastrear la canción seleccionada
cancion_actual = None  # Canción que está cargada/reproduciéndose
estado = 0  # 0 = detenido, 1 = reproduciendo, 2 = pausado
play_boton = None  # Referencia al botón de play/pausa
playlists_frame = None  # Para recargar la interfaz
volumen_actual = 1.0  # Volumen inicial
muted = False
volumen_anterior = 1.0
progress_slider = None
volume_slider = None
duration = 0
seeking = False
current_offset = 0
current_time_label = None
current_artist = ""
current_title = ""
current_cover = None
cover_label = None
artist_label = None
title_label = None

def cargar_imagen(ruta, ancho=None, alto=None):
    img = Image.open(ruta)
    if ancho and alto:
        img = img.resize((ancho, alto))
    return ImageTk.PhotoImage(img)

#---------Funciones para crear botones---------
def botones(root, text, font, bg, fg, width, height, command):
    return ctk.CTkButton(root, text=text, font=font, fg_color=bg, text_color=fg, width=width, height=height, command=command)

def botones_imagen(root, ruta_imagen, width=None, height=None, bg="#4a4a4a", hover_bg="#5a5a5a", command=None):
    img = Image.open(ruta_imagen)
    if width and height:
        img = img.resize((width, height))
    img_tk = ImageTk.PhotoImage(img)
    
    boton = ctk.CTkButton(
        root,
        image=img_tk,
        text="",
        fg_color=bg,
        hover_color=hover_bg,
        width=width if width else 50,
        height=height if height else 50,
        command=command
    )
    # Guardar referencia a la imagen para evitar que sea recolectada por basura
    boton.image = img_tk
    return boton

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
        cancion_btn = ctk.CTkButton(frame, text=f"🎶 {cancion}", command=lambda c=cancion: seleccionar_cancion(c), fg_color="#3a3a3a", hover_color="#4a4a4a", corner_radius=8)
        cancion_btn.pack(pady=5, fill="x", padx=10)
        cancion_btn.bind("<Double-Button-1>", lambda event, c=cancion: seleccionar_cancion_doble(c))

    update_callback(playlist_actual)

#-------Funciones para reproducir canciones---------
def seleccionar_cancion(nombre):
    """Selecciona una canción para reproducir después"""
    global cancion_seleccionada
    cancion_seleccionada = nombre

def seleccionar_cancion_doble(nombre):
    """Selecciona la canción al hacer doble clic"""
    seleccionar_cancion(nombre)
    if play_boton is not None:
        play(play_boton)


def registrar_play_boton(boton):
    global play_boton
    play_boton = boton


def play(play_boton):
    global estado, cancion_actual, cancion_seleccionada, playlist_actual, playlists, MUSICA_DIR, duration, seeking, current_offset, current_artist, current_title, current_cover
    if not (cancion_seleccionada and playlist_actual and cancion_seleccionada in playlists[playlist_actual]):
        messagebox.showwarning("Atención", "Selecciona una canción primero")
        return

    ruta_cancion = os.path.join(MUSICA_DIR, cancion_seleccionada)
    if not os.path.exists(ruta_cancion):
        messagebox.showerror("Error", "No se encontró el archivo de la canción")
        return

    global cancion_actual

    if estado == 0 or cancion_seleccionada != cancion_actual:
        try:
            seeking = False
            current_offset = 0
            pygame.mixer.music.stop()
            pygame.mixer.music.load(ruta_cancion)
            audio = MP3(ruta_cancion)
            duration = audio.info.length
            # Extraer metadata
            global current_artist, current_title, current_cover
            current_title = str(audio.tags.get('TIT2', 'Unknown Title')) if audio.tags and 'TIT2' in audio.tags else 'Unknown Title'
            current_artist = str(audio.tags.get('TPE1', 'Unknown Artist')) if audio.tags and 'TPE1' in audio.tags else 'Unknown Artist'
            if audio.tags and 'APIC:' in audio.tags:
                cover_data = audio.tags['APIC:'].data
                current_cover = Image.open(io.BytesIO(cover_data)).resize((200, 200))
            else:
                # Placeholder
                current_cover = Image.open('assets/placeholder.png').resize((200, 200)) if os.path.exists('assets/placeholder.png') else Image.new('RGB', (200, 200), color='gray')
            update_cover_panel()
            if progress_slider:
                progress_slider.configure(to=duration)
                progress_slider.set(0)
            pygame.mixer.music.play()
            cancion_actual = cancion_seleccionada
            imagen_pause = cargar_imagen("assets/botones/pause.png", ancho=50, alto=50)
            play_boton.configure(image=imagen_pause)
            play_boton.image = imagen_pause
            estado = 1
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo reproducir la canción: {e}")

    elif estado == 1:
        pygame.mixer.music.pause()
        imagen_play = cargar_imagen("assets/botones/play-button.png", ancho=50, alto=50)
        play_boton.configure(image=imagen_play)
        play_boton.image = imagen_play
        estado = 2

    else:
        if cancion_seleccionada != cancion_actual:
            try:
                seeking = False
                current_offset = 0
                pygame.mixer.music.stop()
                pygame.mixer.music.load(ruta_cancion)
                audio = MP3(ruta_cancion)
                duration = audio.info.length
                # Extraer metadata

                current_title = str(audio.tags.get('TIT2', 'Unknown Title')) if audio.tags and 'TIT2' in audio.tags else 'Unknown Title'
                current_artist = str(audio.tags.get('TPE1', 'Unknown Artist')) if audio.tags and 'TPE1' in audio.tags else 'Unknown Artist'
                if audio.tags and 'APIC:' in audio.tags:
                    cover_data = audio.tags['APIC:'].data
                    current_cover = Image.open(io.BytesIO(cover_data)).resize((200, 200))
                else:
                    # Placeholder
                    current_cover = Image.open('assets/placeholder.png').resize((200, 200)) if os.path.exists('assets/placeholder.png') else Image.new('RGB', (200, 200), color='gray')
                # Si no hay metadata, intentar parsear del nombre del archivo
                if current_title == 'Unknown Title' or current_artist == 'Unknown Artist':
                    filename = os.path.basename(ruta_cancion).replace('.mp3', '')
                    if ' - ' in filename:
                        parts = filename.split(' - ', 1)
                        if len(parts) == 2:
                            current_artist = parts[0].strip()
                            current_title = parts[1].strip()
                    else:
                        current_title = filename
                        current_artist = 'Unknown Artist'
                update_cover_panel()
                if progress_slider:
                    progress_slider.configure(to=duration)
                    progress_slider.set(0)
                pygame.mixer.music.play()
                cancion_actual = cancion_seleccionada
                imagen_pause = cargar_imagen("assets/botones/pause.png", ancho=50, alto=50)
                play_boton.configure(image=imagen_pause)
                play_boton.image = imagen_pause
                estado = 1
            except Exception as e:
                messagebox.showerror("Error", f"No se pudo reproducir la canción: {e}")
        else:
            pygame.mixer.music.unpause()
            imagen_pause = cargar_imagen("assets/botones/pause.png", ancho=50, alto=50)
            play_boton.configure(image=imagen_pause)
            play_boton.image = imagen_pause
            estado = 1
        

    
def next_song():
    global cancion_seleccionada, estado
    if not playlist_actual or not playlists[playlist_actual]:
        return
    try:
        index = playlists[playlist_actual].index(cancion_seleccionada)
        next_index = (index + 1) % len(playlists[playlist_actual])
        cancion_seleccionada = playlists[playlist_actual][next_index]
        if estado == 1 or estado == 2:
            play(play_boton)
    except ValueError:
        pass

def previous_song():
    global cancion_seleccionada, estado
    if not playlist_actual or not playlists[playlist_actual]:
        return
    try:
        index = playlists[playlist_actual].index(cancion_seleccionada)
        prev_index = (index - 1) % len(playlists[playlist_actual])
        cancion_seleccionada = playlists[playlist_actual][prev_index]
        if estado == 1 or estado == 2:
            play(play_boton)
    except ValueError:
        pass

def toggle_mute():
    global muted, volumen_anterior, volumen_actual
    if muted:
        pygame.mixer.music.set_volume(volumen_anterior)
        volumen_actual = volumen_anterior
        muted = False
        if volume_slider:
            volume_slider.set(volumen_actual)
    else:
        volumen_anterior = volumen_actual
        pygame.mixer.music.set_volume(0.0)
        volumen_actual = 0.0
        muted = True
        if volume_slider:
            volume_slider.set(0.0)

def set_volume(value):
    global volumen_actual, muted
    volumen_actual = float(value)
    pygame.mixer.music.set_volume(volumen_actual)
    if volumen_actual > 0:
        muted = False

def seek(value, root):
    global estado, seeking, current_offset
    seeking = True
    current_offset = float(value)
    if estado == 1 or estado == 2:
        pygame.mixer.music.stop()
        pygame.mixer.music.play(start=current_offset)
        if estado == 2:
            pygame.mixer.music.pause()
    # Después de un pequeño delay, permitir actualizaciones
    def end_seek():
        global seeking
        seeking = False
    root.after(1000, end_seek)

def update_progress(root):
    if estado == 1 and progress_slider and not seeking:
        pos = current_offset + pygame.mixer.music.get_pos() / 1000.0
        if pos >= 0 and pos <= duration:
            progress_slider.set(pos)
    # Actualizar labels de tiempo siempre que esté reproduciendo
    if estado == 1:
        pos = current_offset + pygame.mixer.music.get_pos() / 1000.0
        if pos >= 0 and pos <= duration:
            current_sec = int(pos)
            current_str = f"{current_sec // 60}:{current_sec % 60:02d}"
            if current_time_label:
                current_time_label.configure(text=current_str)
    root.after(500, lambda: update_progress(root))

def registrar_progress_slider(slider):
    global progress_slider
    progress_slider = slider

def registrar_volume_slider(slider):
    global volume_slider
    volume_slider = slider

def registrar_time_labels(current_label):
    global current_time_label
    current_time_label = current_label

def update_cover_panel():
    global cover_label, artist_label, title_label, current_cover, current_artist, current_title
    if cover_label and current_cover:
        cover_img = ImageTk.PhotoImage(current_cover)
        cover_label.configure(image=cover_img)
        cover_label.image = cover_img
    if artist_label:
        artist_label.configure(text=current_artist)
    if title_label:
        title_label.configure(text=current_title)

def registrar_cover_widgets(c_label, a_label, t_label):
    global cover_label, artist_label, title_label
    cover_label = c_label
    artist_label = a_label
    title_label = t_label

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
        filetypes=[("Archivos MP3", "*.mp3, *.flac")]
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




