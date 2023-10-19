import tkinter as tk
from tkinter import ttk
from ttkthemes import ThemedStyle
import datetime

from MenuCapitalSix import MenuCapitalSix
from MenuLojao import MenuLojao
from MenuQualitplacas import MenuQualitplacas
from MenuBancos import MenuBancos
from MenuEmporio import MenuEmporio
from StartMenu import StartMenu


def main():
    root = tk.Tk()
    root.title("Sigma")
    # root.geometry("700x470")
    root.state("zoomed")
    icon_path = r".\assets\icon.ico"
    root.iconbitmap(icon_path)
    style = ThemedStyle(root)
    style.set_theme("vista")

    tab_control = ttk.Notebook(root)
    tab_control.pack(expand=1, fill="both")

    # Guia para início
    start_tab = ttk.Frame(tab_control)
    tab_control.add(start_tab, text="   Início   ")

    # Guia para Bancos
    bancos_tab = ttk.Frame(tab_control)
    tab_control.add(bancos_tab, text="   Bancos   ")

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

    app = MenuLojao(lojao_tab)
    app = MenuEmporio(emporio_tab)
    app = MenuCapitalSix(capital_six_tab)
    app = MenuQualitplacas(qualitplacas_tab)
    app = MenuBancos(bancos_tab)
    start_menu = StartMenu(start_tab)
    app = start_menu

    check_validate(start_menu, tab_control)

    root.mainloop()


def check_validate(start_menu, tab_control):
    data_validade = datetime.date(2023, 12, 31)
    if data_validade < datetime.date.today():
        start_menu.set_status("Expirado")
        for tab_id in tab_control.tabs():
            if (
                tab_id != tab_control.tabs()[0]
            ):  # Não desabilite a guia "Início" (StartMenu)
                tab_control.tab(tab_id, state="disabled")


if __name__ == "__main__":
    main()
