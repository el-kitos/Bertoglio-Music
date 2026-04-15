import os
import customtkinter as ctk
from PIL import Image, ImageTk
from interfazVisual import cuadros_pag_principal, aplicar_botones, botones, botones_imagen, agregar_canciones, cargar_canciones, crear_playlist, cargar_playlists, play, registrar_play_boton

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
    aplicar_botones(play_boton, 0.65, 0.9)

    panel = cuadros_pag_principal(root, update_buttons)

    update_buttons(None)

main()
root.mainloop()


















