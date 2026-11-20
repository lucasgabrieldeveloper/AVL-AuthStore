"""
Utilitários de formatação, validação de CPF e visualização gráfica de árvores.
"""

import re
from typing import Optional, List
from .models import AVLNode


def sanitizar_cpf(cpf: str) -> str:
    """
    Remove caracteres de formatação (pontos, traços e espaços) do CPF,
    deixando apenas dígitos numéricos.
    """
    if not cpf:
        return ""
    return re.sub(r"\D", "", cpf.strip())


def formatar_cpf(cpf: str) -> str:
    """
    Formata uma string de 11 dígitos numéricos para o padrão visual '000.000.000-00'.
    Caso não tenha 11 dígitos, retorna a representação sanitizada.
    """
    limpo = sanitizar_cpf(cpf)
    if len(limpo) == 11:
        return f"{limpo[:3]}.{limpo[3:6]}.{limpo[6:9]}-{limpo[9:]}"
    return limpo


def validar_cpf_digitos(cpf: str) -> bool:
    """
    Valida se o CPF é estruturalmente válido e calcula os dígitos verificadores
    de acordo com a regra oficial da Receita Federal do Brasil.
    """
    digitos = sanitizar_cpf(cpf)

    if len(digitos) != 11:
        return False

    # Rejeita CPFs com todos os dígitos idênticos (ex: 111.111.111-11)
    if digitos == digitos[0] * 11:
        return False

    # Cálculo do primeiro dígito verificador
    soma_1 = sum(int(digitos[i]) * (10 - i) for i in range(9))
    resto_1 = (soma_1 * 10) % 11
    d1 = 0 if resto_1 == 10 else resto_1
    if int(digitos[9]) != d1:
        return False

    # Cálculo do segundo dígito verificador
    soma_2 = sum(int(digitos[i]) * (11 - i) for i in range(10))
    resto_2 = (soma_2 * 10) % 11
    d2 = 0 if resto_2 == 10 else resto_2
    if int(digitos[10]) != d2:
        return False

    return True


def renderizar_arvore_ascii(raiz: Optional[AVLNode], prefixo: str = "", eh_filho_esq: bool = True) -> List[str]:
    """
    Gera uma representação textual visual da Árvore AVL em formato de diagrama de ramos.
    Exibe a chave (CPF), altura (h) e fator de balanceamento (FB) de cada nó.
    """
    linhas: List[str] = []
    if raiz is None:
        return linhas

    fb = (raiz.esquerda.altura if raiz.esquerda else 0) - (raiz.direita.altura if raiz.direita else 0)
    info_no = f"[{formatar_cpf(raiz.cpf)}] (h={raiz.altura}, FB={fb})"

    if raiz.direita is not None:
        linhas.extend(
            renderizar_arvore_ascii(
                raiz.direita,
                prefixo + ("│   " if eh_filho_esq else "    "),
                False,
            )
        )

    linhas.append(prefixo + ("└── " if eh_filho_esq else "┌── ") + info_no)

    if raiz.esquerda is not None:
        linhas.extend(
            renderizar_arvore_ascii(
                raiz.esquerda,
                prefixo + ("    " if eh_filho_esq else "│   "),
                True,
            )
        )

    return linhas
