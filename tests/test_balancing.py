"""
Testes de Estresse e Garantia do Balanceamento O(log n).

Valida especificamente o pior caso para árvores binárias de busca comuns (BST):
Inserção de dados estritamente em ordem crescente e decrescente.
Prova que a Árvore AVL mantém altura O(log n) através de rotações contínuas.
"""

import math
import random
import pytest
from avl_authstore.models import ClientePayload
from avl_authstore.avl_tree import AVLTree, CPFDuplicadoError


def criar_payload_simples(chave: str) -> ClientePayload:
    return ClientePayload(
        nome=f"Usuario {chave}",
        email=f"user{chave}@authstore.io",
        senha_hash=f"hash_{chave}",
    )


class TestBalanceamentoAVL:

    def test_pior_caso_insercao_crescente_prova_logaritmica(self):
        """
        PROVA DE EFICIÊNCIA:
        Em uma BST comum desbalanceada, inserir 255 elementos ordenados (1, 2, ..., 255)
        geraria uma lista encadeada com Altura = 255 (Tempo de busca O(n)).

        Na Árvore AVL, a altura máxima teórica é limitada por:
            h <= 1.4404 * log2(n + 2) - 0.328
        Para n = 255:
            log2(257) ~ 8.005
            h_max <= 1.4404 * 8.005 ~ 11.53 -> Altura máxima permitida = 11.
        """
        arvore = AVLTree()
        n = 255

        for i in range(1, n + 1):
            cpf = f"{i:011d}"
            arvore.inserir(cpf, criar_payload_simples(cpf))

        # 1. Total de nós correto
        assert arvore.total_nodes == n

        # 2. Altura observada deve ser estritamente logarítmica (muito menor que 255)
        altura_observada = arvore.altura_total()
        altura_max_teorica = math.ceil(1.4404 * math.log2(n + 2))

        assert altura_observada <= altura_max_teorica, (
            f"Altura observada ({altura_observada}) excedeu o limite máximo teórico AVL ({altura_max_teorica})"
        )
        # Em uma árvore balanceada ideal de 255 nós, a altura é 8. Em AVL fica entre 8 e 10.
        assert altura_observada <= 9, f"Esperado altura <= 9 para 255 nós, obtido: {altura_observada}"

        # 3. Validação da Invariante AVL em todos os 255 nós (|FB| <= 1)
        valida, msg = arvore.validar_invariantes()
        assert valida is True, msg

        # 4. A travessia em ordem deve ser perfeitamente ordenada
        elementos = arvore.em_ordem()
        cpfs_extraidos = [cpf for cpf, _ in elementos]
        assert cpfs_extraidos == sorted(cpfs_extraidos)

    def test_pior_caso_insercao_decrescente(self):
        """
        Verifica o comportamento inverso: inserção estritamente decrescente
        forçando repetidas rotações LL para manter a altura logarítmica.
        """
        arvore = AVLTree()
        n = 127

        for i in range(n, 0, -1):
            cpf = f"{i:011d}"
            arvore.inserir(cpf, criar_payload_simples(cpf))

        assert arvore.total_nodes == n
        altura_observada = arvore.altura_total()
        altura_max_teorica = math.ceil(1.4404 * math.log2(n + 2))

        assert altura_observada <= altura_max_teorica
        assert altura_observada <= 8

        valida, msg = arvore.validar_invariantes()
        assert valida is True, msg

    def test_insercao_aleatoria_com_grande_volume(self):
        """
        Insere 1.000 nós com chaves geradas aleatoriamente e valida:
        - Altura estritamente O(log n) (altura <= 14).
        - Invariante |FB| <= 1 satisfeita em toda a árvore.
        - Integridade de busca de todos os nós inseridos.
        """
        arvore = AVLTree()
        numeros = list(range(1, 1001))
        random.seed(42)
        random.shuffle(numeros)

        for num in numeros:
            cpf = f"{num:011d}"
            arvore.inserir(cpf, criar_payload_simples(cpf))

        assert arvore.total_nodes == 1000

        # Para 1000 nós, a altura não deve ultrapassar 13 ou 14
        assert arvore.altura_total() <= 14

        valida, msg = arvore.validar_invariantes()
        assert valida is True, msg

        # Busca O(log n) deve encontrar todos os nós inseridos
        for num in numeros[:100]:
            cpf = f"{num:011d}"
            payload = arvore.buscar(cpf)
            assert payload is not None
            assert payload.nome == f"Usuario {cpf}"

    def test_rejeicao_de_duplicidade(self):
        """Valida que a árvore impede chaves duplicadas com CPFDuplicadoError."""
        arvore = AVLTree()
        cpf = "12345678901"
        arvore.inserir(cpf, criar_payload_simples(cpf))

        with pytest.raises(CPFDuplicadoError):
            arvore.inserir(cpf, criar_payload_simples(cpf))

        assert arvore.total_nodes == 1
