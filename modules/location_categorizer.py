import re

def categorize_location(treated_name):
    """
    Categoriza um local com base em palavras-chave em seu nome tratado.
    A função foi projetada para ser facilmente extensível.

    Args:
        treated_name (str): O nome do local já limpo e padronizado.

    Returns:
        str: A categoria do local.
    """
    if not isinstance(treated_name, str) or not treated_name:
        return "Não Categorizado"

    # Converte para minúsculas para uma comparação que não diferencia maiúsculas/minúsculas
    lower_name = treated_name.lower()

    # A ordem das verificações é importante para a precisão
    if 'areninha' in lower_name:
        return "Areninha"
    
    if 'calçadao' in lower_name or 'calcadao' in lower_name:
        return "Calçadão"

    if 'cuca' in lower_name:
        return "Cuca"

    if 'praça' in lower_name or 'praca' in lower_name:
        return "Praça"
        
    if 'uaps' in lower_name:
        return "UAPS"

    if 'parque' in lower_name and 'rua' not in lower_name:
        return "Parque"

    # Palavras-chave para identificar vias públicas
    via_publica_keywords = ['avenida', 'rua', ' com ', 'px', 'r do', 'ix']
    if any(keyword in lower_name for keyword in via_publica_keywords):
        return "Via Pública"

    # Categoria padrão se nenhuma das anteriores corresponder
    return "Local Público"