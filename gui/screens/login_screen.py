"""
Tela A: Login / Autenticação (RF02).

Permite ao cliente entrar no sistema informando CPF e senha.
Consome o método de busca e validação criptográfica O(log n) do UserDictionaryService.
"""

import customtkinter as ctk
from CTkMessagebox import CTkMessagebox
from gui.components import CPFEntry
from gui.theme import (
    COLOR_BG_DARK,
    COLOR_SURFACE_DARK,
    COLOR_PRIMARY,
    COLOR_PRIMARY_HOVER,
    COLOR_SECONDARY,
    COLOR_TEXT_PRIMARY,
    COLOR_TEXT_SECONDARY,
    COLOR_TEXT_MUTED,
    COLOR_BORDER,
    FONT_TITLE,
    FONT_SUBTITLE,
    FONT_LABEL,
    FONT_BODY,
    FONT_BUTTON,
    FONT_SMALL,
)


class LoginScreen(ctk.CTkFrame):
    """
    Frame de Autenticação de Usuários.
    """

    def __init__(self, master, app) -> None:
        super().__init__(master, fg_color="transparent")
        self.app = app

        # Layout responsivo de 2 colunas:
        # Coluna 0: Painel de Apresentação / Hero Branding
        # Coluna 1: Card de Formulário de Login
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self._construir_painel_lateral()
        self._construir_card_login()

    def _construir_painel_lateral(self) -> None:
        """Painel visual esquerdo com destaque para os diferenciais da Árvore AVL."""
        painel_esquerdo = ctk.CTkFrame(
            self,
            fg_color=COLOR_SURFACE_DARK,
            corner_radius=16,
            border_width=1,
            border_color=COLOR_BORDER,
        )
        painel_esquerdo.grid(row=0, column=0, padx=(30, 15), pady=30, sticky="nsew")

        # Conteúdo centralizado verticalmente no painel esquerdo
        conteudo = ctk.CTkFrame(painel_esquerdo, fg_color="transparent")
        conteudo.place(relx=0.5, rely=0.5, anchor="center")

        # Ícone / Emblema
        lbl_emblema = ctk.CTkLabel(
            conteudo,
            text="⚡ AVL",
            font=(FONT_TITLE[0], 36, "bold"),
            text_color=COLOR_PRIMARY,
        )
        lbl_emblema.pack(pady=(0, 10))

        # Título do Projeto
        lbl_titulo = ctk.CTkLabel(
            conteudo,
            text="AVL-AuthStore",
            font=FONT_TITLE,
            text_color=COLOR_TEXT_PRIMARY,
        )
        lbl_titulo.pack(pady=(0, 6))

        # Subtítulo Descritivo
        lbl_sub = ctk.CTkLabel(
            conteudo,
            text="Dicionário Chave-Valor em Memória\ncom Árvore Binária Auto-Balanceada",
            font=FONT_SUBTITLE,
            text_color=COLOR_TEXT_SECONDARY,
            justify="center",
        )
        lbl_sub.pack(pady=(0, 24))

        # Cards Informativos de Recursos
        recursos = [
            ("O(log n) Garantido", "Busca, inserção e remoção no pior caso"),
            ("Rebalanceamento Ativo", "Rotações LL, RR, LR e RL em tempo real"),
            ("Segurança Criptográfica", "PBKDF2-HMAC-SHA256 com Salt dinâmico"),
            ("Alta Concorrência", "Thread-Safe com sincronização reentrante"),
        ]

        for titulo, desc in recursos:
            card = ctk.CTkFrame(conteudo, fg_color=COLOR_BG_DARK, corner_radius=10, border_width=1, border_color=COLOR_BORDER)
            card.pack(fill="x", padx=10, pady=5)

            lbl_t = ctk.CTkLabel(card, text=f"✓  {titulo}", font=FONT_LABEL, text_color=COLOR_PRIMARY, anchor="w")
            lbl_t.pack(anchor="w", padx=12, pady=(8, 2))

            lbl_d = ctk.CTkLabel(card, text=desc, font=FONT_SMALL, text_color=COLOR_TEXT_MUTED, anchor="w")
            lbl_d.pack(anchor="w", padx=12, pady=(0, 8))

    def _construir_card_login(self) -> None:
        """Card do formulário de autenticação."""
        card_login = ctk.CTkFrame(
            self,
            fg_color=COLOR_SURFACE_DARK,
            corner_radius=16,
            border_width=1,
            border_color=COLOR_BORDER,
        )
        card_login.grid(row=0, column=1, padx=(15, 30), pady=30, sticky="nsew")

        # Conteúdo do formulário
        form = ctk.CTkFrame(card_login, fg_color="transparent")
        form.place(relx=0.5, rely=0.5, anchor="center")

        lbl_boas_vindas = ctk.CTkLabel(
            form,
            text="Acesse sua Conta",
            font=FONT_TITLE,
            text_color=COLOR_TEXT_PRIMARY,
        )
        lbl_boas_vindas.pack(anchor="w", pady=(0, 4))

        lbl_instrucao = ctk.CTkLabel(
            form,
            text="Informe seu CPF e senha para autenticar",
            font=FONT_SUBTITLE,
            text_color=COLOR_TEXT_SECONDARY,
        )
        lbl_instrucao.pack(anchor="w", pady=(0, 24))

        # Campo: CPF
        lbl_cpf = ctk.CTkLabel(form, text="CPF do Cliente", font=FONT_LABEL, text_color=COLOR_TEXT_PRIMARY)
        lbl_cpf.pack(anchor="w", pady=(0, 4))

        self.entry_cpf = CPFEntry(
            form,
            placeholder_text="000.000.000-00",
            width=320,
            height=42,
            corner_radius=8,
            font=FONT_BODY,
        )
        self.entry_cpf.pack(pady=(0, 16))

        # Campo: Senha
        lbl_senha = ctk.CTkLabel(form, text="Senha de Acesso", font=FONT_LABEL, text_color=COLOR_TEXT_PRIMARY)
        lbl_senha.pack(anchor="w", pady=(0, 4))

        self.entry_senha = ctk.CTkEntry(
            form,
            placeholder_text="Digite sua senha",
            show="*",
            width=320,
            height=42,
            corner_radius=8,
            font=FONT_BODY,
        )
        self.entry_senha.pack(pady=(0, 24))
        self.entry_senha.bind("<Return>", lambda event: self._executar_login())

        # Botão: Entrar
        self.btn_entrar = ctk.CTkButton(
            form,
            text="Entrar no Sistema",
            font=FONT_BUTTON,
            fg_color=COLOR_PRIMARY,
            hover_color=COLOR_PRIMARY_HOVER,
            width=320,
            height=44,
            corner_radius=8,
            command=self._executar_login,
        )
        self.btn_entrar.pack(pady=(0, 16))

        # Divisor
        divisor = ctk.CTkFrame(form, height=1, fg_color=COLOR_BORDER)
        divisor.pack(fill="x", pady=(0, 16))

        # Botão: Ir para Cadastro
        lbl_sem_conta = ctk.CTkLabel(
            form,
            text="Ainda não tem cadastro no sistema?",
            font=FONT_SMALL,
            text_color=COLOR_TEXT_MUTED,
        )
        lbl_sem_conta.pack(pady=(0, 6))

        self.btn_cadastro = ctk.CTkButton(
            form,
            text="Criar Novo Cadastro",
            font=FONT_BUTTON,
            fg_color="transparent",
            hover_color=COLOR_BG_DARK,
            border_width=1,
            border_color=COLOR_PRIMARY,
            text_color=COLOR_PRIMARY,
            width=320,
            height=40,
            corner_radius=8,
            command=lambda: self.app.show_screen("cadastro"),
        )
        self.btn_cadastro.pack()

    def _executar_login(self) -> None:
        """Processa a autenticação com validação visual e chamada ao backend AVL."""
        cpf_limpo = self.entry_cpf.get_raw()
        senha = self.entry_senha.get().strip()

        # Validação de preenchimento
        if not cpf_limpo:
            CTkMessagebox(
                title="Atenção",
                message="Por favor, digite o seu CPF para prosseguir.",
                icon="warning",
            )
            self.entry_cpf.focus_set()
            return

        if not senha:
            CTkMessagebox(
                title="Atenção",
                message="Por favor, digite sua senha de acesso.",
                icon="warning",
            )
            self.entry_senha.focus_set()
            return

        # Chamada ao Backend (RF02)
        sucesso, mensagem, dados_usuario = self.app.servico.autenticar_detalhado(
            cpf=cpf_limpo,
            senha=senha,
        )

        if sucesso and dados_usuario is not None:
            # Login bem-sucedido -> Notifica o app e redireciona ao Dashboard
            self.app.login_success(dados_usuario)
        else:
            # Falha de autenticação (usuário inexistente ou senha errada)
            CTkMessagebox(
                title="Falha na Autenticação",
                message=mensagem,
                icon="cancel",
            )
            self.entry_senha.delete(0, ctk.END)
            self.entry_senha.focus_set()
