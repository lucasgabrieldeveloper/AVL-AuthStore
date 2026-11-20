"""
Camada de Serviço de Negócio do AVL-AuthStore para Integração com a Interface Gráfica.

Implementa a fachada UserDictionaryService que consome a Árvore AVL em memória,
provendo métodos síncronos de alta performance e thread-safe para o front-end CustomTkinter.
"""

from typing import Optional, List, Dict, Any, Tuple
from avl_authstore.service import UserDictionaryService as CoreUserService
from avl_authstore.avl_tree import AVLTree, CPFDuplicadoError, CPFNotFoundError
from avl_authstore.utils import sanitizar_cpf, formatar_cpf


class UserDictionaryService:
    """
    Controlador de serviço de usuários para consumo da interface gráfica (GUI).
    Encapsula o armazenamento baseado em Árvore AVL e gerencia a sessão.
    """

    def __init__(self, arvore: Optional[AVLTree] = None) -> None:
        """
        Inicializa o serviço de usuários com uma árvore AVL em memória.
        """
        self._core = CoreUserService(arvore=arvore)

    # =========================================================================
    # RF02 - Autenticação
    # =========================================================================

    def autenticar(self, cpf: str, senha: str) -> bool:
        """
        Autentica o cliente recebendo CPF e senha em tempo O(log n).

        Args:
            cpf: CPF do usuário (com ou sem formatação).
            senha: Senha em texto puro a ser validada contra o hash seguro.

        Returns:
            True se a senha estiver correta, False caso contrário.
        """
        sucesso, _, _ = self._core.autenticar_cliente(cpf=cpf, senha_pura=senha)
        return sucesso

    def autenticar_detalhado(
        self, cpf: str, senha: str
    ) -> Tuple[bool, str, Optional[Dict[str, Any]]]:
        """
        Versão detalhada de autenticação que retorna a mensagem descritiva
        e o dicionário de dados do usuário logado.
        """
        return self._core.autenticar_cliente(cpf=cpf, senha_pura=senha)

    # =========================================================================
    # RF01 - Cadastro
    # =========================================================================

    def cadastrar_cliente(
        self, cpf: str, nome: str, email: str, senha: str
    ) -> Tuple[bool, str]:
        """
        Cadastra um novo cliente no dicionário AVL após verificação O(log n) de unicidade.

        Args:
            cpf: Chave primária única.
            nome: Nome completo do cliente.
            email: E-mail do cliente.
            senha: Senha que será criptografada com salt e PBKDF2.

        Returns:
            Tupla (sucesso: bool, mensagem: str).
        """
        try:
            self._core.cadastrar_cliente(
                cpf=cpf,
                nome=nome,
                email=email,
                senha_pura=senha,
            )
            return True, "Cliente cadastrado com sucesso na Árvore AVL!"
        except CPFDuplicadoError as e:
            return False, str(e)
        except ValueError as e:
            return False, str(e)
        except Exception as e:
            return False, f"Erro inesperado no cadastro: {str(e)}"

    # =========================================================================
    # RF03 - Remoção
    # =========================================================================

    def remover_cliente(self, cpf: str) -> bool:
        """
        Remove o cliente associado ao CPF informado, rebalanceando a árvore.

        Args:
            cpf: CPF do cliente a ser excluído.

        Returns:
            True se removido com sucesso, False caso o CPF não exista.
        """
        try:
            return self._core.remover_cliente(cpf=cpf)
        except (CPFNotFoundError, ValueError):
            return False

    # =========================================================================
    # RF04 - Atualização
    # =========================================================================

    def atualizar_cadastro(
        self,
        cpf: str,
        nome: Optional[str] = None,
        email: Optional[str] = None,
        nova_senha: Optional[str] = None,
    ) -> bool:
        """
        Atualiza os dados de um cliente existente na árvore mantendo o CPF imutável.

        Returns:
            True se atualizado com sucesso, False caso ocorra erro ou cliente inexistente.
        """
        try:
            self._core.atualizar_cliente(
                cpf=cpf,
                nome=nome,
                email=email,
                nova_senha_pura=nova_senha,
            )
            return True
        except (CPFNotFoundError, ValueError):
            return False

    # =========================================================================
    # RF05 - Listagem Ordenada (In-Order Traversal)
    # =========================================================================

    def listar_ordenado(self) -> List[Dict[str, Any]]:
        """
        Retorna a lista de todos os clientes em ordem estritamente crescente de CPF.
        Complexidade: O(n).
        """
        return self._core.listar_clientes_ordenados()

    # =========================================================================
    # RF06 & Métricas Estruturais da Árvore AVL
    # =========================================================================

    def obter_altura_arvore(self) -> int:
        """Retorna a altura máxima atual da Árvore AVL."""
        return self._core.altura_arvore

    def obter_fator_balanceamento_raiz(self) -> int:
        """
        Retorna o Fator de Balanceamento (FB) do nó raiz da árvore.
        FB = altura(esquerda) - altura(direita).
        Se a árvore estiver vazia, retorna 0.
        """
        with self._core._lock:
            if self._core._tree.raiz is None:
                return 0
            return self._core._tree.obter_fb(self._core._tree.raiz)

    def obter_total_clientes(self) -> int:
        """Retorna a quantidade total de nós (clientes) ativos na árvore."""
        return self._core.total_clientes

    def obter_cliente(self, cpf: str) -> Optional[Dict[str, Any]]:
        """Busca O(log n) dos dados públicos do cliente pelo CPF."""
        return self._core.obter_cliente(cpf=cpf)

    def diagnostico_arvore(self) -> Dict[str, Any]:
        """Retorna métricas completas de diagnóstico da estrutura AVL."""
        return self._core.diagnostico_arvore()
