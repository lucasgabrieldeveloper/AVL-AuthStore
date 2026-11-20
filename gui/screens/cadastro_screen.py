"""
Tela B: Cadastro de Novo Cliente (RF01).

Permite registrar novos clientes na Árvore AVL com validação de campos,
comparação de senhas e inserção balanceada com hashing de segurança.
"""

import customtkinter as ctk
from CTkMessagebox import CTkMessagebox
from gui.components import CPFEntry
from gui.theme import (
    COLOR_SURFACE_DARK,
    COLOR_PRIMARY,
    COLOR_PRIMARY_HOVER,
    COLOR_TEXT_PRIMARY,
    COLOR_TEXT_SECONDARY,
    COLOR_TEXT_MUTED,
    COLOR_BORDER,
    COLOR_BG_DARK,
    FONT_TITLE,
    FONT_SUBTITLE,
    FONT_LABEL,
    FONT_BODY,
    FONT_BUTTON,
    FONT_SMALL,
)


class CadastroScreen(ctk.CTkFrame):
    """
    Frame de Cadastro de Novos Clientes.
    """

    def __init__(self, master, app) -> None:
        super().__init__(master, fg_color="transparent")
        self.app = app

        self._construir_interface()

    def _construir_interface(self) -> None:
        # Card Centralizado com rolagem se necessário
        scroll = ctk.CTkScrollableFrame(
            self,
            fg_color=COLOR_SURFACE_DARK,
            corner_radius=16,
            border_width=1,
            border_color=COLOR_BORDER,
            width=540,
            height=560,
        )
        scroll.place(relx=0.5, rely=0.5, anchor="center")

        # Cabeçalho
        lbl_titulo = ctk.CTkLabel(
            scroll,
            text="Criar Nova Conta",
            font=FONT_TITLE,
            text_color=COLOR_TEXT_PRIMARY,
        )
        lbl_titulo.pack(anchor="w", padx=30, pady=(24, 4))

        lbl_sub = ctk.CTkLabel(
            scroll,
            text="Os dados serão indexados em uma Árvore AVL balanceada",
            font=FONT_SUBTITLE,
            text_color=COLOR_TEXT_SECONDARY,
        )
        lbl_sub.pack(anchor="w", padx=30, pady=(0, 20))

        # Divisor
        ctk.CTkFrame(scroll, height=1, fg_color=COLOR_BORDER).pack(fill="x", padx=30, pady=(0, 16))

        # Campo: CPF
        ctk.CTkLabel(scroll, text="CPF (Chave Primária Única) *", font=FONT_LABEL, text_color=COLOR_TEXT_PRIMARY).pack(anchor="w", padx=30, pady=(0, 4))
        self.entry_cpf = CPFEntry(
            scroll,
            placeholder_text="000.000.000-00",
            height=40,
            corner_radius=8,
            font=FONT_BODY,
        )
        self.entry_cpf.pack(fill="x", padx=30, pady=(0, 14))

        # Campo: Nome Completo
        ctk.CTkLabel(scroll, text="Nome Completo *", font=FONT_LABEL, text_color=COLOR_TEXT_PRIMARY).pack(anchor="w", padx=30, pady=(0, 4))
        self.entry_nome = ctk.CTkEntry(
            scroll,
            placeholder_text="Ex: Maria dos Santos",
            height=40,
            corner_radius=8,
            font=FONT_BODY,
        )
        self.entry_nome.pack(fill="x", padx=30, pady=(0, 14))

        # Campo: E-mail
        ctk.CTkLabel(scroll, text="Endereço de E-mail *", font=FONT_LABEL, text_color=COLOR_TEXT_PRIMARY).pack(anchor="w", padx=30, pady=(0, 4))
        self.entry_email = ctk.CTkEntry(
            scroll,
            placeholder_text="exemplo@email.com",
            height=40,
            corner_radius=8,
            font=FONT_BODY,
        )
        self.entry_email.pack(fill="x", padx=30, pady=(0, 14))

        # Campo: Senha
        ctk.CTkLabel(scroll, text="Senha de Acesso *", font=FONT_LABEL, text_color=COLOR_TEXT_PRIMARY).pack(anchor="w", padx=30, pady=(0, 4))
        self.entry_senha = ctk.CTkEntry(
            scroll,
            placeholder_text="Mínimo 4 caracteres",
            show="*",
            height=40,
            corner_radius=8,
            font=FONT_BODY,
        )
        self.entry_senha.pack(fill="x", padx=30, pady=(0, 14))

        # Campo: Confirmar Senha
        ctk.CTkLabel(scroll, text="Confirmar Senha *", font=FONT_LABEL, text_color=COLOR_TEXT_PRIMARY).pack(anchor="w", padx=30, pady=(0, 4))
        self.entry_confirmar_senha = ctk.CTkEntry(
            scroll,
            placeholder_text="Repita sua senha",
            show="*",
            height=40,
            corner_radius=8,
            font=FONT_BODY,
        )
        self.entry_confirmar_senha.pack(fill="x", padx=30, pady=(0, 24))

        # Botão: Cadastrar
        self.btn_cadastrar = ctk.CTkButton(
            scroll,
            text="Confirmar Cadastro",
            font=FONT_BUTTON,
            fg_color=COLOR_PRIMARY,
            hover_color=COLOR_PRIMARY_HOVER,
            height=44,
            corner_radius=8,
            command=self._executar_cadastro,
        )
        self.btn_cadastrar.pack(fill="x", padx=30, pady=(0, 12))

        # Botão: Voltar para Login
        self.btn_voltar = ctk.CTkButton(
            scroll,
            text="Já possuo uma conta (Voltar ao Login)",
            font=FONT_BUTTON,
            fg_color="transparent",
            hover_color=COLOR_BG_DARK,
            border_width=1,
            border_color=COLOR_BORDER,
            text_color=COLOR_TEXT_SECONDARY,
            height=40,
            corner_radius=8,
            command=lambda: self.app.show_screen("login"),
        )
        self.btn_voltar.pack(fill="x", padx=30, pady=(0, 24))

    def _executar_cadastro(self) -> None:
        """Valida entradas e dispara o cadastro no serviço AVL."""
        cpf_limpo = self.entry_cpf.get_raw()
        nome = self.entry_nome.get().strip()
        email = self.entry_email.get().strip()
        senha = self.entry_senha.get().strip()
        confirmar_senha = self.entry_confirmar_senha.get().strip()

        # Validação 1: Campos obrigatórios
        if not cpf_limpo:
            CTkMessagebox(title="Campo Obrigatório", message="Informe o CPF do cliente.", icon="warning")
            self.entry_cpf.focus_set()
            return

        if len(cpf_limpo) < 11:
            CTkMessagebox(title="CPF Incompleto", message="O CPF deve conter os 11 dígitos numéricos.", icon="warning")
            self.entry_cpf.focus_set()
            return

        if not nome:
            CTkMessagebox(title="Campo Obrigatório", message="Informe o nome completo do cliente.", icon="warning")
            self.entry_nome.focus_set()
            return

        if not email or "@" not in email:
            CTkMessagebox(title="E-mail Inválido", message="Informe um endereço de e-mail válido com '@'.", icon="warning")
            self.entry_email.focus_set()
            return

        if not senha:
            CTkMessagebox(title="Campo Obrigatório", message="Informe uma senha de acesso.", icon="warning")
            self.entry_senha.focus_set()
            return

        if len(senha) < 4:
            CTkMessagebox(title="Senha Muito Curta", message="A senha deve possuir no mínimo 4 caracteres.", icon="warning")
            self.entry_senha.focus_set()
            return

        # Validação 2: Senhas idênticas
        if senha != confirmar_senha:
            CTkMessagebox(
                title="Senhas Divergentes",
                message="A senha e a confirmação de senha não coincidem. Por favor, digite novamente.",
                icon="cancel",
            )
            self.entry_confirmar_senha.delete(0, ctk.END)
            self.entry_confirmar_senha.focus_set()
            return

        # Dispara RF01 no Backend AVL
        sucesso, mensagem = self.app.servico.cadastrar_cliente(
            cpf=cpf_limpo,
            nome=nome,
            email=email,
            senha=senha,
        )

        if sucesso:
            # Feedback visual de sucesso
            msg = CTkMessagebox(
                title="Cadastro Realizado!",
                message=f"Cliente '{nome}' cadastrado com sucesso na Árvore AVL!\n\nDeseja ir para a tela de Login?",
                icon="check",
                option_1="Ir para Login",
                option_2="Cadastrar Outro",
            )
            if msg.get() == "Ir para Login":
                self.app.show_screen("login")
            else:
                # Limpa os campos para novo cadastro
                self.entry_cpf.delete(0, ctk.END)
                self.entry_nome.delete(0, ctk.END)
                self.entry_email.delete(0, ctk.END)
                self.entry_senha.delete(0, ctk.END)
                self.entry_confirmar_senha.delete(0, ctk.END)
                self.entry_cpf.focus_set()
        else:
            # Erro (por exemplo, CPF Duplicado)
            CTkMessagebox(
                title="Erro no Cadastro",
                message=mensagem,
                icon="cancel",
            )
            self.entry_cpf.focus_set()
