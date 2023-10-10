import tkinter as tk
from tkinter import ttk, filedialog
from ttkthemes import ThemedStyle
import threading
import PyPDF2
import os
import datetime

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
        self.root.geometry("700x400")
        icon_path = r".\assets\icon.ico"
        self.root.iconbitmap(icon_path)

        self.file_path = None
        self.selected_empresa_var = tk.StringVar(self.root)
        self.selected_empresa_var.set("")

        self.selected_bank_var = tk.StringVar(self.root)
        self.selected_bank_var.set("")  # Valor inicial vazio para o banco

        self.progress_bar = ttk.Progressbar(self.root, mode="determinate")
        self.progress_bar.pack_forget()  # Oculta a barra de progresso inicialmente

        self.create_widgets()

    def create_widgets(self):
        style = ThemedStyle(self.root)
        style.set_theme(
            "arc"
        )  # Altere o tema para o tema "arc" para uma aparência mais moderna

        self.combobox_style = ttk.Style()
        self.combobox_style.configure(
            "Custom.TCombobox",
            font=("Arial", 12),
            padding=7,
            borderwidth=2,
            relief="solid",
        )

        empresas = list(empresa_bancos.keys())
        self.empresa_menu = ttk.Combobox(
            self.root,
            textvariable=self.selected_empresa_var,
            values=empresas,
            font=("Arial", 12),  # Aumente o tamanho da fonte
            style="Custom.TCombobox",
            state="readonly",
        )
        self.empresa_menu.pack(pady=40, padx=20, fill=tk.X)

        # Inicialize o menu suspenso do banco com a lista de bancos vazia
        self.bank_menu = ttk.Combobox(
            self.root,
            textvariable=self.selected_bank_var,
            values=[],
            font=("Arial", 12),  # Aumente o tamanho da fonte
            style="Custom.TCombobox",
            state="readonly",
        )
        self.bank_menu.pack(pady=20, padx=20, fill=tk.X)

        self.button_style = ttk.Style()
        self.button_style.configure("TButton", font=("Arial", 12))

        self.select_button = ttk.Button(
            self.root,
            text="Selecionar PDF",
            command=self.select_pdf,
            width=20,
            padding=10,
            style="TButton",
        )
        self.select_button.pack(pady=15)

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
            self.select_button.config(state="disabled")
            self.empresa_menu.config(state="disabled")
            self.bank_menu.config(state="disabled")
            return

        # Atualize a lista de bancos com base na empresa selecionada
        self.update_bank_menu()

    def update_bank_menu(self, *args):
        selected_empresa = self.selected_empresa_var.get()
        if selected_empresa in empresa_bancos:
            bancos = empresa_bancos[selected_empresa]
            self.bank_menu["values"] = bancos
            self.selected_bank_var.set(
                bancos[0]
            )  # Seleciona o primeiro banco como padrão
        else:
            self.bank_menu["values"] = []
            self.selected_bank_var.set("")

            # Adicione o rastreador de evento ao menu suspenso de empresas
            self.empresa_menu.bind("<<ComboboxSelected>>", self.update_bank_menu)

    def select_pdf(self):
        self.file_path = filedialog.askopenfilename(filetypes=[("PDF files", "*.pdf")])
        if self.file_path:
            file_name = os.path.basename(self.file_path)
            self.status_label.config(text=f"Arquivo Selecionado: {file_name}")
            self.process_button.config(state="normal")
            self.progress_bar.pack_forget()  # Oculta a barra de progresso
        else:
            self.status_label.config(text="Nenhum arquivo PDF selecionado.")
            self.process_button.config(state="disabled")

    def processar_pdf_thread(self):
        self.process_button.config(state="disabled")
        pdf_thread = threading.Thread(target=self.processar_pdf)
        pdf_thread.start()

    def processar_pdf(self):
        self.progress_bar.pack(
            pady=20, padx=20, fill=tk.X
        )  # Mostra a barra de progresso

        with open(self.file_path, "rb") as pdf_file:
            dados_pdf = PyPDF2.PdfReader(pdf_file)

            selected_empresa = self.selected_empresa_var.get()
            selected_bank = self.selected_bank_var.get()  # Obtém o banco selecionado

            if selected_bank == "Banco A":
                # Processar com base no banco A
                pass
            elif selected_bank == "Banco B":
                # Processar com base no banco B
                pass

            if (
                selected_empresa == "CAPITAL SIX"
                or selected_empresa == "EMPÓRIO ASTRAL"
            ):
                # Chame a função de processamento para a empresa Empório Astral
                df = process_capital_emporio(dados_pdf, self.progress_bar)

            elif (
                selected_empresa == "CENTRAL DE COMPRAS"
                or selected_empresa == "CH COMÉRCIO"
                or selected_empresa == "COMERCIAL MCD"
                or selected_empresa == "JGS COMÉRCIO"
                or selected_empresa == "LOJA ASTRAL"
                or selected_empresa == "SF COMÉRCIO"
            ):
                # Chame a função de processamento para a empresa Capital Six
                df = process_lojao(dados_pdf, self.progress_bar)

            elif selected_empresa == "QUALITPLACAS":
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
