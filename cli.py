"""
Interface de Linha de Comando (CLI) para o sistema AVL-AuthStore.

Permite a interação completa com o UserDictionaryService:
- Cadastrar cliente (RF01)
- Autenticar cliente (RF02)
- Remover cliente (RF03)
- Atualizar cadastro (RF04)
- Listar clientes ordenados (RF05)
- Verificar fator de balanceamento e diagnósticos (RF06)
- Visualizar diagrama ASCII da Árvore AVL
"""

import sys
import argparse
from typing import Optional
from avl_authstore.service import UserDictionaryService
from avl_authstore.avl_tree import CPFDuplicadoError, CPFNotFoundError
from avl_authstore.utils import formatar_cpf, renderizar_arvore_ascii


def imprimir_cabecalho() -> None:
    print("=" * 70)
    print("       AVL-AuthStore: Sistema de Autenticação em Memória (AVL)       ")
    print("       Armazenamento O(log n) Estrito com Rebalanceamento Ativo      ")
    print("=" * 70)


def imprimir_menu() -> None:
    print("\n[MENU PRINCIPAL]")
    print("  1. Cadastrar Novo Cliente (RF01)")
    print("  2. Autenticar Cliente (RF02)")
    print("  3. Consultar Cliente por CPF")
    print("  4. Atualizar Dados Cadastrais (RF04)")
    print("  5. Remover Cliente (RF03)")
    print("  6. Listar Todos os Clientes em Ordem Crescente (RF05)")
    print("  7. Consultar Fator de Balanceamento (FB) de um Nó (RF06)")
    print("  8. Diagnóstico Estrutural e Visualizar Árvore AVL (ASCII)")
    print("  9. Popular Dados de Teste (Cenário de Demonstração)")
    print("  0. Sair")
    print("-" * 70)


def acao_cadastrar(service: UserDictionaryService) -> None:
    print("\n--- CADASTRO DE CLIENTE (RF01) ---")
    cpf = input("Digite o CPF (com ou sem pontuação): ").strip()
    nome = input("Digite o Nome Completo: ").strip()
    email = input("Digite o E-mail: ").strip()
    senha = input("Digite a Senha: ").strip()

    try:
        resultado = service.cadastrar_cliente(cpf=cpf, nome=nome, email=email, senha_pura=senha)
        print("\n[SUCESSO] Cliente cadastrado com êxito!")
        print(f"  CPF: {resultado['cpf_formatado']}")
        print(f"  Nome: {resultado['nome']}")
        print(f"  E-mail: {resultado['email']}")
        print(f"  Data Cadastro (UTC): {resultado['data_cadastro']}")
        print(f"  Total de Nós na AVL: {service.total_clientes} | Altura: {service.altura_arvore}")
    except CPFDuplicadoError as e:
        print(f"\n[ERRO DE DUPLICIDADE] {e}")
    except ValueError as e:
        print(f"\n[ERRO DE VALIDAÇÃO] {e}")


def acao_autenticar(service: UserDictionaryService) -> None:
    print("\n--- AUTENTICAÇÃO DE CLIENTE (RF02) ---")
    cpf = input("Digite o CPF do cliente: ").strip()
    senha = input("Digite a senha: ").strip()

    sucesso, mensagem, dados = service.autenticar_cliente(cpf=cpf, senha_pura=senha)
    if sucesso and dados is not None:
        print(f"\n[AUTENTICADO COM SUCESSO] {mensagem}")
        print(f"  Bem-vindo(a), {dados['nome']}!")
        print(f"  CPF: {dados['cpf_formatado']}")
        print(f"  E-mail: {dados['email']}")
        print(f"  Cadastrado em: {dados['data_cadastro']}")
    else:
        print(f"\n[FALHA NA AUTENTICAÇÃO] {mensagem}")


def acao_consultar(service: UserDictionaryService) -> None:
    print("\n--- CONSULTAR CLIENTE POR CPF ---")
    cpf = input("Digite o CPF: ").strip()
    cliente = service.obter_cliente(cpf)
    if cliente is not None:
        fb = service.obter_fator_balanceamento(cpf)
        print("\n[CLIENTE LOCALIZADO]")
        print(f"  CPF: {cliente['cpf_formatado']}")
        print(f"  Nome: {cliente['nome']}")
        print(f"  E-mail: {cliente['email']}")
        print(f"  Data Cadastro: {cliente['data_cadastro']}")
        print(f"  Fator de Balanceamento (FB) deste nó: {fb}")
    else:
        print(f"\n[NÃO ENCONTRADO] Nenhum cliente encontrado com o CPF informado.")


