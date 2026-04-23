import customtkinter as ctk
from PIL import Image, ImageTk
from tkinter import filedialog, simpledialog, messagebox
import os
import shutil
import json
import pygame
from mutagen.mp3 import MP3
from mutagen.id3 import ID3, APIC
from mutagen.flac import FLAC
import io

pygame.mixer.init()

# Variables globales de interfaz
playlists_frame = None  # Para recargar la interfaz
interfaz_callback = None
mostrando_playlists = True

# Variables globales de música
playlists = {}
playlist_actual = None
cancion_seleccionada = None
cancion_actual = None
estado = 0  # 0 = detenido, 1 = reproduciendo, 2 = pausado
play_boton = None
volumen_actual = 1.0
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
shuffle_enabled = False
loop_enabled = False
song_ended = False
search_entry = None
search_results_frame = None
search_results_visible = False
seleccion_desde_busqueda = False

# Cache de metadatos para búsqueda: {nombre_cancion: {'title': ..., 'artist': ..., 'album': ...}}
metadatos_cache = {}

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MUSICA_DIR = os.path.join(BASE_DIR, "musica")
DATABASE_PATH = os.path.join(BASE_DIR, "BaseDeDatos.json")
ASSET_DIR = os.path.join(BASE_DIR, "assets")

def cargar_imagen(ruta, ancho=None, alto=None):
    if isinstance(ruta, str) and not os.path.isabs(ruta):
        ruta = os.path.normpath(os.path.join(ASSET_DIR, ruta))
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
    global playlists, playlists_frame, interfaz_callback

    interfaz_callback = update_callback

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
    global mostrando_playlists

    mostrando_playlists = True

    # Limpiar el frame
    for widget in frame.winfo_children():
        widget.destroy()

    # Mostrar cada playlist como un botón
    for nombre_playlist in playlists:
        btn_playlist = ctk.CTkButton(frame, text=f"📁 {nombre_playlist}", command=lambda n=nombre_playlist: seleccionar_playlist(n, frame, update_callback), fg_color="#3a3a3a", hover_color="#4a4a4a", corner_radius=8)
        btn_playlist.pack(pady=5, fill="x", padx=10)

    update_callback(None, cancion_seleccionada)

def volver_a_playlists(frame, update_callback):
    global playlist_actual, mostrando_playlists
    playlist_actual = None
    mostrando_playlists = True
    cargar_playlists(frame, update_callback)

def seleccionar_playlist(nombre_playlist, frame, update_callback):
    global playlist_actual, cancion_seleccionada, mostrando_playlists
    playlist_actual = nombre_playlist
    cancion_seleccionada = None
    mostrando_playlists = False

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

    update_callback(playlist_actual, cancion_seleccionada)

#-------Funciones para reproducir canciones---------
def seleccionar_cancion(nombre):
    """Selecciona una canción para reproducir después"""
    global cancion_seleccionada, playlist_actual
    cancion_seleccionada = nombre
    # Si no hay playlist actual, buscar en qué playlist está la canción
    if not playlist_actual:
        for nombre_playlist, canciones in playlists.items():
            if nombre in canciones:
                playlist_actual = nombre_playlist
                break
    if interfaz_callback:
        interfaz_callback(playlist_actual, cancion_seleccionada)

def seleccionar_cancion_doble(nombre):
    """Selecciona la canción al hacer doble clic"""
    seleccionar_cancion(nombre)
    if play_boton is not None:
        play(play_boton)

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
            cargar_playlists(playlists_frame, interfaz_callback)

def guardar_playlists():
    with open(DATABASE_PATH, "w", encoding="utf-8") as f:
        json.dump(playlists, f, ensure_ascii=False, indent=2)

def eliminar_cancion():
    global cancion_seleccionada, cancion_actual, estado
    if not playlist_actual or not cancion_seleccionada:
        messagebox.showwarning("Atención", "Selecciona una canción primero")
        return

    if cancion_seleccionada not in playlists.get(playlist_actual, []):
        messagebox.showwarning("Atención", "La canción ya no está en la playlist")
        return

    if messagebox.askyesno("Confirmar", f"¿Eliminar '{cancion_seleccionada}' de la playlist?"):
        playlists[playlist_actual].remove(cancion_seleccionada)
        guardar_playlists()

        if cancion_seleccionada == cancion_actual:
            pygame.mixer.music.stop()
            estado = 0
            cancion_actual = None

        cancion_seleccionada = None
        if playlists_frame and interfaz_callback:
            if mostrando_playlists:
                cargar_playlists(playlists_frame, interfaz_callback)
            else:
                seleccionar_playlist(playlist_actual, playlists_frame, interfaz_callback)
        else:
            if interfaz_callback:
                interfaz_callback(playlist_actual, cancion_seleccionada)

