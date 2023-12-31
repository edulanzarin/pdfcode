import pandas as pd
import re


def process_qualitplacas(dados_pdf, progress_bar, aplicar_substituicoes):
    registros_qualitplacas = []
    linhas_imprimir = False
    linha_anterior_valor_zero = False
    quebra_condicao = "QUALITPLACAS"

    total_pages = len(dados_pdf.pages)
    current_page = 0

    for pagina_num, pagina in enumerate(dados_pdf.pages, 1):
        texto_pagina = pagina.extract_text()
        linhas = texto_pagina.split("\n")
        quebra_pagina = False
        linhas_quebra = 0

        for linha in linhas:
            if quebra_condicao in linha:
                quebra_pagina = True
                linhas_quebra = 0

            if quebra_pagina and pagina_num == 1:  # Apenas para a primeira página
                linhas_quebra += 1
                if (
                    linhas_quebra >= 8
                    and "Histórico" not in linha
                    and "Complemento" not in linha
                ):
                    linhas_quebra = 0
                    linhas_imprimir = True
                    quebra_pagina = False

            if linhas_imprimir:
                if (
                    "Histórico" not in linha
                    and "Complemento" not in linha
                    and "Página:" not in linha
                ):
                    partes = linha.split()
                    if len(partes) > 2:
                        if "BANCO SAFRA MATRIZ" in linha or "9VIACREDI" in linha:
                            partes = [partes[0]] + partes[-3:] + partes
                            data = partes[0]
                            if (
                                "RECEITA DE REBATE" not in linha
                                and "DEVOLUÇÃO DE COMPRA" not in linha
                            ):
                                valor = partes[2]
                                credito = ""
                            else:
                                valor = partes[1]
                                credito = partes[1]

                            if (
                                valor != "0"
                                and valor != "0,00"
                                and valor != "0,0"
                                and "DESPESAS BANCARIA" not in linha
                                and "ALUGUEIS MAQUINA" not in linha
                            ):
                                if valor == credito:
                                    linha_anterior_valor_zero = False
                                    valor = ""
                                else:
                                    linha_anterior_valor_zero = False
                            else:
                                linha_anterior_valor_zero = True
                        else:
                            if linha_anterior_valor_zero:
                                linha_anterior_valor_zero = False
                            else:
                                if "REC.REF.DOC.:" in linha:
                                    partes[0] = partes[0].replace("REC.REF.DOC.:", "")
                                if "PAG.REF.DOC.:" in linha:
                                    partes[0] = partes[0].replace("PAG.REF.DOC.:", "")
                                if (
                                    "PAG.REF.DOC.:AGR" not in linha
                                    and "REC.REF.DOC.:AGR" not in linha
                                ):
                                    if "-" in partes[0]:
                                        partes[0] = partes[0].split("-", 1)[0].lstrip()
                                else:
                                    partes[0] = partes[0].replace(
                                        "PAG.REF.DOC.:AGR", ""
                                    )
                                    partes[0] = partes[0].replace(
                                        "REC.REF.DOC.:AGR", ""
                                    )
                                    if "-" in partes[0]:
                                        partes[0] = partes[0].split("-")[1]
                                    if "/" in partes[0]:
                                        partes[0] = partes[0].split("/")[1]
                                    if "-" in partes[0]:
                                        partes[0] = partes[0].split("-", 1)[1].lstrip()
                                if "SACADO" in linha:
                                    partes[1] = partes[1].replace("SACADO:", "")
                                if "DESC.TITULO" in linha:
                                    partes[0] = partes[0].replace("DESC.TITULO", "")
                                    if "-" in partes[1]:
                                        partes[1] = partes[1].split("-", 1)[0].lstrip()
                                    if "/" in partes[1]:
                                        partes[1] = partes[1].split("/", 1)[0].lstrip()
                                    fornecedor = "DESCONTO DO TITULO " + nota
                                else:
                                    if "-" in partes[1]:
                                        partes[1] = partes[1].split("-", 1)[1].lstrip()

                                if "PAG.REF.DOC.: " in linha:
                                    fornecedor = " ".join(partes[2::])
                                    nota = partes[1]
                                else:
                                    fornecedor = " ".join(partes[1:])
                                    nota = partes[0]

                                    nota = re.sub(r"[a-zA-Z]", "", nota)

                                    if aplicar_substituicoes:
                                        credito, valor = substituir_lista(
                                            [credito, valor]
                                        )
                                        credito, valor = substituir_virgula_por_ponto(
                                            [credito, valor]
                                        )

                                    current_page += 1
                                    progress_value = (current_page / total_pages) * 100
                                    progress_bar["value"] = progress_value

                                    registros_qualitplacas.append(
                                        {
                                            "DATA": data,
                                            "FORNECEDOR": fornecedor,
                                            "NOTA": nota,
                                            "VALOR": valor,
                                            "DESCONTO": credito,
                                        }
                                    )

    df = pd.DataFrame(registros_qualitplacas)
    progress_bar["value"] = 100

    df_styled = df.style.applymap(lambda x: "color: red", subset=["VALOR"])
    df_styled = df_styled.applymap(lambda x: "color: blue", subset=["DESCONTO"])

    return df_styled  # Certifique-se de que você está retornando o DataFrame aqui


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
