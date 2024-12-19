import pandas as pd
from datetime import datetime

# Função para ler feriados de um arquivo Excel
def ler_feriados_excel(caminho_arquivo):
    """
    Lê as datas de feriados de um arquivo Excel.

    :param caminho_arquivo: Caminho para o arquivo Excel.
    :return: Conjunto de datas de feriados.
    """
    df = pd.read_excel(caminho_arquivo)
    df['Data'] = pd.to_datetime(df['Data']).dt.date  # Converte a coluna 'Data' para objetos date
    feriados = set(df['Data'])
    return feriados

# Caminho para o arquivo Excel
caminho_arquivo_excel = './ambima_feriados_nacionais.xlsx'

# Converta os feriados para objetos date para uso eficiente
FERIADOS = ler_feriados_excel(caminho_arquivo_excel)