import pandas as pd


def process_francesinha_sicredi(dados_pdf, progress_bar):
    valor_list = []
    recebido_list = []
    diferenca_list = []

    total_pages = len(dados_pdf.pages)
    current_page = 0

    for pagina in dados_pdf.pages:
        texto_pagina = pagina.extract_text()
        linhas = texto_pagina.split("\n")
        linhas_imprimir = True

        for linha in linhas:
            if "LIQUIDADO" not in linha:
                linhas_imprimir = False
            else:
                linhas_imprimir = True

            if "Valor Liquidado" not in linha and linhas_imprimir:
                partes = linha.split()
                if len(partes) >= 6:
                    if partes[-2] == "LIQUIDADO":
                        valor_str = partes[-4]
                        recebido_str = partes[-3]
                        try:
                            valor = float(valor_str.replace(".", "").replace(",", "."))
                            recebido = float(
                                recebido_str.replace(".", "").replace(",", ".")
                            )
                            diferenca = recebido - valor
                        except ValueError:
                            valor = None
                            recebido = None
                            diferenca = None
                    else:
                        valor = None
                        recebido = None
                        diferenca = None

                    if diferenca != 0:
                        current_page += 1
                        progress_value = (current_page / total_pages) * 100
                        progress_bar["value"] = progress_value
                        
                        valor_list.append(valor)
                        recebido_list.append(recebido)
                        diferenca_list.append(diferenca)

    df = pd.DataFrame(
        {"VALOR": valor_list, "RECEBIDO": recebido_list, "DIFERENCA": diferenca_list}
    )

    # Certifique-se de que a barra de progresso esteja definida como 100% quando terminar
    progress_bar["value"] = 100

    return df
