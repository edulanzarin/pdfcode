import pandas as pd
import re


def process_lojao(dados_pdf, progress_bar):
    registros_lojao = []
    linhas_quebra = 0
    contador_linhas = 0
    fornecedor_atual = None
    quebra_condicao = [
        "11-CENTRAL",
        "09-LOJÃO",
        "05-LOJÃO",
        "13-JGS",
        "01-LOJÃO",
        "03-LOJÃO",
    ]
    linhas_imprimir = False

    total_pages = len(dados_pdf.pages)
    current_page = 0

    for pagina_num, pagina in enumerate(dados_pdf.pages, 1):
        texto_pagina = pagina.extract_text()
        linhas = texto_pagina.split("\n")
        quebra_pagina = False  # Adicione essa linha para inicializar a variável

        for linha in linhas:
            if any(condicao in linha for condicao in quebra_condicao):
                quebra_pagina = True
                linhas_quebra = 0
                contador_linhas = 0

            if quebra_pagina:
                linhas_quebra += 1
                if linhas_quebra >= 4:
                    linhas_imprimir = True
                    quebra_pagina = False

            if (
                linhas_imprimir
                and contador_linhas >= 4
                and "Total da pessoa" not in linha
            ):
                if "Pessoa:" in linha:
                    if fornecedor_atual and pagamentos_fornecedor_atual:
                        registros_lojao.extend(pagamentos_fornecedor_atual)
                    match = re.search(r"Pessoa:\s+(\d+\s+)?(.+)", linha)
                    if match:
                        fornecedor_nome = match.group(2).strip()
                        fornecedor_atual = fornecedor_nome
                        pagamentos_fornecedor_atual = []
                elif fornecedor_atual:
                    partes = linha.split()
                    if len(partes) >= 11:
                        nota = (
                            partes[2]
                            if "NF" in partes[1] or "NF" in partes[1]
                            else partes[1]
                        )

                        if "/" in nota:
                            nota = nota.split("/")[0]
                        elif "." in nota:
                            nota = nota.split(".")[0]
                        elif "," in nota:
                            nota = nota.split(",")[0]

                        nota = re.sub(r"[a-zA-Z]", "", nota)
                        nota = nota.replace(":", "")

                        datas = re.findall(r"\d{2}/\d{2}/\d{4}", linha)
                        valores = re.findall(r"\d+(?:\.\d+,\d+|\.\d+,\d+|\,\d+)", linha)
                        # Realizar substituições em uma lista de valores
                        valores = [
                            valor.replace(".", "").replace(",", ".").replace(".00", "")
                            for valor in valores
                        ]
                        substituicoes = [
                            ".00",
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
                        if valores and len(valores) > 1:
                            for i in range(len(valores)):
                                valor = valores[i]
                                for substituicao in substituicoes:
                                    if valor.endswith(substituicao):
                                        valores[i] = valor[:-2] + substituicao[-2]
                        else:
                            valores = [""] * len(
                                valores
                            )  # Crie uma lista vazia com o mesmo comprimento

                        # Os valores resultantes estarão na lista 'valores'

                        current_page += 1
                        progress_value = (current_page / total_pages) * 100
                        progress_bar["value"] = progress_value

                        pagamentos_fornecedor_atual.append(
                            {
                                "DATA": datas[2] if datas and len(datas) > 2 else "",
                                "FORNECEDOR": fornecedor_atual,
                                "NOTA": nota,
                                "VALOR": (valores[1])
                                if valores and len(valores) > 1
                                else "",
                            }
                        )

            contador_linhas += 1

        if fornecedor_atual and pagamentos_fornecedor_atual:
            registros_lojao.extend(pagamentos_fornecedor_atual)

    df = pd.DataFrame(registros_lojao)
    progress_bar["value"] = 100
    df_styled = df.style.applymap(lambda x: "color: red", subset=["VALOR"])

    return df_styled  # Certifique-se de que você está retornando o DataFrame aqui