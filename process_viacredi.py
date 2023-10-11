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


def process_viacredi(dados_pdf):
    data_list = []
    descricao_list = []
    valor_list = []

    linhas_imprimir = True  # Variável de controle para a primeira página

    for pagina_num, pagina in enumerate(dados_pdf.pages, 1):
        texto_pagina = pagina.extract_text()
        linhas = texto_pagina.split("\n")

        for linha_num, linha in enumerate(linhas, 1):
            partes = linha.split()
            if len(partes) > 5:
                if pagina_num == 1 and linha_num < 6:
                    continue  # Ignorar as cinco primeiras linhas da primeira página
                if "Saldo da conta" in linha:
                    linhas_imprimir = False
                    break  # Parar de processar quando encontrar "Saldo da conta"

                data = partes[0]
                valor = partes[-2]
                descricao = " ".join(partes[1:-3])

                data_list.append(data)
                descricao_list.append(descricao)
                valor_list.append(valor)

        if not linhas_imprimir:
            break  # Parar de processar páginas subsequentes

    # Criar um DataFrame com os dados
    df = pd.DataFrame(
        {
            "DATA": data_list,
            "DESCRICAO": descricao_list,
            "NOTA": "",
            "VALOR": valor_list,
        }
    )

    # Substituir "." por "" e "," por "." em VALOR
    df["VALOR"] = (
        df["VALOR"].str.replace(".", "").str.replace(",", ".").str.replace("-", "")
    )

    # Aplicar estilos ao DataFrame
    df_styled = df.style.applymap(paint_text_with_color, subset=["VALOR"])

    return df_styled
