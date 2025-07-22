import re

def standardize_address_name(raw_name):
    """
    Recebe um nome de host bruto do Zabbix e o converte em um endereço padronizado.
    """
    if not isinstance(raw_name, str):
        return ""

    # 1. Normalização inicial: maiúsculas, separadores padrão
    name = raw_name.upper()
    name = name.replace('.', '-')
    name = name.replace('|', ' ') # Adicionado para remover o caractere '|'

    # 2. Remover prefixos comuns e o ID inicial.
    name = re.sub(r'^(CITINOVA-WIFI|CITINOVA-SEGER|CITINOVA-FLA|CITINOVA-SCSP|CITINOVA-AMC|CITINOVAWIFI|AP-\d+)-?\d*-?', '', name)
    name = re.sub(r'^(CITINOVA)-?', '', name)

    # 3. Remover palavras-chave de projeto que aparecem no meio do nome.
    # A regra para 'WIFOR' foi melhorada para remover números associados.
    unwanted_patterns = [
        r'\b(CLI|CITINOVA|WIFI)\b',
        r'\bWIFOR([-\s]*\d+)*\b',     # Remove "WIFOR", "WIFOR 01", "WIFOR-24", etc.
        r'\bPOSTE([-\s]*\d+)*\b',
        r'\bP[-\s]+\d+\b'             # Adicionado para remover "P-41", "P 41", etc.
    ]
    for pattern in unwanted_patterns:
        name = re.sub(pattern, '', name)

    # 4. Padronizar termos de endereço e cruzamentos
    name = name.replace('-X-', ' com ')
    
    replacements = {
        'AV-': 'Avenida ', 'RUA-': 'Rua ',
        'SEN-': 'Senador ', 'DES-': 'Desembargador ',
        'PRES-': 'Presidente ', 'DR-': 'Doutor ', 'HIST-': 'Historiador ',
        'GEN-': 'General ', 'PE-': 'Padre ', 'MAL-': 'Marechal '
    }
    for old, new in replacements.items():
        name = name.replace(old, new)

    # 5. Limpeza final
    name = re.sub(r'#.*', '', name) # Remove '#' e tudo que vem depois
    name = name.replace('-', ' ')
    name = re.sub(r'\s{2,}', ' ', name).strip() # Remove espaços duplos
    name = re.sub(r'^\d+\s', '', name) # Remove números no início da string
    
    # Capitaliza de forma inteligente (title case) e ajusta preposições
    name = name.title()
    for word in ['De', 'Da', 'Do', 'Dos', 'Das', 'E', 'Com']:
        name = name.replace(' ' + word + ' ', ' ' + word.lower() + ' ')
        
    return name.strip()