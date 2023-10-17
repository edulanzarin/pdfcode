import tkinter as tk
from tkinter import ttk
from ttkthemes import ThemedStyle

from MenuCapitalSix import MenuCapitalSix
from MenuLojao import MenuLojao
from MenuQualitplacas import MenuQualitplacas
from MenuBancos import MenuBancos
from MenuEmporio import MenuEmporio
from StartMenu import StartMenu


def main():
    root = tk.Tk()
    root.title("Sigma")
    root.geometry("700x470")
    icon_path = r".\assets\icon.ico"
    root.iconbitmap(icon_path)
    style = ThemedStyle(root)
    style.set_theme("arc")

    tab_control = ttk.Notebook(root)
    tab_control.pack(expand=1, fill="both")

    # Guia para início
    start_tab = ttk.Frame(tab_control)
    tab_control.add(start_tab, text="   Início   ")

    # Guia para Lojão
    lojao_tab = ttk.Frame(tab_control)
    tab_control.add(lojao_tab, text="    Lojão    ")

    # Guia para Empório Astral
    emporio_tab = ttk.Frame(tab_control)
    tab_control.add(emporio_tab, text="Empório Astral")

    # Guia para Capital Six
    capital_six_tab = ttk.Frame(tab_control)
    tab_control.add(capital_six_tab, text="Capital Six")

    # Guia para Qualitplacas
    qualitplacas_tab = ttk.Frame(tab_control)
    tab_control.add(qualitplacas_tab, text="Qualitplacas")

    # Guia para Bancos
    bancos_tab = ttk.Frame(tab_control)
    tab_control.add(bancos_tab, text="   Bancos   ")

    app = MenuLojao(lojao_tab)
    app = MenuEmporio(emporio_tab)
    app = MenuCapitalSix(capital_six_tab)
    app = MenuQualitplacas(qualitplacas_tab)
    app = MenuBancos(bancos_tab)
    app = StartMenu(start_tab)

    root.mainloop()


if __name__ == "__main__":
    main()
