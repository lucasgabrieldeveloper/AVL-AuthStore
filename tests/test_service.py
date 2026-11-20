"""
Testes unitários e de integração para a camada de serviço: UserDictionaryService.

Valida os Requisitos Funcionais do Sistema:
- RF01 - Cadastrar Cliente
- RF02 - Autenticar Cliente
- RF03 - Remover Cliente
- RF04 - Atualizar Cadastro
- RF05 - Listar/Consultar Ordenada (In-Order)
- RF06 - Verificação de Balanceamento
- Concorrência Segura (Multithreading)
"""

import threading
import pytest
from avl_authstore.service import UserDictionaryService
from avl_authstore.avl_tree import CPFDuplicadoError, CPFNotFoundError


class TestUserDictionaryService:

    @pytest.fixture
    def service(self) -> UserDictionaryService:
        return UserDictionaryService()

    # -------------------------------------------------------------------------
    # RF01 - Cadastrar Cliente
    # -------------------------------------------------------------------------

    def test_rf01_cadastrar_cliente_com_sucesso(self, service: UserDictionaryService):
        """Valida cadastro bem-sucedido e sanitização automática de CPF."""
        res = service.cadastrar_cliente(
            cpf="111.222.333-44",
            nome="Clarice Lispector",
            email="clarice@authstore.io",
            senha_pura="SegredoForte@2026",
        )

        assert res["cpf"] == "11122233344"
        assert res["cpf_formatado"] == "111.222.333-44"
        assert res["nome"] == "Clarice Lispector"
        assert res["email"] == "clarice@authstore.io"
        assert "senha_pura" not in res
        assert service.total_clientes == 1
        assert service.altura_arvore == 1

    def test_rf01_rejeitar_cpf_duplicado(self, service: UserDictionaryService):
        """Impede que o mesmo CPF seja cadastrado duas vezes."""
        service.cadastrar_cliente("11122233344", "Usuario 1", "u1@auth.io", "senha1")

        with pytest.raises(CPFDuplicadoError):
            service.cadastrar_cliente("111.222.333-44", "Usuario Duplicado", "dup@auth.io", "senha2")

        assert service.total_clientes == 1

    def test_rf01_validacao_campos_obrigatorios(self, service: UserDictionaryService):
        """Rejeita entradas com e-mail inválido, senha curta ou campos vazios."""
        with pytest.raises(ValueError):
            service.cadastrar_cliente("", "Nome", "email@valido.com", "senha123")

        with pytest.raises(ValueError):
            service.cadastrar_cliente("11122233344", "", "email@valido.com", "senha123")

        with pytest.raises(ValueError):
            service.cadastrar_cliente("11122233344", "Nome", "email-invalido", "senha123")

        with pytest.raises(ValueError):
            service.cadastrar_cliente("11122233344", "Nome", "email@valido.com", "12")

    # -------------------------------------------------------------------------
    # RF02 - Autenticar Cliente
    # -------------------------------------------------------------------------

    def test_rf02_autenticacao_sucesso_e_falha(self, service: UserDictionaryService):
        """Valida autenticação com senha correta, senha incorreta e usuário inexistente."""
        cpf = "123.456.789-00"
        senha = "SenhaSuperSecreta@123"
        service.cadastrar_cliente(cpf, "Machado de Assis", "machado@authstore.io", senha)

        # 1. Autenticação com credencial correta
        sucesso, msg, dados = service.autenticar_cliente(cpf, senha)
        assert sucesso is True
        assert dados is not None
        assert dados["nome"] == "Machado de Assis"
        assert "sucesso" in msg.lower()

        # 2. Autenticação com senha incorreta
        sucesso_erro, msg_erro, dados_erro = service.autenticar_cliente(cpf, "SenhaErrada")
        assert sucesso_erro is False
        assert dados_erro is None
        assert "incorreta" in msg_erro.lower()

        # 3. Autenticação de CPF inexistente
        sucesso_inex, msg_inex, _ = service.autenticar_cliente("99999999999", senha)
        assert sucesso_inex is False
        assert "não cadastrado" in msg_inex.lower()

    # -------------------------------------------------------------------------
    # RF03 - Remover Cliente
    # -------------------------------------------------------------------------

    def test_rf03_remover_cliente(self, service: UserDictionaryService):
        """Remove cliente e garante que ele não pode mais ser autenticado nem encontrado."""
        cpf = "222.333.444-55"
        service.cadastrar_cliente(cpf, "Carlos Drummond", "carlos@auth.io", "minhasenha")

        assert service.total_clientes == 1
        removido = service.remover_cliente(cpf)
        assert removido is True
        assert service.total_clientes == 0

        # Não é mais possível autenticar
        sucesso, _, _ = service.autenticar_cliente(cpf, "minhasenha")
        assert sucesso is False

        # Remover novamente deve levantar exceção
        with pytest.raises(CPFNotFoundError):
            service.remover_cliente(cpf)

    # -------------------------------------------------------------------------
    # RF04 - Atualizar Cadastro
    # -------------------------------------------------------------------------

    def test_rf04_atualizar_cadastro(self, service: UserDictionaryService):
        """Atualiza nome, e-mail e senha, garantindo a imutabilidade do CPF."""
        cpf = "333.444.555-66"
        service.cadastrar_cliente(cpf, "Nome Antigo", "antigo@auth.io", "senhaAntiga")

        atualizado = service.atualizar_cliente(
            cpf=cpf,
            nome="Nome Novo",
            email="novo@auth.io",
            nova_senha_pura="senhaNova123",
        )

        assert atualizado["nome"] == "Nome Novo"
        assert atualizado["email"] == "novo@auth.io"

        # A senha antiga não deve mais autenticar
        sucesso_antiga, _, _ = service.autenticar_cliente(cpf, "senhaAntiga")
        assert sucesso_antiga is False

        # A nova senha deve autenticar perfeitamente
        sucesso_nova, _, dados = service.autenticar_cliente(cpf, "senhaNova123")
        assert sucesso_nova is True
        assert dados["nome"] == "Nome Novo"

    # -------------------------------------------------------------------------
    # RF05 - Listar/Consultar Ordenada (In-Order)
    # -------------------------------------------------------------------------

    def test_rf05_listar_clientes_ordenados(self, service: UserDictionaryService):
        """Garante que a listagem In-Order retorna os CPFs em ordem estritamente crescente."""
        cpfs_desordenados = [
            ("50000000000", "E"),
            ("20000000000", "B"),
            ("70000000000", "G"),
            ("10000000000", "A"),
            ("30000000000", "C"),
            ("60000000000", "F"),
            ("40000000000", "D"),
        ]

        for cpf, nome in cpfs_desordenados:
            service.cadastrar_cliente(cpf, nome, f"{nome.lower()}@auth.io", "senha123")

        lista = service.listar_clientes_ordenados()
        cpfs_retornados = [item["cpf"] for item in lista]

        assert cpfs_retornados == sorted(cpfs_retornados)
        assert [item["nome"] for item in lista] == ["A", "B", "C", "D", "E", "F", "G"]

    # -------------------------------------------------------------------------
    # RF06 - Verificação de Balanceamento
    # -------------------------------------------------------------------------

    def test_rf06_verificacao_fator_balanceamento(self, service: UserDictionaryService):
        """Verifica o FB de um nó específico da árvore."""
        # Inserção que forma uma raiz com dois filhos simétricos
        service.cadastrar_cliente("200", "Raiz", "raiz@auth.io", "senha123")
        service.cadastrar_cliente("100", "Esq", "esq@auth.io", "senha123")
        service.cadastrar_cliente("300", "Dir", "dir@auth.io", "senha123")

        fb_raiz = service.obter_fator_balanceamento("200")
        fb_esq = service.obter_fator_balanceamento("100")
        fb_dir = service.obter_fator_balanceamento("300")

        assert fb_raiz == 0
        assert fb_esq == 0
        assert fb_dir == 0

        with pytest.raises(CPFNotFoundError):
            service.obter_fator_balanceamento("999999999")

    # -------------------------------------------------------------------------
    # Concorrência Multithread
    # -------------------------------------------------------------------------

    def test_alta_concorrencia_thread_safety(self, service: UserDictionaryService):
        """
        Executa 50 threads concorrentes de cadastro e consulta simultânea
        para provar thread-safety e ausência de condições de corrida (Race Conditions).
        """
        num_threads = 50
        erros = []

        def worker(indice: int):
            cpf = f"{indice:011d}"
            try:
                service.cadastrar_cliente(
                    cpf=cpf,
                    nome=f"Usuario Concorrente {indice}",
                    email=f"user{indice}@concorrente.io",
                    senha_pura=f"Senha@{indice}",
                )
                sucesso, _, _ = service.autenticar_cliente(cpf, f"Senha@{indice}")
                if not sucesso:
                    erros.append(f"Falha ao autenticar usuario {indice}")
            except Exception as e:
                erros.append(str(e))

        threads = [threading.Thread(target=worker, args=(i,)) for i in range(1, num_threads + 1)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        assert len(erros) == 0, f"Erros durante concorrência: {erros}"
        assert service.total_clientes == num_threads

        # A árvore deve permanecer perfeitamente balanceada
        diag = service.diagnostico_arvore()
        assert diag["invariante_valida"] is True
