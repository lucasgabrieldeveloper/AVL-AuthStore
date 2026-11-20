"""
Testes unitários para validação de Remoção em Árvore AVL.

Cobre detalhadamente os 3 casos canônicos de BST com rebalanceamento ascendente:
- Caso 1: Nó folha (sem filhos).
- Caso 2: Nó com apenas um filho (esquerdo ou direito).
- Caso 3: Nó com dois filhos (substituição por Sucessor In-Order).
- Rebalanceamento por rotação disparado após remoção.
- Esvaziamento completo da árvore.
"""

import random
import pytest
from avl_authstore.models import ClientePayload
from avl_authstore.avl_tree import AVLTree, CPFNotFoundError


def payload(chave: str) -> ClientePayload:
    return ClientePayload(
        nome=f"Nome {chave}",
        email=f"{chave}@teste.com",
        senha_hash=f"hash_{chave}",
    )


class TestRemocaoAVL:

    def test_caso_1_remocao_folha(self):
        """
        Caso 1: Remoção de um nó sem filhos (folha).
        Árvore inicial:
               20
              /  \
            10    30
        Remove 10 (folha). A árvore deve permanecer com 20 na raiz e 30 à direita.
        """
        arvore = AVLTree()
        arvore.inserir("20", payload("20"))
        arvore.inserir("10", payload("10"))
        arvore.inserir("30", payload("30"))

        sucesso = arvore.remover("10")
        assert sucesso is True
        assert arvore.total_nodes == 2
        assert arvore.buscar("10") is None
        assert arvore.raiz.esquerda is None
        assert arvore.raiz.direita.cpf == "30"

        valida, msg = arvore.validar_invariantes()
        assert valida is True, msg

    def test_caso_2_remocao_no_com_um_filho(self):
        """
        Caso 2: Remoção de nó com apenas um filho.
        Cria árvore com nó que possui apenas filho direito ou apenas esquerdo.
        """
        arvore = AVLTree()
        # Inserção de sequência balanceada
        arvore.inserir("50", payload("50"))
        arvore.inserir("30", payload("30"))
        arvore.inserir("70", payload("70"))
        arvore.inserir("20", payload("20"))  # Filho esquerdo de 30

        # O nó 30 possui apenas filho esquerdo (20)
        assert arvore.raiz.esquerda.cpf == "30"
        assert arvore.raiz.esquerda.esquerda.cpf == "20"
        assert arvore.raiz.esquerda.direita is None

        # Remove 30
        arvore.remover("30")
        assert arvore.total_nodes == 3
        assert arvore.buscar("30") is None
        # O filho 20 deve ter assumido o lugar de 30
        assert arvore.raiz.esquerda.cpf == "20"

        valida, msg = arvore.validar_invariantes()
        assert valida is True, msg

    def test_caso_3_remocao_no_com_dois_filhos_sucessor_in_order(self):
        """
        Caso 3: Remoção de nó com dois filhos.
        O nó deve ser substituído pelo seu Sucessor In-Order (o menor valor da subárvore direita).
        """
        arvore = AVLTree()
        # Árvore balanceada com raiz 50
        elementos = ["50", "20", "80", "10", "30", "70", "90", "60", "75"]
        for elem in elementos:
            arvore.inserir(elem, payload(elem))

        # O nó 80 possui dois filhos: subárvore esquerda (raiz 70) e direita (90).
        # O sucessor in-order de 80 é o menor nó da subárvore direita de 80, que é 90.
        # Vamos remover o próprio nó 80
        arvore.remover("80")

        assert arvore.buscar("80") is None
        assert arvore.total_nodes == len(elementos) - 1

        # A árvore deve continuar estritamente ordenada e balanceada
        valida, msg = arvore.validar_invariantes()
        assert valida is True, msg

        # Todos os outros elementos devem continuar acessíveis
        for elem in elementos:
            if elem != "80":
                assert arvore.buscar(elem) is not None

    def test_remocao_da_raiz_com_dois_filhos(self):
        """Remoção do nó raiz que possui subárvores esquerda e direita."""
        arvore = AVLTree()
        for elem in ["40", "20", "60", "10", "30", "50", "70"]:
            arvore.inserir(elem, payload(elem))

        assert arvore.raiz.cpf == "40"
        # Sucessor in-order de 40 é o menor da direita: 50
        arvore.remover("40")

        assert arvore.buscar("40") is None
        assert arvore.raiz.cpf == "50"
        assert arvore.total_nodes == 6

        valida, msg = arvore.validar_invariantes()
        assert valida is True, msg

    def test_remocao_que_dispara_rebalanceamento(self):
        """
        Remove um nó que provoca desbalanceamento em ancestral,
        forçando a árvore a aplicar uma rotação para restabelecer a invariante.
        """
        arvore = AVLTree()
        # Árvore:
        #        30
        #       /  \
        #      20   40
        #     /
        #    10
        arvore.inserir("30", payload("30"))
        arvore.inserir("20", payload("20"))
        arvore.inserir("40", payload("40"))
        arvore.inserir("10", payload("10"))

        # Altura da esquerda é 2 (20->10), direita é 1 (40). FB(30) = 2 - 1 = +1.
        # Ao remover 40, subárvore direita passa a ter altura 0.
        # FB(30) vira 2 - 0 = +2 -> viola a invariante!
        # Como FB(20) = 1 >= 0, dispara Rotação LL no nó 30.
        arvore.remover("40")

        # Nova raiz deve ser 20
        assert arvore.raiz.cpf == "20"
        assert arvore.raiz.esquerda.cpf == "10"
        assert arvore.raiz.direita.cpf == "30"
        assert arvore.obter_fb(arvore.raiz) == 0

        valida, msg = arvore.validar_invariantes()
        assert valida is True, msg

    def test_remover_chave_inexistente_lanca_excecao(self):
        """Tentar remover chave não cadastrada deve lançar CPFNotFoundError."""
        arvore = AVLTree()
        arvore.inserir("11111111111", payload("11111111111"))

        with pytest.raises(CPFNotFoundError):
            arvore.remover("99999999999")

    def test_remocao_massiva_ate_esvaziar(self):
        """
        Insere 100 elementos e remove todos em ordem aleatória,
        garantindo integridade da árvore após cada remoção unitária.
        """
        arvore = AVLTree()
        itens = [f"{i:03d}" for i in range(100)]
        for item in itens:
            arvore.inserir(item, payload(item))

        random.seed(123)
        random.shuffle(itens)

        for i, item in enumerate(itens):
            arvore.remover(item)
            assert arvore.buscar(item) is None
            assert arvore.total_nodes == 100 - (i + 1)

            valida, msg = arvore.validar_invariantes()
            assert valida is True, f"Falha após remover {item}: {msg}"

        assert arvore.total_nodes == 0
        assert arvore.raiz is None
        assert arvore.altura_total() == 0
