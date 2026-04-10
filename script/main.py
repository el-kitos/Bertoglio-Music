import os
import customtkinter as ctk
from PIL import Image, ImageTk
from interfazVisual import cuadros_pag_principal, aplicar_botones, botones, agregar_canciones, cargar_canciones

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ASSET_PATH = os.path.join(ROOT_DIR, "assets", "background.png")

root = ctk.CTk()
root.title("Reproductor de Música")
root.geometry("1366x768")
root.iconbitmap("assets/icon.ico")

image = Image.open(ASSET_PATH)
bg_image = ImageTk.PhotoImage(image)

bg_label = ctk.CTkLabel(root, image=bg_image, text="")
bg_label.place(relx=0, rely=0, relwidth=1, relheight=1)



def main():
    panel = cuadros_pag_principal(root)
    cargar_canciones()

    agregar_cancion_boton = botones(root, "➕ Agregar Canción", ctk.CTkFont(size=14, weight="bold"), "#4a4a4a", "#ffffff", 200, 50, command=agregar_canciones)
    aplicar_botones(agregar_cancion_boton, 0.06, 0.05)

main()
root.mainloop()


















