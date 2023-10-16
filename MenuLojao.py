import tkinter as tk
from tkinter import ttk, filedialog
from ttkthemes import ThemedStyle
import threading
import PyPDF2
import os
import pandas as pd
from process_lojao import process_lojao

empresas = [
    "Central de Compras",
    "CH Comércio",
    "Comercial MCD",
    "JGS Comércio",
    "Loja Astral",
    "SF Comércio",
]


class MenuLojao:
    def __init__(self, root):
        self.root = root

        self.empresa_file_path = None
        self.empresa_df = None

        self.progress_bar = ttk.Progressbar(self.root, mode="determinate")
        self.progress_bar.pack_forget()

        self.process_button_enabled = False

        self.selected_empresa_var = tk.StringVar(self.root)
        self.selected_empresa_var.set("")

        style = ThemedStyle(self.root)
        style.set_theme("arc")

        self.create_widgets()

    def create_widgets(self):
        self.title_label = ttk.Label(self.root, text="Lojão", font=("Arial", 12))
        self.title_label.pack(pady=10)

        self.space_label = ttk.Label(self.root, text="")
        self.space_label.pack(pady=22)

        # Frame para os botões
        button_frame = ttk.Frame(self.root)
        button_frame.pack(pady=20)

        self.start_label = ttk.Label(
            button_frame, text="Selecionar Loja", font=("Arial", 10)
        )
        self.start_label.pack(side="left", padx=5)

        # Frame para as ComboBoxes de seleção
        combobox_frame = ttk.Frame(button_frame)
        combobox_frame.pack(side="left")

        self.empresa_menu = ttk.Combobox(
            combobox_frame,
            textvariable=self.selected_empresa_var,
            values=empresas,
            font=("Arial", 10),
            style="Custom.TCombobox",
            state="readonly",
            width=30,
        )
        self.empresa_menu.pack(side="left")

        select_frame = ttk.Frame(self.root)
        select_frame.pack(pady=20)

        self.select_empresa_button = ttk.Button(
            select_frame,
            text="Selecionar Relatório",
            command=self.select_empresa_pdf,
            width=25,
        )
        self.select_empresa_button.pack(side="left", padx=5)

        self.process_button_frame = ttk.Frame(self.root)
        self.process_button_frame.pack(pady=10)

        self.process_button = ttk.Button(
            self.process_button_frame,
            text="Processar PDF",
            command=self.processar_pdf_thread,
            width=25,
        )
        self.process_button.pack()
        self.process_button.config(state="disabled")

        status_frame = ttk.Frame(self.root)
        status_frame.pack(pady=40)

        self.status_label = ttk.Label(status_frame, text="", font=("Arial", 12))
        self.status_label.pack()

        self.check_process_button_state()

    def select_empresa_pdf(self):
        self.empresa_file_path = filedialog.askopenfilename(
            filetypes=[("PDF files", "*.pdf")]
        )
        if self.empresa_file_path:
            file_name = os.path.basename(self.empresa_file_path)
            self.status_label.config(text=f"Relatório: {file_name}")
            self.check_process_button_state()

    def check_process_button_state(self):
        if self.empresa_file_path:
            self.process_button.config(state="normal")
        else:
            self.process_button.config(state="disabled")

    def processar_pdf_thread(self):
        self.process_button.config(state="disabled")
        pdf_thread = threading.Thread(target=self.processar_pdf)
        pdf_thread.start()

    def processar_pdf(self):
        self.progress_bar.pack(pady=20, padx=20, fill=tk.X)

        if self.empresa_file_path:
            with open(self.empresa_file_path, "rb") as empresa_pdf_file:
                dados_empresa_pdf = PyPDF2.PdfReader(empresa_pdf_file)

                self.empresa_df = process_lojao(dados_empresa_pdf, self.progress_bar)

        if self.empresa_df is not None:
            save_path = filedialog.asksaveasfilename(
                defaultextension=".xlsx", filetypes=[("Excel files", "*.xlsx")]
            )
            if not save_path:
                self.status_label.config(text="Nenhum local de salvamento selecionado.")
                self.progress_bar.pack_forget()
                return

            with pd.ExcelWriter(save_path, engine="xlsxwriter") as writer:
                self.empresa_df.to_excel(writer, sheet_name="Planilha1", index=False)

                worksheet = writer.sheets["Planilha1"]
                worksheet.set_column("D:D", None, None, {"num_format": "General"})

        self.progress_bar.pack_forget()
        self.root.after(10, self.finish_processing)

    def finish_processing(self):
        self.status_label.config(text="Processamento concluído.")
        self.process_button.config(state="normal")


def main():
    root = tk.Tk()
    app = MenuLojao(root)
    root.mainloop()


if __name__ == "__main__":
    main()
