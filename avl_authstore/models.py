"""
Modelos de dados fundamentais para o sistema AVL-AuthStore.

Define as estruturas base de armazenamento em memória:
- ClientePayload: Objeto que encapsula os dados cadastrais do cliente.
- AVLNode: Estrutura do nó da árvore balanceada AVL contendo chave, valor, altura e ponteiros.
"""

from __future__ import annotations
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Optional


@dataclass
class ClientePayload:
    """
    Payload de dados associado a um cliente (Valor armazenado no dicionário AVL).

    Atributos:
        nome (str): Nome completo do cliente.
        email (str): Endereço de e-mail do cliente.
        senha_hash (str): Hash criptográfico seguro da senha (PBKDF2-HMAC-SHA256).
        data_cadastro (str): Carimbo de data/hora da criação do cadastro no formato ISO-8601 UTC.
    """
    nome: str
    email: str
    senha_hash: str
    data_cadastro: str = ""

    def __post_init__(self) -> None:
        # Se a data de cadastro não for informada na inicialização, gera a data UTC corrente
        if not self.data_cadastro:
            self.data_cadastro = datetime.now(timezone.utc).isoformat()

    def to_dict(self) -> dict:
        """Converte o payload em um dicionário para exibição e serialização."""
        return {
            "nome": self.nome,
            "email": self.email,
            "senha_hash": self.senha_hash,
            "data_cadastro": self.data_cadastro,
        }


class AVLNode:
    """
    Representação do Nó da Árvore AVL.

    Atributos:
        cpf (str): Chave primária de identificação do cliente (única e imutável).
        payload (ClientePayload): Valor associado à chave (dados do cliente).
        altura (int): Altura do nó na árvore. Nós folha possuem altura = 1; nós nulos têm altura = 0.
        esquerda (Optional[AVLNode]): Ponteiro/referência para a subárvore esquerda (filhos com chaves menores).
        direita (Optional[AVLNode]): Ponteiro/referência para a subárvore direita (filhos com chaves maiores).
    """

    def __init__(self, cpf: str, payload: ClientePayload) -> None:
        """
        Inicializa um novo nó folha da árvore AVL.

        Etapas:
        1. Atribui o CPF fornecido como a chave do nó.
        2. Armazena o payload do cliente como o valor associado.
        3. Define a altura inicial como 1 (por definição, um nó folha recém-criado tem altura 1).
        4. Inicializa os ponteiros dos filhos esquerdo e direito como None.
        """
        self.cpf: str = cpf
        self.payload: ClientePayload = payload
        self.altura: int = 1
        self.esquerda: Optional[AVLNode] = None
        self.direita: Optional[AVLNode] = None

    def __repr__(self) -> str:
        return f"AVLNode(cpf='{self.cpf}', altura={self.altura})"