def acao_atualizar(service: UserDictionaryService) -> None:
    print("\n--- ATUALIZAR CADASTRO (RF04) ---")
    cpf = input("Digite o CPF do cliente a atualizar: ").strip()

    cliente_existente = service.obter_cliente(cpf)
    if cliente_existente is None:
        print(f"\n[NÃO ENCONTRADO] O CPF '{cpf}' não foi localizado.")
        return

    print(f"\nCliente Atual: {cliente_existente['nome']} ({cliente_existente['email']})")
    print("Deixe o campo em branco para manter o valor atual.")

    novo_nome = input(f"Novo nome [{cliente_existente['nome']}]: ").strip()
    novo_email = input(f"Novo e-mail [{cliente_existente['email']}]: ").strip()
    nova_senha = input("Nova senha (deixe vazio para não alterar): ").strip()

    try:
        atualizado = service.atualizar_cliente(
            cpf=cpf,
            nome=novo_nome if novo_nome else None,
            email=novo_email if novo_email else None,
            nova_senha_pura=nova_senha if nova_senha else None,
        )
        print("\n[SUCESSO] Dados cadastrais atualizados com sucesso!")
        print(f"  CPF (Imutável): {atualizado['cpf_formatado']}")
        print(f"  Nome: {atualizado['nome']}")
        print(f"  E-mail: {atualizado['email']}")
    except (CPFNotFoundError, ValueError) as e:
        print(f"\n[ERRO] {e}")


def acao_remover(service: UserDictionaryService) -> None:
    print("\n--- REMOVER CLIENTE (RF03) ---")
    cpf = input("Digite o CPF do cliente a remover: ").strip()
    confirmacao = input(f"Confirma a remoção do cliente com CPF {cpf}? (s/N): ").strip().lower()

    if confirmacao != "s":
        print("[CANCELADO] Operação cancelada pelo usuário.")
        return

    try:
        service.remover_cliente(cpf)
        print("\n[SUCESSO] Cliente removido do sistema com sucesso!")
        print(f"  A árvore foi rebalanceada automaticamente.")
        print(f"  Total de Nós restante: {service.total_clientes} | Nova Altura: {service.altura_arvore}")
    except CPFNotFoundError as e:
        print(f"\n[ERRO DE REMOÇÃO] {e}")


def acao_listar_ordenados(service: UserDictionaryService) -> None:
    print("\n--- LISTAGEM ORDENADA DE CLIENTES (RF05 - IN-ORDER) ---")
    clientes = service.listar_clientes_ordenados()

    if not clientes:
        print("[AVISO] Nenhum cliente cadastrado no momento.")
        return

    print(f"Total de registros encontrados: {len(clientes)}\n")
    print(f"{'CPF':<18} | {'NOME':<25} | {'E-MAIL':<30} | {'DATA CADASTRO (UTC)'}")
    print("-" * 95)
    for c in clientes:
        print(f"{c['cpf_formatado']:<18} | {c['nome']:<25} | {c['email']:<30} | {c['data_cadastro']}")
    print("-" * 95)


def acao_consultar_fb(service: UserDictionaryService) -> None:
    print("\n--- CONSULTAR FATOR DE BALANCEAMENTO (RF06) ---")
    cpf = input("Digite o CPF do nó a ser verificado: ").strip()
    try:
        fb = service.obter_fator_balanceamento(cpf)
        print(f"\n[FATOR DE BALANCEAMENTO] CPF: {formatar_cpf(cpf)}")
        print(f"  FB = {fb} (altura_esquerda - altura_direita)")
        if fb == 0:
            print("  Status: Subárvores perfeitamente simétricas em altura.")
        elif fb == 1:
            print("  Status: Levemente pesado à esquerda (dentro da invariante AVL).")
        elif fb == -1:
            print("  Status: Levemente pesado à direita (dentro da invariante AVL).")
        else:
            print(f"  Status: ATENÇÃO! Invariante violada (|FB| = {abs(fb)} > 1).")
    except CPFNotFoundError as e:
        print(f"\n[ERRO] {e}")


