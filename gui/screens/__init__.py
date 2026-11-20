"""
Telas (Frames) da Interface Gráfica do AVL-AuthStore.
"""

from .login_screen import LoginScreen
from .cadastro_screen import CadastroScreen
from .dashboard_screen import DashboardScreen
from .atualizar_screen import AtualizarScreen
from .metricas_screen import MetricasScreen

__all__ = [
    "LoginScreen",
    "CadastroScreen",
    "DashboardScreen",
    "AtualizarScreen",
    "MetricasScreen",
]
