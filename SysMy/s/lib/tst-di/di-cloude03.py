from datetime import date, datetime, timedelta
from typing import List, Tuple, Dict
import math
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import numpy as np
from matplotlib.ticker import PercentFormatter

class CalculadoraDIFuturo:
    def __init__(self, cdi_atual: float = None):
        self.dias_uteis_ano = 252
        self.dias_totais_ano = 365
        self.cdi_atual = cdi_atual
    
    # [Métodos anteriores permanecem iguais]
    def calcular_cdi_estimado(self, 
                            taxa_di_futuro: float,
                            data_inicio: date,
                            data_vencimento: date) -> dict:
        dias_totais = (data_vencimento - data_inicio).days
        dias_uteis = int(dias_totais * (self.dias_uteis_ano/self.dias_totais_ano))
        
        taxa_di_diaria = ((1 + taxa_di_futuro/100) ** (1/self.dias_uteis_ano)) - 1
        fator_acumulado = (1 + taxa_di_diaria) ** dias_uteis
        cdi_estimado = ((fator_acumulado - 1) * (self.dias_uteis_ano/dias_uteis)) * 100
        taxa_periodo = (fator_acumulado - 1) * 100
        
        return {
            'cdi_estimado_aa': round(cdi_estimado, 4),
            'taxa_periodo': round(taxa_periodo, 4),
            'taxa_diaria': round(taxa_di_diaria * 100, 4),
            'dias_uteis': dias_uteis,
            'dias_totais': dias_totais
        }
    
    def calcular_premio_cdi(self, taxa_di_futuro: float) -> float:
        if self.cdi_atual is None:
            raise ValueError("CDI atual não foi definido na inicialização")
        return round(taxa_di_futuro - self.cdi_atual, 4)
    
    def calcular_forward_rate(self, 
                            taxa1: float, 
                            taxa2: float,
                            data1: date,
                            data2: date) -> dict:
        if data2 <= data1:
            raise ValueError("Data 2 deve ser posterior à Data 1")
            
        dias_totais = (data2 - data1).days
        dias_uteis = int(dias_totais * (self.dias_uteis_ano/self.dias_totais_ano))
        
        fator1 = (1 + taxa1/100)
        fator2 = (1 + taxa2/100)
        
        hoje = date.today()
        du_t1 = int((data1 - hoje).days * (self.dias_uteis_ano/self.dias_totais_ano))
        du_t2 = int((data2 - hoje).days * (self.dias_uteis_ano/self.dias_totais_ano))
        
        fator_forward = ((fator2 ** (du_t2/self.dias_uteis_ano)) / 
                        (fator1 ** (du_t1/self.dias_uteis_ano))) ** (self.dias_uteis_ano/(du_t2-du_t1))
        taxa_forward = (fator_forward - 1) * 100
        
        premio_v1 = taxa_forward - taxa1
        
        return {
            'taxa_forward': round(taxa_forward, 4),
            'premio_v1': round(premio_v1, 4),
            'dias_uteis': dias_uteis,
            'periodo': f"{data1.strftime('%d/%m/%Y')} - {data2.strftime('%d/%m/%Y')}"
        }

    def plotar_curva_juros(self, contratos: List[Tuple[date, float]], titulo: str = "Curva de Juros DI Futuro"):
        """
        Plota a curva de juros com os vencimentos
        """
        # Prepara dados
        datas = [c[0] for c in contratos]
        taxas = [c[1] for c in contratos]
        
        # Configuração do plot
        plt.figure(figsize=(12, 6))
        
        # Plot principal
        plt.plot(datas, taxas, 'bo-', label='Taxa DI Futuro')
        
        # Adiciona CDI atual se disponível
        if self.cdi_atual is not None:
            plt.axhline(y=self.cdi_atual, color='r', linestyle='--', label=f'CDI Atual ({self.cdi_atual}%)')
        
        # Configurações do gráfico
        plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%d/%m/%y'))
        plt.gca().yaxis.set_major_formatter(PercentFormatter())
        
        plt.title(titulo)
        plt.xlabel('Data de Vencimento')
        plt.ylabel('Taxa (% a.a.)')
        plt.grid(True, linestyle='--', alpha=0.7)
        plt.legend()
        
        # Rotaciona labels do eixo x
        plt.xticks(rotation=45)
        
        # Ajusta layout
        plt.tight_layout()
        
        return plt.gcf()

    def plotar_taxas_forward(self, contratos: List[Tuple[date, float]], titulo: str = "Taxas Forward entre Vencimentos"):
        """
        Plota as taxas forward entre os vencimentos
        """
        # Calcula forwards
        forwards = []
        datas_meio = []
        for i in range(len(contratos)-1):
            data1, taxa1 = contratos[i]
            data2, taxa2 = contratos[i+1]
            
            forward = self.calcular_forward_rate(taxa1, taxa2, data1, data2)
            forwards.append(forward['taxa_forward'])
            
            # Calcula data média entre os vencimentos para posicionar a barra
            data_meio = data1 + (data2 - data1) / 2
            datas_meio.append(data_meio)
        
        # Configuração do plot
        plt.figure(figsize=(12, 6))
        
        # Plot de barras
        plt.bar(datas_meio, forwards, width=20, alpha=0.6, label='Taxa Forward')
        
        # Adiciona valores em cima das barras
        for i, v in enumerate(forwards):
            plt.text(mdates.date2num(datas_meio[i]), v + 0.1, f'{v:.2f}%', 
                    ha='center', va='bottom')
        
        # Configurações do gráfico
        plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%d/%m/%y'))
        plt.gca().yaxis.set_major_formatter(PercentFormatter())
        
        plt.title(titulo)
        plt.xlabel('Período')
        plt.ylabel('Taxa Forward (% a.a.)')
        plt.grid(True, linestyle='--', alpha=0.7)
        plt.legend()
        
        # Rotaciona labels do eixo x
        plt.xticks(rotation=45)
        
        # Ajusta layout
        plt.tight_layout()
        
        return plt.gcf()

    def analisar_expectativas_copom(self, contratos: List[Tuple[date, float]]) -> List[Dict]:
        """
        Analisa as expectativas implícitas de decisões do COPOM baseado na curva
        """
        # Datas aproximadas das reuniões do COPOM em 2024-2026
        # Normalmente são 8 reuniões por ano, aproximadamente a cada 45 dias
        datas_copom = []
        data_base = date(2024, 1, 31)  # Primeira reunião de 2024
        
        while data_base <= date(2026, 12, 31):
            datas_copom.append(data_base)
            data_base += timedelta(days=45)  # Aproximação das reuniões
        
        # Análise por período entre vencimentos
        analise_copom = []
        for i in range(len(contratos)-1):
            data1, taxa1 = contratos[i]
            data2, taxa2 = contratos[i+1]
            
            # Calcula taxa forward do período
            forward = self.calcular_forward_rate(taxa1, taxa2, data1, data2)
            
            # Conta reuniões do COPOM no período
            reunioes_periodo = len([d for d in datas_copom 
                                  if data1 <= d <= data2])
            
            # Calcula mudança necessária por reunião
            mudanca_total = forward['taxa_forward'] - taxa1
            mudanca_por_reuniao = mudanca_total / max(1, reunioes_periodo)
            
            analise_copom.append({
                'periodo': forward['periodo'],
                'taxa_forward': forward['taxa_forward'],
                'taxa_inicial': taxa1,
                'taxa_final': taxa2,
                'mudanca_total': round(mudanca_total, 3),
                'reunioes_copom': reunioes_periodo,
                'mudanca_por_reuniao': round(mudanca_por_reuniao, 3)
            })
            
        return analise_copom
    
    def imprimir_analise_detalhada(self, contratos: List[Tuple[date, float]]):
        """
        Imprime análise detalhada da curva no console
        """
        print("\n=== ANÁLISE DETALHADA DA CURVA DI FUTURO ===")
        print(f"\nData da análise: {date.today().strftime('%d/%m/%Y')}")
        print(f"CDI atual: {self.cdi_atual}% a.a.")
        
        # 1. Curva de juros
        print("\n1. CURVA DE JUROS")
        print("-" * 50)
        print(f"{'Vencimento':<12} {'Taxa':<8} {'Prêmio CDI':<12} {'CDI Est.':<10}")
        print("-" * 50)
        
        for data, taxa in contratos:
            premio = self.calcular_premio_cdi(taxa)
            cdi_est = self.calcular_cdi_estimado(taxa, date.today(), data)
            print(f"{data.strftime('%d/%m/%Y'):<12} "
                  f"{taxa:<8.3f} "
                  f"{premio:<12.3f} "
                  f"{cdi_est['cdi_estimado_aa']:<10.3f}")
        
        # 2. Taxas Forward
        print("\n2. TAXAS FORWARD")
        print("-" * 70)
        print(f"{'Período':<25} {'Taxa Forward':<12} {'Prêmio v1':<12} {'Dias Úteis':<10}")
        print("-" * 70)
        
        for i in range(len(contratos)-1):
            data1, taxa1 = contratos[i]
            data2, taxa2 = contratos[i+1]
            forward = self.calcular_forward_rate(taxa1, taxa2, data1, data2)
            
            print(f"{forward['periodo']:<25} "
                  f"{forward['taxa_forward']:<12.3f} "
                  f"{forward['premio_v1']:<12.3f} "
                  f"{forward['dias_uteis']:<10}")
        
        # 3. Expectativas COPOM
        print("\n3. EXPECTATIVAS IMPLÍCITAS DO COPOM")
        print("-" * 90)
        print(f"{'Período':<25} {'Forward':<8} {'Mudança':<10} {'Reuniões':<10} {'Mud/Reunião':<12}")
        print("-" * 90)
        
        analise_copom = self.analisar_expectativas_copom(contratos)
        for analise in analise_copom:
            print(f"{analise['periodo']:<25} "
                  f"{analise['taxa_forward']:<8.3f} "
                  f"{analise['mudanca_total']:>+10.3f} "
                  f"{analise['reunioes_copom']:^10} "
                  f"{analise['mudanca_por_reuniao']:>+12.3f}")

    def encontrar_di_mais_proximo(self, contratos: List[Tuple[date, float]], 
                                 data_alvo: date) -> Tuple[date, float]:
        """
        Encontra o contrato DI mais próximo de uma data específica
        """
        if not contratos:
            return None
            
        # Ordena contratos por proximidade à data alvo
        contratos_ordenados = sorted(contratos, 
                                   key=lambda x: abs((x[0] - data_alvo).days))
        return contratos_ordenados[0]
    
    def analisar_expectativas_por_reuniao(self, 
                                         contratos: List[Tuple[date, float]]) -> List[Dict]:
        """
        Analisa expectativas para cada reunião do COPOM usando os DIs mais próximos
        """
        # Datas aproximadas das próximas reuniões do COPOM
        datas_copom_2024 = [
            date(2024, 1, 31),
            date(2024, 3, 20),
            date(2024, 5, 8),
            date(2024, 6, 19),
            date(2024, 8, 1),
            date(2024, 9, 18),
            date(2024, 11, 7),
            date(2024, 12, 11)
        ]
        
        datas_copom_2025 = [
            date(2025, 1, 29),
            date(2025, 3, 19),
            date(2025, 5, 7),
            date(2025, 6, 18),
            date(2025, 7, 30),
            date(2025, 9, 17),
            date(2025, 11, 5),
            date(2025, 12, 10)
        ]
        
        datas_copom_2026 = [
            date(2026, 1, 28),
            date(2026, 3, 18),
            date(2026, 5, 6),
            date(2026, 6, 17),
            date(2026, 7, 29),
            date(2026, 9, 16),
            date(2026, 11, 4),
            date(2026, 12, 9)
        ]
        
        datas_copom = datas_copom_2024 + datas_copom_2025 + datas_copom_2026
        
        # Análise por reunião
        analise_reunioes = []
        taxa_anterior = self.cdi_atual
        
        for data_copom in datas_copom:
            if data_copom <= date.today():
                continue
                
            # Encontra DI mais próximo
            contrato_proximo = self.encontrar_di_mais_proximo(contratos, data_copom)
            if contrato_proximo:
                data_di, taxa_di = contrato_proximo
                
                # Calcula mudança esperada
                mudanca = taxa_di - taxa_anterior
                
                analise_reunioes.append({
                    'data_copom': data_copom,
                    'di_proximo': data_di,
                    'taxa_di': taxa_di,
                    'taxa_anterior': taxa_anterior,
                    'mudanca_esperada': round(mudanca, 3)
                })
                
                taxa_anterior = taxa_di
        
        return analise_reunioes
    
    def imprimir_analise_reunioes(self, contratos: List[Tuple[date, float]]):
        """
        Imprime análise detalhada por reunião do COPOM
        """
        print("\n=== ANÁLISE POR REUNIÃO DO COPOM ===")
        print(f"\nData da análise: {date.today().strftime('%d/%m/%Y')}")
        print(f"CDI atual: {self.cdi_atual}% a.a.")
        
        analise = self.analisar_expectativas_por_reuniao(contratos)
        
        print("\nExpectativas por Reunião:")
        print("-" * 85)
        print(f"{'Data COPOM':<12} {'DI Ref.':<12} {'Taxa DI':<10} {'Taxa Ant.':<10} {'Mudança':<12}")
        print("-" * 85)
        
        for a in analise:
            print(f"{a['data_copom'].strftime('%d/%m/%Y'):<12} "
                  f"{a['di_proximo'].strftime('%d/%m/%Y'):<12} "
                  f"{a['taxa_di']:<10.3f} "
                  f"{a['taxa_anterior']:<10.3f} "
                  f"{a['mudanca_esperada']:>+12.3f}")

def exemplo_completo():
    # CDI atual
    cdi_atual = 12.25
    
    # Valor atual taxa DI futuro
    contratos = [
        (date(2025, 1, 2), 12.183),
        (date(2025, 7, 1), 14.100),
        (date(2026, 1, 2), 15.100),
        (date(2026, 7, 1), 15.435),
        (date(2026, 7, 4), 15.405)
    ]
    
    # Inicializa calculadora
    calc = CalculadoraDIFuturo(cdi_atual=cdi_atual)
    
    # Imprime análise por reunião
    calc.imprimir_analise_reunioes(contratos)
    
    # Imprime análise forward (mantida do código anterior)
    calc.imprimir_analise_detalhada(contratos)

if __name__ == "__main__":
    exemplo_completo()