import pandas as pd
import re
import datetime

def converter_data_americana_para_formato_desejado(data_americana):
    try:
        data_formato_americano = datetime.datetime.strptime(data_americana, "%m/%d/%Y")
        data_formato_desejado = data_formato_americano.strftime("%d/%m/%Y")
        return data_formato_desejado
    except ValueError:
        # Trate qualquer erro de formato de data aqui
        return data_americana  # Retorne a data original se houver erro

def process_safra_internacional(dados_pdf, progress_bar):
    data_list = []
    descricao_list = []
    valor_list = []
    pagamento_list = []

    total_pages = len(dados_pdf.pages)
    current_page = 0

    for pagina_num, pagina in enumerate(dados_pdf.pages):
        linhas = pagina.extract_text().split("\n")
        if pagina_num == 0:
            start_line = 6
        else:
            start_line = 0
        last_date = ""
        descricao_anterior = ""
        linhas_puladas = 0
        for i, linha in enumerate(linhas[start_line:]):
            if "Banco Safra S/A" in linha:
                linhas_puladas = 8
                continue
            if linhas_puladas > 0:
                linhas_puladas -= 1
                continue
            if "Account Balance" not in linha:
                partes = linha.split()
                if len(partes) >= 1:
                    if "/" in partes[0]:
                        if any(char.isdigit() for char in partes[-1]) and not any(char.isalpha() for char in partes[-1]):
                            if "-" in partes[-1]:
                                valor = ""
                                pagamento = partes[-1]
                            else:
                                valor = partes[-1]
                                pagamento = ""
                            data = re.sub(r"[^0-9/]", "", partes[0])
                            data = converter_data_americana_para_formato_desejado(data)  # Converter a data
                            descricao = " ".join(partes[1:-2])
                            last_date = data
                        else:
                            descricao_anterior = partes[1:-2]
                            continue
                    else:
                        if any(char.isdigit() for char in partes[-1]) and not any(char.isalpha() for char in partes[-1]):
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
                        else:
                            continue

                    valor = (
                        valor.replace("-", "")
                    )
                    pagamento = (
                        pagamento.replace("-", "")
                    )

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
