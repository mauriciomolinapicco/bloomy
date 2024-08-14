from django.core.exceptions import ValidationError

def validate_password(password, password_confirmation):
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
    try:
        quantity = int(quantity)
    except ValueError:
        raise ValidationError("A quantidade deve ser um integer.")

    if quantity < 1 or quantity > 9:
        raise ValidationError("A quantidade deve estar entre 1 e 9.")
