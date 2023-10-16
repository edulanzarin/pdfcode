import pandas as pd

def process_sicredi(dados_pdf, progress_bar, aplicar_substituicoes):
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
                descricao = " ".join(partes[1:-2])

                if "-" in partes[-2]:
                    pagamento = partes[-2]
                    valor = ""
                else:
                    pagamento = ""
                    valor = partes[-2]

                if aplicar_substituicoes:
                    valor, pagamento = substituir_lista([valor, pagamento])
                    valor, pagamento = substituir_virgula_por_ponto([valor, pagamento])

                pagamento = pagamento.replace("-", "")

                current_page += 1
                progress_value = (current_page / total_pages) * 100
                progress_bar["value"] = progress_value

                data_list.append(data)
                descricao_list.append(descricao)
                valor_list.append(valor)
                pagamento_list.append(pagamento)

        if not linhas_imprimir:
            break  # Parar de processar páginas subsequentes

    # Chamar a função `substituir_lista` antes de criar o DataFrame, se as substituições forem aplicadas
    if aplicar_substituicoes:
        valor_list = substituir_virgula_por_ponto(valor_list)
        pagamento_list = substituir_virgula_por_ponto(pagamento_list)


    # Criar um DataFrame com os dados
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