def play(play_boton):
    global estado, cancion_actual, cancion_seleccionada, playlist_actual, playlists, MUSICA_DIR, duration, seeking, current_offset, current_artist, current_title, current_cover, song_ended

    # Usar cancion_actual si cancion_seleccionada no está disponible (ej. después de borrar búsqueda)
    cancion_a_verificar = cancion_seleccionada if cancion_seleccionada else cancion_actual
    playlist_a_verificar = playlist_actual if playlist_actual else "Canciones"  # Playlist por defecto
    
    same_song = cancion_a_verificar and cancion_actual and cancion_a_verificar == cancion_actual
    
    # Verificar si la canción está en alguna playlist
    valid_selection = False
    if cancion_a_verificar and playlist_a_verificar:
        for nombre_playlist, canciones in playlists.items():
            if cancion_a_verificar in canciones:
                playlist_a_verificar = nombre_playlist
                valid_selection = True
                break

    if estado == 1 and same_song:
        pygame.mixer.music.pause()
        imagen_play = cargar_imagen("../assets/botones/play-button.png", ancho=50, alto=50)
        play_boton.configure(image=imagen_play)
        play_boton.image = imagen_play
        estado = 2
        return

    if estado == 2 and same_song:
        pygame.mixer.music.unpause()
        imagen_pause = cargar_imagen("../assets/botones/pause.png", ancho=50, alto=50)
        play_boton.configure(image=imagen_pause)
        play_boton.image = imagen_pause
        estado = 1
        return

    if not valid_selection:
        messagebox.showwarning("Atención", "Selecciona una canción primero")
        return

    # Usar la primera playlist que contenga la canción
    ruta_cancion = None
    for nombre_playlist, canciones in playlists.items():
        if cancion_a_verificar in canciones:
            playlist_actual = nombre_playlist
            ruta_cancion = os.path.join(MUSICA_DIR, cancion_a_verificar)
            break
    
    if not ruta_cancion:
        ruta_cancion = os.path.join(MUSICA_DIR, cancion_a_verificar)
    
    if not os.path.exists(ruta_cancion):
        messagebox.showerror("Error", "No se encontró el archivo de la canción")
        return

    try:
        seeking = False
        current_offset = 0
        pygame.mixer.music.stop()
        pygame.mixer.music.load(ruta_cancion)
        
        # Resetear metadatos a valores por defecto antes de extraer
        current_title = 'Unknown Title'
        current_artist = 'Unknown Artist'
        current_cover = None
        duration = 0
        
        # Determinar el tipo de archivo y extraer metadata
        ext = os.path.splitext(ruta_cancion)[1].lower()
        if ext == '.mp3':
            audio = MP3(ruta_cancion)
            duration = audio.info.length
            current_title = str(audio.tags.get('TIT2', 'Unknown Title')) if audio.tags and 'TIT2' in audio.tags else 'Unknown Title'
            current_artist = str(audio.tags.get('TPE1', 'Unknown Artist')) if audio.tags and 'TPE1' in audio.tags else 'Unknown Artist'
            cover_data = audio.tags.get('APIC:', None).data if audio.tags and 'APIC:' in audio.tags else None
        elif ext == '.flac':
            audio = FLAC(ruta_cancion)
            duration = audio.info.length
            current_title = str(audio.tags.get('title', ['Unknown Title'])[0]) if 'title' in audio.tags else 'Unknown Title'
            current_artist = str(audio.tags.get('artist', ['Unknown Artist'])[0]) if 'artist' in audio.tags else 'Unknown Artist'
            cover_data = audio.pictures[0].data if audio.pictures else None
        else:
            # Para otros formatos, usar valores por defecto
            duration = 0
            current_title = 'Unknown Title'
            current_artist = 'Unknown Artist'
            cover_data = None
        
        if cover_data:
            current_cover = cargar_imagen(io.BytesIO(cover_data), ancho=200, alto=200)
        else:
            current_cover = cargar_imagen('../assets/placeholder.png', ancho=200, alto=200) if os.path.exists('../assets/placeholder.png') else None
        
        update_cover_panel()
        if progress_slider:
            progress_slider.configure(to=duration)
            progress_slider.set(0)
        pygame.mixer.music.play()
        cancion_actual = cancion_seleccionada
        imagen_pause = cargar_imagen("../assets/botones/pause.png", ancho=50, alto=50)
        play_boton.configure(image=imagen_pause)
        play_boton.image = imagen_pause
        estado = 1
        song_ended = False
    except Exception as e:
        messagebox.showerror("Error", f"No se pudo reproducir la canción: {e}")

