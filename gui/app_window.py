"""
Janela Principal da Aplicação (AppWindow).

Gerencia a janela principal, dimensões, tema e a alternância dinâmica
entre as diferentes telas (Frames) do sistema AVL-AuthStore.
"""

import customtkinter as ctk
from typing import Optional, Dict, Any
from services.user_service import UserDictionaryService
from gui.theme import (
    COLOR_BG_DARK,
    COLOR_BORDER,
    FONT_FAMILY,
)


class AppWindow(ctk.CTk):
    """
    Janela mestre da interface gráfica.
    Atua como orquestrador central de navegação entre as telas.
    """

    def __init__(self, servico: Optional[UserDictionaryService] = None) -> None:
        super().__init__()

        # 1. Configurações da Janela
        self.title("AVL-AuthStore | Sistema de Autenticação em Memória O(log n)")
        self.geometry("980x640")
        self.minsize(880, 560)
        self.configure(fg_color=COLOR_BG_DARK)

        # 2. Centralização da Janela na Tela do Usuário
        self._centralizar_janela(980, 640)

        # 3. Associação da Camada de Serviço (Model/Controller)
        self.servico: UserDictionaryService = servico if servico is not None else UserDictionaryService()

        # 4. Estado da Sessão Ativa
        self.current_user: Optional[Dict[str, Any]] = None

        # 5. Contêiner Principal de Telas (Layout Flexível)
        self.content_container = ctk.CTkFrame(
            self,
            fg_color="transparent",
            corner_radius=0,
        )
        self.content_container.pack(fill="both", expand=True)

        # 6. Referência para a tela atualmente ativa
        self._tela_atual: Optional[ctk.CTkFrame] = None

        # 7. Inicia na Tela de Login
        self.show_screen("login")

    def _centralizar_janela(self, largura: int, altura: int) -> None:
        """Calcula e posiciona a janela no centro geométrico do monitor."""
        self.update_idletasks()
        largura_tela = self.winfo_screenwidth()
        altura_tela = self.winfo_screenheight()
        pos_x = max(0, int((largura_tela - largura) / 2))
        pos_y = max(0, int((altura_tela - altura) / 2))
        self.geometry(f"{largura}x{altura}+{pos_x}+{pos_y}")

    def show_screen(self, screen_name: str, **kwargs) -> None:
        """
        Alterna para a tela solicitada, destruindo a tela anterior
        e montando a nova tela dentro do contêiner principal.
        """
        # Destrói a tela atual para liberar memória
        if self._tela_atual is not None:
            self._tela_atual.destroy()
            self._tela_atual = None

        # Importações sob demanda (Lazy Loading) para evitar importações circulares
        if screen_name == "login":
            from gui.screens.login_screen import LoginScreen
            self._tela_atual = LoginScreen(master=self.content_container, app=self)

        elif screen_name == "cadastro":
            from gui.screens.cadastro_screen import CadastroScreen
            self._tela_atual = CadastroScreen(master=self.content_container, app=self)

        elif screen_name == "dashboard":
            from gui.screens.dashboard_screen import DashboardScreen
            self._tela_atual = DashboardScreen(master=self.content_container, app=self)

        elif screen_name == "atualizar":
            from gui.screens.atualizar_screen import AtualizarScreen
            self._tela_atual = AtualizarScreen(master=self.content_container, app=self)

        elif screen_name == "metricas":
            from gui.screens.metricas_screen import MetricasScreen
            self._tela_atual = MetricasScreen(master=self.content_container, app=self)

        else:
            raise ValueError(f"Tela desconhecida solicitada: '{screen_name}'")

        # Exibe a nova tela ocupando todo o espaço do contêiner
        self._tela_atual.pack(fill="both", expand=True)

    def login_success(self, user_data: Dict[str, Any]) -> None:
        """
        Callback acionado após autenticação bem-sucedida.
        Armazena os dados do cliente na sessão e redireciona ao Dashboard.
        """
        self.current_user = user_data
        self.show_screen("dashboard")

    def logout(self) -> None:
        """
        Encerra a sessão ativa do usuário e retorna à tela de login.
        """
        self.current_user = None
        self.show_screen("login")
