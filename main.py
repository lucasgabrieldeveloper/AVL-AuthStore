"""
AVL-AuthStore: Aplicação Desktop com Interface Gráfica Moderna (CustomTkinter).

Sistema de Cadastro e Autenticação de Clientes com Armazenamento em Memória
utilizando uma Árvore AVL balanceada estrita O(log n).

Para instalar as dependências necessárias da interface gráfica:
    pip install customtkinter CTkMessagebox
"""

import sys
import argparse
import customtkinter as ctk
from gui.app_window import AppWindow
from services.user_service import UserDictionaryService


def popular_dados_exemplo(servico: UserDictionaryService) -> None:
    """Insere clientes de exemplo na árvore AVL para fins de demonstração e testes."""
    clientes_demo = [
        ("50000000000", "Carlos Drummond de Andrade", "carlos@authstore.io", "Senha@123"),
        ("20000000000", "Clarice Lispector", "clarice@authstore.io", "Senha@456"),
        ("70000000000", "Machado de Assis", "machado@authstore.io", "Senha@789"),
        ("10000000000", "Guimarães Rosa", "guimaraes@authstore.io", "Senha@101"),
        ("30000000000", "Cecília Meireles", "cecilia@authstore.io", "Senha@102"),
        ("60000000000", "Jorge Amado", "jorge@authstore.io", "Senha@103"),
        ("80000000000", "Graciliano Ramos", "graciliano@authstore.io", "Senha@104"),
    ]
    for cpf, nome, email, senha in clientes_demo:
        servico.cadastrar_cliente(cpf=cpf, nome=nome, email=email, senha=senha)


def main() -> None:
    # 1. Configuração de Argumentos CLI
    parser = argparse.ArgumentParser(
        description="AVL-AuthStore GUI: Interface Gráfica Moderna em CustomTkinter"
    )
    parser.add_argument(
        "--demo",
        action="store_true",
        help="Inicia a aplicação já com 7 clientes cadastrados para testar o balanceamento da árvore",
    )
    args = parser.parse_args()

    # 2. Configurações Globais do CustomTkinter (Design System Dark Mode)
    ctk.set_appearance_mode("dark")
    ctk.set_default_color_theme("blue")

    # 3. Inicialização da Camada de Serviço (Model/Controller AVL em RAM)
    servico = UserDictionaryService()

    # Se a flag --demo for passada, pré-popula dados
    if args.demo:
        popular_dados_exemplo(servico)

    # 4. Inicialização da Janela Principal da Aplicação
    app = AppWindow(servico=servico)
    app.mainloop()


if __name__ == "__main__":
    main()
