"""
Implementação Manual e Estrita de Árvore AVL atuando como Dicionário Chave-Valor.

Garante que todas as operações de busca, inserção e remoção ocorram em tempo O(log n)
no pior caso, mantendo a invariante de que para todo nó v, |FB(v)| <= 1.

Convenção adotada rigorosamente:
    FB(nó) = altura(esquerda) - altura(direita)

Regras de Rotação:
    - FB > 1 e filho_esquerdo.FB >= 0: Rotação Simples à Direita (LL)
    - FB < -1 e filho_direito.FB <= 0: Rotação Simples à Esquerda (RR)
    - FB > 1 e filho_esquerdo.FB < 0: Rotação Dupla à Direita (LR) -> RR no filho esquerdo, depois LL no nó
    - FB < -1 e filho_direito.FB > 0: Rotação Dupla à Esquerda (RL) -> LL no filho direito, depois RR no nó
"""

from typing import Optional, List, Tuple
from .models import AVLNode, ClientePayload


class CPFDuplicadoError(Exception):
    """Exceção lançada ao tentar inserir um CPF que já existe na árvore."""
    pass


class CPFNotFoundError(Exception):
    """Exceção lançada ao tentar buscar, atualizar ou remover um CPF inexistente."""
    pass


class AVLTree:
    """
    Árvore AVL (Adelson-Velsky e Landis) implementada manualmente como Dicionário.

    Atributos:
        raiz (Optional[AVLNode]): Ponteiro para o nó raiz da árvore.
        total_nodes (int): Contagem total de nós atualmente armazenados na árvore.
    """

    def __init__(self) -> None:
        """
        Inicializa um dicionário AVL vazio.
        Etapa 1: A raiz é definida como None.
        Etapa 2: O contador total de nós é iniciado em 0.
        """
        self.raiz: Optional[AVLNode] = None
        self.total_nodes: int = 0

    # =========================================================================
    # 1. Métodos Auxiliares de Altura e Fator de Balanceamento (FB)
    # =========================================================================

    def _altura(self, no: Optional[AVLNode]) -> int:
        """
        Etapa: Retorna a altura de um nó específico de forma segura.
        - Se o nó for nulo (None), a altura é considerada 0 (convenção AVL padrão).
        - Se o nó existir, retorna seu atributo de altura previamente calculado.
        Complexidade: O(1).
        """
        if no is None:
            return 0
        return no.altura

    def _atualizar_altura(self, no: AVLNode) -> None:
        """
        Etapa: Recalcula a altura de um nó não-nulo a partir de seus filhos diretos.
        Fórmula: altura(nó) = 1 + max(altura(esquerda), altura(direita)).
        Complexidade: O(1).
        """
        altura_esq = self._altura(no.esquerda)
        altura_dir = self._altura(no.direita)
        no.altura = 1 + max(altura_esq, altura_dir)

    def obter_fb(self, no: Optional[AVLNode]) -> int:
        """
        Etapa: Calcula o Fator de Balanceamento (FB) de um nó.
        Convenção unificada adotada:
            FB = altura(subárvore esquerda) - altura(subárvore direita)

        Interpretação:
            FB > 0  -> Subárvore esquerda mais alta (pesada à esquerda).
            FB < 0  -> Subárvore direita mais alta (pesada à direita).
            FB == 0 -> Subárvores perfeitamente equilibradas em altura.
            |FB| > 1 -> Invariante violada! Disparar rebalanceamento imediato.
        Complexidade: O(1).
        """
        if no is None:
            return 0
        return self._altura(no.esquerda) - self._altura(no.direita)

    # =========================================================================
    # 2. Métodos de Rotação Manual
    # =========================================================================

    def rotacaoLL(self, no: AVLNode) -> AVLNode:
        r"""
        Rotação Simples à Direita (Caso Left-Left / LL).
        Aplicada quando o nó está desbalanceado para a esquerda (FB > 1) e a inserção
        ou o desequilíbrio ocorreu na subárvore esquerda do filho esquerdo (FB_filho >= 0).

        Diagrama de Transformação:
                 A (no)                      B (nova_raiz)
                / \                         / \
               B   T3       ===>           T1  A
              / \                             / \
             T1  T2                          T2  T3

        Passo a passo da implementação:
        1. Identifica a nova raiz: o filho esquerdo do nó desbalanceado ('B').
        2. Isola a subárvore que trocará de pai: o filho direito da nova raiz ('T2').
        3. Realiza a rotação: o nó original ('A') se torna filho direito da nova raiz ('B').
        4. Realoca a subárvore 'T2' como filho esquerdo do nó original ('A').
        5. Recalcula a altura do nó 'A' (que desceu de nível).
        6. Recalcula a altura da nova raiz 'B' (que subiu de nível).
        7. Retorna a nova raiz para ser conectada ao pai na recursão.
        """
        # Passo 1: Salva referência para a nova raiz
        nova_raiz = no.esquerda
        assert nova_raiz is not None, "rotacaoLL chamada em nó com filho esquerdo nulo"

        # Passo 2: Salva a subárvore que será reposicionada
        subarvore_t2 = nova_raiz.direita

        # Passo 3 e 4: Reorganiza os ponteiros
        nova_raiz.direita = no
        no.esquerda = subarvore_t2

        # Passo 5: Recalcula altura do nó antigo primeiro (filho agora)
        self._atualizar_altura(no)

        # Passo 6: Recalcula altura da nova raiz em seguida
        self._atualizar_altura(nova_raiz)

        # Passo 7: Retorna a nova raiz balanceada
        return nova_raiz

    def rotacaoRR(self, no: AVLNode) -> AVLNode:
        r"""
        Rotação Simples à Esquerda (Caso Right-Right / RR).
        Aplicada quando o nó está desbalanceado para a direita (FB < -1) e a inserção
        ou o desequilíbrio ocorreu na subárvore direita do filho direito (FB_filho <= 0).

        Diagrama de Transformação:
               A (no)                         B (nova_raiz)
              / \                            / \
             T1  B           ===>           A   T3
                / \                        / \
               T2  T3                     T1  T2

        Passo a passo da implementação:
        1. Identifica a nova raiz: o filho direito do nó desbalanceado ('B').
        2. Isola a subárvore que trocará de pai: o filho esquerdo da nova raiz ('T2').
        3. Realiza a rotação: o nó original ('A') se torna filho esquerdo da nova raiz ('B').
        4. Realoca a subárvore 'T2' como filho direito do nó original ('A').
        5. Recalcula a altura do nó 'A' (que desceu de nível).
        6. Recalcula a altura da nova raiz 'B' (que subiu de nível).
        7. Retorna a nova raiz para ser conectada ao pai na recursão.
        """
        # Passo 1: Salva referência para a nova raiz
        nova_raiz = no.direita
        assert nova_raiz is not None, "rotacaoRR chamada em nó com filho direito nulo"

        # Passo 2: Salva a subárvore que será reposicionada
        subarvore_t2 = nova_raiz.esquerda

        # Passo 3 e 4: Reorganiza os ponteiros
        nova_raiz.esquerda = no
        no.direita = subarvore_t2

        # Passo 5: Recalcula altura do nó antigo primeiro (filho agora)
        self._atualizar_altura(no)

        # Passo 6: Recalcula altura da nova raiz em seguida
        self._atualizar_altura(nova_raiz)

        # Passo 7: Retorna a nova raiz balanceada
        return nova_raiz

    def rotacaoLR(self, no: AVLNode) -> AVLNode:
        """
        Rotação Dupla à Direita (Caso Left-Right / LR).
        Aplicada quando o nó está pesado à esquerda (FB > 1), porém seu filho esquerdo
        está pesado à direita (FB < 0) em formato de 'joelho' ou 'ziguezague'.

        Passo a passo da implementação:
        1. Aplica uma Rotação Simples à Esquerda (rotacaoRR) sobre o filho esquerdo do nó,
           transformando o formato ziguezague em formato linear (LL).
        2. Conecta o resultado como o novo filho esquerdo do nó.
        3. Aplica uma Rotação Simples à Direita (rotacaoLL) sobre o nó principal.
        4. Retorna a nova raiz resultante.
        """
        assert no.esquerda is not None, "rotacaoLR chamada em nó com filho esquerdo nulo"
        # Passo 1 e 2: Rotação simples à esquerda no filho esquerdo
        no.esquerda = self.rotacaoRR(no.esquerda)

        # Passo 3 e 4: Rotação simples à direita no nó desbalanceado
        return self.rotacaoLL(no)

    def rotacaoRL(self, no: AVLNode) -> AVLNode:
        """
        Rotação Dupla à Esquerda (Caso Right-Left / RL).
        Aplicada quando o nó está pesado à direita (FB < -1), porém seu filho direito
        está pesado à esquerda (FB > 0) em formato de 'joelho' ou 'ziguezague'.

        Passo a passo da implementação:
        1. Aplica uma Rotação Simples à Direita (rotacaoLL) sobre o filho direito do nó,
           transformando o formato ziguezague em formato linear (RR).
        2. Conecta o resultado como o novo filho direito do nó.
        3. Aplica uma Rotação Simples à Esquerda (rotacaoRR) sobre o nó principal.
        4. Retorna a nova raiz resultante.
        """
        assert no.direita is not None, "rotacaoRL chamada em nó com filho direito nulo"
        # Passo 1 e 2: Rotação simples à direita no filho direito
        no.direita = self.rotacaoLL(no.direita)

        # Passo 3 e 4: Rotação simples à esquerda no nó desbalanceado
        return self.rotacaoRR(no)

    def balancear(self, no: AVLNode) -> AVLNode:
        """
        Método Geral de Rebalanceamento AVL.
        Avalia a invariante de balanceamento (|FB| <= 1). Caso violada, escolhe
        e executa a rotação exata requerida, retornando a nova subárvore balanceada.

        Passo a passo:
        1. Recalcula a altura atual do nó para refletir as alterações recentes dos filhos.
        2. Calcula o Fator de Balanceamento FB = altura(esq) - altura(dir).
        3. Se FB > 1 (pesado à esquerda):
           - Se FB do filho esquerdo >= 0: executa Rotação Simples LL.
           - Se FB do filho esquerdo < 0: executa Rotação Dupla LR.
        4. Se FB < -1 (pesado à direita):
           - Se FB do filho direito <= 0: executa Rotação Simples RR.
           - Se FB do filho direito > 0: executa Rotação Dupla RL.
        5. Se -1 <= FB <= 1: a invariante é respeitada; retorna o nó inalterado.
        """
        # Passo 1: Atualiza a altura do nó
        self._atualizar_altura(no)

        # Passo 2: Obtém o fator de balanceamento
        fb = self.obter_fb(no)

        # Passo 3: Caso desbalanceado à esquerda
        if fb > 1:
            fb_filho_esq = self.obter_fb(no.esquerda)
            if fb_filho_esq >= 0:
                # Caso LL: Rotação Simples à Direita
                return self.rotacaoLL(no)
            else:
                # Caso LR: Rotação Dupla à Direita
                return self.rotacaoLR(no)

        # Passo 4: Caso desbalanceado à direita
        if fb < -1:
            fb_filho_dir = self.obter_fb(no.direita)
            if fb_filho_dir <= 0:
                # Caso RR: Rotação Simples à Esquerda
                return self.rotacaoRR(no)
            else:
                # Caso RL: Rotação Dupla à Esquerda
                return self.rotacaoRL(no)

        # Passo 5: Já equilibrado
        return no

    # =========================================================================
    # 3. Operações Core: Inserção e Busca (Recursivas, O(log n))
    # =========================================================================

    def inserir(self, cpf: str, payload: ClientePayload) -> None:
        """
        Insere um novo cliente na árvore AVL.
        Garante que a chave (CPF) seja única e mantém a árvore estritamente balanceada.

        Complexidade de Tempo: O(log n) no pior caso.
        """
        # A inserção recursiva atualiza a raiz da árvore e incrementa a contagem de nós
        self.raiz = self._inserir_recursivo(self.raiz, cpf, payload)

    def _inserir_recursivo(
        self, no: Optional[AVLNode], cpf: str, payload: ClientePayload
    ) -> AVLNode:
        """
        Passo a passo da inserção recursiva AVL:
        1. Caso Base: Nó nulo encontrado. Cria um novo nó folha com altura 1,
           incrementa o contador de nós e retorna o novo nó.
        2. Navegação BST:
           - Se cpf < no.cpf: desce pela subárvore esquerda.
           - Se cpf > no.cpf: desce pela subárvore direita.
           - Se cpf == no.cpf: detecta chave duplicada e lança CPFDuplicadoError.
        3. Ao desempilhar a recursão (subindo até a raiz):
           - Chama balancear(no), que recalcula a altura e aplica rotações se |FB| > 1.
        4. Retorna a subárvore rebalanceada para o nó pai.
        """
        # Etapa 1: Ponto de inserção da nova folha
        if no is None:
            self.total_nodes += 1
            return AVLNode(cpf=cpf, payload=payload)

        # Etapa 2: Navegação comparativa BST
        if cpf < no.cpf:
            no.esquerda = self._inserir_recursivo(no.esquerda, cpf, payload)
        elif cpf > no.cpf:
            no.direita = self._inserir_recursivo(no.direita, cpf, payload)
        else:
            # CPF já existente: rejeita duplicações
            raise CPFDuplicadoError(f"O CPF '{cpf}' já se encontra cadastrado no sistema.")

        # Etapa 3 e 4: Recálculo de altura e rebalanceamento automático
        return self.balancear(no)

    def buscar(self, cpf: str) -> Optional[ClientePayload]:
        """
        Busca o payload de um cliente pelo CPF em tempo O(log n).

        Retorna:
            ClientePayload se o CPF for encontrado, ou None caso contrário.
        """
        no = self._buscar_no_recursivo(self.raiz, cpf)
        return no.payload if no is not None else None

    def _buscar_no_recursivo(self, no: Optional[AVLNode], cpf: str) -> Optional[AVLNode]:
        """
        Passo a passo da busca recursiva em BST balanceada:
        1. Se o nó for nulo, a chave não existe na árvore; retorna None.
        2. Se a chave for exatamente igual a no.cpf, o nó foi localizado; retorna o nó.
        3. Se cpf < no.cpf, a busca é direcionada recursivamente à esquerda.
        4. Se cpf > no.cpf, a busca é direcionada recursivamente à direita.
        Complexidade: Exatamente proporcional à altura da árvore: O(log n).
        """
        if no is None:
            return None
        if cpf == no.cpf:
            return no
        if cpf < no.cpf:
            return self._buscar_no_recursivo(no.esquerda, cpf)
        return self._buscar_no_recursivo(no.direita, cpf)

    def contem(self, cpf: str) -> bool:
        """
        Verifica se um CPF existe na árvore em tempo O(log n).
        """
        return self._buscar_no_recursivo(self.raiz, cpf) is not None

    # =========================================================================
    # 4. Operações Complexas: Remoção (3 Casos de BST + Rebalanceamento) e Atualização
    # =========================================================================

    def _encontrar_minimo(self, no: AVLNode) -> AVLNode:
        """
        Etapa auxiliar: Localiza o nó com menor chave a partir de uma dada subárvore
        (o nó mais à esquerda). Utilizado para encontrar o Sucessor In-Order.
        """
        atual = no
        while atual.esquerda is not None:
            atual = atual.esquerda
        return atual

    def remover(self, cpf: str) -> bool:
        """
        Remove o cliente associado ao CPF informado.

        Passos de alto nível:
        1. Executa busca para verificar se o nó existe. Se não existir, lança CPFNotFoundError.
        2. Aciona a remoção recursiva a partir da raiz.
        3. Retorna True confirmando o sucesso da remoção.
        Complexidade de Tempo: O(log n) no pior caso.
        """
        if not self.contem(cpf):
            raise CPFNotFoundError(f"Não foi possível remover: CPF '{cpf}' não cadastrado.")

        self.raiz = self._remover_recursivo(self.raiz, cpf)
        return True

    def _remover_recursivo(self, no: Optional[AVLNode], cpf: str) -> Optional[AVLNode]:
        """
        Passo a passo da remoção recursiva em Árvore AVL:
        1. Caso Base: Se o nó for nulo, retorna None.
        2. Navegação BST:
           - Se cpf < no.cpf: no.esquerda = _remover_recursivo(no.esquerda, cpf)
           - Se cpf > no.cpf: no.direita = _remover_recursivo(no.direita, cpf)
        3. Nó Localizado (cpf == no.cpf) - Tratamento dos 3 Casos Canônicos de BST:
           - CASO 1: Nó Folha (sem filhos):
             Decrementa o contador total de nós e retorna None ao pai.
           - CASO 2a: Nó possui apenas Filho Direito:
             Decrementa o contador e retorna o filho direito para substituir o nó.
           - CASO 2b: Nó possui apenas Filho Esquerdo:
             Decrementa o contador e retorna o filho esquerdo para substituir o nó.
           - CASO 3: Nó possui DOIS Filhos (esquerda e direita presentes):
             a. Localiza o Sucessor In-Order (menor nó da subárvore direita).
             b. Copia os dados do sucessor (cpf e payload) para o nó atual.
             c. Remove recursivamente o nó sucessor da subárvore direita.
                (O contador total de nós será decrementado na chamada recursiva do sucessor).
        4. Se após a remoção o nó se tornou nulo (remoção de folha isolada), retorna None.
        5. Rebalanceamento Ascendente:
           - Ao desempilhar a recursão, chama balancear(no) para cada ancestral até a raiz.
           - Recalcula a altura e dispara rotações caso |FB| > 1.
        6. Retorna a subárvore rebalanceada.
        """
        if no is None:
            return None

        # Etapa 2: Localização do nó por comparação
        if cpf < no.cpf:
            no.esquerda = self._remover_recursivo(no.esquerda, cpf)
        elif cpf > no.cpf:
            no.direita = self._remover_recursivo(no.direita, cpf)
        else:
            # Etapa 3: Nó encontrado!

            # Caso 1: Nó folha
            if no.esquerda is None and no.direita is None:
                self.total_nodes -= 1
                return None

            # Caso 2a: Apenas filho direito
            if no.esquerda is None:
                self.total_nodes -= 1
                return no.direita

            # Caso 2b: Apenas filho esquerdo
            if no.direita is None:
                self.total_nodes -= 1
                return no.esquerda

            # Caso 3: Dois filhos presentes
            # a. Localiza o sucessor in-order (menor elemento da subárvore direita)
            sucessor = self._encontrar_minimo(no.direita)

            # b. Copia os dados do sucessor para o nó corrente
            no.cpf = sucessor.cpf
            no.payload = sucessor.payload

            # c. Remove o nó sucessor da subárvore direita (que terá 0 ou 1 filho)
            no.direita = self._remover_recursivo(no.direita, sucessor.cpf)

        # Se o nó corrente não existe mais, encerra
        if no is None:
            return None

        # Etapa 5 e 6: Rebalanceamento obrigatório na subida da pilha
        return self.balancear(no)

    def atualizar(self, cpf: str, novo_payload: ClientePayload) -> bool:
        """
        Atualiza os dados de um cliente existente na árvore.
        Nota: O CPF é a chave primária imutável; apenas o payload é atualizado.

        Complexidade: O(log n).
        """
        no = self._buscar_no_recursivo(self.raiz, cpf)
        if no is None:
            raise CPFNotFoundError(f"Não foi possível atualizar: CPF '{cpf}' não cadastrado.")

        # Substitui o payload em memória mantendo a chave e a estrutura da árvore intactas
        no.payload = novo_payload
        return True

    # =========================================================================
    # 5. Travessias e Diagnósticos
    # =========================================================================

    def em_ordem(self) -> List[Tuple[str, ClientePayload]]:
        """
        Realiza a travessia In-Order (Em-Ordem) na árvore AVL.
        Como se trata de uma BST balanceada, os elementos são retornados
        estritamente em ordem crescente de CPF.

        Retorna:
            Lista de tuplas (cpf, payload) ordenadas crescentemente.
        Complexidade: O(n), visitando cada nó exatamente uma vez.
        """
        resultado: List[Tuple[str, ClientePayload]] = []
        self._em_ordem_recursivo(self.raiz, resultado)
        return resultado

    def _em_ordem_recursivo(
        self, no: Optional[AVLNode], acumulador: List[Tuple[str, ClientePayload]]
    ) -> None:
        """
        Travessia recursiva em três tempos:
        1. Visita recursivamente a subárvore esquerda (valores menores).
        2. Processa o nó corrente.
        3. Visita recursivamente a subárvore direita (valores maiores).
        """
        if no is not None:
            self._em_ordem_recursivo(no.esquerda, acumulador)
            acumulador.append((no.cpf, no.payload))
            self._em_ordem_recursivo(no.direita, acumulador)

    def altura_total(self) -> int:
        """Retorna a altura máxima atual da árvore a partir da raiz."""
        return self._altura(self.raiz)

    def obter_fb_por_cpf(self, cpf: str) -> int:
        """
        Retorna o Fator de Balanceamento do nó correspondente ao CPF informado.
        Lança CPFNotFoundError caso o nó não exista.
        """
        no = self._buscar_no_recursivo(self.raiz, cpf)
        if no is None:
            raise CPFNotFoundError(f"CPF '{cpf}' não localizado na árvore.")
        return self.obter_fb(no)

    def validar_invariantes(self) -> Tuple[bool, str]:
        """
        Função de diagnóstico e auditoria interna.
        Valida recursivamente em toda a árvore:
        1. A propriedade de ordenação BST (esquerda < nó < direita).
        2. A integridade do cálculo de altura (altura == 1 + max(h_esq, h_dir)).
        3. A invariante estrita da AVL: |FB| <= 1 para todos os nós.

        Retorna:
            (True, "OK") se todas as invariantes forem satisfeitas, ou (False, erro).
        """
        return self._validar_recursivo(self.raiz, None, None)

    def _validar_recursivo(
        self,
        no: Optional[AVLNode],
        limite_inferior: Optional[str],
        limite_superior: Optional[str],
    ) -> Tuple[bool, str]:
        """Validação profunda nó a nó de todas as invariantes de BST e AVL."""
        if no is None:
            return True, "OK"

        # 1. Validação de ordenação BST
        if limite_inferior is not None and no.cpf <= limite_inferior:
            return False, f"Violação de BST: nó {no.cpf} menor ou igual ao limite {limite_inferior}"
        if limite_superior is not None and no.cpf >= limite_superior:
            return False, f"Violação de BST: nó {no.cpf} maior ou igual ao limite {limite_superior}"

        # 2. Validação da altura
        altura_calculada = 1 + max(self._altura(no.esquerda), self._altura(no.direita))
        if no.altura != altura_calculada:
            return (
                False,
                f"Violação de Altura no nó {no.cpf}: armazenada={no.altura}, calculada={altura_calculada}",
            )

        # 3. Validação do Fator de Balanceamento (|FB| <= 1)
        fb = self.obter_fb(no)
        if abs(fb) > 1:
            return False, f"Violação da Invariante AVL no nó {no.cpf}: FB={fb} (|FB| > 1)"

        # Valida subárvore esquerda
        valida_esq, msg_esq = self._validar_recursivo(no.esquerda, limite_inferior, no.cpf)
        if not valida_esq:
            return False, msg_esq

        # Valida subárvore direita
        valida_dir, msg_dir = self._validar_recursivo(no.direita, no.cpf, limite_superior)
        if not valida_dir:
            return False, msg_dir

        return True, "OK"


# Alias para conformidade com a nomenclatura especificada no documento
AVLDictionary = AVLTree
