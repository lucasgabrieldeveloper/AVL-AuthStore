# AVL-AuthStore

Sistema de Cadastro e Autenticação de Clientes com Armazenamento em Memória (RAM), estruturado sobre uma **Árvore AVL (Adelson-Velsky e Landis)** atuando como **Dicionário Chave-Valor** de alta performance, acompanhado de uma **Interface Gráfica Moderna (GUI)** construída com `CustomTkinter` e `CTkMessagebox`.

Garante que todas as operações de busca, inserção e remoção ocorram em tempo **$O(\log n)$** no pior caso, com rebalanceamento imediato, suporte a alta concorrência e experiência de usuário visualmente moderna e fluida.

---

## 1. Arquitetura e Estrutura do Projeto

O projeto adota estrita separação de responsabilidades (MVC): a camada visual (View) apenas consome os serviços da camada de controle e negócio (Controller/Model), sem conter regras internas de rotação da árvore.

```
AVL-AuthStore/
├── main.py                   # Ponto de entrada da aplicação Desktop GUI (CustomTkinter)
├── cli.py                    # Interface de Linha de Comando (CLI alternativa)
├── requirements.txt          # Dependências do projeto (customtkinter, CTkMessagebox, pytest)
├── README.md                 # Documentação técnica e guia de execução
│
├── gui/                      # Camada de Interface Gráfica (View)
│   ├── __init__.py           # Exportação do componente mestre AppWindow
│   ├── app_window.py         # Janela mestre e orquestrador de navegação entre telas
│   ├── theme.py              # Design System moderno Dark Mode (cores, tipografia, espaçamentos)
│   ├── components.py         # Componentes reutilizáveis (CPFEntry com máscara e MetricCard)
│   └── screens/              # Telas (Frames) da aplicação
│       ├── __init__.py
│       ├── login_screen.py      # Tela A: Login / Autenticação (RF02)
│       ├── cadastro_screen.py   # Tela B: Cadastro de Novo Cliente (RF01)
│       ├── dashboard_screen.py  # Tela C: Dashboard e Menu Principal (Pós-Login)
│       ├── atualizar_screen.py  # Tela D: Atualização de Dados Cadastrais (RF04)
│       └── metricas_screen.py   # Tela E: Painel de Métricas AVL e Listagem In-Order (RF05/RF06)
│
├── services/                 # Camada de Integração para a Interface Gráfica
│   ├── __init__.py
│   └── user_service.py       # Fachada unificada UserDictionaryService
│
├── avl_authstore/            # Núcleo da Estrutura de Dados e Lógica de Negócio (Model)
│   ├── __init__.py
│   ├── models.py             # ClientePayload e AVLNode
│   ├── avl_tree.py           # Árvore AVL manual com rotações LL, RR, LR, RL e remoção
│   ├── service.py            # UserDictionaryService com sincronização RLock (Thread-Safe)
│   ├── security.py           # Hashing PBKDF2-HMAC-SHA256 e salts criptográficos
│   └── utils.py              # Validações, sanitização de CPF e renderizador ASCII
│
└── tests/                    # Suíte de Testes Unitários e de Integração (Pytest)
    ├── __init__.py
    ├── test_rotations.py     # Validação das 4 rotações (LL, RR, LR, RL)
    ├── test_balancing.py     # Prova matemática de O(log n) no pior caso de inserção
    ├── test_deletion.py      # Casos de remoção (folha, 1 filho, 2 filhos e rebalanceamento)
    ├── test_service.py       # Requisitos RF01-RF06 e teste multithread (50 threads)
    └── test_gui_service_integration.py # Contratos de tipo da camada de serviço da GUI
```

---

## 2. Invariante e Regras de Balanceamento (Estritas)

### Convenção do Fator de Balanceamento (FB)
$$\text{FB}(\text{nó}) = \text{altura}(\text{subárvore esquerda}) - \text{altura}(\text{subárvore direita})$$

