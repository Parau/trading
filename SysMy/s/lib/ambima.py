from datetime import datetime, timedelta
from ambima_feriados import FERIADOS  # Importa a lista de feriados do módulo ambima_feriados

def dias_uteis(data_inicial: datetime, data_final: datetime) -> int:
    """
    Calcula o número de dias úteis entre duas datas, considerando feriados nacionais.
    
    :param data_inicial: Data inicial (inclusive). Passar somente data e não data com hora. Ex.: datetime(2023, 1, 1).date()
    :param data_final: Data final (exclusive). Passar somente data e não data com hora. Ex.: datetime(2024, 1, 1).date()
    :return: Número de dias úteis entre as duas datas.
    """
    #print(f"Datas recebidas pelo dias_uteis para calculo: {data_inicial} e {data_final}")

    if data_inicial > data_final:
        data_inicial, data_final = data_final, data_inicial

    delta = timedelta(days=1)
    dias_uteis_contagem = 0

    while data_inicial < data_final:
        if data_inicial.weekday() < 5 and data_inicial not in FERIADOS:
            dias_uteis_contagem += 1
        data_inicial += delta

    return dias_uteis_contagem

def dias_uteis_no_ano(ano: int) -> int:
    """
    Calcula o número de dias úteis em um determinado ano.

    :param ano: Ano para o cálculo.
    :return: Número de dias úteis no ano especificado.
    """
    data_inicial = datetime(ano, 1, 1).date()
    data_final = datetime(ano + 1, 1, 1).date()

    #print(f"Datas que serão enviadas ao dias_uteis: {data_inicial} e {data_final}")

    return dias_uteis(data_inicial, data_final)

# Exemplos de uso
if __name__ == "__main__":
    # Exemplo: Dias úteis entre duas datas
    data1 = datetime(2023, 1, 1).date()
    data2 = datetime(2023, 1, 10).date()
    print(f"Dias úteis entre {data1} e {data2}: {dias_uteis(data1, data2)}")

    data1 = datetime(2023, 1, 1).date()
    data2 = datetime(2024, 1, 1).date()
    print(f"Dias úteis entre {data1} e {data2}: {dias_uteis(data1, data2)}")

    # Exemplo: Dias úteis em um ano
    ano = 2023
    print(f"Dias úteis no ano de {ano}: {dias_uteis_no_ano(ano)}")