def next_song():
    global cancion_seleccionada, playlist_actual, estado, shuffle_enabled
    
    # Buscar la canción actual en cualquier playlist
    cancion_a_buscar = cancion_seleccionada if cancion_seleccionada else cancion_actual
    if not cancion_a_buscar:
        return
    
    # Encontrar la playlist que contiene la canción
    playlist_encontrada = None
    for nombre_playlist, canciones in playlists.items():
        if cancion_a_buscar in canciones:
            playlist_encontrada = nombre_playlist
            break
    
    if not playlist_actual or not playlist_encontrada:
        return
    
    playlist = playlists[playlist_encontrada]
    playlist_actual = playlist_encontrada
    current_index = 0

    try:
        if cancion_a_buscar and cancion_a_buscar in playlist:
            current_index = playlist.index(cancion_a_buscar)
    except ValueError:
        current_index = 0

    if shuffle_enabled:
        import random
        available_indices = [i for i in range(len(playlist)) if i != current_index]
        if available_indices:
            next_index = random.choice(available_indices)
        else:
            next_index = current_index
    else:
        next_index = (current_index + 1) % len(playlist)

    cancion_seleccionada = playlist[next_index]
    if play_boton and (estado == 1 or estado == 2):
        play(play_boton)

def previous_song():
    global cancion_seleccionada, playlist_actual, estado, shuffle_enabled
    
    # Buscar la canción actual en cualquier playlist
    cancion_a_buscar = cancion_seleccionada if cancion_seleccionada else cancion_actual
    if not cancion_a_buscar:
        return
    
    # Encontrar la playlist que contiene la canción
    playlist_encontrada = None
    for nombre_playlist, canciones in playlists.items():
        if cancion_a_buscar in canciones:
            playlist_encontrada = nombre_playlist
            break
    
    if not playlist_actual or not playlist_encontrada:
        return
    
    playlist = playlists[playlist_encontrada]
    playlist_actual = playlist_encontrada
    current_index = 0

    try:
        if cancion_a_buscar and cancion_a_buscar in playlist:
            current_index = playlist.index(cancion_a_buscar)
    except ValueError:
        current_index = 0

    if shuffle_enabled:
        import random
        available_indices = [i for i in range(len(playlist)) if i != current_index]
        if available_indices:
            prev_index = random.choice(available_indices)
        else:
            prev_index = current_index
    else:
        prev_index = (current_index - 1) % len(playlist)

    cancion_seleccionada = playlist[prev_index]
    if play_boton and (estado == 1 or estado == 2):
        play(play_boton)

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
    global estado, seeking, current_offset, song_ended
    seeking = True
    current_offset = float(value)
    song_ended = False
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
    global estado, loop_enabled, seeking, current_offset, duration, song_ended
    if estado == 1:
        if pygame.mixer.music.get_busy():
            pos = current_offset + pygame.mixer.music.get_pos() / 1000.0
            if pos >= 0 and pos <= duration:
                if progress_slider:
                    progress_slider.set(pos)
                current_sec = int(pos)
                current_str = f"{current_sec // 60}:{current_sec % 60:02d}"
                if current_time_label:
                    current_time_label.configure(text=current_str)
        else:
            if not song_ended:
                song_ended = True
                if loop_enabled:
                    pygame.mixer.music.play(start=0)
                    if progress_slider:
                        progress_slider.set(0)
                    current_offset = 0
                    seeking = False
                    song_ended = False
                else:
                    next_song()
    root.after(500, lambda: update_progress(root))

def toggle_shuffle(boton):
    global shuffle_enabled
    shuffle_enabled = not shuffle_enabled
    boton.configure(fg_color="#6a6a6a" if shuffle_enabled else "#4a4a4a")

