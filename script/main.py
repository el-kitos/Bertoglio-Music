import os
import customtkinter as ctk
from PIL import Image, ImageTk
from interfazVisual import cuadros_pag_principal, aplicar_botones, botones, botones_imagen, agregar_canciones, cargar_canciones, crear_playlist, cargar_playlists, play, registrar_play_boton, next_song, previous_song, toggle_mute, set_volume, seek, update_progress, registrar_progress_slider, registrar_volume_slider, registrar_time_labels, registrar_cover_widgets, update_cover_panel

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ASSET_PATH = os.path.join(ROOT_DIR, "assets", "background.png")

root = ctk.CTk()
root.title("Reproductor de Música")
root.geometry("1366x768")
root.iconbitmap(os.path.join(ROOT_DIR, "assets", "icon.ico"))

image = Image.open(ASSET_PATH)
bg_image = ImageTk.PhotoImage(image)

bg_label = ctk.CTkLabel(root, image=bg_image, text="")
bg_label.place(relx=0, rely=0, relwidth=1, relheight=1)

def update_buttons(current_playlist):
    if current_playlist:
        if agregar_cancion_boton:
            aplicar_botones(agregar_cancion_boton, 0.06, 0.08)
            agregar_cancion_boton.lift()
        if crear_playlist_boton:
            crear_playlist_boton.place_forget()
    else:
        if crear_playlist_boton:
            aplicar_botones(crear_playlist_boton, 0.06, 0.08)
            crear_playlist_boton.lift()
        if agregar_cancion_boton:
            agregar_cancion_boton.place_forget()

def main():
    cargar_canciones()

    global agregar_cancion_boton, crear_playlist_boton
    agregar_cancion_boton = botones(root, "➕ Agregar Canción", ctk.CTkFont(size=14, weight="bold"), "#4a4a4a", "#ffffff", 200, 50, command=agregar_canciones)
    crear_playlist_boton = botones(root, "📁 Crear Playlist", ctk.CTkFont(size=14, weight="bold"), "#4a4a4a", "#ffffff", 200, 50, command=crear_playlist)
    play_boton = botones_imagen(root, ruta_imagen="assets/botones/play-button.png", width=50, height=50, bg="#4a4a4a", hover_bg="#5a5a5a", command=lambda: play(play_boton))
    registrar_play_boton(play_boton)
    aplicar_botones(play_boton, 0.45, 0.93)

    previous_boton = botones_imagen(root, ruta_imagen="assets/botones/rewind.png", width=50, height=50, bg="#4a4a4a", hover_bg="#5a5a5a", command=previous_song)
    aplicar_botones(previous_boton, 0.40, 0.93)

    next_boton = botones_imagen(root, ruta_imagen="assets/botones/next.png", width=50, height=50, bg="#4a4a4a", hover_bg="#5a5a5a", command=next_song)
    aplicar_botones(next_boton, 0.5, 0.93)

    mute_boton = botones_imagen(root, ruta_imagen="assets/botones/volume-mute.png", width=50, height=50, bg="#4a4a4a", hover_bg="#5a5a5a", command=toggle_mute)
    aplicar_botones(mute_boton, 0.55, 0.93)

    volume_slider = ctk.CTkSlider(root, from_=0, to=1, command=set_volume)
    volume_slider.set(1.0)
    volume_slider.place(relx=0.6, rely=0.93, relwidth=0.15, relheight=0.05)
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

    update_buttons(None)

    # Panel derecho para portada y info
    panel_derecho = ctk.CTkFrame(root, width=300, height=768, fg_color="#2b2b2b", corner_radius=15)
    panel_derecho.place(x=1020, y=0)

    # Portada
    placeholder_img = Image.new('RGB', (200, 200), color='gray')
    cover_img = ImageTk.PhotoImage(placeholder_img)
    cover_label = ctk.CTkLabel(panel_derecho, image=cover_img, text="")
    cover_label.pack(pady=50)

    # Artista
    artist_label = ctk.CTkLabel(panel_derecho, text="Artista", font=ctk.CTkFont(size=16, weight="bold"), text_color="#ffffff")
    artist_label.pack(pady=10)

    # Título
    title_label = ctk.CTkLabel(panel_derecho, text="Canción", font=ctk.CTkFont(size=14), text_color="#ffffff")
    title_label.pack(pady=5)

    registrar_cover_widgets(cover_label, artist_label, title_label)
    update_cover_panel()

main()
root.mainloop()


















