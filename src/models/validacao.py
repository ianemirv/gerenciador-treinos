"""Funções de validação usadas por todas as classes.

Elas aceitam tanto números quanto textos (como os que vêm do input()),
convertem para o tipo certo e lançam ValueError com uma mensagem clara
quando o valor é inválido.
"""


def texto_obrigatorio(valor, campo):
    texto = str(valor).strip() if valor is not None else ""
    if not texto:
        raise ValueError(f"O campo '{campo}' não pode ficar vazio.")
    return texto


def numero_positivo(valor, campo, permitir_zero=False):
    try:
        numero = float(str(valor).replace(",", "."))
    except (TypeError, ValueError):
        raise ValueError(f"O campo '{campo}' precisa ser um número.")
    if numero < 0 or (numero == 0 and not permitir_zero):
        condicao = "maior ou igual a zero" if permitir_zero else "maior que zero"
        raise ValueError(f"O campo '{campo}' precisa ser {condicao}.")
    return numero


def inteiro_positivo(valor, campo, permitir_zero=False):
    numero = numero_positivo(valor, campo, permitir_zero)
    if not numero.is_integer():
        raise ValueError(f"O campo '{campo}' precisa ser um número inteiro.")
    return int(numero)
