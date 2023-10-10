import PyPDF2
import tkinter as tk
from tkinter import filedialog
import pandas as pd
import re
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill


def paint_text_with_color(value):
    if "-" in value:
        return "color: red"
    else:
        return "color: blue"


def process_sicredi(dados_pdf):
    linhas_imprimir = True
    linhas_impressas = 0
    data_list = []
    descricao_list = []
    valor_list = []

    for pagina_num, pagina in enumerate(dados_pdf.pages, 1):
        linhas_quebra = 0

        if pagina_num == 1:
            texto_pagina = pagina.extract_text()
            linhas = texto_pagina.split("\n")

            for linha in linhas:
                if "Saldo da conta" in linha:
                    linhas_imprimir = False
                    break

                if linhas_imprimir and linhas_quebra >= 6:
                    partes = linha.split()
                    if len(partes) > 5:
                        data = partes[0]
                        valor = partes[-2]
                        descricao = " ".join(partes[1:-4])

                        data_list.append(data)
                        descricao_list.append(descricao)
                        valor_list.append(valor)

                linhas_impressas += 1
                linhas_quebra += 1

    # Criar um DataFrame com os dados
    df = pd.DataFrame(
        {"DATA": data_list, "DESCRICAO": descricao_list, "VALOR": valor_list}
    )

    # Substituir "." por "" e "," por "." em VALOR
    df["VALOR"] = df["VALOR"].str.replace(".", "").str.replace(",", ".")

    # Aplicar estilos ao DataFrame
    df_styled = df.style.applymap(paint_text_with_color, subset=["VALOR"])

    return df_styled


# Exemplo de uso
pdf_file_path = "seu_arquivo.pdf"
pdf_reader = PyPDF2.PdfFileReader(open(pdf_file_path, "rb"))

styled_df = process_sicredi(pdf_reader)

# Agora você pode usar styled_df em sua classe ou onde for necessário