def toggle_loop(boton):
    global loop_enabled
    loop_enabled = not loop_enabled
    boton.configure(fg_color="#6a6a6a" if loop_enabled else "#4a4a4a")

def registrar_play_boton(boton):
    global play_boton
    play_boton = boton

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
    if cover_label:
        if current_cover:
            cover_label.configure(image=current_cover)
            cover_label.image = current_cover
        else:
            # Resetear a imagen por defecto (gris)
            gray_img = Image.new('RGB', (200, 200), color='gray')
            tk_img = ImageTk.PhotoImage(gray_img)
            cover_label.configure(image=tk_img)
            cover_label.image = tk_img
    if artist_label:
        artist_label.configure(text=current_artist)
    if title_label:
        title_label.configure(text=current_title)

def registrar_cover_widgets(c_label, a_label, t_label):
    global cover_label, artist_label, title_label
    cover_label = c_label
    artist_label = a_label
    title_label = t_label

def cargar_canciones():
    global playlists, metadatos_cache
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
    
    # Filtrar canciones que no existen en el directorio musica
    for playlist_name in playlists:
        playlists[playlist_name] = [song for song in playlists[playlist_name] if os.path.exists(os.path.join(MUSICA_DIR, song))]
    
    # Guardar las playlists filtradas
    guardar_playlists()
    
    # Limpiar cache de metadatos al cargar nuevas playlists
    metadatos_cache = {}

#-------Funciones de búsqueda-------
def obtener_metadatos_cancion(nombre_cancion):
    """Obtiene los metadatos (título, artista, álbum) de una canción"""
    global metadatos_cache, MUSICA_DIR
    
    # Verificar si ya está en cache
    if nombre_cancion in metadatos_cache:
        return metadatos_cache[nombre_cancion]
    
    ruta_cancion = os.path.join(MUSICA_DIR, nombre_cancion)
    if not os.path.exists(ruta_cancion):
        metadatos_cache[nombre_cancion] = {'title': nombre_cancion, 'artist': '', 'album': ''}
        return metadatos_cache[nombre_cancion]
    
    try:
        ext = os.path.splitext(ruta_cancion)[1].lower()
        metadatos = {'title': nombre_cancion, 'artist': '', 'album': ''}
        
        if ext == '.mp3':
            audio = MP3(ruta_cancion)
            metadatos['title'] = str(audio.tags.get('TIT2', nombre_cancion)) if audio.tags and 'TIT2' in audio.tags else nombre_cancion
            metadatos['artist'] = str(audio.tags.get('TPE1', '')) if audio.tags and 'TPE1' in audio.tags else ''
            metadatos['album'] = str(audio.tags.get('TALB', '')) if audio.tags and 'TALB' in audio.tags else ''
        elif ext == '.flac':
            audio = FLAC(ruta_cancion)
            metadatos['title'] = str(audio.tags.get('title', [nombre_cancion])[0]) if 'title' in audio.tags else nombre_cancion
            metadatos['artist'] = str(audio.tags.get('artist', [''])[0]) if 'artist' in audio.tags else ''
            metadatos['album'] = str(audio.tags.get('album', [''])[0]) if 'album' in audio.tags else ''
        
        metadatos_cache[nombre_cancion] = metadatos
        return metadatos
    except Exception:
        metadatos_cache[nombre_cancion] = {'title': nombre_cancion, 'artist': '', 'album': ''}
        return metadatos_cache[nombre_cancion]

def buscar_canciones(query, update_callback):
    """Busca canciones en todas las playlists por nombre, artista o álbum"""
    if not query or len(query.strip()) < 1:
        return []
    
    query_lower = query.lower().strip()
    resultados = []
    
    # Buscar en todas las playlists
    for nombre_playlist, canciones in playlists.items():
        for cancion in canciones:
            # Obtener metadatos de la canción
            metadatos = obtener_metadatos_cancion(cancion)
            
            # Buscar en nombre de archivo, título, artista y álbum
            if (query_lower in cancion.lower() or 
                query_lower in metadatos['title'].lower() or 
                query_lower in metadatos['artist'].lower() or 
                query_lower in metadatos['album'].lower()):
                resultados.append((nombre_playlist, cancion, metadatos))
    
    return resultados

