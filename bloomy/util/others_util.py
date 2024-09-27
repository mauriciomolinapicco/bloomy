from django.core.exceptions import ValidationError

def validate_password(password, password_confirmation):
    """
    Valida a segurança de uma senha e sua confirmação.

    Esta função verifica se a senha e sua confirmação coincidem,
    e se a senha atende aos requisitos de segurança:
    - Deve ter pelo menos 8 caracteres.
    - Deve conter pelo menos um dígito.
    - Deve conter pelo menos uma letra (maiúscula e minúscula).

    Args:
        password (str): A senha a ser validada.
        password_confirmation (str): A confirmação da senha.

    Raises:
        ValidationError: Se as senhas não coincidirem ou se a senha
        não atender aos requisitos de segurança.

    Returns:
        None: Se a senha for válida, nenhuma exceção é lançada.
    """
    if password != password_confirmation:
        return 'As senhas não coincidem'
    if len(password) < 8:
        return 'A senha deve ter pelo menos 8 caracteres'
    if not any(char.isdigit() for char in password):
        return 'A senha deve conter pelo menos um dígito'
    if not any(char.isalpha() for char in password):
        return 'A senha deve conter pelo menos uma letra'
    if not any(char.isupper() for char in password):
        return 'A senha deve conter pelo menos uma letra maiúscula'
    if not any(char.islower() for char in password):
        return 'A senha deve conter pelo menos uma letra minúscula'
    return None


def validate_quantity(quantity):
    """
    Valida a quantidade informada.

    Esta função verifica se a quantidade é um número inteiro
    e se está dentro do intervalo permitido (1 a 9).

    Args:
        quantity (str|int): A quantidade a ser validada.

    Raises:
        ValidationError: Se a quantidade não for um inteiro ou
        se estiver fora do intervalo permitido.

    Returns:
        None: Se a quantidade for válida, nenhuma exceção é lançada.
    """
    try:
        quantity = int(quantity)
    except ValueError:
        raise ValidationError("A quantidade deve ser um integer.")

    if quantity < 1 or quantity > 9:
        raise ValidationError("A quantidade deve estar entre 1 e 9.")
