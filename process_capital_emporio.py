import PyPDF2
import pandas as pd


def process_capital_emporio(dados_pdf, progress_bar):
    registros_capital_emporio = []

    total_pages = len(dados_pdf.pages)
    current_page = 0

    for pagina in dados_pdf.pages:
        texto_pagina = pagina.extract_text()
        linhas = texto_pagina.split("\n")
        # É o Padrão 2, processar 6 linhas após a quebra
        for linha in linhas[5:]:
            # linha = linha.replace("PAGAMENTO REALIZADO", "")

            partes = linha.split()
            if (
                len(partes) >= 5
                and "A VISTA" not in linha
                and "BOLETO 1" not in linha
                and "DESPESAS FIXAS" not in linha
                and "DESPESAS VARIAVEIS" not in linha
                and "ESCRITÓRIO DESPESAS" not in linha
                and "INVESTIMENTO" not in linha
                and "RETIRADA SOCIOS" not in linha
                and "SEM PORTADOR" not in linha
            ):
                numero_duplicata = partes[0]
                nome_empresa = " ".join(partes[1:-4] + ["NF" + numero_duplicata])
                data_vencimento = "N/A"
                valor = partes[-1]

                valor = valor.replace(".", "").replace(",", ".").replace(".00", "")
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
                for substituicao in substituicoes:
                    if valor.endswith(substituicao):
                        valor = valor[:-2] + substituicao[-2]

                current_page += 1
                progress_value = (current_page / total_pages) * 100
                progress_bar["value"] = progress_value

                registros_capital_emporio.append(
                    {
                        "DATA": data_vencimento,
                        "FORNECEDOR": nome_empresa,
                        "VALOR": valor,
                    }
                )

    df = pd.DataFrame(registros_capital_emporio)
    progress_bar["value"] = 100

    df_styled = df.style.applymap(lambda x: "color: red", subset=["VALOR"])

    return df_styled  # Certifique-se de que você está retornando o DataFrame aqui

    df_styled = process_capital_emporio(dados_pdf, self.progress_bar)

    # Retorne o DataFrame estilizado para a função main()
    return df_styled
