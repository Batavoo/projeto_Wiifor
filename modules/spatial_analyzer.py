import pandas as pd
from shapely.geometry import Point
from shapely.wkt import loads as wkt_loads

def load_polygons(filepath, name_col, wkt_col):
    """
    Carrega um arquivo CSV de polígonos e o converte em uma lista de
    tuplas (nome, objeto_poligono).
    """
    try:
        df = pd.read_csv(filepath)
        polygons = []
        for _, row in df.iterrows():
            # Converte a string WKT em um objeto de polígono real
            polygon_geom = wkt_loads(row[wkt_col])
            polygons.append((row[name_col], polygon_geom))
        print(f"Sucesso: {len(polygons)} polígonos carregados de '{filepath}'.")
        return polygons
    except Exception as e:
        print(f"ERRO ao carregar polígonos de '{filepath}': {e}")
        return []

def find_containing_polygon(point, polygons_list):
    """
    Encontra o nome do polígono que contém um determinado ponto.
    """
    for name, polygon in polygons_list:
        if polygon.contains(point):
            return name
    return "Fora de Área" # Retorno padrão se nenhum polígono contiver o ponto

def apply_spatial_analysis(df):
    """
    Aplica a análise espacial ao DataFrame, adicionando colunas de bairro e regional.
    """
    print("\nIniciando análise espacial para bairros e regionais...")

    # Carrega os polígonos dos arquivos CSV
    bairros_polygons = load_polygons(
        filepath="poligonos/Bairros_de_Fortaleza.csv",
        name_col="nome",
        wkt_col="WKT"
    )
    regionais_polygons = load_polygons(
        filepath="poligonos/Regionais_de_Fortaleza.csv", # Supondo que este seja o nome do arquivo
        name_col="nome",
        wkt_col="WKT"
    )

    # Prepara listas para armazenar os resultados
    bairros = []
    regionais = []

    # Itera sobre cada linha do DataFrame de hosts
    for _, row in df.iterrows():
        # Verifica se há dados de latitude/longitude válidos
        if pd.notna(row['latitude']) and pd.notna(row['longitude']):
            # Cria um objeto Point para a coordenada atual
            point = Point(row['longitude'], row['latitude'])
            
            # Encontra o bairro e a regional correspondentes
            bairro = find_containing_polygon(point, bairros_polygons)
            regional = find_containing_polygon(point, regionais_polygons)
            
            bairros.append(bairro)
            regionais.append(regional)
        else:
            # Adiciona valores nulos se não houver coordenadas
            bairros.append(None)
            regionais.append(None)

    # Adiciona os resultados como novas colunas no DataFrame
    df['bairro'] = bairros
    df['regional'] = regionais
    
    print("Análise espacial finalizada.")
    return df