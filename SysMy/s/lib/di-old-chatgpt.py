# https://okai.com.br/blog/o-que-e-preciso-saber-antes-de-operar-di-futuro

from datetime import datetime
from ambima import dias_uteis, dias_uteis_no_ano




def calcular_preco_contrato(taxa, dias_uteis):
    """
    Calcula o Preço Unitário (PU) de um contrato DI futuro
    
    :param taxa: Taxa anual do contrato (em decimal)
    :param dias_uteis: Dias úteis restantes até o vencimento
    :return: Preço Unitário do contrato
    """
    base_dias_uteis = 252 #dias_uteis_no_ano(datetime.today().year)  # Base de dias úteis no ano
    
    pu = 100000 / (1 + taxa) ** (dias_uteis / base_dias_uteis)
    
    return pu

def calcular_cdi_acumulado(taxa_di, dias_uteis):
    """
    Calcula o CDI acumulado estimado ao final do contrato.
    
    :param taxa_di: Taxa DI futura (% ao ano).
    :param dias_uteis: Número de dias úteis até o vencimento do contrato.
    :return: CDI acumulado estimado.
    """
    # Taxa DI futura para o cálculo do PU
    pu = 100000 / ((1 + taxa_di / 100) ** (dias_uteis / 252))
    
    # CDI acumulado estimado
    cdi_acumulado = (100000 / pu) ** (252 / dias_uteis) - 1
    return cdi_acumulado

def calcular_cdi_acumulado2(taxa_di, dias_uteis):
    """
    Calcula o CDI acumulado estimado ao final do contrato.
    
    :param taxa_di: Taxa DI futura (% ao ano).
    :param dias_uteis: Número de dias úteis até o vencimento do contrato.
    :return: CDI acumulado estimado (% no período).
    """
    # Calcula o CDI acumulado para o período
    cdi_acumulado = (1 + taxa_di / 100) ** (dias_uteis / 252) - 1
    return cdi_acumulado

def calcular_cdi_total(cdi_hoje, taxa_di, dias_uteis):
    """
    Calcula o CDI total estimado ao final do contrato, considerando o CDI acumulado até hoje.
    
    :param cdi_hoje: CDI acumulado até a data atual (em decimal, ex: 0.06 para 6%).
    :param taxa_di: Taxa DI futura (em decimal, ex: 0.1520 para 15.20% ao ano).
    :param dias_uteis: Número de dias úteis restantes até o vencimento.
    :return: CDI total estimado (em decimal).
    """
    # CDI futuro implícito
    cdi_futuro = (1 + taxa_di) ** (dias_uteis / 252) - 1
    
    # CDI total acumulado
    cdi_total = (1 + cdi_hoje) * (1 + cdi_futuro) - 1
    return cdi_total

if __name__ == "__main__":
  # Exemplo de uso
  taxa_atual = 0.152  # Taxa anual de 15,20%
  cdi_hoje = 0.1225 #CDI de 12,25%
  vencimento = "2026-07-01"

  data_hoje = datetime.today().date()
  data_vencimento = datetime.strptime(vencimento, '%Y-%m-%d').date()
  d_uteis = dias_uteis(data_hoje, data_vencimento)
  print(f"dias uteis: {d_uteis}")

  preco_contrato = calcular_preco_contrato(taxa_atual, d_uteis)
  print(f"Preço do contrato: {preco_contrato} ao ano")

  #cdi_estimado = calcular_cdi_acumulado2(taxa_atual*100, d_uteis)
  #print(f"CDI estimado ao final do contrato: {cdi_estimado:.2%}")

  cdi_estimado_total = calcular_cdi_total(cdi_hoje, taxa_atual, d_uteis)
  print(f"CDI estimado ao final do contrato (usando selic): {cdi_estimado_total:.2%}")


  #taxa_justa = calcular_taxa_justa_em_taxa(taxa_atual, vencimento)
  #print(f"Taxa justa implícita: {taxa_justa:.2%} ao ano")


  #=================================================================================================
  def calcular_taxa_implícita(taxa_atual):
    """
    Calcula a taxa implícita usando a taxa atual
    
    :param taxa_atual: Taxa atual do contrato (em decimal)
    :return: Taxa implícita (em percentual)
    """
    preco_contrato = calcular_preco_contrato(taxa_atual)
    taxa_implícita = (100000 / preco_contrato - 1) * 100
    return taxa_implícita

def calcular_taxa_justa_em_taxa(taxa_atual, vencimento):
    """
    Calcula a taxa justa implícita para um contrato DI com base na taxa atual.

    :param taxa_atual: Taxa anual atual do contrato DI futuro (em decimal, ex: 0.152 para 15,20% ao ano)
    :param vencimento: Data de vencimento do contrato no formato 'YYYY-MM-DD' (ex: '2026-01-01')
    :return: Taxa justa implícita (em decimal, ex: 0.1025 para 10,25% ao ano)
    """
    # Data atual e vencimento
    data_hoje = datetime.today().date()
    data_vencimento = datetime.strptime(vencimento, '%Y-%m-%d').date()
    
    # Dias úteis no prazo
    dias_corridos = dias_uteis(data_hoje, data_vencimento)
    anos_uteis = dias_corridos / dias_uteis_no_ano(data_hoje.year)  # Converter para anos úteis

    # Validar dados de entrada
    if taxa_atual <= 0:
        raise ValueError("A taxa atual do contrato DI deve ser maior que zero.")
    if anos_uteis <= 0:
        raise ValueError("A data de vencimento deve ser futura.")

    # Cálculo da taxa justa implícita
    taxa_justa = (1 + taxa_atual) ** anos_uteis - 1
    return taxa_justa