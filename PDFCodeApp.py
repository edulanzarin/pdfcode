import tkinter as tk
from tkinter import filedialog, ttk
from ttkthemes import ThemedStyle
import threading
import PyPDF2
import os
import datetime

from process_capital_emporio import process_capital_emporio
from process_lojao import process_lojao
from process_qualitplacas import process_qualitplacas

data_validade = datetime.datetime(2023, 12, 1)


class PDFCodeApp:
    def __init__(self, root):
        self.root = root
        self.root.title("PDFCode")
        self.root.geometry("600x350")
        icon_path = r".\assets\icon.ico"
        self.root.iconbitmap(icon_path)

        self.file_path = None
        self.selected_empresa_var = tk.StringVar(self.root)
        self.selected_empresa_var.set("Qualitplacas")

        self.create_widgets()

    def create_widgets(self):
        style = ThemedStyle(self.root)
        style.set_theme("vista")
        style.configure("TCombobox", padding=7, borderwidth=2, relief="solid")

        empresas = ["Qualitplacas", "Lojão Astral", "Capital Six", "Empório Astral"]
        self.empresa_menu = ttk.Combobox(
            self.root,
            textvariable=self.selected_empresa_var,
            values=empresas,
            font=("Arial", 10),
        )
        self.empresa_menu.bind("<Enter>", self.change_cursor)
        self.empresa_menu.pack(pady=20)

        self.select_button = ttk.Button(
            self.root,
            text="Selecionar PDF",
            command=self.select_pdf,
            width=22,
            padding=10,
        )
        self.select_button.bind("<Enter>", self.change_cursor)
        self.select_button.pack(pady=20)

        self.process_button = ttk.Button(
            self.root,
            text="Processar PDF",
            command=self.processar_pdf_thread,
            width=22,
            padding=10,
        )
        self.process_button.bind("<Enter>", self.change_cursor)
        self.process_button.pack(pady=15)
        self.process_button.config(state="disabled")

        self.status_label = ttk.Label(self.root, text="", font=("Arial", 10))
        self.status_label.pack()

        self.progress_bar = ttk.Progressbar(self.root, mode="determinate")
        self.progress_bar.pack_forget()

        if datetime.datetime.now() > data_validade:
            self.status_label.config(text="A licença expirou.")
            self.process_button.config(state="disabled")
            self.select_button.config(state="disabled")
            self.empresa_menu.config(state="disabled")

    def select_pdf(self):
        self.file_path = filedialog.askopenfilename(filetypes=[("PDF files", "*.pdf")])
        if self.file_path:
            file_name = os.path.basename(self.file_path)
            self.status_label.config(text=f"{file_name}")
            self.process_button.config(state="normal")
        else:
            self.status_label.config(text="Nenhum arquivo PDF selecionado.")
            self.process_button.config(state="disabled")

    def change_cursor(self, event):
        self.select_button.config(cursor="hand2")
        self.process_button.config(cursor="hand2")
        self.empresa_menu.config(cursor="hand2")

    def processar_pdf_thread(self):
        self.process_button.config(state="disabled")
        self.progress_bar.pack(pady=20)

        pdf_thread = threading.Thread(target=self.processar_pdf)
        pdf_thread.start()

    def processar_pdf(self):
        with open(self.file_path, "rb") as pdf_file:
            dados_pdf = PyPDF2.PdfReader(pdf_file)

            selected_empresa = self.selected_empresa_var.get()

            if (
                selected_empresa == "Capital Six"
                or selected_empresa == "Empório Astral"
            ):
                # Chame a função de processamento para a empresa Empório Astral
                df = process_capital_emporio(dados_pdf, self.progress_bar)

            elif selected_empresa == "Lojão Astral":
                # Chame a função de processamento para a empresa Capital Six
                df = process_lojao(dados_pdf, self.progress_bar)

            elif selected_empresa == "Qualitplacas":
                # Chame a função de processamento para a empresa Qualitplacas
                df = process_qualitplacas(dados_pdf, self.progress_bar)

            if selected_empresa:
                save_path = filedialog.asksaveasfilename(
                    defaultextension=".xlsx", filetypes=[("Excel files", "*.xlsx")]
                )
                if not save_path:
                    self.status_label.config(
                        text="Nenhum local de salvamento selecionado."
                    )
                    self.progress_bar.pack_forget()  # Oculta a barra de progresso
                    return

                df.to_excel(save_path, index=False)

        self.progress_bar.pack_forget()
        self.root.after(10, self.finish_processing)

    def finish_processing(self):
        self.status_label.config(text="Processamento concluído.")
        self.process_button.config(state="normal")


def main():
    root = tk.Tk()
    app = PDFCodeApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
