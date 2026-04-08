import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk  # Import Pillow modules
from Musica import cuadros

root = tk.Tk()
root.title("Reproductor de Musica")
root.geometry("1920x1080")

image = Image.open("assets/background.png")
bg_image = ImageTk.PhotoImage(image)

# Create a label and place it at (0,0) covering the whole window
bg_label = tk.Label(root, image=bg_image)
bg_label.place(x=0, y=0, relwidth=1, relheight=1)

cuadros(root)
root.mainloop()


















