import tkinter as tk
from tkinter import ttk
from ttkthemes import ThemedStyle

from MenuCapitalSix import MenuCapitalSix
from MenuLojao import MenuLojao
from MenuQualitplacas import MenuQualitplacas
from MenuBancos import MenuBancos


def main():
    root = tk.Tk()
    root.title("Menu Lateral")
    root.title("PDFCode")
    root.geometry("700x470")
    icon_path = r".\assets\minecraft.ico"
    root.iconbitmap(icon_path)
    style = ThemedStyle(root)
    style.set_theme("arc")

    tab_control = ttk.Notebook(root)
    tab_control.pack(expand=1, fill="both")

    # Guia para Lojão
    lojao_tab = ttk.Frame(tab_control)
    tab_control.add(lojao_tab, text="    Lojão    ")

    # Guia para Capital Six
    capital_six_tab = ttk.Frame(tab_control)
    tab_control.add(capital_six_tab, text="Capital Six")

    # Guia para Qualitplacas
    qualitplacas_tab = ttk.Frame(tab_control)
    tab_control.add(qualitplacas_tab, text="Qualitplacas")

    # Guia para Bancos
    bancos_tab = ttk.Frame(tab_control)
    tab_control.add(bancos_tab, text="   Bancos   ")

    app = MenuCapitalSix(capital_six_tab)
    app = MenuLojao(lojao_tab)
    app = MenuQualitplacas(qualitplacas_tab)
    app = MenuBancos(bancos_tab)

    root.mainloop()


if __name__ == "__main__":
    main()
