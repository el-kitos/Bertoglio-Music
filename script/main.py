import os
import customtkinter as ctk
from PIL import Image, ImageTk
from interfazVisual import cuadros_pag_principal, aplicar_botones, botones, botones_imagen, agregar_canciones, cargar_canciones, crear_playlist, cargar_playlists, play, registrar_play_boton, next_song, previous_song, toggle_mute, set_volume, seek, update_progress, registrar_progress_slider, registrar_volume_slider, registrar_time_labels, registrar_cover_widgets, update_cover_panel, eliminar_cancion, toggle_shuffle, toggle_loop, crear_barra_busqueda, obtener_seleccion_desde_busqueda, resetear_seleccion_busqueda

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
ASSET_DIR = os.path.abspath(os.path.join(SCRIPT_DIR, "..", "assets"))

root = ctk.CTk()
root.title("Bertoglio Music")
root.geometry("1366x768")
root.iconbitmap(os.path.join(ASSET_DIR, "icon.ico"))

image = Image.open(os.path.join(ASSET_DIR, "background.png"))
bg_image = ImageTk.PhotoImage(image)

bg_label = ctk.CTkLabel(root, image=bg_image, text="")
bg_label.place(relx=0, rely=0, relwidth=1, relheight=1)

def update_buttons(current_playlist, current_song=None):
    # Verificar si la canción fue seleccionada desde la búsqueda
    desde_busqueda = obtener_seleccion_desde_busqueda()
    
    if current_playlist:
        if agregar_cancion_boton:
            aplicar_botones(agregar_cancion_boton, 0.06, 0.08)
            agregar_cancion_boton.lift()
        if crear_playlist_boton:
            crear_playlist_boton.place_forget()
        # Solo mostrar botón de eliminar si hay canción Y NO fue seleccionada desde búsqueda
        if current_song and eliminar_cancion_boton and not desde_busqueda:
            aplicar_botones(eliminar_cancion_boton, 0.06, 0.16)
            eliminar_cancion_boton.lift()
        elif eliminar_cancion_boton:
            eliminar_cancion_boton.place_forget()
    else:
        if crear_playlist_boton:
            aplicar_botones(crear_playlist_boton, 0.06, 0.08)
            crear_playlist_boton.lift()
        if agregar_cancion_boton:
            agregar_cancion_boton.place_forget()
        if eliminar_cancion_boton:
            eliminar_cancion_boton.place_forget()
    
    # Resetear el flag después de actualizar los botones
    resetear_seleccion_busqueda()

def main():
    cargar_canciones()

    global agregar_cancion_boton, crear_playlist_boton, eliminar_cancion_boton
    agregar_cancion_boton = botones(root, "➕ Agregar Canción", ctk.CTkFont(size=14, weight="bold"), "#4a4a4a", "#ffffff", 200, 50, command=agregar_canciones)
    crear_playlist_boton = botones(root, "📁 Crear Playlist", ctk.CTkFont(size=14, weight="bold"), "#4a4a4a", "#ffffff", 200, 50, command=crear_playlist)
    eliminar_cancion_boton = botones(root, "🗑️ Eliminar Canción", ctk.CTkFont(size=14, weight="bold"), "#9f1f1f", "#ffffff", 200, 50, command=eliminar_cancion)
    eliminar_cancion_boton.place_forget()

    previous_boton = botones_imagen(root, ruta_imagen=os.path.join(ASSET_DIR, "botones", "rewind.png"), width=50, height=50, bg="#4a4a4a", hover_bg="#5a5a5a", command=previous_song)
    aplicar_botones(previous_boton, 0.40, 0.93)

    shuffle_boton = botones_imagen(root, ruta_imagen=os.path.join(ASSET_DIR, "botones", "shuffle.png"), width=50, height=50, bg="#4a4a4a", hover_bg="#5a5a5a", command=lambda: toggle_shuffle(shuffle_boton))
    aplicar_botones(shuffle_boton, 0.35, 0.93)

    play_boton = botones_imagen(root, ruta_imagen=os.path.join(ASSET_DIR, "botones", "play-button.png"), width=50, height=50, bg="#4a4a4a", hover_bg="#5a5a5a", command=lambda: play(play_boton))
    registrar_play_boton(play_boton)
    aplicar_botones(play_boton, 0.45, 0.93)

    next_boton = botones_imagen(root, ruta_imagen=os.path.join(ASSET_DIR, "botones", "next.png"), width=50, height=50, bg="#4a4a4a", hover_bg="#5a5a5a", command=next_song)
    aplicar_botones(next_boton, 0.50, 0.93)

    loop_boton = botones_imagen(root, ruta_imagen=os.path.join(ASSET_DIR, "botones", "loop.png"), width=50, height=50, bg="#4a4a4a", hover_bg="#5a5a5a", command=lambda: toggle_loop(loop_boton))
    aplicar_botones(loop_boton, 0.55, 0.93)

    mute_boton = botones_imagen(root, ruta_imagen=os.path.join(ASSET_DIR, "botones", "volume-mute.png"), width=50, height=50, bg="#4a4a4a", hover_bg="#5a5a5a", command=toggle_mute)
    aplicar_botones(mute_boton, 0.60, 0.93)

    volume_slider = ctk.CTkSlider(root, from_=0, to=1, command=set_volume)
    volume_slider.set(1.0)
    volume_slider.place(relx=0.65, rely=0.93, relwidth=0.15, relheight=0.05)
    registrar_volume_slider(volume_slider)

    progress_slider = ctk.CTkSlider(root, from_=0, to=100, command=lambda value: seek(value, root))
    progress_slider.place(relx=0.3, rely=0.85, relwidth=0.4, relheight=0.05)
    registrar_progress_slider(progress_slider)

    # Labels para tiempo
    current_time_label = ctk.CTkLabel(root, text="0:00", font=ctk.CTkFont(size=12), text_color="#3d3b3b")
    current_time_label.place(relx=0.71, rely=0.85)

    registrar_time_labels(current_time_label)

    update_progress(root)

    panel = cuadros_pag_principal(root, update_buttons)

    # Crear barra de búsqueda en el centro
    crear_barra_busqueda(root, update_buttons)

    update_buttons(None)

    # Panel derecho para portada y info
    panel_derecho = ctk.CTkFrame(root, width=300, height=768, fg_color="#2b2b2b", corner_radius=15)
    panel_derecho.place(x=1200, y=0)

    # Portada
    placeholder_img = Image.new('RGB', (200, 200), color='gray')
    cover_img = ImageTk.PhotoImage(placeholder_img)
    cover_label = ctk.CTkLabel(panel_derecho, image=cover_img, text="")
    cover_label.pack(pady=50)

    # Artista
    artist_label = ctk.CTkLabel(panel_derecho, text="Artista", font=ctk.CTkFont(size=16, weight="bold"), text_color="#ffffff")
    artist_label.pack(anchor="e", fill="x", padx=(0, 20), pady=10)

    # Título
    title_label = ctk.CTkLabel(panel_derecho, text="Canción", font=ctk.CTkFont(size=14), text_color="#ffffff")
    title_label.pack(anchor="e", fill="x", padx=(0, 20), pady=5)

    registrar_cover_widgets(cover_label, artist_label, title_label)
    update_cover_panel()

main()
root.mainloop()


















