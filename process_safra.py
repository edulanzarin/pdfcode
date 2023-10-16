import pandas as pd
import re


# Função para processar uma página do PDF
def process_safra(dados_pdf, progress_bar, aplicar_substituicoes):
    data_list = []
    descricao_list = []
    valor_list = []
    pagamento_list = []

    total_pages = len(dados_pdf.pages)
    current_page = 0

    for pagina_num, pagina in enumerate(dados_pdf.pages):
        linhas = pagina.extract_text().split("\n")
        if pagina_num == 0:
            start_line = 8
        else:
            start_line = 2
        last_date = ""
        descricao_anterior = ""
        linhas_puladas = 0
        for i, linha in enumerate(linhas[start_line:]):
            if "Banco Safra S/A" in linha:
                linhas_puladas = 10
                continue
            if linhas_puladas > 0:
                linhas_puladas -= 1
                continue
            if "SALDO" not in linha:
                partes = linha.split()
                if len(partes) >= 3:
                    if "/" in partes[0]:
                        if any(char.isdigit() for char in partes[-1]):
                            if "-" in partes[-1]:
                                valor = ""
                                pagamento = partes[-1]
                            else:
                                valor = partes[-1]
                                pagamento = ""
                            # Usar uma expressão regular para remover letras da data
                            data = re.sub(r"[^0-9/]", "", partes[0])
                            descricao = " ".join(partes[1:-2])
                            last_date = data
                        else:
                            descricao_anterior = partes[1:-2]
                            continue
                    else:
                        if "-" in partes[-1]:
                            valor = ""
                            pagamento = partes[-1]
                        else:
                            valor = partes[-1]
                            pagamento = ""
                        descricao = (
                            " ".join(descricao_anterior) + " " + " ".join(partes[0:-2])
                        )
                        data = last_date

                    if aplicar_substituicoes:
                        valor, pagamento = substituir_lista([valor, pagamento])
                        valor, pagamento = substituir_virgula_por_ponto(
                            [valor, pagamento]
                        )

                    pagamento = pagamento.replace("-", "")

                    current_page += 1
                    progress_value = (current_page / total_pages) * 100
                    progress_bar["value"] = progress_value

                    data_list.append(data)
                    descricao_list.append(descricao)
                    valor_list.append(valor)
                    pagamento_list.append(pagamento)

    df = pd.DataFrame(
        {
            "DATA": data_list,
            "DESCRICAO": descricao_list,
            "RECEBIMENTO": valor_list,
            "PAGAMENTO": pagamento_list,
        }
    )
    progress_bar["value"] = 100

    return df


def substituir_lista(valores_ou_pagamentos):
    for i in range(len(valores_ou_pagamentos)):
        valor_ou_pagamento = valores_ou_pagamentos[i]
        # Remova apenas os pontos de milhar (substitua "." por uma string vazia)
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
