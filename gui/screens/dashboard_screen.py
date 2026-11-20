"""
Tela C: Dashboard / Menu Principal (Pós-Login).

Painel central do cliente autenticado com acesso a:
- Atualização de dados cadastrais (RF04)
- Exclusão da conta com rebalanceamento AVL (RF03)
- Consulta do painel de métricas e listagem in-order (RF05/RF06)
- Logout do sistema
"""

import customtkinter as ctk
from CTkMessagebox import CTkMessagebox
from gui.components import MetricCard
from gui.theme import (
    COLOR_SURFACE_DARK,
    COLOR_PRIMARY,
    COLOR_PRIMARY_HOVER,
    COLOR_SECONDARY,
    COLOR_SECONDARY_HOVER,
    COLOR_DANGER,
    COLOR_DANGER_HOVER,
    COLOR_SUCCESS,
    COLOR_TEXT_PRIMARY,
    COLOR_TEXT_SECONDARY,
    COLOR_TEXT_MUTED,
    COLOR_BORDER,
    FONT_TITLE,
    FONT_SUBTITLE,
    FONT_SECTION,
    FONT_LABEL,
    FONT_BODY,
    FONT_BUTTON,
    FONT_SMALL,
)


class DashboardScreen(ctk.CTkFrame):
    """
    Frame do Dashboard Principal do Cliente Autenticado.
    """

    def __init__(self, master, app) -> None:
        super().__init__(master, fg_color="transparent")
        self.app = app

        # Resgata dados da sessão ativa
        self.user = self.app.current_user or {
            "cpf": "",
            "cpf_formatado": "",
            "nome": "Cliente",
            "email": "",
            "data_cadastro": "",
        }

        self._construir_interface()

    def _construir_interface(self) -> None:
        # Contêiner central com rolagem suave
        scroll = ctk.CTkScrollableFrame(self, fg_color="transparent")
        scroll.pack(fill="both", expand=True, padx=40, pady=30)

        # 1. Barra de Boas-Vindas e Sessão
        card_usuario = ctk.CTkFrame(
            scroll,
            fg_color=COLOR_SURFACE_DARK,
            corner_radius=16,
            border_width=1,
            border_color=COLOR_BORDER,
        )
        card_usuario.pack(fill="x", pady=(0, 20))

        topo = ctk.CTkFrame(card_usuario, fg_color="transparent")
        topo.pack(fill="x", padx=24, pady=20)

        # Avatar simbólico
        avatar = ctk.CTkLabel(
            topo,
            text="👤",
            font=(FONT_TITLE[0], 40),
        )
        avatar.pack(side="left", padx=(0, 16))

        info_box = ctk.CTkFrame(topo, fg_color="transparent")
        info_box.pack(side="left", fill="both", expand=True)

        lbl_ola = ctk.CTkLabel(
            info_box,
            text=f"Bem-vindo, {self.user.get('nome', 'Cliente')}!",
            font=FONT_TITLE,
            text_color=COLOR_TEXT_PRIMARY,
            anchor="w",
        )
        lbl_ola.pack(anchor="w")

        detalhes = f"CPF: {self.user.get('cpf_formatado', self.user.get('cpf'))}   •   E-mail: {self.user.get('email')}   •   Sessão Ativa"
        lbl_detalhes = ctk.CTkLabel(
            info_box,
            text=detalhes,
            font=FONT_SMALL,
            text_color=COLOR_TEXT_SECONDARY,
            anchor="w",
        )
        lbl_detalhes.pack(anchor="w", pady=(2, 0))

        btn_sair = ctk.CTkButton(
            topo,
            text="Sair da Conta",
            font=FONT_SMALL,
            fg_color="transparent",
            hover_color=COLOR_DANGER,
            border_width=1,
            border_color=COLOR_BORDER,
            text_color=COLOR_TEXT_SECONDARY,
            width=110,
            height=36,
            corner_radius=8,
            command=self.app.logout,
        )
        btn_sair.pack(side="right")

        # 2. Resumo de Métricas Rápidas da Árvore AVL
        lbl_sec_metricas = ctk.CTkLabel(
            scroll,
            text="Visão Geral da Estrutura AVL em Memória",
            font=FONT_SECTION,
            text_color=COLOR_TEXT_PRIMARY,
        )
        lbl_sec_metricas.pack(anchor="w", pady=(0, 10))

        grid_cards = ctk.CTkFrame(scroll, fg_color="transparent")
        grid_cards.pack(fill="x", pady=(0, 24))
        grid_cards.grid_columnconfigure((0, 1, 2), weight=1)

        # Consulta métricas da árvore
        total_nos = self.app.servico.obter_total_clientes()
        altura = self.app.servico.obter_altura_arvore()
        fb_raiz = self.app.servico.obter_fator_balanceamento_raiz()

        card_total = MetricCard(
            grid_cards,
            titulo="Total de Clientes (Nós)",
            valor_inicial=str(total_nos),
            subtitulo="Armazenados em RAM",
            cor_destaque=COLOR_PRIMARY,
        )
        card_total.grid(row=0, column=0, padx=(0, 10), sticky="ew")

        card_altura = MetricCard(
            grid_cards,
            titulo="Altura da Árvore (h)",
            valor_inicial=str(altura),
            subtitulo="Complexidade O(log n) garantida",
            cor_destaque=COLOR_SUCCESS,
        )
        card_altura.grid(row=0, column=1, padx=5, sticky="ew")

        card_fb = MetricCard(
            grid_cards,
            titulo="FB da Raiz (h_esq - h_dir)",
            valor_inicial=f"{fb_raiz:+d}" if fb_raiz != 0 else "0",
            subtitulo="Invariante: |FB| <= 1",
            cor_destaque=COLOR_SECONDARY,
        )
        card_fb.grid(row=0, column=2, padx=(10, 0), sticky="ew")

        # 3. Ações e Navegação
        lbl_sec_acoes = ctk.CTkLabel(
            scroll,
            text="Ações Disponíveis",
            font=FONT_SECTION,
            text_color=COLOR_TEXT_PRIMARY,
        )
        lbl_sec_acoes.pack(anchor="w", pady=(0, 12))

        grid_acoes = ctk.CTkFrame(scroll, fg_color="transparent")
        grid_acoes.pack(fill="x", pady=(0, 20))
        grid_acoes.grid_columnconfigure((0, 1), weight=1)

        # Botão Ação: Atualizar Dados (Tela D)
        card_acao_atualizar = ctk.CTkFrame(
            grid_acoes,
            fg_color=COLOR_SURFACE_DARK,
            corner_radius=12,
            border_width=1,
            border_color=COLOR_BORDER,
        )
        card_acao_atualizar.grid(row=0, column=0, padx=(0, 10), pady=6, sticky="nsew")

        ctk.CTkLabel(
            card_acao_atualizar,
            text="📝  Atualizar Meus Dados",
            font=FONT_BUTTON,
            text_color=COLOR_TEXT_PRIMARY,
        ).pack(anchor="w", padx=16, pady=(16, 4))

        ctk.CTkLabel(
            card_acao_atualizar,
            text="Altere seu nome completo, e-mail de contato ou redefina sua senha.",
            font=FONT_SMALL,
            text_color=COLOR_TEXT_MUTED,
            wraplength=340,
            justify="left",
        ).pack(anchor="w", padx=16, pady=(0, 12))

        btn_ir_atualizar = ctk.CTkButton(
            card_acao_atualizar,
            text="Editar Dados Cadastrais",
            font=FONT_BUTTON,
            fg_color=COLOR_PRIMARY,
            hover_color=COLOR_PRIMARY_HOVER,
            height=38,
            corner_radius=8,
            command=lambda: self.app.show_screen("atualizar"),
        )
        btn_ir_atualizar.pack(fill="x", padx=16, pady=(0, 16))

        # Botão Ação: Ver Métricas da Árvore (Tela E)
        card_acao_metricas = ctk.CTkFrame(
            grid_acoes,
            fg_color=COLOR_SURFACE_DARK,
            corner_radius=12,
            border_width=1,
            border_color=COLOR_BORDER,
        )
        card_acao_metricas.grid(row=0, column=1, padx=(10, 0), pady=6, sticky="nsew")

        ctk.CTkLabel(
            card_acao_metricas,
            text="📊  Painel de Métricas e Clientes",
            font=FONT_BUTTON,
            text_color=COLOR_TEXT_PRIMARY,
        ).pack(anchor="w", padx=16, pady=(16, 4))

        ctk.CTkLabel(
            card_acao_metricas,
            text="Consulte a listagem In-Order ordenada por CPF e a auditoria de invariantes da AVL.",
            font=FONT_SMALL,
            text_color=COLOR_TEXT_MUTED,
            wraplength=340,
            justify="left",
        ).pack(anchor="w", padx=16, pady=(0, 12))

        btn_ir_metricas = ctk.CTkButton(
            card_acao_metricas,
            text="Ver Métricas da Árvore",
            font=FONT_BUTTON,
            fg_color=COLOR_SECONDARY,
            hover_color=COLOR_SECONDARY_HOVER,
            height=38,
            corner_radius=8,
            command=lambda: self.app.show_screen("metricas"),
        )
        btn_ir_metricas.pack(fill="x", padx=16, pady=(0, 16))

        # 4. Zona de Perigo / Exclusão de Conta (RF03)
        card_perigo = ctk.CTkFrame(
            scroll,
            fg_color=COLOR_SURFACE_DARK,
            corner_radius=12,
            border_width=1,
            border_color=COLOR_DANGER,
        )
        card_perigo.pack(fill="x", pady=(10, 20))

        linha_perigo = ctk.CTkFrame(card_perigo, fg_color="transparent")
        linha_perigo.pack(fill="x", padx=20, pady=16)

        texto_perigo = ctk.CTkFrame(linha_perigo, fg_color="transparent")
        texto_perigo.pack(side="left", fill="both", expand=True)

        ctk.CTkLabel(
            texto_perigo,
            text="⚠️  Excluir Minha Conta (Remoção AVL)",
            font=FONT_LABEL,
            text_color=COLOR_DANGER,
        ).pack(anchor="w")

        ctk.CTkLabel(
            texto_perigo,
            text="Ao excluir sua conta, o nó correspondente ao seu CPF será removido da Árvore AVL em O(log n) e as rotações de rebalanceamento serão disparadas imediatamente.",
            font=FONT_SMALL,
            text_color=COLOR_TEXT_MUTED,
            wraplength=520,
            justify="left",
        ).pack(anchor="w", pady=(2, 0))

        btn_excluir = ctk.CTkButton(
            linha_perigo,
            text="Excluir Minha Conta",
            font=FONT_BUTTON,
            fg_color=COLOR_DANGER,
            hover_color=COLOR_DANGER_HOVER,
            width=170,
            height=40,
            corner_radius=8,
            command=self._confirmar_exclusao_conta,
        )
        btn_excluir.pack(side="right")

    def _confirmar_exclusao_conta(self) -> None:
        """Solicita confirmação e executa a remoção do cliente na Árvore AVL."""
        cpf = self.user.get("cpf", "")
        nome = self.user.get("nome", "Cliente")

        msg = CTkMessagebox(
            title="Confirmação de Exclusão",
            message=(
                f"Tem certeza que deseja excluir permanentemente a conta de {nome} (CPF: {cpf})?\n\n"
                "Essa operação removerá o nó da árvore AVL e rebalanceará a estrutura em O(log n)."
            ),
            icon="warning",
            option_1="Cancelar",
            option_2="Sim, Excluir",
        )

        if msg.get() == "Sim, Excluir":
            sucesso = self.app.servico.remover_cliente(cpf)
            if sucesso:
                CTkMessagebox(
                    title="Conta Removida",
                    message="Sua conta foi excluída com sucesso e a árvore AVL foi rebalanceada.",
                    icon="check",
                )
                self.app.logout()
            else:
                CTkMessagebox(
                    title="Erro na Exclusão",
                    message="Não foi possível remover a conta da árvore AVL.",
                    icon="cancel",
                )