- $\text{FB} > 0$: Subárvore esquerda mais alta (pesada à esquerda).
- $\text{FB} < 0$: Subárvore direita mais alta (pesada à direita).
- $\text{FB} = 0$: Subárvores perfeitamente equilibradas.

### Invariante AVL
Para todo nó $v$ da árvore:
$$|\text{FB}(v)| \le 1$$
Se após uma inserção ou remoção $|\text{FB}(v)| > 1$, o rebalanceamento é disparado **imediatamente** na subida da pilha de recursão.

### As 4 Rotações Manuais

1. **Rotação Simples à Direita (LL)**:
   - Disparada quando $\text{FB}(v) > 1$ e $\text{FB}(v.\text{esquerda}) \ge 0$.
2. **Rotação Simples à Esquerda (RR)**:
   - Disparada quando $\text{FB}(v) < -1$ e $\text{FB}(v.\text{direita}) \le 0$.
3. **Rotação Dupla à Direita (LR)**:
   - Disparada quando $\text{FB}(v) > 1$ e $\text{FB}(v.\text{esquerda}) < 0$.
   - Executa `rotacaoRR` no filho esquerdo e `rotacaoLL` no nó.
4. **Rotação Dupla à Esquerda (RL)**:
   - Disparada quando $\text{FB}(v) < -1$ e $\text{FB}(v.\text{direita}) > 0$.
   - Executa `rotacaoLL` no filho direito e `rotacaoRR` no nó.

---

## 3. Telas da Interface Gráfica (`CustomTkinter`)

A aplicação conta com um design moderno em **Dark Mode**:

* **Tela A - Login (`LoginScreen`)**:
  - Painel de apresentação da árvore AVL e card de acesso.
  - Campo CPF com máscara automática (`000.000.000-00`) e senha com máscara (`*`).
  - Autenticação $O(\log n)$ com feedback via `CTkMessagebox`.
* **Tela B - Cadastro (`CadastroScreen`)**:
  - Formulário de criação de conta com validação de campos obrigatórios e confirmação de senha.
  - Detecção imediata de duplicidade de CPF.
* **Tela C - Dashboard (`DashboardScreen`)**:
  - Exibição personalizada do cliente autenticado e sessão ativa.
  - Cards rápidos com métricas da árvore AVL (Total de clientes, Altura, FB da raiz).
  - Ações para atualizar dados, ver métricas ou excluir a própria conta (com janela de confirmação modal).
* **Tela D - Atualização (`AtualizarScreen`)**:
  - Edição de nome e e-mail.
  - CPF desabilitado/read-only (imutável, preservando a propriedade BST).
  - Campo opcional para redefinição de senha.
* **Tela E - Métricas e Listagem (`MetricasScreen`)**:
  - Cards detalhados: Altura atual ($h$), Total de nós ($n$), FB da raiz e Auditoria da Invariante ($|\text{FB}| \le 1$).
  - Tabela com listagem completa dos clientes em ordem crescente de CPF (**Travessia In-Order**).
  - Campo de busca e filtro em tempo real por nome ou CPF.

---

## 4. Instruções de Instalação e Execução

### Pré-requisitos
- Python 3.10 ou superior.

### 1. Criar e Ativar Ambiente Virtual
```powershell
python -m venv .venv

# No Windows:
.\.venv\Scripts\activate

# No Linux ou macOS:
source .venv/bin/activate
```

### 2. Instalar Dependências
```powershell
pip install -r requirements.txt
```
*(ou manualmente: `pip install customtkinter CTkMessagebox pytest`)*

### 3. Executar a Aplicação Gráfica Desktop (GUI)
```powershell
python main.py
```

Para iniciar a aplicação com 7 clientes previamente cadastrados (ideal para visualizar as métricas da árvore e a tabela ordenada):
```powershell
python main.py --demo
```

### 4. Executar a Suíte Completa de Testes Unitários
```powershell
pytest -v
```
*(Executa 30 testes unitários e de integração cobrindo rotações, prova de $O(\log n)$, remoções, concorrência e métodos de serviço).*
