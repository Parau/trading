import QuantLib as ql
from datetime import date, timedelta
import pandas as pd
import numpy as np

class AnaliseDICopom:
    def __init__(self, cdi_atual: float, contratos: list):
        """
        Inicializa a análise com CDI atual e contratos DI
        
        Args:
            cdi_atual (float): Taxa CDI atual em % ao ano
            contratos: Lista de tuplas (data_vencimento, taxa)
        """
        self.cdi_atual = cdi_atual
        self.contratos = contratos
        self.calendar = ql.Brazil()
        self.day_counter = ql.Business252()  # Convenção brasileira 252 dias úteis
        
    def criar_curva_di(self):
        """
        Cria a curva DI usando os contratos futuros
        """
        # Configura data inicial
        hoje = ql.Date().todaysDate()
        ql.Settings.instance().evaluationDate = hoje
        
        # Prepara os dados para a curva
        dates = [hoje]
        rates = [self.cdi_atual/100]
        
        for data_contrato, taxa in self.contratos:
            ql_date = ql.Date(data_contrato.day, data_contrato.month, data_contrato.year)
            dates.append(ql_date)
            rates.append(taxa/100)
            
        # Cria a curva
        curve = ql.MonotonicCubicZeroCurve(dates, rates, self.day_counter, self.calendar)
        curve.enableExtrapolation()
        
        return curve
    
    def calcular_implicita_di(self):
        """
        Calcula a taxa implícita considerando o juro atual e o valor do contrato atual.
        """
        premios = []
        for data, taxa in self.contratos:
            premio = round(taxa - self.cdi_atual, 3)
            du = self.calendar.businessDaysBetween(
                ql.Date().todaysDate(),
                ql.Date(data.day, data.month, data.year)
            )
            premios.append({
                'data': data.strftime('%d/%m/%Y'),
                'taxa_di': taxa,
                'premio': premio,
                'dias_uteis': du
            })
        return premios
    
    def calcular_expectativas_copom(self):
        """
        Calcula as expectativas implícitas para as reuniões do COPOM
        """
        curve = self.criar_curva_di()
        
        # Datas aproximadas das próximas reuniões do COPOM
        datas_copom = [
            # 2025
            date(2025, 1, 30),  # Janeiro
            date(2025, 3, 20),  # Março
            date(2025, 5, 8),   # Maio
            date(2025, 6, 26),  # Junho
            date(2025, 7, 31),  # Julho
            date(2025, 9, 18),  # Setembro
            date(2025, 11, 6),  # Novembro
            date(2025, 12, 11), # Dezembro

            # 2026
            date(2026, 1, 30),  # Janeiro
            date(2026, 3, 26),  # Março
            date(2026, 5, 7),   # Maio
            date(2026, 6, 18),  # Junho
            date(2026, 7, 23),  # Julho
            date(2026, 9, 26),  # Setembro
        ]
        
        expectativas = []
        taxa_anterior = self.cdi_atual
        
        for data_copom in datas_copom:
            ql_date = ql.Date(data_copom.day, data_copom.month, data_copom.year)
            
            # Taxa forward até a data do COPOM
            taxa_forward = curve.forwardRate(
                ql.Date().todaysDate(),
                ql_date,
                self.day_counter,
                ql.Simple
            ).rate() * 100
            
            # Variação esperada
            variacao = round(taxa_forward - taxa_anterior, 3)
            
            expectativas.append({
                'data_copom': data_copom.strftime('%d/%m/%Y'),
                'taxa_esperada': round(taxa_forward, 3),
                'variacao': variacao
            })
            
            taxa_anterior = taxa_forward
            
        return expectativas

def exemplo_uso():
    # Dados de entrada
    cdi_atual = 12.25
    contratos = [
        (date(2025, 1, 2), 12.165),  # DI1F25
        (date(2025, 7, 1), 14.020),  # DI1N25
        (date(2026, 1, 2), 14.930),  # DI1F26
        (date(2026, 7, 1), 15.165),  # DI1N26
        (date(2027, 1, 2), 15.060),  # DI1F27
        (date(2027, 7, 1), 14.850),  # DI1N27
        (date(2028, 1, 2), 14.630),  # DI1F28
        (date(2028, 7, 1), 14.470),  # DI1N28
        (date(2029, 1, 2), 14.320),  # DI1F29
        (date(2029, 7, 1), 14.180),  # DI1N29
        (date(2030, 1, 2), 14.090),  # DI1F30
        (date(2030, 7, 1), 13.950),  # DI1N30
        (date(2031, 1, 2), 13.880),  # DI1F31
        (date(2032, 1, 2), 13.700),  # DI1F32
    ]
    
    # Inicializa análise
    analise = AnaliseDICopom(cdi_atual, contratos)
    
    # Calcula prêmios
    premios = analise.calcular_implicita_di()
    print("Taxa implícita:")
    for p in premios:
        print(f"Data: {p['data']}, Taxa atual: {p['taxa_di']}%, Prêmio: {p['premio']}%, DU: {p['dias_uteis']}")
    
    print("\nExpectativas implícitas COPOM 2025:")
    expectativas = analise.calcular_expectativas_copom()
    for exp in expectativas:
        print(f"COPOM {exp['data_copom']}: {exp['taxa_esperada']}% ({exp['variacao']:+.3f}%)")

if __name__ == "__main__":
    exemplo_uso()