def mostrar_resultados_busqueda(query, frame, update_callback):
    """Muestra los resultados de búsqueda en un frame"""
    global search_results_frame
    
    # Limpiar resultados anteriores
    for widget in frame.winfo_children():
        widget.destroy()
    
    if not query or len(query.strip()) < 1:
        return
    
    resultados = buscar_canciones(query, update_callback)
    
    if not resultados:
        label_no_results = ctk.CTkLabel(frame, text="No se encontraron canciones", text_color="#888888")
        label_no_results.pack(pady=10)
        return
    
    # Mostrar resultados con metadatos
    for item in resultados:
        nombre_playlist = item[0]
        cancion = item[1]
        metadatos = item[2] if len(item) > 2 else {'title': cancion, 'artist': '', 'album': ''}
        
        # Crear texto con información adicional
        texto = f"🎵 {metadatos['title']}"
        if metadatos['artist']:
            texto += f"\n   └ {metadatos['artist']}"
        if metadatos['album']:
            texto += f" • {metadatos['album']}"
        
        btn_resultado = ctk.CTkButton(
            frame, 
            text=texto,
            command=lambda p=nombre_playlist, c=cancion: seleccionar_y_reproducir(p, c),
            fg_color="#3a3a3a", 
            hover_color="#4a4a4a", 
            corner_radius=8,
            anchor="w",
            height=50
        )
        btn_resultado.pack(pady=3, fill="x", padx=5)

def seleccionar_y_reproducir(playlist_name, song_name):
    """Selecciona una canción de los resultados de búsqueda y la reproduce"""
    global playlist_actual, cancion_seleccionada, seleccion_desde_busqueda
    playlist_actual = playlist_name
    cancion_seleccionada = song_name
    seleccion_desde_busqueda = True
    if interfaz_callback:
        interfaz_callback(playlist_actual, cancion_seleccionada)
    if play_boton:
        play(play_boton)

def obtener_seleccion_desde_busqueda():
    """Retorna si la canción actual fue seleccionada desde la búsqueda"""
    global seleccion_desde_busqueda
    return seleccion_desde_busqueda

def resetear_seleccion_busqueda():
    """Resetea el flag de selección desde búsqueda"""
    global seleccion_desde_busqueda
    seleccion_desde_busqueda = False

def crear_barra_busqueda(root, update_callback):
    """Crea la barra de búsqueda y el frame de resultados"""
    global search_entry, search_results_frame
    
    # Frame contenedor para la búsqueda
    search_container = ctk.CTkFrame(root, fg_color="transparent")
    search_container.place(relx=0.35, rely=0.02, relwidth=0.5, relheight=0.08)
    
    # Barra de búsqueda
    search_entry = ctk.CTkEntry(
        search_container, 
        placeholder_text="🔍 Buscar canción...",
        font=ctk.CTkFont(size=14),
        fg_color="#2b2b2b",
        border_color="#4a4a4a",
        text_color="#ffffff"
    )
    search_entry.pack(fill="x", pady=5)
    
    # Frame para resultados (inicialmente oculto)
    search_results_frame = ctk.CTkScrollableFrame(
        root,
        width=400,
        height=300,
        fg_color="#1f1f1f",
        corner_radius=10
    )
    search_results_frame.place_forget()
    
    # Bind para buscar mientras se escribe
    search_entry.bind('<KeyRelease>', lambda event: on_search_input(search_entry.get(), update_callback))
    
    # Bind para perder foco
    search_entry.bind('<FocusOut>', lambda event: ocultar_resultados())
    
    return search_container, search_results_frame

def on_search_input(query, update_callback):
    """Se ejecuta cuando el usuario escribe en la barra de búsqueda"""
    global search_results_frame, search_results_visible
    
    if not query or len(query.strip()) < 1:
        search_results_frame.place_forget()
        search_results_visible = False
        return
    
    # Posicionar el frame de resultados debajo de la barra de búsqueda
    search_results_frame.lift()
    search_results_frame.place(relx=0.35, rely=0.09, relwidth=0.5, relheight=0.4)
    search_results_visible = True
    
    # Mostrar resultados
    mostrar_resultados_busqueda(query, search_results_frame, update_callback)

def ocultar_resultados():
    """Oculta el frame de resultados cuando se pierde el foco"""
    global search_results_frame, search_results_visible
    search_results_frame.place_forget()
    search_results_visible = False




