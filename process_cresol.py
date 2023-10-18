import re
import pandas as pd


def process_cresol(dados_pdf, progress_bar, aplicar_substituicoes):
    data_list = []
    descricao_list = []
    pagamento_list = []
    recebimento_list = []

    total_pages = len(dados_pdf.pages)
    current_page = 0
    stop_process = False

    for pagina_num, pagina in enumerate(dados_pdf.pages, 1):
        texto_pagina = pagina.extract_text()
        linhas = texto_pagina.split("\n")

        if pagina_num == 1:
            linhas_a_pular = 24
        else:
            linhas_a_pular = 6

        for linha_num, linha in enumerate(linhas, 1):
            partes = linha.split(" ")

            if "(=)" in linha or "(+)" in linha or "(-)" in linha:
                stop_process = True
                break

            if (
                len(partes) >= 5
                and "SALDO ANTERIOR" not in linha
                and "página" not in linha
            ):
                if linha_num <= linhas_a_pular:
                    continue

                valores_monetarios = re.findall(
                    r"\b\d{1,3}(?:\.\d{3})*(?:,\d{2})\b", linha
                )

                for valor in valores_monetarios:
                    linha = re.sub(r"\b\d{1,3}(?:\.\d{3})*(?:,\d{2})\b", "", linha)

                partes = linha.split(" ", 1)

                data = partes[0]
                descricao = partes[1]

                if " C " in descricao:
                    pagamento = ""
                    recebimento = valor
                elif " D " in descricao:
                    recebimento = ""
                    pagamento = valor
                else:
                    pagamento = ""
                    recebimento = ""

                if aplicar_substituicoes:
                    recebimento, pagamento = substituir_lista([recebimento, pagamento])
                    recebimento, pagamento = substituir_virgula_por_ponto(
                        [recebimento, pagamento]
                    )

                current_page += 1
                progress_value = (current_page / total_pages) * 100
                progress_bar["value"] = progress_value

                data_list.append(data)
                descricao_list.append(descricao)
                pagamento_list.append(pagamento)
                recebimento_list.append(recebimento)

            if stop_process:
                break

    df = pd.DataFrame(
        {
            "DATA": data_list,
            "DESCRICAO": descricao_list,
            "RECEBIMENTO": recebimento_list,
            "PAGAMENTO": pagamento_list,
        }
    )

    progress_bar["value"] = 100
    return df


def substituir_lista(valores_ou_pagamentos):
    for i in range(len(valores_ou_pagamentos)):
        valor_ou_pagamento = valores_ou_pagamentos[i]
        valor_ou_pagamento = valor_ou_pagamento.replace(".", "")
        valores_ou_pagamentos[i] = valor_ou_pagamento
    return valores_ou_pagamentos


def substituir_virgula_por_ponto(valores_ou_pagamentos):
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
    ]

    for i in range(len(valores_ou_pagamentos)):
        valor_ou_pagamento_sem = valores_ou_pagamentos[i]
        # Substitua a vírgula por ponto no formato decimal
        valor_ou_pagamento_sem = valor_ou_pagamento_sem.replace(",", ".")
        valor_ou_pagamento_sem = valor_ou_pagamento_sem.replace(".00", "")

        for substituicao in substituicoes:
            if valor_ou_pagamento_sem.endswith(substituicao):
                valor_ou_pagamento_sem = valor_ou_pagamento_sem[:-2] + substituicao[-2]
        valores_ou_pagamentos[i] = valor_ou_pagamento_sem
    return valores_ou_pagamentos
