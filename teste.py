import pandas as pd
from tkinter import filedialog
import tkinter as tk
from tkinter import ttk


def open_file_and_modify_cells():
    # Abra a caixa de diálogo para escolher um arquivo de planilha
    file_path = filedialog.askopenfilename(
        filetypes=[("Planilhas Excel", "*.xlsx"), ("Planilhas CSV", "*.csv")]
    )

    if not file_path:
        return  # Se nenhum arquivo for selecionado, saia da função

    try:
        # Tente ler o arquivo usando pandas
        if file_path.endswith(".xlsx"):
            df = pd.read_excel(file_path, engine="openpyxl")
        elif file_path.endswith(".csv"):
            df = pd.read_csv(file_path)

        # Verifique se a planilha não está vazia
        if not df.empty:
            # Crie uma cópia do DataFrame original
            modified_df = df.copy()

            # Atualize a coluna "DEB" com 1496 onde a coluna "PAGAMENTO" é igual a 2
            modified_df.loc[modified_df["DESCRICAO"].str.contains("liquidacao boleto", case=False), "DEB"] = 1496

            # Abra a caixa de diálogo para escolher onde salvar o novo arquivo
            save_path = filedialog.asksaveasfilename(
                filetypes=[("Planilhas Excel", "*.xlsx"), ("Planilhas CSV", "*.csv")]
            )

            if save_path:
                # Certifique-se de que o arquivo seja salvo com a extensão .xlsx
                if not save_path.endswith(".xlsx"):
                    save_path += ".xlsx"

                # Salve as alterações no novo arquivo
                modified_df.to_excel(save_path, engine="openpyxl", index=False)
                print(
                    "As células foram modificadas com sucesso e o novo arquivo foi salvo como xlsx."
                )

        else:
            print("A planilha está vazia.")

    except Exception as e:
        print(f"Ocorreu um erro ao ler ou salvar o arquivo: {e}")


def main():
    root = tk.Tk()
    app = ttk.Frame(root)
    app.grid()
    open_button = ttk.Button(
        app,
        text="Escolher Planilha e Modificar Células",
        command=open_file_and_modify_cells,
    )
    open_button.pack(padx=10, pady=10)

    root.mainloop()


if __name__ == "__main__":
    main()
