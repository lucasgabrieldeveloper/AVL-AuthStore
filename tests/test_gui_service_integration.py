"""
Testes de integração para a interface services.user_service.UserDictionaryService.

Garante que todos os métodos esperados pela interface gráfica (GUI)
respondam conforme as regras de negócio e contratos de tipos.
"""

import pytest
from services.user_service import UserDictionaryService


class TestGuiServiceIntegration:

    @pytest.fixture
    def servico(self) -> UserDictionaryService:
        return UserDictionaryService()

    def test_cadastrar_cliente_contrato(self, servico: UserDictionaryService):
        """Valida que cadastrar_cliente retorna tuple(bool, str)."""
        sucesso, msg = servico.cadastrar_cliente(
            cpf="12345678900",
            nome="Aluno Teste",
            email="aluno@teste.com",
            senha="senhaSegura123",
        )
        assert sucesso is True
        assert isinstance(msg, str)
        assert servico.obter_total_clientes() == 1

        # Tentativa de duplicidade
        sucesso_dup, msg_dup = servico.cadastrar_cliente(
            cpf="123.456.789-00",
            nome="Aluno Duplicado",
            email="dup@teste.com",
            senha="senhaSegura123",
        )
        assert sucesso_dup is False
        assert "já" in msg_dup.lower()

    def test_autenticar_contrato(self, servico: UserDictionaryService):
        """Valida que autenticar retorna bool."""
        servico.cadastrar_cliente("11122233344", "Teste Auth", "auth@teste.com", "senha123")

        # Senha correta
        assert servico.autenticar("111.222.333-44", "senha123") is True
        # Senha incorreta
        assert servico.autenticar("111.222.333-44", "senhaErrada") is False
        # Usuário inexistente
        assert servico.autenticar("99999999999", "senha123") is False

    def test_atualizar_cadastro_contrato(self, servico: UserDictionaryService):
        """Valida que atualizar_cadastro retorna bool."""
        servico.cadastrar_cliente("22233344455", "Nome Original", "original@teste.com", "senha123")

        # Atualiza nome e email
        atualizou = servico.atualizar_cadastro(
            cpf="222.333.444-55",
            nome="Nome Atualizado",
            email="novo@teste.com",
            nova_senha="novaSenha456",
        )
        assert atualizou is True

        # Verifica dados atualizados
        dados = servico.obter_cliente("22233344455")
        assert dados is not None
        assert dados["nome"] == "Nome Atualizado"
        assert dados["email"] == "novo@teste.com"

        # Autentica com a nova senha
        assert servico.autenticar("22233344455", "novaSenha456") is True
        assert servico.autenticar("22233344455", "senha123") is False

    def test_remover_cliente_contrato(self, servico: UserDictionaryService):
        """Valida que remover_cliente retorna bool."""
        servico.cadastrar_cliente("33344455566", "Para Remover", "rem@teste.com", "senha123")
        assert servico.obter_total_clientes() == 1

        removido = servico.remover_cliente("333.444.555-66")
        assert removido is True
        assert servico.obter_total_clientes() == 0

        # Tenta remover novamente
        assert servico.remover_cliente("333.444.555-66") is False

    def test_listar_ordenado_e_metricas_contrato(self, servico: UserDictionaryService):
        """Valida listar_ordenado(), obter_altura_arvore() e obter_fator_balanceamento_raiz()."""
        cpfs = ["500", "200", "700", "100", "300", "600", "800"]
        for c in cpfs:
            servico.cadastrar_cliente(c, f"Nome {c}", f"email{c}@teste.com", "senha123")

        lista = servico.listar_ordenado()
        assert len(lista) == 7
        assert [item["cpf"] for item in lista] == ["100", "200", "300", "500", "600", "700", "800"]

        altura = servico.obter_altura_arvore()
        fb_raiz = servico.obter_fator_balanceamento_raiz()

        assert altura == 3
        assert fb_raiz == 0
