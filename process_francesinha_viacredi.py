import pandas as pd


def process_francesinha_viacredi(dados_pdf, progress_bar):
    linhas_imprimir = True  # Inicializado como True para imprimir a primeira página
    diferenca_list = []

    total_pages = len(dados_pdf.pages)
    current_page = 0

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

                        current_page += 1
                        progress_value = (current_page / total_pages) * 100
                        progress_bar["value"] = progress_value

                        diferenca_list.append(diferenca)

    # Criar um DataFrame com os dados
    df = pd.DataFrame({"DIFERENCA": diferenca_list})
    progress_bar["value"] = 100

    return df
