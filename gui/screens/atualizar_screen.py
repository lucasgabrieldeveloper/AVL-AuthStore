"""
Tela D: Atualização de Dados Cadastrais (RF04).

Permite a alteração de dados de um cliente existente:
- CPF é estritamente imutável (chave primária da árvore AVL).
- Nome e E-mail são atualizados in-place.
- A senha pode ser redefinida com novo hash criptográfico.
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


class AtualizarScreen(ctk.CTkFrame):
    """
    Frame de Atualização de Cadastro do Cliente.
    """

    def __init__(self, master, app) -> None:
        super().__init__(master, fg_color="transparent")
        self.app = app

        # Dados da sessão atual
        self.user = self.app.current_user or {
            "cpf": "",
            "cpf_formatado": "",
            "nome": "",
            "email": "",
            "data_cadastro": "",
        }

        self._construir_interface()

    def _construir_interface(self) -> None:
        scroll = ctk.CTkScrollableFrame(
            self,
            fg_color=COLOR_SURFACE_DARK,
            corner_radius=16,
            border_width=1,
            border_color=COLOR_BORDER,
            width=540,
            height=580,
        )
        scroll.place(relx=0.5, rely=0.5, anchor="center")

        # Cabeçalho
        lbl_titulo = ctk.CTkLabel(
            scroll,
            text="Atualizar Cadastro",
            font=FONT_TITLE,
            text_color=COLOR_TEXT_PRIMARY,
        )
        lbl_titulo.pack(anchor="w", padx=30, pady=(24, 4))

        lbl_sub = ctk.CTkLabel(
            scroll,
            text="Altere seus dados. O CPF é a chave da árvore e não pode ser alterado.",
            font=FONT_SUBTITLE,
            text_color=COLOR_TEXT_SECONDARY,
        )
        lbl_sub.pack(anchor="w", padx=30, pady=(0, 20))

        # Divisor
        ctk.CTkFrame(scroll, height=1, fg_color=COLOR_BORDER).pack(fill="x", padx=30, pady=(0, 16))

        # Campo: CPF (Read-only / Desabilitado)
        ctk.CTkLabel(
            scroll,
            text="CPF (Chave Primária Imutável)",
            font=FONT_LABEL,
            text_color=COLOR_TEXT_SECONDARY,
        ).pack(anchor="w", padx=30, pady=(0, 4))

        self.entry_cpf = CPFEntry(
            scroll,
            height=40,
            corner_radius=8,
            font=FONT_BODY,
            fg_color=COLOR_BG_DARK,
            border_color=COLOR_BORDER,
        )
        self.entry_cpf.set_cpf(self.user.get("cpf", ""))
        self.entry_cpf.configure(state="disabled")  # Desabilitado / Read-Only
        self.entry_cpf.pack(fill="x", padx=30, pady=(0, 14))

        # Campo: Nome Completo
        ctk.CTkLabel(
            scroll,
            text="Nome Completo *",
            font=FONT_LABEL,
            text_color=COLOR_TEXT_PRIMARY,
        ).pack(anchor="w", padx=30, pady=(0, 4))

        self.entry_nome = ctk.CTkEntry(
            scroll,
            height=40,
            corner_radius=8,
            font=FONT_BODY,
        )
        self.entry_nome.insert(0, self.user.get("nome", ""))
        self.entry_nome.pack(fill="x", padx=30, pady=(0, 14))

        # Campo: E-mail
        ctk.CTkLabel(
            scroll,
            text="Endereço de E-mail *",
            font=FONT_LABEL,
            text_color=COLOR_TEXT_PRIMARY,
        ).pack(anchor="w", padx=30, pady=(0, 4))

        self.entry_email = ctk.CTkEntry(
            scroll,
            height=40,
            corner_radius=8,
            font=FONT_BODY,
        )
        self.entry_email.insert(0, self.user.get("email", ""))
        self.entry_email.pack(fill="x", padx=30, pady=(0, 14))

        # Divisor de Seção de Senha
        lbl_sec_senha = ctk.CTkLabel(
            scroll,
            text="Alteração de Senha (Opcional)",
            font=FONT_LABEL,
            text_color=COLOR_PRIMARY,
        )
        lbl_sec_senha.pack(anchor="w", padx=30, pady=(10, 4))

        lbl_desc_senha = ctk.CTkLabel(
            scroll,
            text="Preencha apenas se desejar redefinir sua senha de acesso.",
            font=FONT_SMALL,
            text_color=COLOR_TEXT_MUTED,
        )
        lbl_desc_senha.pack(anchor="w", padx=30, pady=(0, 10))

        # Campo: Nova Senha
        ctk.CTkLabel(
            scroll,
            text="Nova Senha",
            font=FONT_LABEL,
            text_color=COLOR_TEXT_PRIMARY,
        ).pack(anchor="w", padx=30, pady=(0, 4))

        self.entry_nova_senha = ctk.CTkEntry(
            scroll,
            placeholder_text="Deixe em branco para não alterar",
            show="*",
            height=40,
            corner_radius=8,
            font=FONT_BODY,
        )
        self.entry_nova_senha.pack(fill="x", padx=30, pady=(0, 14))

        # Campo: Confirmar Nova Senha
        ctk.CTkLabel(
            scroll,
            text="Confirmar Nova Senha",
            font=FONT_LABEL,
            text_color=COLOR_TEXT_PRIMARY,
        ).pack(anchor="w", padx=30, pady=(0, 4))

        self.entry_confirmar_nova_senha = ctk.CTkEntry(
            scroll,
            placeholder_text="Repita a nova senha",
            show="*",
            height=40,
            corner_radius=8,
            font=FONT_BODY,
        )
        self.entry_confirmar_nova_senha.pack(fill="x", padx=30, pady=(0, 24))

        # Linha de Botões de Ação
        grid_botoes = ctk.CTkFrame(scroll, fg_color="transparent")
        grid_botoes.pack(fill="x", padx=30, pady=(0, 24))
        grid_botoes.grid_columnconfigure((0, 1), weight=1)

        btn_cancelar = ctk.CTkButton(
            grid_botoes,
            text="Cancelar",
            font=FONT_BUTTON,
            fg_color="transparent",
            hover_color=COLOR_BG_DARK,
            border_width=1,
            border_color=COLOR_BORDER,
            text_color=COLOR_TEXT_SECONDARY,
            height=42,
            corner_radius=8,
            command=lambda: self.app.show_screen("dashboard"),
        )
        btn_cancelar.grid(row=0, column=0, padx=(0, 8), sticky="ew")

        btn_salvar = ctk.CTkButton(
            grid_botoes,
            text="Salvar Alterações",
            font=FONT_BUTTON,
            fg_color=COLOR_PRIMARY,
            hover_color=COLOR_PRIMARY_HOVER,
            height=42,
            corner_radius=8,
            command=self._salvar_alteracoes,
        )
        btn_salvar.grid(row=0, column=1, padx=(8, 0), sticky="ew")

    def _salvar_alteracoes(self) -> None:
        """Valida e aplica as modificações no serviço backend."""
        cpf = self.user.get("cpf", "")
        nome = self.entry_nome.get().strip()
        email = self.entry_email.get().strip()
        nova_senha = self.entry_nova_senha.get().strip()
        confirmar_senha = self.entry_confirmar_nova_senha.get().strip()

        # Validação básica
        if not nome:
            CTkMessagebox(title="Campo Obrigatório", message="O nome não pode ficar em branco.", icon="warning")
            self.entry_nome.focus_set()
            return

        if not email or "@" not in email:
            CTkMessagebox(title="E-mail Inválido", message="Informe um e-mail válido com '@'.", icon="warning")
            self.entry_email.focus_set()
            return

        # Se digitou nova senha, valida
        if nova_senha:
            if len(nova_senha) < 4:
                CTkMessagebox(
                    title="Senha Muito Curta",
                    message="A nova senha deve possuir pelo menos 4 caracteres.",
                    icon="warning",
                )
                self.entry_nova_senha.focus_set()
                return

            if nova_senha != confirmar_senha:
                CTkMessagebox(
                    title="Senhas Divergentes",
                    message="A nova senha e a confirmação não coincidem.",
                    icon="cancel",
                )
                self.entry_confirmar_nova_senha.focus_set()
                return

        # Chamada ao Backend (RF04)
        sucesso = self.app.servico.atualizar_cadastro(
            cpf=cpf,
            nome=nome,
            email=email,
            nova_senha=nova_senha if nova_senha else None,
        )

        if sucesso:
            # Atualiza os dados na sessão ativa da janela
            self.app.current_user["nome"] = nome
            self.app.current_user["email"] = email

            CTkMessagebox(
                title="Sucesso!",
                message="Dados cadastrais atualizados com êxito na Árvore AVL!",
                icon="check",
            )
            # Retorna ao Dashboard
            self.app.show_screen("dashboard")
        else:
            CTkMessagebox(
                title="Erro de Atualização",
                message="Não foi possível atualizar o cadastro no sistema.",
                icon="cancel",
            )
