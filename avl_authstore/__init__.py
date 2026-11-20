"""
AVL-AuthStore: Sistema de Cadastro e Autenticação em Memória
baseado em Árvore AVL balanceada atuando como Dicionário Chave-Valor.
"""

from .models import ClientePayload, AVLNode
from .avl_tree import AVLTree, AVLDictionary
from .service import UserDictionaryService
from .security import hash_password, verify_password

__all__ = [
    "ClientePayload",
    "AVLNode",
    "AVLTree",
    "AVLDictionary",
    "UserDictionaryService",
    "hash_password",
    "verify_password",
]
