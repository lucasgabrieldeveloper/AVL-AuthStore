"""
Camada de Serviço de Negócio do AVL-AuthStore: UserDictionaryService.

Encapsula a AVLTree e expõe os requisitos funcionais do sistema:
- RF01: Cadastrar Cliente
- RF02: Autenticar Cliente
- RF03: Remover Cliente
- RF04: Atualizar Cadastro
- RF05: Listar/Consultar Ordenada (In-Order)
- RF06: Verificação de Balanceamento

Garante concorrência segura com travas reentrantes (threading.RLock)
e hashing criptográfico das credenciais de acesso.
"""

import threading
from typing import Optional, List, Tuple, Dict, Any
from .models import ClientePayload
from .avl_tree import AVLTree, CPFDuplicadoError, CPFNotFoundError
from .security import hash_password, verify_password
from .utils import sanitizar_cpf, formatar_cpf


class UserDictionaryService:
    """
    Serviço central de autenticação e gerenciamento de usuários em memória.
    Atua como fachada de alto nível para a estrutura de dados AVL.
    """

    def __init__(self, arvore: Optional[AVLTree] = None) -> None:
        """
        Inicializa o serviço de usuários.

        Etapas:
        1. Instancia ou associa uma Árvore AVL manual.
        2. Configura uma trava reentrante (threading.RLock) para sincronização
           multithread, garantindo operações atômicas mesmo sob alta concorrência.
        """
        self._tree: AVLTree = arvore if arvore is not None else AVLTree()
        self._lock = threading.RLock()

    @property
    def total_clientes(self) -> int:
        """Retorna o número total de clientes ativos cadastrados."""
        with self._lock:
            return self._tree.total_nodes

    @property
    def altura_arvore(self) -> int:
        """Retorna a altura atual da árvore AVL."""
        with self._lock:
            return self._tree.altura_total()

    # =========================================================================
    # RF01 - Cadastrar Cliente
    # =========================================================================

    def cadastrar_cliente(
        self, cpf: str, nome: str, email: str, senha_pura: str
    ) -> Dict[str, Any]:
        """
        RF01 - Cadastrar Cliente:
        Insere um novo cliente no dicionário AVL.

        Passo a passo da implementação:
        1. Sanitiza a chave de CPF (remove formatações/pontuações).
        2. Valida obrigatoriedade de campos e robustez mínima.
        3. Busca O(log n) prévia: Verifica se a chave já existe na árvore.
           Se existir, lança CPFDuplicadoError impedindo a duplicação.
        4. Criptografa a senha gerando hash seguro via PBKDF2-HMAC-SHA256 com salt aleatório.
        5. Cria o objeto ClientePayload com os metadados e data de cadastro.
        6. Insere o par (cpf, payload) na AVLTree, disparando rotações e rebalanceamento
           caso ocorra violação de invariante (|FB| > 1).
        7. Retorna os dados cadastrados (sem a senha em texto plano).
        """
        cpf_limpo = sanitizar_cpf(cpf)
        if not cpf_limpo:
            raise ValueError("O CPF informado é inválido ou vazio.")
        if not nome or not nome.strip():
            raise ValueError("O nome do cliente não pode ser vazio.")
        if not email or "@" not in email:
            raise ValueError("O e-mail informado é inválido.")
        if not senha_pura or len(senha_pura) < 4:
            raise ValueError("A senha deve possuir pelo menos 4 caracteres.")

        with self._lock:
            # Etapa 3: Verificação O(log n) de unicidade de chave
            if self._tree.contem(cpf_limpo):
                raise CPFDuplicadoError(
                    f"Falha de cadastro: O CPF {formatar_cpf(cpf_limpo)} já está cadastrado."
                )

            # Etapa 4: Hashing criptográfico da senha
            senha_hash = hash_password(senha_pura)

            # Etapa 5: Criação do payload
            payload = ClientePayload(
                nome=nome.strip(),
                email=email.strip().lower(),
                senha_hash=senha_hash,
            )

            # Etapa 6: Inserção balanceada na árvore AVL
            self._tree.inserir(cpf_limpo, payload)

            # Etapa 7: Retorno seguro dos dados cadastrados
            return {
                "cpf": cpf_limpo,
                "cpf_formatado": formatar_cpf(cpf_limpo),
                "nome": payload.nome,
                "email": payload.email,
                "data_cadastro": payload.data_cadastro,
            }

    # =========================================================================
    # RF02 - Autenticar Cliente
    # =========================================================================

    def autenticar_cliente(
        self, cpf: str, senha_pura: str
    ) -> Tuple[bool, str, Optional[Dict[str, Any]]]:
        """
        RF02 - Autenticar Cliente:
        Recebe CPF e senha, localiza o cliente em O(log n) e valida o hash.

        Passo a passo da implementação:
        1. Sanitiza o CPF fornecido.
        2. Realiza busca O(log n) pelo nó correspondente na árvore AVL.
        3. Se o cliente não existir, retorna (False, "Cliente não encontrado", None).
        4. Se existir, extrai o hash seguro armazenado no ClientePayload.
        5. Utiliza a função verify_password com verificação em tempo constante
           para comparar a senha enviada com o hash e salt guardados.
        6. Se a senha conferir, retorna (True, "Autenticação bem-sucedida", dados_usuario).
        7. Se for divergente, retorna (False, "Senha incorreta", None).
        """
        cpf_limpo = sanitizar_cpf(cpf)
        if not cpf_limpo:
            return False, "CPF informado é inválido.", None

        with self._lock:
            # Etapa 2: Busca O(log n)
            payload = self._tree.buscar(cpf_limpo)

            # Etapa 3: Cliente inexistente
            if payload is None:
                return False, f"Cliente com CPF {formatar_cpf(cpf_limpo)} não cadastrado.", None

            # Etapa 4 e 5: Verificação criptográfica do hash
            autenticado = verify_password(senha_pura, payload.senha_hash)

            if autenticado:
                dados_usuario = {
                    "cpf": cpf_limpo,
                    "cpf_formatado": formatar_cpf(cpf_limpo),
                    "nome": payload.nome,
                    "email": payload.email,
                    "data_cadastro": payload.data_cadastro,
                }
                return True, "Autenticação realizada com sucesso!", dados_usuario
            else:
                return False, "Credenciais inválidas: Senha incorreta.", None

    # =========================================================================
    # RF03 - Remover Cliente
    # =========================================================================

    def remover_cliente(self, cpf: str) -> bool:
        """
        RF03 - Remover Cliente:
        Remove o nó associado ao CPF informado tratando os casos de remoção em BST
        e rebalanceando a árvore recursivamente até a raiz.

        Passo a passo da implementação:
        1. Sanitiza o CPF fornecido.
        2. Adquire a trava reentrante para segurança em concorrência.
        3. Executa a remoção na árvore AVL via self._tree.remover(cpf_limpo).
        4. Caso o CPF não exista, propaga CPFNotFoundError.
        5. Retorna True em caso de sucesso.
        """
        cpf_limpo = sanitizar_cpf(cpf)
        if not cpf_limpo:
            raise ValueError("CPF inválido ou não informado.")

        with self._lock:
            # Dispara remoção balanceada O(log n)
            return self._tree.remover(cpf_limpo)

    # =========================================================================
    # RF04 - Atualizar Cadastro
    # =========================================================================

    def atualizar_cliente(
        self,
        cpf: str,
        nome: Optional[str] = None,
        email: Optional[str] = None,
        nova_senha_pura: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        RF04 - Atualizar Cadastro:
        Altera os dados (nome, e-mail, senha) de um cliente localizado pelo CPF.

        Passo a passo da implementação:
        1. Sanitiza o CPF.
        2. Localiza o payload atual do cliente em tempo O(log n).
        3. Se não encontrado, lança CPFNotFoundError.
        4. O CPF (chave primária) permanece estritamente imutável para preservar a ordem BST.
        5. Atualiza os campos requisitados:
           - Se fornecido novo nome, atualiza nome.
           - Se fornecido novo email, atualiza email.
           - Se fornecida nova senha, gera novo hash seguro com novo salt e atualiza senha_hash.
        6. Atualiza o payload do nó na árvore AVL.
        7. Retorna os dados cadastrais atualizados.
        """
        cpf_limpo = sanitizar_cpf(cpf)
        if not cpf_limpo:
            raise ValueError("CPF inválido ou não informado.")

        with self._lock:
            # Etapa 2: Localização do registro existente
            payload_atual = self._tree.buscar(cpf_limpo)
            if payload_atual is None:
                raise CPFNotFoundError(
                    f"Não foi possível atualizar: CPF {formatar_cpf(cpf_limpo)} não encontrado."
                )

            # Etapa 5: Atualizações parciais ou totais
            novo_nome = nome.strip() if nome is not None and nome.strip() else payload_atual.nome

            if email is not None:
                if "@" not in email:
                    raise ValueError("O novo e-mail fornecido é inválido.")
                novo_email = email.strip().lower()
            else:
                novo_email = payload_atual.email

            if nova_senha_pura is not None and nova_senha_pura.strip():
                if len(nova_senha_pura) < 4:
                    raise ValueError("A nova senha deve possuir pelo menos 4 caracteres.")
                novo_senha_hash = hash_password(nova_senha_pura)
            else:
                novo_senha_hash = payload_atual.senha_hash

            # Cria novo payload mantendo a data original de cadastro
            novo_payload = ClientePayload(
                nome=novo_nome,
                email=novo_email,
                senha_hash=novo_senha_hash,
                data_cadastro=payload_atual.data_cadastro,
            )

            # Etapa 6: Salva no nó AVL
            self._tree.atualizar(cpf_limpo, novo_payload)

            return {
                "cpf": cpf_limpo,
                "cpf_formatado": formatar_cpf(cpf_limpo),
                "nome": novo_payload.nome,
                "email": novo_payload.email,
                "data_cadastro": novo_payload.data_cadastro,
            }

    # =========================================================================
    # RF05 - Listar/Consultar Ordenada (In-Order Traversal)
    # =========================================================================

    def listar_clientes_ordenados(self) -> List[Dict[str, Any]]:
        """
        RF05 - Listar/Consultar Ordenada:
        Exibe todos os clientes cadastrados em ordem crescente de CPF.

        Passo a passo da implementação:
        1. Executa a travessia In-Order na árvore AVL (esquerda -> raiz -> direita).
        2. Retorna a lista completa ordenada com metadados para exibição.
        Complexidade: O(n).
        """
        with self._lock:
            registros = self._tree.em_ordem()
            return [
                {
                    "cpf": cpf,
                    "cpf_formatado": formatar_cpf(cpf),
                    "nome": payload.nome,
                    "email": payload.email,
                    "data_cadastro": payload.data_cadastro,
                }
                for cpf, payload in registros
            ]

    # =========================================================================
    # RF06 - Verificação de Balanceamento
    # =========================================================================

    def obter_fator_balanceamento(self, cpf: str) -> int:
        """
        RF06 - Verificação de Balanceamento:
        Função que retorna o Fator de Balanceamento (FB) de um nó específico da árvore.

        Retorna:
            Inteiro representando o FB = altura(esquerda) - altura(direita).
        Lança:
            CPFNotFoundError se o CPF não estiver presente na árvore.
        """
        cpf_limpo = sanitizar_cpf(cpf)
        with self._lock:
            return self._tree.obter_fb_por_cpf(cpf_limpo)

    def obter_cliente(self, cpf: str) -> Optional[Dict[str, Any]]:
        """
        Consulta os dados públicos de um cliente pelo CPF em O(log n).
        """
        cpf_limpo = sanitizar_cpf(cpf)
        with self._lock:
            payload = self._tree.buscar(cpf_limpo)
            if payload is None:
                return None
            return {
                "cpf": cpf_limpo,
                "cpf_formatado": formatar_cpf(cpf_limpo),
                "nome": payload.nome,
                "email": payload.email,
                "data_cadastro": payload.data_cadastro,
            }

    def diagnostico_arvore(self) -> Dict[str, Any]:
        """
        Retorna informações estruturais de diagnóstico da árvore AVL interna:
        - Total de nós
        - Altura da árvore
        - Validação de invariantes
        """
        with self._lock:
            valida, msg = self._tree.validar_invariantes()
            return {
                "total_nos": self._tree.total_nodes,
                "altura": self._tree.altura_total(),
                "invariante_valida": valida,
                "mensagem_diagnostico": msg,
            }
