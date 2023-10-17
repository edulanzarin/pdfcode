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

        status_frame = ttk.Frame(self.root)
        status_frame.pack(pady=30)

        # Carregue o GIF usando PIL
        image = Image.open(r".\assets\pdf.png")  # Substitua pelo caminho do seu GIF
        width, height = 250, 150  # Tamanho desejado (ajuste conforme necessário)
        image = image.resize((width, height))  # Redimensiona a imagem suavemente

        photo = ImageTk.PhotoImage(image)

        # Crie o Label para exibir o GIF
        self.status_label = ttk.Label(status_frame, image=photo)
        self.status_label.photo = photo  # Mantenha uma referência para evitar que o GIF seja coletado pelo garbage collector
        self.status_label.pack()


def main():
    root = tk.Tk()
    app = StartMenu(root)
    root.mainloop()


if __name__ == "__main__":
    main()
