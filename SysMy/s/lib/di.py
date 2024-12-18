# https://okai.com.br/blog/o-que-e-preciso-saber-antes-de-operar-di-futuro

from datetime import datetime

def calcular_taxa_justa_em_taxa(taxa_atual, vencimento):
    """
    Calcula a taxa justa implícita para um contrato DI com base na taxa atual.

    :param taxa_atual: Taxa anual atual do contrato DI futuro (em decimal, ex: 0.152 para 15,20% ao ano)
    :param vencimento: Data de vencimento do contrato no formato 'YYYY-MM-DD' (ex: '2026-01-01')
    :return: Taxa justa implícita (em decimal, ex: 0.1025 para 10,25% ao ano)
    """
    # Data atual e vencimento
    data_hoje = datetime.today()
    data_vencimento = datetime.strptime(vencimento, '%Y-%m-%d')
    
    # Dias úteis no prazo (assumindo 252 dias úteis por ano)
    dias_corridos = (data_vencimento - data_hoje).days
    anos_uteis = dias_corridos / 252  # Converter para anos úteis

    # Validar dados de entrada
    if taxa_atual <= 0:
        raise ValueError("A taxa atual do contrato DI deve ser maior que zero.")
    if anos_uteis <= 0:
        raise ValueError("A data de vencimento deve ser futura.")

    # Cálculo da taxa justa implícita
    taxa_justa = (1 + taxa_atual) ** anos_uteis - 1
    return taxa_justa


def calcular_preco_contrato(taxa, dias_uteis):
    """
    Calcula o Preço Unitário (PU) de um contrato DI futuro
    
    :param taxa: Taxa anual do contrato (em decimal)
    :param dias_uteis: Dias úteis restantes até o vencimento
    :return: Preço Unitário do contrato
    """
    base_dias_uteis = 252  # Base padrão de dias úteis no ano
    
    pu = 100000 / (1 + taxa) ** (dias_uteis / base_dias_uteis)
    
    return pu

def calcular_taxa_implícita(taxa_atual):
    """
    Calcula a taxa implícita usando a taxa atual
    
    :param taxa_atual: Taxa atual do contrato (em decimal)
    :return: Taxa implícita (em percentual)
    """
    preco_contrato = calcular_preco_contrato(taxa_atual)
    taxa_implícita = (100000 / preco_contrato - 1) * 100
    return taxa_implícita

#taxa_atual = 0.1550
#taxa_implicita = calcular_taxa_implícita(taxa_atual)
#print(f"Taxa implícita: {taxa_implicita:.2f}% ao ano", calcular_preco_contrato(taxa_atual))




import pandas as pd
from pandas.tseries.holiday import BrazilianCalendar

def dias_uteis_b3(data_inicial_str, data_final_str):
    try:
        data_inicial = pd.to_datetime(data_inicial_str).date()
        data_final = pd.to_datetime(data_final_str).date()

        if data_final < data_inicial:
            raise ValueError("Data final anterior à data inicial.")

        cal = BrazilianCalendar()
        dias_uteis = pd.bdate_range(start=data_inicial, end=data_final, freq=cal)
        return len(dias_uteis)

    except ValueError as e:
        return str(e)
    except Exception as e:
        return f"Erro: {e}"

# Testes
print(dias_uteis_b3("2024-10-26", "2024-11-10"))  # Output: 11
print(dias_uteis_b3("2024-11-10", "2024-10-26"))  # Output: Data final anterior à data inicial.
print(dias_uteis_b3("2024-10-26", "data_invalida")) # Output: Erro: Invalid date specified








"""
if __name__ == "__main__":
  # Exemplo de uso
  taxa_atual = 0.152  # Taxa anual de 15,20%
  vencimento = "2026-01-02"

  taxa_justa = calcular_taxa_justa_em_taxa(taxa_atual, vencimento)
  print(f"Taxa justa implícita: {taxa_justa:.4%} ao ano")
"""