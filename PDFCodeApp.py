import tkinter as tk
from tkinter import ttk, filedialog
from ttkthemes import ThemedStyle
import threading
import PyPDF2
import os
import datetime
import pandas as pd

from process_capital_emporio import process_capital_emporio
from process_lojao import process_lojao
from process_qualitplacas import process_qualitplacas
from process_sicredi import process_sicredi

data_validade = datetime.datetime(2023, 12, 1)

# Dicionário que mapeia empresas para seus bancos correspondentes
empresa_bancos = {
    "CAPITAL SIX": ["SICREDI"],
    "EMPÓRIO ASTRAL": ["Banco X", "Banco Y", "Banco Z"],
    "QUALITPLACAS": ["Banco P", "Banco Q", "Banco R"],
    "CENTRAL DE COMPRAS": ["SICREDI"],
    "CH COMÉRCIO": ["SICREDI"]
    # Adicione outras empresas e bancos conforme necessário
}


class PDFCodeApp:
    def __init__(self, root):
        self.root = root
        self.root.title("PDFCode")
        self.root.geometry("700x520")
        icon_path = r".\assets\icon.ico"
        self.root.iconbitmap(icon_path)

        self.empresa_file_path = None
        self.bank_file_path = None
        self.empresa_df = None
        self.bank_df = None

        self.selected_empresa_var = tk.StringVar(self.root)
        self.selected_empresa_var.set("")

        self.selected_bank_var = tk.StringVar(self.root)
        self.selected_bank_var.set("")

        self.enable_bank_selection = (
            True  # Variável para habilitar/desabilitar seleção do banco
        )

        self.progress_bar = ttk.Progressbar(self.root, mode="determinate")
        self.progress_bar.pack_forget()

        self.process_bank_button_enabled = False

        self.create_widgets()

    def create_widgets(self):
        style = ThemedStyle(self.root)
        style.set_theme("arc")

        self.combobox_style = ttk.Style()
        self.combobox_style.configure(
            "Custom.TCombobox",
            font=("Arial", 12),
            padding=7,
            borderwidth=2,
            relief="solid",
        )

        empresas = list(empresa_bancos.keys())

        # Frame para as ComboBoxes de seleção
        combobox_frame = ttk.Frame(self.root)
        combobox_frame.pack(pady=20)

        self.empresa_menu = ttk.Combobox(
            combobox_frame,
            textvariable=self.selected_empresa_var,
            values=empresas,
            font=("Arial", 12),
            style="Custom.TCombobox",
            state="readonly",
        )
        self.empresa_menu.grid(row=0, column=0, padx=10)

        self.bank_menu = ttk.Combobox(
            combobox_frame,
            textvariable=self.selected_bank_var,
            values=[],
            font=("Arial", 12),
            style="Custom.TCombobox",
            state="readonly",
        )
        self.bank_menu.grid(row=0, column=1, padx=10)

        # Frame para os botões
        button_frame = ttk.Frame(self.root)
        button_frame.pack(pady=20)

        self.button_style = ttk.Style()
        self.button_style.configure("TButton", font=("Arial", 12))

        self.select_empresa_button = ttk.Button(
            button_frame,
            text="Relatório",
            command=self.select_empresa_pdf,
            width=25,
            padding=10,
            style="TButton",
        )
        self.select_empresa_button.grid(row=0, column=0, padx=5)

        self.select_bank_button = ttk.Button(
            button_frame,
            text="Extrato",
            command=self.select_bank_pdf,
            width=25,
            padding=10,
            style="TButton",
        )
        self.select_bank_button.grid(row=0, column=1, padx=5)

        self.process_button = ttk.Button(
            self.root,
            text="Processar PDF",
            command=self.processar_pdf_thread,
            width=20,
            padding=10,
            style="TButton",
        )
        self.process_button.pack(pady=15)
        self.process_button.config(state="disabled")

        self.status_label = ttk.Label(self.root, text="", font=("Arial", 12))
        self.status_label.pack(pady=10)

        if datetime.datetime.now() > data_validade:
            self.status_label = ttk.Label(self.root, text="Licença expirada.")
            self.status_label.pack(pady=10)
            self.process_button.config(state="disabled")
            self.select_empresa_button.config(state="disabled")
            self.select_bank_button.config(state="disabled")
            self.empresa_menu.config(state="disabled")
            self.bank_menu.config(state="disabled")
            return

        self.check_process_button_state()

        self.empresa_menu.bind("<<ComboboxSelected>>", self.update_bank_menu)

    def update_bank_menu(self, *args):
        selected_empresa = self.selected_empresa_var.get()
        if selected_empresa in empresa_bancos:
            bancos = empresa_bancos[selected_empresa]
            self.bank_menu["values"] = bancos
            self.selected_bank_var.set("")
            self.enable_bank_selection = True  # Habilitar seleção do banco
        else:
            self.bank_menu["values"] = []
            self.selected_bank_var.set("")
            self.enable_bank_selection = False  # Desabilitar seleção do banco

        if selected_empresa == "QUALITPLACAS":
            self.bank_menu.grid_forget()
            self.select_bank_button.grid_forget()
        else:
            self.bank_menu.grid(row=0, column=1, padx=10)
            self.select_bank_button.grid(row=0, column=2, padx=5)

        self.check_process_button_state()  # Verifique o estado do botão de processamento

    def select_empresa_pdf(self):
        self.empresa_file_path = filedialog.askopenfilename(
            filetypes=[("PDF files", "*.pdf")]
        )
        if self.empresa_file_path:
            file_name = os.path.basename(self.empresa_file_path)
            self.status_label.config(text=f"PDF da Empresa Selecionado: {file_name}")
            self.check_process_button_state()

    def select_bank_pdf(self):
        selected_bank = self.selected_bank_var.get()
        if selected_bank:
            self.bank_file_path = filedialog.askopenfilename(
                filetypes=[("PDF files", "*.pdf")]
            )
            if self.bank_file_path:
                file_name = os.path.basename(self.bank_file_path)
                self.status_label.config(text=f"PDF do Banco Selecionado: {file_name}")
                self.check_process_button_state()

    def check_process_button_state(self):
        selected_empresa = self.selected_empresa_var.get()
        selected_bank = self.selected_bank_var.get()

        if self.empresa_file_path and (
            (selected_bank and self.bank_file_path)
            or not self.process_bank_button_enabled
        ):
            self.process_button.config(state="normal")
        else:
            self.process_button.config(state="disabled")

    def processar_pdf_thread(self):
        self.process_button.config(state="disabled")
        pdf_thread = threading.Thread(target=self.processar_pdf)
        pdf_thread.start()

    def processar_pdf(self):
        self.progress_bar.pack(pady=20, padx=20, fill=tk.X)

        selected_empresa = self.selected_empresa_var.get()
        selected_bank = self.selected_bank_var.get()

        if self.empresa_file_path is None:
            self.status_label.config(text="Selecione o PDF da empresa primeiro.")
            self.progress_bar.pack_forget()
            return

        if selected_empresa == "QUALITPLACAS":
            # Se QUALITPLACAS for selecionada, não processar o PDF do banco
            self.bank_file_path = None

        with open(self.empresa_file_path, "rb") as empresa_pdf_file:
            dados_empresa_pdf = PyPDF2.PdfReader(empresa_pdf_file)

            self.empresa_df = None
            self.bank_df = None

            if (
                selected_empresa == "CAPITAL SIX"
                or selected_empresa == "EMPÓRIO ASTRAL"
            ):
                self.empresa_df = process_capital_emporio(
                    dados_empresa_pdf, self.progress_bar
                )

            elif (
                selected_empresa == "CENTRAL DE COMPRAS"
                or selected_empresa == "CH COMÉRCIO"
                or selected_empresa == "COMERCIAL MCD"
                or selected_empresa == "JGS COMÉRCIO"
                or selected_empresa == "LOJA ASTRAL"
                or selected_empresa == "SF COMÉRCIO"
            ):
                self.empresa_df = process_lojao(dados_empresa_pdf, self.progress_bar)

            elif selected_empresa == "QUALITPLACAS":
                self.empresa_df = process_qualitplacas(
                    dados_empresa_pdf, self.progress_bar
                )

            if selected_bank == "SICREDI" and self.bank_file_path:
                with open(self.bank_file_path, "rb") as bank_pdf_file:
                    dados_bank_pdf = PyPDF2.PdfReader(bank_pdf_file)
                    self.bank_df = process_sicredi(dados_bank_pdf)

            if self.empresa_df is not None:
                save_path = filedialog.asksaveasfilename(
                    defaultextension=".xlsx", filetypes=[("Excel files", "*.xlsx")]
                )
                if not save_path:
                    self.status_label.config(
                        text="Nenhum local de salvamento selecionado."
                    )
                    self.progress_bar.pack_forget()
                    return

                with pd.ExcelWriter(save_path, engine="xlsxwriter") as writer:
                    self.empresa_df.to_excel(
                        writer, sheet_name="Planilha1", index=False
                    )
                    if self.bank_df is not None:
                        self.bank_df.to_excel(
                            writer, sheet_name="Planilha2", index=False
                        )

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
