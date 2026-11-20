"""
Componentes visuais reutilizáveis para a aplicação AVL-AuthStore.
"""

import re
import customtkinter as ctk
from typing import Optional, Callable
from gui.theme import (
    COLOR_SURFACE_DARK,
    COLOR_BORDER,
    COLOR_PRIMARY,
    COLOR_TEXT_PRIMARY,
    COLOR_TEXT_SECONDARY,
    COLOR_TEXT_MUTED,
    FONT_LABEL,
    FONT_BODY,
    FONT_CARD_TITLE,
    FONT_CARD_VALUE,
    FONT_SMALL,
)


class CPFEntry(ctk.CTkEntry):
    """
    Campo de entrada CustomTkinter especializado para CPF.
    Aplica máscara de formatação automática (000.000.000-00) enquanto o usuário digita.
    """

    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        self.bind("<KeyRelease>", self._ao_digitar)
        self.bind("<FocusOut>", self._ao_perder_foco)

    def _formatar_cpf_texto(self, texto: str) -> str:
        """Formata string de números até 11 dígitos com pontuação."""
        apenas_digitos = re.sub(r"\D", "", texto)[:11]
        n = len(apenas_digitos)

        if n <= 3:
            return apenas_digitos
        elif n <= 6:
            return f"{apenas_digitos[:3]}.{apenas_digitos[3:]}"
        elif n <= 9:
            return f"{apenas_digitos[:3]}.{apenas_digitos[3:6]}.{apenas_digitos[6:]}"
        else:
            return f"{apenas_digitos[:3]}.{apenas_digitos[3:6]}.{apenas_digitos[6:9]}-{apenas_digitos[9:]}"

    def _ao_digitar(self, event) -> None:
        # Ignora teclas de navegação comuns
        if event.keysym in ("BackSpace", "Delete", "Left", "Right", "Tab", "Shift_L", "Shift_R", "Control_L", "Control_R"):
            return

        posicao = self.index(ctk.INSERT)
        texto_atual = self.get()
        formatado = self._formatar_cpf_texto(texto_atual)

        if formatado != texto_atual:
            self.delete(0, ctk.END)
            self.insert(0, formatado)
            # Mantém cursor no final se estava digitando normalmente
            self.icursor(ctk.END)

    def _ao_perder_foco(self, event) -> None:
        texto_atual = self.get()
        formatado = self._formatar_cpf_texto(texto_atual)
        if formatado != texto_atual:
            self.delete(0, ctk.END)
            self.insert(0, formatado)

    def get_raw(self) -> str:
        """Retorna apenas os dígitos numéricos (string limpa) para o backend."""
        return re.sub(r"\D", "", self.get())

    def set_cpf(self, cpf: str) -> None:
        """Define o valor do campo aplicando a formatação correta."""
        self.configure(state="normal")
        self.delete(0, ctk.END)
        self.insert(0, self._formatar_cpf_texto(cpf))


class MetricCard(ctk.CTkFrame):
    """
    Card estilizado para exibição de métricas estruturais da Árvore AVL.
    """

    def __init__(
        self,
        master,
        titulo: str,
        valor_inicial: str = "-",
        subtitulo: str = "",
        cor_destaque: Optional[str] = None,
        **kwargs
    ):
        super().__init__(
            master,
            fg_color=COLOR_SURFACE_DARK,
            border_color=COLOR_BORDER,
            border_width=1,
            corner_radius=12,
            **kwargs
        )

        self.lbl_titulo = ctk.CTkLabel(
            self,
            text=titulo.upper(),
            font=FONT_CARD_TITLE,
            text_color=COLOR_TEXT_SECONDARY,
        )
        self.lbl_titulo.pack(anchor="w", padx=16, pady=(14, 4))

        self.lbl_valor = ctk.CTkLabel(
            self,
            text=valor_inicial,
            font=FONT_CARD_VALUE,
            text_color=cor_destaque if cor_destaque else COLOR_TEXT_PRIMARY,
        )
        self.lbl_valor.pack(anchor="w", padx=16, pady=(0, 4))

        self.lbl_subtitulo = ctk.CTkLabel(
            self,
            text=subtitulo,
            font=FONT_SMALL,
            text_color=COLOR_TEXT_MUTED,
        )
        self.lbl_subtitulo.pack(anchor="w", padx=16, pady=(0, 14))

    def atualizar_valor(self, novo_valor: str, novo_subtitulo: Optional[str] = None) -> None:
        self.lbl_valor.configure(text=novo_valor)
        if novo_subtitulo is not None:
            self.lbl_subtitulo.configure(text=novo_subtitulo)