def acao_diagnostico_arvore(service: UserDictionaryService) -> None:
    print("\n--- DIAGNÓSTICO ESTRUTURAL E VISUALIZAÇÃO AVL ---")
    diag = service.diagnostico_arvore()
    print(f"  Total de Nós Ativos: {diag['total_nos']}")
    print(f"  Altura da Árvore: {diag['altura']}")
    print(f"  Invariante AVL (|FB| <= 1 em todos os nós): {'VÁLIDA ✓' if diag['invariante_valida'] else 'INVÁLIDA ✗'}")
    print(f"  Mensagem do Verificador: {diag['mensagem_diagnostico']}")

    print("\n[DIAGRAMA VISUAL DA ÁRVORE AVL]")
    if service.total_clientes == 0:
        print("  (Árvore vazia)")
    else:
        linhas = renderizar_arvore_ascii(service._tree.raiz)
        for linha in linhas:
            print(f"  {linha}")
        print("\nLegenda: [CPF] (h=Altura, FB=Fator de Balanceamento)")


def popular_dados_demonstracao(service: UserDictionaryService) -> None:
    print("\n--- CARREGANDO DADOS DE DEMONSTRAÇÃO ---")
    dados_exemplo = [
        ("50000000000", "Carlos Drummond", "carlos@authstore.io", "Senha@123"),
        ("20000000000", "Clarice Lispector", "clarice@authstore.io", "Senha@456"),
        ("70000000000", "Machado de Assis", "machado@authstore.io", "Senha@789"),
        ("10000000000", "Guimaraes Rosa", "guimaraes@authstore.io", "Senha@101"),
        ("30000000000", "Cecilia Meireles", "cecilia@authstore.io", "Senha@102"),
        ("60000000000", "Jorge Amado", "jorge@authstore.io", "Senha@103"),
        ("80000000000", "Graciliano Ramos", "graciliano@authstore.io", "Senha@104"),
    ]

    for cpf, nome, email, senha in dados_exemplo:
        try:
            service.cadastrar_cliente(cpf, nome, email, senha)
            print(f"  + Cadastrado: {formatar_cpf(cpf)} ({nome})")
        except CPFDuplicadoError:
            pass

    print("\n[SUCESSO] 7 clientes de teste inseridos!")
    print(f"Total de nós: {service.total_clientes} | Altura resultante: {service.altura_arvore}")


def iniciar_cli(service: Optional[UserDictionaryService] = None) -> None:
    """Loop principal interativo da interface de linha de comando."""
    if service is None:
        service = UserDictionaryService()

    imprimir_cabecalho()

    while True:
        try:
            imprimir_menu()
            opcao = input("Selecione uma opção (0-9): ").strip()

            if opcao == "1":
                acao_cadastrar(service)
            elif opcao == "2":
                acao_autenticar(service)
            elif opcao == "3":
                acao_consultar(service)
            elif opcao == "4":
                acao_atualizar(service)
            elif opcao == "5":
                acao_remover(service)
            elif opcao == "6":
                acao_listar_ordenados(service)
            elif opcao == "7":
                acao_consultar_fb(service)
            elif opcao == "8":
                acao_diagnostico_arvore(service)
            elif opcao == "9":
                popular_dados_demonstracao(service)
            elif opcao == "0":
                print("\nEncerrando AVL-AuthStore. Dados em memória liberados. Até logo!")
                break
            else:
                print("\n[OPÇÃO INVÁLIDA] Digite um número de 0 a 9.")
        except KeyboardInterrupt:
            print("\n\nExecução interrompida pelo usuário. Saindo...")
            break
        except Exception as e:
            print(f"\n[ERRO INESPERADO] {e}")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="AVL-AuthStore: Sistema de Cadastro e Autenticação em Árvore AVL"
    )
    parser.add_argument(
        "--demo",
        action="store_true",
        help="Inicia a aplicação populando dados de demonstração automaticamente",
    )
    args = parser.parse_args()

    service = UserDictionaryService()
    if args.demo:
        popular_dados_demonstracao(service)

    iniciar_cli(service)


if __name__ == "__main__":
    main()
