import PyPDF2
import tkinter as tk
from tkinter import filedialog
import pandas as pd

def select_pdf():
    root = tk.Tk()
    root.withdraw()  # Ocultar a janela principal
    file_path = filedialog.askopenfilename(filetypes=[("PDF files", "*.pdf")])
    return file_path

def process_francesinha_viacredi():
    file_path = select_pdf()

    if not file_path:
        print("Nenhum arquivo PDF selecionado.")
        return

    # Abrir o arquivo PDF selecionado
    with open(file_path, "rb") as pdf_file:
        dados_pdf = PyPDF2.PdfReader(pdf_file)
        linhas_imprimir = True  # Inicializado como True para imprimir a primeira página
        diferenca_list = []

        for pagina in dados_pdf.pages:  # Use dados_pdf.pages para acessar as páginas
            texto_pagina = pagina.extract_text()
            linhas = texto_pagina.split("\n")

            for linha in linhas:
                if "LIQUIDADO" not in linha:
                    linhas_imprimir = False
                else:
                    linhas_imprimir = True

                if "Valor Liquidado" not in linha and linhas_imprimir:
                    partes = linha.split()
                    if len(partes) > 10:
                        if partes[-1] != "0,00":
                            diferenca = partes[-1]  # Use [-1] para obter o último item

                            diferenca_list.append(diferenca)

    # Criar um DataFrame com os dados
    df = pd.DataFrame(
        {"DIFERENCA": diferenca_list}
    )

    # Solicitar o local para salvar o arquivo Excel
    save_path = filedialog.asksaveasfilename(
        defaultextension=".xlsx", filetypes=[("Excel files", "*.xlsx")]
    )
    if save_path:
        # Salvar o DataFrame como um arquivo Excel
        df.to_excel(save_path, index=False)
        print(f"Arquivo Excel salvo em: {save_path}")

if __name__ == "__main__":
    process_francesinha_viacredi()
