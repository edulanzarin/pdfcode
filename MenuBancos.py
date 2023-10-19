import tkinter as tk
from tkinter import ttk, filedialog
from ttkthemes import ThemedStyle
import PyPDF2
import os
import pandas as pd
from tkinter.ttk import Treeview
import threading
import itertools
from process_sicredi import process_sicredi
from process_safra import process_safra
from process_safra_internacional import process_safra_internacional
from process_viacredi import process_viacredi
from process_cresol import process_cresol

bancos = ["Viacredi", "Sicredi", "Cresol", "Safra", "Safra Internacional"]


class MenuBancos:
    def __init__(self, root):
        self.root = root
        self.empresa_file_path = None
        self.empresa_df = None
        self.processing_status = "idle"  # Variável de controle de status
        self.progress_bar = ttk.Progressbar(
            self.root, mode="determinate", length=800, maximum=100
        )
        self.progress_bar.pack_forget()
        self.process_button_enabled = False
        self.selected_empresa_var = tk.StringVar(self.root)
        self.selected_empresa_var.set("")
        self.aplicar_substituicoes = tk.BooleanVar()
        self.aplicar_substituicoes.set(False)
        self.row_colors = itertools.cycle(
            ["white", "lightgray"]
        )  # Alternating row colors
        self.rows = []

        style = ThemedStyle(self.root)
        style.set_theme("vista")
        style.configure("Treeview", rowheight=16, fieldbackground="lightgray")

        self.create_widgets()

    def update_treeview(self, df):
        if not df.empty:
            self.treeview.delete(*self.treeview.get_children())
            for i, row in enumerate(df.itertuples(index=False)):
                bg_color = next(self.row_colors)
                self.treeview.insert("", "end", values=row, tags=(i, bg_color))
                self.rows.append(i)
                self.treeview.tag_configure(i, background=bg_color)
            total_width = self.treeview.winfo_width()

            # Define a largura percentual de cada coluna
            column_widths = {
                "DATA": total_width * 0.08,
                "DESCRICAO": total_width * 0.76,
                "RECEBIMENTO": total_width * 0.08,
                "PAGAMENTO": total_width * 0.08,
            }

            # Configure as colunas no Treeview
            for column, width in column_widths.items():
                self.treeview.column(
                    column, width=int(width), anchor="w"
                )  # Define a âncora "w" para alinhar à esquerda

            # Configure os cabeçalhos das colunas
            for column in column_widths.keys():
                self.treeview.heading(
                    column, text=column, anchor="w"
                )  # Define a âncora "w" para alinhar à esquerda

    def create_widgets(self):
        self.title_label = ttk.Label(
            self.root, text="Processar Bancos", font=("Arial", 10)
        )
        self.title_label.pack(pady=5)

        button_frame = ttk.Frame(self.root)
        button_frame.pack(pady=5)

        self.start_label = ttk.Label(
            button_frame, text="Escolher Banco", font=("Arial", 8)
        )
        self.start_label.pack(side="left", padx=5)

        combobox_frame = ttk.Frame(button_frame)
        combobox_frame.pack(side="left")

        self.empresa_menu = ttk.Combobox(
            combobox_frame,
            textvariable=self.selected_empresa_var,
            values=bancos,
            font=("Arial", 8),
            style="Custom.TCombobox",
            state="readonly",
            width=30,
        )
        self.empresa_menu.pack(side="left")

        select_frame = ttk.Frame(self.root)
        select_frame.pack(pady=5)

        self.select_empresa_button = ttk.Button(
            select_frame,
            text="Selecionar",
            command=self.select_empresa_pdf,
            width=15,
            style="Small.TButton",
        )
        self.select_empresa_button.pack(side="left")

        self.process_button = ttk.Button(
            select_frame,
            text="Processar",
            command=self.processar_pdf_thread,
            width=15,
        )
        self.process_button.pack(side="left")

        self.salvar_button = ttk.Button(
            select_frame,
            text="Salvar",
            command=self.salvar_para_excel,
            width=15,
            state="disabled",
        )
        self.salvar_button.pack(side="left")

        self.toggle_substituicoes_button = ttk.Checkbutton(
            self.root,
            text="Remover vírgulas",
            variable=self.aplicar_substituicoes,
        )
        self.toggle_substituicoes_button.pack()

        self.empresa_menu.bind("<<ComboboxSelected>>", self.check_remover_virgulas)

        status_frame = ttk.Frame(self.root)
        status_frame.pack()

        self.status_label = ttk.Label(status_frame, text="", font=("Arial", 10))
        self.status_label.pack(pady=5)

        treeview_frame = ttk.Frame(self.root)
        treeview_frame.pack(fill="x", expand=True)

        self.treeview = Treeview(
            treeview_frame,
            columns=["DATA", "DESCRICAO", "RECEBIMENTO", "PAGAMENTO"],
            show="headings",
            height=28,
        )
        self.treeview.pack(side="left", fill="x", expand=True)

        # Crie uma barra de rolagem vertical
        self.scrollbar = ttk.Scrollbar(
            treeview_frame, orient="vertical", command=self.treeview.yview
        )
        self.treeview.configure(yscrollcommand=self.scrollbar.set)

        self.scrollbar.pack(side="right", fill="y")

        self.progress_frame = ttk.Frame(self.root)
        self.progress_frame.pack(pady=11)

        self.check_process_button_state()

    def select_empresa_pdf(self):
        self.empresa_file_path = filedialog.askopenfilename(
            filetypes=[("PDF files", "*.pdf")]
        )
        if self.empresa_file_path:
            file_name = os.path.basename(self.empresa_file_path)
            self.status_label.config(text=f"Extrato: {file_name}")
            self.check_process_button_state()  # Verifica o estado do botão Processar
            self.process_button.config(state="normal")

    def check_process_button_state(self):
        if self.empresa_file_path and self.processing_status == "idle":
            self.process_button.config(state="normal")
        else:
            self.process_button.config(state="disabled")

    def check_remover_virgulas(self, event=None):
        if self.selected_empresa_var.get() == "Safra Internacional":
            self.toggle_substituicoes_button.config(state="disabled")
        else:
            self.toggle_substituicoes_button.config(state="normal")

    def processar_pdf_thread(self):
        self.process_button.config(state="disabled")
        self.processing_status = "in_progress"
        pdf_thread = threading.Thread(target=self.processar_pdf)
        pdf_thread.start()

    def processar_pdf(self):
        self.progress_frame.pack_forget()
        self.progress_bar.pack()

        banco_selecionado = self.selected_empresa_var.get()
        if self.empresa_file_path:
            with open(self.empresa_file_path, "rb") as empresa_pdf_file:
                dados_empresa_pdf = PyPDF2.PdfReader(empresa_pdf_file)

                # Passe o valor de aplicar_substituicoes para o processamento do banco
                if banco_selecionado == "Sicredi":
                    self.empresa_df = process_sicredi(
                        dados_empresa_pdf,
                        self.progress_bar,
                        self.aplicar_substituicoes.get(),
                    )

                if banco_selecionado == "Safra":
                    self.empresa_df = process_safra(
                        dados_empresa_pdf,
                        self.progress_bar,
                        self.aplicar_substituicoes.get(),
                    )

                if banco_selecionado == "Safra Internacional":
                    self.empresa_df = process_safra_internacional(
                        dados_empresa_pdf, self.progress_bar
                    )

                if banco_selecionado == "Viacredi":
                    self.empresa_df = process_viacredi(
                        dados_empresa_pdf,
                        self.progress_bar,
                        self.aplicar_substituicoes.get(),
                    )

                if banco_selecionado == "Cresol":
                    self.empresa_df = process_cresol(
                        dados_empresa_pdf,
                        self.progress_bar,
                        self.aplicar_substituicoes.get(),
                    )

        self.update_treeview(self.empresa_df)
        self.progress_bar.pack_forget()
        self.progress_frame.pack(pady=11)
        self.processing_status = "completed"
        self.check_process_button_state()
        self.check_save_button_state()  # Atualize o botão Salvar

    def check_save_button_state(self):
        if self.empresa_df is not None and self.processing_status == "completed":
            self.salvar_button.config(state="normal")
        else:
            self.salvar_button.config(state="disabled")

    def salvar_para_excel(self):
        if self.empresa_df is not None:
            save_path = filedialog.asksaveasfilename(
                defaultextension=".xlsx", filetypes=[("Excel files", "*.xlsx")]
            )
            if not save_path:
                self.status_label.config(text="Nenhum local de salvamento selecionado.")
                return

            with pd.ExcelWriter(save_path, engine="xlsxwriter") as writer:
                self.empresa_df.to_excel(writer, sheet_name="Planilha1", index=False)

        self.status_label.config(text="Salvo para Excel.")
        self.salvar_button.config(state="disabled")  # Desabilite o botão novamente


def main():
    root = tk.Tk()
    app = MenuBancos(root)
    root.mainloop()


if __name__ == "__main__":
    main()
