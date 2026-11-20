"""
Módulo de Segurança e Criptografia do AVL-AuthStore.

Implementa funções para hashing seguro de senhas e verificação criptográfica
utilizando PBKDF2 com algoritmo HMAC-SHA256 e salts gerados aleatoriamente.
"""

import hashlib
import os
import secrets


def hash_password(password: str, iterations: int = 100_000) -> str:
    """
    Gera um hash seguro para a senha informada utilizando PBKDF2-HMAC-SHA256.

    Estrutura do hash gerado:
        algoritmo$iterações$salt_hex$hash_hex

    Args:
        password: Senha em texto puro a ser protegida.
        iterations: Número de iterações do algoritmo KDF para desacelerar ataques de força bruta.

    Returns:
        String formatada contendo metadados, salt e hash derivado.
    """
    if not password:
        raise ValueError("A senha não pode ser vazia.")

    # Gera 16 bytes de salt criptograficamente seguro (128 bits de entropia)
    salt = secrets.token_bytes(16)

    # Deriva a chave criptográfica aplicando HMAC-SHA256 repetidamente
    key = hashlib.pbkdf2_hmac(
        hash_name="sha256",
        password=password.encode("utf-8"),
        salt=salt,
        iterations=iterations,
    )

    # Converte salt e chave para hexadecimal e monta a string de armazenamento
    salt_hex = salt.hex()
    key_hex = key.hex()
    return f"pbkdf2_sha256${iterations}${salt_hex}${key_hex}"


def verify_password(password: str, stored_hash: str) -> bool:
    """
    Verifica se a senha fornecida corresponde ao hash armazenado no payload.

    Args:
        password: Senha em texto puro informada na autenticação.
        stored_hash: String no formato algoritmo$iterações$salt_hex$hash_hex.

    Returns:
        True se a senha estiver correta, False caso contrário.
    """
    if not password or not stored_hash:
        return False

    try:
        parts = stored_hash.split("$")
        if len(parts) != 4:
            return False

        algorithm, iterations_str, salt_hex, key_hex = parts
        if algorithm != "pbkdf2_sha256":
            return False

        iterations = int(iterations_str)
        salt = bytes.fromhex(salt_hex)
        expected_key = bytes.fromhex(key_hex)

        # Recalcula o hash da senha enviada com os mesmos parâmetros e salt
        derived_key = hashlib.pbkdf2_hmac(
            hash_name="sha256",
            password=password.encode("utf-8"),
            salt=salt,
            iterations=iterations,
        )

        # Compara em tempo constante para mitigar ataques de temporização (Timing Attacks)
        return secrets.compare_digest(derived_key, expected_key)
    except Exception:
        return False
