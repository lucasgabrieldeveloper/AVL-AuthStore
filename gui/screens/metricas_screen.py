"""
Tela E: Painel de Métricas e Listagem Ordenada (RF05 e RF06).

Apresenta:
- Diagnóstico em tempo real da Árvore AVL (Altura, Total de Nós, FB da Raiz e Invariantes).
- Listagem completa dos clientes em ordem crescente de CPF (Travessia In-Order).
- Campo de filtro/busca para localizar clientes instantaneamente.
- Botão de retorno ao Dashboard principal.
"""

import math
import customtkinter as ctk
from gui.components import MetricCard
from gui.theme import (
    COLOR_BG_DARK,
    COLOR_SURFACE_DARK,
    COLOR_SURFACE_LIGHT,
    COLOR_PRIMARY,
    COLOR_PRIMARY_HOVER,
    COLOR_SECONDARY,
    COLOR_SUCCESS,
    COLOR_WARNING,
    COLOR_DANGER,
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


class MetricasScreen(ctk.CTkFrame):
    """
    Frame de Métricas Estruturais da AVL e Listagem In-Order de Clientes.
    """

    def __init__(self, master, app) -> None:
        super().__init__(master, fg_color="transparent")
        self.app = app

        # Cache dos clientes para suporte a filtro
        self._todos_clientes = []

        self._construir_interface()
        self._carregar_dados()

    def _construir_interface(self) -> None:
        # Layout principal com padding
        self.pack_propagate(False)

        # 1. Barra Superior com Título e Botão de Voltar
        topo = ctk.CTkFrame(self, fg_color="transparent")
        topo.pack(fill="x", padx=30, pady=(24, 16))

        titulo_box = ctk.CTkFrame(topo, fg_color="transparent")
        titulo_box.pack(side="left")

        lbl_titulo = ctk.CTkLabel(
            titulo_box,
            text="Métricas da Árvore AVL & Listagem",
            font=FONT_TITLE,
            text_color=COLOR_TEXT_PRIMARY,
        )
        lbl_titulo.pack(anchor="w")

        lbl_sub = ctk.CTkLabel(
            titulo_box,
            text="Comprovação do balanceamento O(log n) e ordenação In-Order",
            font=FONT_SUBTITLE,
            text_color=COLOR_TEXT_SECONDARY,
        )
        lbl_sub.pack(anchor="w")

        btn_voltar = ctk.CTkButton(
            topo,
            text="← Voltar ao Menu",
            font=FONT_BUTTON,
            fg_color=COLOR_SURFACE_DARK,
            hover_color=COLOR_SURFACE_LIGHT,
            border_width=1,
            border_color=COLOR_BORDER,
            text_color=COLOR_TEXT_PRIMARY,
            width=150,
            height=40,
            corner_radius=8,
            command=lambda: self.app.show_screen("dashboard"),
        )
        btn_voltar.pack(side="right")

        # 2. Grid de Cards de Métricas da Árvore AVL (RF06)
        grid_metricas = ctk.CTkFrame(self, fg_color="transparent")
        grid_metricas.pack(fill="x", padx=30, pady=(0, 16))
        grid_metricas.grid_columnconfigure((0, 1, 2, 3), weight=1)

        self.card_total = MetricCard(
            grid_metricas,
            titulo="Total de Nós (n)",
            valor_inicial="0",
            subtitulo="Nós na árvore AVL",
            cor_destaque=COLOR_PRIMARY,
        )
        self.card_total.grid(row=0, column=0, padx=(0, 8), sticky="ew")

        self.card_altura = MetricCard(
            grid_metricas,
            titulo="Altura Atual (h)",
            valor_inicial="0",
            subtitulo="Limite: O(log n)",
            cor_destaque=COLOR_SUCCESS,
        )
        self.card_altura.grid(row=0, column=1, padx=4, sticky="ew")

        self.card_fb_raiz = MetricCard(
            grid_metricas,
            titulo="FB da Raiz",
            valor_inicial="0",
            subtitulo="h_esq - h_dir",
            cor_destaque=COLOR_SECONDARY,
        )
        self.card_fb_raiz.grid(row=0, column=2, padx=4, sticky="ew")

        self.card_invariante = MetricCard(
            grid_metricas,
            titulo="Invariante AVL",
            valor_inicial="VÁLIDA ✓",
            subtitulo="|FB| <= 1 em todos os nós",
            cor_destaque=COLOR_SUCCESS,
        )
        self.card_invariante.grid(row=0, column=3, padx=(8, 0), sticky="ew")

        # 3. Barra de Busca e Filtro de Clientes
        barra_busca = ctk.CTkFrame(self, fg_color="transparent")
        barra_busca.pack(fill="x", padx=30, pady=(0, 10))

        lbl_lista = ctk.CTkLabel(
            barra_busca,
            text="Clientes Cadastrados (Travessia In-Order / Ordem Crescente de CPF)",
            font=FONT_LABEL,
            text_color=COLOR_TEXT_PRIMARY,
        )
        lbl_lista.pack(side="left")

        self.entry_busca = ctk.CTkEntry(
            barra_busca,
            placeholder_text="🔍 Filtrar por nome ou CPF...",
            width=260,
            height=34,
            corner_radius=8,
            font=FONT_BODY,
        )
        self.entry_busca.pack(side="right")
        self.entry_busca.bind("<KeyRelease>", lambda e: self._aplicar_filtro())

        # 4. Cabeçalho Fixo da Tabela de Clientes
        cabecalho_tabela = ctk.CTkFrame(
            self,
            fg_color=COLOR_SURFACE_DARK,
            corner_radius=8,
            height=38,
            border_width=1,
            border_color=COLOR_BORDER,
        )
        cabecalho_tabela.pack(fill="x", padx=30, pady=(0, 4))
        cabecalho_tabela.pack_propagate(False)

        col_cpf = ctk.CTkLabel(cabecalho_tabela, text="CPF (CHAVE)", font=FONT_LABEL, text_color=COLOR_TEXT_SECONDARY, width=170, anchor="w")
        col_cpf.pack(side="left", padx=(16, 10))

        col_nome = ctk.CTkLabel(cabecalho_tabela, text="NOME COMPLETO", font=FONT_LABEL, text_color=COLOR_TEXT_SECONDARY, width=220, anchor="w")
        col_nome.pack(side="left", padx=10)

        col_email = ctk.CTkLabel(cabecalho_tabela, text="E-MAIL", font=FONT_LABEL, text_color=COLOR_TEXT_SECONDARY, width=240, anchor="w")
        col_email.pack(side="left", padx=10)

        col_data = ctk.CTkLabel(cabecalho_tabela, text="DATA CADASTRO (UTC)", font=FONT_LABEL, text_color=COLOR_TEXT_SECONDARY, anchor="w")
        col_data.pack(side="left", padx=10, fill="x", expand=True)

        # 5. Área Rolável com as Linhas da Tabela (RF05)
        self.scroll_tabela = ctk.CTkScrollableFrame(
            self,
            fg_color=COLOR_BG_DARK,
            corner_radius=8,
            border_width=1,
            border_color=COLOR_BORDER,
        )
        self.scroll_tabela.pack(fill="both", expand=True, padx=30, pady=(0, 24))

    def _carregar_dados(self) -> None:
        """Carrega métricas e a listagem In-Order do backend."""
        # Consulta diagnósticos da árvore AVL
        diag = self.app.servico.diagnostico_arvore()
        total_nos = diag["total_nos"]
        altura = diag["altura"]
        fb_raiz = self.app.servico.obter_fator_balanceamento_raiz()
        invariante_valida = diag["invariante_valida"]

        # Calcula altura máxima teórica para N nós em AVL: h <= 1.44 * log2(n+2)
        if total_nos > 0:
            h_max_teorica = math.ceil(1.4404 * math.log2(total_nos + 2))
            sub_altura = f"Máximo Teórico AVL: {h_max_teorica}"
        else:
            sub_altura = "Árvore vazia"

        # Atualiza Cards
        self.card_total.atualizar_valor(str(total_nos))
        self.card_altura.atualizar_valor(str(altura), novo_subtitulo=sub_altura)
        self.card_fb_raiz.atualizar_valor(f"{fb_raiz:+d}" if fb_raiz != 0 else "0")

        if invariante_valida:
            self.card_invariante.atualizar_valor("VÁLIDA ✓", novo_subtitulo="|FB| <= 1 em todos os nós")
        else:
            self.card_invariante.atualizar_valor("VIOLADA ✗", novo_subtitulo="Atenção: Invariante violada!")

        # Consulta lista ordenada In-Order
        self._todos_clientes = self.app.servico.listar_ordenado()
        self._renderizar_linhas(self._todos_clientes)

    def _renderizar_linhas(self, clientes: list) -> None:
        """Renderiza as linhas da tabela no contêiner com cores alternadas."""
        # Limpa widgets anteriores da tabela
        for widget in self.scroll_tabela.winfo_children():
            widget.destroy()

        if not clientes:
            lbl_vazio = ctk.CTkLabel(
                self.scroll_tabela,
                text="Nenhum cliente cadastrado no momento.",
                font=FONT_BODY,
                text_color=COLOR_TEXT_MUTED,
            )
            lbl_vazio.pack(pady=40)
            return

        for idx, c in enumerate(clientes):
            cor_linha = COLOR_SURFACE_DARK if idx % 2 == 0 else COLOR_BG_DARK
            linha = ctk.CTkFrame(
                self.scroll_tabela,
                fg_color=cor_linha,
                corner_radius=6,
                height=42,
            )
            linha.pack(fill="x", pady=2)
            linha.pack_propagate(False)

            # CPF formatado com destaque
            lbl_cpf = ctk.CTkLabel(
                linha,
                text=c.get("cpf_formatado", c.get("cpf")),
                font=FONT_LABEL,
                text_color=COLOR_PRIMARY,
                width=170,
                anchor="w",
            )
            lbl_cpf.pack(side="left", padx=(16, 10))

            # Nome
            lbl_nome = ctk.CTkLabel(
                linha,
                text=c.get("nome", ""),
                font=FONT_BODY,
                text_color=COLOR_TEXT_PRIMARY,
                width=220,
                anchor="w",
            )
            lbl_nome.pack(side="left", padx=10)

            # Email
            lbl_email = ctk.CTkLabel(
                linha,
                text=c.get("email", ""),
                font=FONT_SMALL,
                text_color=COLOR_TEXT_SECONDARY,
                width=240,
                anchor="w",
            )
            lbl_email.pack(side="left", padx=10)

            # Data de Cadastro
            data_raw = c.get("data_cadastro", "")
            data_exibicao = data_raw[:19].replace("T", " ") if data_raw else "-"
            lbl_data = ctk.CTkLabel(
                linha,
                text=data_exibicao,
                font=FONT_SMALL,
                text_color=COLOR_TEXT_MUTED,
                anchor="w",
            )
            lbl_data.pack(side="left", padx=10, fill="x", expand=True)

    def _aplicar_filtro(self) -> None:
        """Filtra os clientes da lista em tempo real com base no texto digitado."""
        termo = self.entry_busca.get().strip().lower()
        if not termo:
            self._renderizar_linhas(self._todos_clientes)
            return

        filtrados = [
            c for c in self._todos_clientes
            if termo in c.get("nome", "").lower()
            or termo in c.get("cpf", "")
            or termo in c.get("cpf_formatado", "")
            or termo in c.get("email", "").lower()
        ]
        self._renderizar_linhas(filtrados)
