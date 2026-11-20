"""
Testes unitários específicos para validação das 4 Rotações Manuais da Árvore AVL:
1. Rotação Simples à Direita (LL)
2. Rotação Simples à Esquerda (RR)
3. Rotação Dupla à Direita (LR)
4. Rotação Dupla à Esquerda (RL)
"""

import pytest
from avl_authstore.models import ClientePayload, AVLNode
from avl_authstore.avl_tree import AVLTree


def criar_payload_teste(nome: str) -> ClientePayload:
    """Função auxiliar para instanciar payloads de teste."""
    return ClientePayload(
        nome=nome,
        email=f"{nome.lower().replace(' ', '')}@teste.com",
        senha_hash="hash_teste",
    )


class TestRotacoesAVL:
    """Validação detalhada das rotações manuais e do rebalanceamento imediato."""

    def test_rotacao_simples_direita_ll(self):
        """
        Cenário Caso LL: Inserção estritamente descendente (30 -> 20 -> 10).
        Sem rotação, a árvore desbalancearia para a esquerda:
               30 (FB = +2)
              /
             20 (FB = +1)
            /
           10 (FB = 0)

        A rotação LL deve transformar a estrutura em:
               20 (FB = 0, h = 2)
              /  \
            10    30 (ambos h = 1, FB = 0)
        """
        arvore = AVLTree()
        arvore.inserir("30", criar_payload_teste("Nó 30"))
        arvore.inserir("20", criar_payload_teste("Nó 20"))
        arvore.inserir("10", criar_payload_teste("Nó 10"))

        assert arvore.raiz is not None
        assert arvore.raiz.cpf == "20"
        assert arvore.raiz.esquerda is not None and arvore.raiz.esquerda.cpf == "10"
        assert arvore.raiz.direita is not None and arvore.raiz.direita.cpf == "30"

        # Validação de alturas
        assert arvore.raiz.altura == 2
        assert arvore.raiz.esquerda.altura == 1
        assert arvore.raiz.direita.altura == 1

        # Validação do Fator de Balanceamento FB = altura(esq) - altura(dir)
        assert arvore.obter_fb(arvore.raiz) == 0
        assert arvore.obter_fb(arvore.raiz.esquerda) == 0
        assert arvore.obter_fb(arvore.raiz.direita) == 0

        # Validação das invariantes gerais
        valida, msg = arvore.validar_invariantes()
        assert valida is True, msg

    def test_rotacao_simples_esquerda_rr(self):
        """
        Cenário Caso RR: Inserção estritamente ascendente (10 -> 20 -> 30).
        Sem rotação, a árvore desbalancearia para a direita:
           10 (FB = -2)
             \
              20 (FB = -1)
                \
                 30 (FB = 0)

        A rotação RR deve transformar a estrutura em:
               20 (FB = 0, h = 2)
              /  \
            10    30 (ambos h = 1, FB = 0)
        """
        arvore = AVLTree()
        arvore.inserir("10", criar_payload_teste("Nó 10"))
        arvore.inserir("20", criar_payload_teste("Nó 20"))
        arvore.inserir("30", criar_payload_teste("Nó 30"))

        assert arvore.raiz is not None
        assert arvore.raiz.cpf == "20"
        assert arvore.raiz.esquerda is not None and arvore.raiz.esquerda.cpf == "10"
        assert arvore.raiz.direita is not None and arvore.raiz.direita.cpf == "30"

        assert arvore.raiz.altura == 2
        assert arvore.raiz.esquerda.altura == 1
        assert arvore.raiz.direita.altura == 1

        assert arvore.obter_fb(arvore.raiz) == 0
        assert arvore.obter_fb(arvore.raiz.esquerda) == 0
        assert arvore.obter_fb(arvore.raiz.direita) == 0

        valida, msg = arvore.validar_invariantes()
        assert valida is True, msg

    def test_rotacao_dupla_direita_lr(self):
        """
        Cenário Caso LR: Inserção em formato ziguezague (30 -> 10 -> 20).
        Estrutura intermediária antes da rotação:
               30 (FB = +2)
              /
            10 (FB = -1)
              \
               20 (FB = 0)

        Requer Rotação Dupla LR:
        1. Rotação RR no filho esquerdo (10).
        2. Rotação LL no nó raiz (30).
        Resultado esperado:
               20 (FB = 0, h = 2)
              /  \
            10    30 (ambos h = 1, FB = 0)
        """
        arvore = AVLTree()
        arvore.inserir("30", criar_payload_teste("Nó 30"))
        arvore.inserir("10", criar_payload_teste("Nó 10"))
        arvore.inserir("20", criar_payload_teste("Nó 20"))

        assert arvore.raiz is not None
        assert arvore.raiz.cpf == "20"
        assert arvore.raiz.esquerda is not None and arvore.raiz.esquerda.cpf == "10"
        assert arvore.raiz.direita is not None and arvore.raiz.direita.cpf == "30"

        assert arvore.raiz.altura == 2
        assert arvore.obter_fb(arvore.raiz) == 0

        valida, msg = arvore.validar_invariantes()
        assert valida is True, msg

    def test_rotacao_dupla_esquerda_rl(self):
        """
        Cenário Caso RL: Inserção em formato ziguezague (10 -> 30 -> 20).
        Estrutura intermediária antes da rotação:
           10 (FB = -2)
             \
              30 (FB = +1)
             /
            20 (FB = 0)

        Requer Rotação Dupla RL:
        1. Rotação LL no filho direito (30).
        2. Rotação RR no nó raiz (10).
        Resultado esperado:
               20 (FB = 0, h = 2)
              /  \
            10    30 (ambos h = 1, FB = 0)
        """
        arvore = AVLTree()
        arvore.inserir("10", criar_payload_teste("Nó 10"))
        arvore.inserir("30", criar_payload_teste("Nó 30"))
        arvore.inserir("20", criar_payload_teste("Nó 20"))

        assert arvore.raiz is not None
        assert arvore.raiz.cpf == "20"
        assert arvore.raiz.esquerda is not None and arvore.raiz.esquerda.cpf == "10"
        assert arvore.raiz.direita is not None and arvore.raiz.direita.cpf == "30"

        assert arvore.raiz.altura == 2
        assert arvore.obter_fb(arvore.raiz) == 0

        valida, msg = arvore.validar_invariantes()
        assert valida is True, msg

    def test_chamada_direta_metodos_rotacao(self):
        """
        Testa explicitamente as chamadas diretas aos métodos:
        rotacaoLL, rotacaoRR, rotacaoLR, rotacaoRL.
        """
        arvore = AVLTree()

        # Montagem manual de desbalanceamento LL
        no30 = AVLNode("30", criar_payload_teste("30"))
        no20 = AVLNode("20", criar_payload_teste("20"))
        no10 = AVLNode("10", criar_payload_teste("10"))
        no30.esquerda = no20
        no20.esquerda = no10
        arvore._atualizar_altura(no10)
        arvore._atualizar_altura(no20)
        arvore._atualizar_altura(no30)

        nova_raiz = arvore.rotacaoLL(no30)
        assert nova_raiz.cpf == "20"
        assert nova_raiz.esquerda.cpf == "10"
        assert nova_raiz.direita.cpf == "30"
