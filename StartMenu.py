import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk


class StartMenu:
    def __init__(self, root):
        self.root = root
        self.create_widgets()

    def create_widgets(self):
        self.title_label = ttk.Label(self.root, text="Sigma", font=("Arial", 12))
        self.title_label.pack(pady=10)

        self.space_label = ttk.Label(self.root, text="")
        self.space_label.pack(pady=25)

        image_frame = ttk.Frame(self.root)
        image_frame.pack(pady=30)

        image = Image.open(r".\assets\pdf.png")
        width, height = 150, 90
        image = image.resize((width, height))

        photo = ImageTk.PhotoImage(image)

        self.image_label = ttk.Label(image_frame, image=photo)
        self.image_label.photo = photo
        self.image_label.pack()

        status_frame = ttk.Frame(self.root)
        status_frame.pack(pady=30)

        # Crie o Label para exibir o GIF
        self.status_label = ttk.Label(status_frame)
        self.status_label.pack()

    def set_status(self, text):
        self.status_label.config(text=text)


def main():
    root = tk.Tk()
    app = StartMenu(root)
    root.mainloop()


if __name__ == "__main__":
    main()
