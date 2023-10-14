import PyPDF2
import pandas as pd
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill


def process_sicredi(dados_pdf, progress_bar):
    data_list = []
    descricao_list = []
    valor_list = []
    pagamento_list = []
    linhas_imprimir = True  # Variável de controle para a primeira página

    total_pages = len(dados_pdf.pages)
    current_page = 0

    for pagina_num, pagina in enumerate(dados_pdf.pages, 1):
        texto_pagina = pagina.extract_text()
        linhas = texto_pagina.split("\n")

        for linha_num, linha in enumerate(linhas, 1):
            partes = linha.split()
            if len(partes) >= 5:
                if pagina_num == 1 and linha_num < 6:
                    continue  # Ignorar as cinco primeiras linhas da primeira página
                if "Saldo da conta" in linha:
                    linhas_imprimir = False
                    break  # Parar de processar quando encontrar "Saldo da conta"

                data = partes[0]

                if "-" in partes[-2]:
                    pagamento = partes[-2]
                    valor = ""
                else:
                    pagamento = ""
                    valor = partes[-2]

                substituicoes = [
                    ".10",
                    ".20",
                    ".30",
                    ".40",
                    ".50",
                    ".60",
                    ".70",
                    ".80",
                    ".90",
                ]  # Adicione mais substituições se necessário

                valor = (
                    valor.replace(".", "")
                    .replace(",", ".")
                    .replace(".00", "")
                    .replace("-", "")
                )

                for substituicao in substituicoes:
                    if valor.endswith(substituicao):
                        valor = valor[:-2] + substituicao[-2]

                pagamento = (
                    pagamento.replace(".", "")
                    .replace(",", ".")
                    .replace(".00", "")
                    .replace("-", "")
                )

                for substituicao in substituicoes:
                    if pagamento.endswith(substituicao):
                        pagamento = pagamento[:-2] + substituicao[-2]

                descricao = " ".join(partes[1:-2])

                current_page += 1
                progress_value = (current_page / total_pages) * 100
                progress_bar["value"] = progress_value

                data_list.append(data)
                descricao_list.append(descricao)
                valor_list.append(valor)
                pagamento_list.append(pagamento)

        if not linhas_imprimir:
            break  # Parar de processar páginas subsequentes

    # Criar um DataFrame com os dados
    df = pd.DataFrame(
        {
            "DATA": data_list,
            "DESCRICAO": descricao_list,
            "VALOR": valor_list,
            "PAGAMENTO": pagamento_list,
        }
    )
    progress_bar["value"] = 100

    return df
