import math
from datetime import datetime, date
from typing import List, Tuple
import numpy as np

class AnaliseDIFuturo:
    def __init__(self, cdi_atual: float):
        """
        Inicializa a análise com o CDI atual
        
        Args:
            cdi_atual (float): Taxa CDI atual em % ao ano
        """
        self.cdi_atual = cdi_atual
    
    def calcular_cdi_estimado(self, taxa_di_futuro: float, data_inicio: date, 
                            data_vencimento: date) -> float:
        """
        Calcula o CDI estimado com base na taxa do DI Futuro
        """
        taxa_di_252 = ((taxa_di_futuro / 100) + 1) ** (1/252)
        dias_totais = (data_vencimento - data_inicio).days
        dias_uteis = int(dias_totais * (252/365))
        
        fator_acumulado = taxa_di_252 ** dias_uteis
        cdi_estimado = ((fator_acumulado - 1) * 100) * (252/dias_uteis)
        
        return round(cdi_estimado, 2)
    
    def calcular_forward_rate(self, taxa1: float, taxa2: float, 
                            data1: date, data2: date) -> float:
        """
        Calcula a taxa forward entre dois vencimentos
        
        Args:
            taxa1 (float): Taxa do primeiro vencimento em % aa
            taxa2 (float): Taxa do segundo vencimento em % aa
            data1 (date): Data do primeiro vencimento
            data2 (date): Data do segundo vencimento
        
        Returns:
            float: Taxa forward em % aa
        """
        # Calcula os dias úteis entre as datas
        dias_uteis = int((data2 - data1).days * (252/365))
        
        # Converte taxas anuais para fatores diários
        fator1 = (1 + taxa1/100)
        fator2 = (1 + taxa2/100)
        
        # Calcula o fator forward
        du_t1 = int((data1 - date.today()).days * (252/365))
        du_t2 = int((data2 - date.today()).days * (252/365))
        
        fator_forward = ((fator2 ** (du_t2/252)) / (fator1 ** (du_t1/252))) ** (252/(du_t2-du_t1))
        
        # Converte fator para taxa
        forward = (fator_forward - 1) * 100
        
        return round(forward, 2)
    
    def gerar_curva_juros(self, contratos: List[Tuple[date, float]]) -> dict:
        """
        Gera a curva de juros completa usando os vencimentos disponíveis
        
        Args:
            contratos: Lista de tuplas (data_vencimento, taxa)
        
        Returns:
            dict: Dicionário com análises da curva
        """
        hoje = date.today()
        
        # Ordena contratos por data
        contratos_ordenados = sorted(contratos, key=lambda x: x[0])
        
        # Calcula forwards entre vencimentos consecutivos
        forwards = []
        for i in range(len(contratos_ordenados)-1):
            data1, taxa1 = contratos_ordenados[i]
            data2, taxa2 = contratos_ordenados[i+1]
            forward = self.calcular_forward_rate(taxa1, taxa2, data1, data2)
            forwards.append({
                'periodo': f"{data1.strftime('%d/%m/%y')} - {data2.strftime('%d/%m/%y')}",
                'taxa_forward': forward
            })
        
        # Calcula prêmios em relação ao CDI atual
        premios = []
        for data, taxa in contratos_ordenados:
            premio = round(taxa - self.cdi_atual, 2)
            premios.append({
                'data': data.strftime('%d/%m/%y'),
                'premio': premio
            })
        
        return {
            'vencimentos': [{'data': data.strftime('%d/%m/%y'), 'taxa': taxa}
                          for data, taxa in contratos_ordenados],
            'forwards': forwards,
            'premios_cdi': premios,
            'inclinacao_curva': round(contratos_ordenados[-1][1] - contratos_ordenados[0][1], 2)
        }

def exemplo_uso():
    # CDI atual
    cdi_atual = 12.25
    
    # Exemplo de contratos (data, taxa)
    contratos = [
        (date(2025, 1, 2), 12.183),
        (date(2025, 7, 1), 14.100),
        (date(2026, 1, 2), 15.100),
        (date(2026, 7, 1), 15.435),
        (date(2026, 7, 4), 15.405)
    ]
    
    # Inicializa análise
    analise = AnaliseDIFuturo(cdi_atual)
    
    # Gera curva completa
    curva = analise.gerar_curva_juros(contratos)
    
    # Imprime resultados
    print(f"CDI Atual: {cdi_atual}% a.a.\n")
    
    print("Curva de Juros:")
    for venc in curva['vencimentos']:
        print(f"Vencimento {venc['data']}: {venc['taxa']}% a.a.")
    
    print("\nTaxas Forward:")
    for fwd in curva['forwards']:
        print(f"{fwd['periodo']}: {fwd['taxa_forward']}% a.a.")
    
    print("\nPrêmios sobre CDI atual:")
    for premio in curva['premios_cdi']:
        print(f"Vencimento {premio['data']}: {premio['premio']}%")
    
    print(f"\nInclinação da Curva: {curva['inclinacao_curva']}%")

if __name__ == "__main__":
    exemplo_uso()