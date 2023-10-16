import tkinter as tk
from tkinter import ttk, filedialog
from ttkthemes import ThemedStyle
import threading
import PyPDF2
import os
import pandas as pd
from process_capital_six import process_capital_six
from process_francesinha_viacredi import process_francesinha_viacredi
from process_francesinha_sicredi import process_francesinha_sicredi


class MenuCapitalSix:
    def __init__(self, root):
        self.root = root

        self.empresa_file_path = None
        self.francesinha_file_path = None
        self.progress_bar = ttk.Progressbar(self.root, mode="determinate")
        self.progress_bar.pack_forget()
        self.empresa_df = None
        self.francesinha_df = None

        self.create_widgets()
        style = ThemedStyle(self.root)
        style.set_theme("arc")

    def create_widgets(self):
        self.title_label = ttk.Label(self.root, text="Capital Six", font=("Arial", 12))
        self.title_label.pack(pady=10)

        self.space_label = ttk.Label(self.root, text="")
        self.space_label.pack(pady=40)

        button_frame = ttk.Frame(self.root)
        button_frame.pack(pady=30)

        self.select_empresa_button = ttk.Button(
            button_frame,
            text="Selecionar Relatório",
            command=self.select_empresa_pdf,
            width=25,
            # padding=10,
        )
        self.select_empresa_button.grid(row=0, column=0)

        self.select_francesinha_button = ttk.Button(
            button_frame,
            text="Selecionar Francesinha",
            command=self.select_francesinha_pdf,
            width=25,
            # padding=10,
        )
        self.select_francesinha_button.grid(row=0, column=1)

        self.process_button_frame = ttk.Frame(self.root)
        self.process_button_frame.pack(pady=20)

        self.process_button = ttk.Button(
            self.process_button_frame,
            text="Processar PDF",
            command=self.processar_pdf_thread,
            width=25,
            # padding=10,
            state="disabled",
        )
        self.process_button.pack()

        status_frame = ttk.Frame(self.root)
        status_frame.pack(pady=40)

        self.status_label = ttk.Label(status_frame, text="", font=("Arial", 12))
        self.status_label.pack()

    def select_empresa_pdf(self):
        self.empresa_file_path = filedialog.askopenfilename(
            filetypes=[("PDF files", "*.pdf")]
        )
        if self.empresa_file_path:
            file_name = os.path.basename(self.empresa_file_path)
            self.status_label.config(text=f"Relatório: {file_name}")
            self.check_process_button_state()

    def select_francesinha_pdf(self):
        self.francesinha_file_path = filedialog.askopenfilename(
            filetypes=[("PDF files", "*.pdf")]
        )
        if self.francesinha_file_path:
            file_name = os.path.basename(self.francesinha_file_path)
            self.status_label.config(text=f"Francesinha: {file_name}")
            self.check_process_button_state()

    def check_process_button_state(self):
        if self.empresa_file_path or self.francesinha_file_path:
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

                # Chame a função para processar o PDF da CAPITAL SIX
                self.empresa_df = process_capital_six(
                    dados_empresa_pdf, self.progress_bar
                )

        if self.francesinha_file_path:
            with open(self.francesinha_file_path, "rb") as francesinha_pdf_file:
                dados_francesinha_pdf = PyPDF2.PdfReader(francesinha_pdf_file)

                # Verifique o nome do arquivo da Francesinha
                file_name = os.path.basename(self.francesinha_file_path)
                if "SICREDI" in file_name.upper():
                    self.francesinha_df = process_francesinha_sicredi(
                        dados_francesinha_pdf, self.progress_bar
                    )
                elif "VIACREDI" in file_name.upper():
                    self.francesinha_df = process_francesinha_viacredi(
                        dados_francesinha_pdf, self.progress_bar
                    )

        if self.empresa_df is not None:
            self.save_dataframe(self.empresa_df, "Empresa")

        if self.francesinha_df is not None:
            self.save_dataframe(self.francesinha_df, "Francesinha")

        self.progress_bar.pack_forget()
        self.root.after(10, self.finish_processing)

    def save_dataframe(self, df, sheet_name):
        save_path = filedialog.asksaveasfilename(
            defaultextension=".xlsx", filetypes=[("Excel files", "*.xlsx")]
        )
        if not save_path:
            self.status_label.config(text="Nenhum local de salvamento selecionado.")
            return

        with pd.ExcelWriter(save_path, engine="xlsxwriter") as writer:
            df.to_excel(writer, sheet_name=sheet_name, index=False)

    def finish_processing(self):
        self.status_label.config(text="Processamento concluído.")
        self.process_button.config(state="normal")


def main():
    root = tk.Tk()
    app = MenuCapitalSix(root)
    root.mainloop()


if __name__ == "__main__":
    main()
