import re

def limpiar_texto(texto):
    """
    Limpia el texto eliminando espacios múltiples, saltos innecesarios y dejando un texto limpio.
    """
    texto = re.sub(r'\s+', ' ', texto)  # elimina múltiples espacios
    texto = re.sub(r'\n+', '\n', texto)  # evita saltos de línea múltiples
    return texto.strip()
