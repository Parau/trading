"""
Módulo principal de análise de opções para negociação de futuros do dólar,
focado na identificação de níveis de suporte e resistência através da exposição ao gamma.
"""

import numpy as np
import pandas as pd
from scipy.stats import norm
from sklearn.cluster import DBSCAN

try:
    # Para importação como parte de um pacote (por exemplo, na aplicação servidor)
    from .data_loader import OptionsDataLoader
except ImportError:
    # Funciona quando o script é executado diretamente (teste em console)
    from data_loader import OptionsDataLoader

try:
    from .config import *
except ImportError:
    from config import *


class OptionsAnalysis:
    def __init__(self, current_price, contract_filter, calls='calls.csv', puts='puts.csv'):
        # Carrega e prepara os dados
        with open(calls, 'r', encoding='utf-8') as f:
            calls_csv = f.read()
    
        with open(puts, 'r', encoding='utf-8') as f:
            puts_csv = f.read()

        loader = OptionsDataLoader()
        self.df = loader.prepare_data(calls_csv, puts_csv, contract_filter)
        self.current_price = current_price

    def getOptionsData(self):
        return self.df

    def calculate_gamma(self, S, K, T, r, sigma):
        """
        Calcula o gamma de uma opção usando a fórmula Black–Scholes.
        Note que o gamma é o mesmo para calls e puts.
        """
        d1 = (np.log(S / K) + (r + 0.5 * sigma**2) * T) / (sigma * np.sqrt(T))
        gamma = norm.pdf(d1) / (S * sigma * np.sqrt(T))
        return gamma

    def calculate_gamma_exposure(self, days_to_expiry):
        """
        Calcula a exposição total de gamma, considerando o lado da opção.
        Para calls, a exposição é positiva (indicando resistência);
        para puts, a exposição é negativa (indicando suporte).

        Fórmula:
            gamma_exposure = gamma * sinal * OI * CONTRACT_SIZE
        onde:
            - gamma é calculado via Black–Scholes
            - sinal é +1 para calls e -1 para puts
            - OI é o open interest da opção
            - CONTRACT_SIZE é o tamanho do contrato (fator de escala)

        Esta função também agrega a exposição por Strike para facilitar a identificação
        de zonas com suporte (exposição negativa) e resistência (exposição positiva).
        """
        # Assegura que 'Strike' e 'OI' sejam numéricos
        self.df['Strike'] = pd.to_numeric(self.df['Strike'], errors='coerce')
        self.df['OI'] = pd.to_numeric(self.df['OI'], errors='coerce')

        # Função interna para calcular a exposição para cada linha (opção)
        def compute_exposure(row):
            try:
                gamma = self.calculate_gamma(
                    S=float(self.current_price),
                    K=float(row.Strike),
                    T=float(days_to_expiry) / 252,  # Assumindo 252 dias de negociação
                    r=SELIC_RATE,
                    sigma=DEFAULT_VOLATILITY
                )
                # Definir o sinal de acordo com o tipo de opção.
                # Calls trazem pressão de venda (resistência): sinal positivo
                # Puts trazem pressão de compra (suporte): sinal negativo
                option_type = row.Tipo.strip().lower()
                sign = 1 if option_type == 'call' else -1
                # Calcula a exposição ponderada com open interest e o fator de contrato
                return float(gamma * sign * row.OI * CONTRACT_SIZE)
            except (ValueError, TypeError) as e:
                print(f"Error processing row: {row}, Error: {e}")
                return 0.0

        # Calcular Gamma Exposure usando apply com lambda
        self.df['Gamma_Exposure'] = self.df.apply(lambda row: compute_exposure(row), axis=1)

        # Agrega a exposição de gamma por Strike para visualizar o efeito líquido
        exposure_by_strike = (
            self.df.groupby('Strike')['Gamma_Exposure']
            .sum()
            .reset_index()
            .rename(columns={'Gamma_Exposure': 'Net_Gamma_Exposure'})
        )

        # Junta as colunas agregadas ao DataFrame principal para análises futuras
        self.df = pd.merge(self.df, exposure_by_strike, on='Strike', how='left')

        return self.df

    def analyze_strike_clusters(self):
        """
        Realiza uma análise de agrupamento (cluster) dos strikes,
        baseando-se em Strike e OI, para identificar áreas onde a exposição de gamma
        pode estar acumulada.
        """
        X = np.array(self.df[['Strike', 'OI']])
        X_normalized = (X - X.mean(axis=0)) / X.std(axis=0)

        clustering = DBSCAN(eps=DBSCAN_EPS, min_samples=DBSCAN_MIN_SAMPLES).fit(X_normalized)
        self.df['Cluster'] = clustering.labels_

        return self.df

    def calculate_volume_profile(self):
        """
        Calcula o perfil de volume agrupando os níveis de preço com intervalos definidos.
        """
        price_levels = pd.IntervalIndex.from_arrays(
            self.df['Strike'] - 0.025,
            self.df['Strike'] + 0.025
        )
        return self.df.groupby(pd.cut(self.df['Strike'], price_levels))['OI'].sum()

    def calculate_liquidity_score(self):
        """
        Calcula um score de liquidez baseado na variação entre os preços de venda e compra,
        e na concentração de open interest.
        """
        self.df['Spread'] = self.df['Venda'] - self.df['Compra']

        max_spread = self.df['Spread'].max()
        if max_spread > 0:
            spread_score = 1 - self.df['Spread'] / max_spread
        else:
            spread_score = 1

        self.df['Liquidity_Score'] = (
            (self.df['OI'] / self.df['OI'].max() * OI_WEIGHT) +
            (spread_score * SPREAD_WEIGHT)
        )

        return self.df

    def detect_critical_levels(self):
        """
        Detecta níveis críticos (potenciais suportes e resistências) considerando puts e calls separadamente.
        Utiliza a agregação do open interest para identificar zonas com alta concentração e classifica cada nível.
        """
        # Calcula o peso do OI separadamente para puts e calls
        self.df['OI_Weight'] = self.df.groupby('Tipo')['OI'].transform(lambda x: x / x.sum())

        # Identifica níveis com alta concentração (acima de média + desvio padrão)
        mask = self.df['OI_Weight'] > self.df.groupby('Tipo')['OI_Weight'].transform(
            lambda x: x.mean() + x.std()
        )
        critical_levels = self.df[mask].copy()

        def is_itm(row, current_price):
            """
            Determina se a opção está ITM:
              - Call ITM: Strike < Preço Atual;
              - Put ITM: Strike > Preço Atual.
            """
            strike = float(row['Strike'])
            current = float(current_price)
            if row['Tipo'].strip().lower() == 'call':
                return strike < current
            else:
                return strike > current

        def classify_barrier(row):
            """
            Classifica barreiras baseado no tipo de opção:
              - Para Calls:
                  OTM (Strike > Preço) -> Resistência (venda para hedge)
                  ITM (Strike < Preço) -> Suporte (compradores defendem ITM)
              - Para Puts:
                  OTM (Strike < Preço) -> Suporte (compra para hedge)
                  ITM (Strike > Preço) -> Resistência
            """
            strike = float(row['Strike'])
            current = float(self.current_price)
            is_call = row['Tipo'].strip().lower() == 'call'
            if is_call:
                return 'Resistência' if strike > current else 'Suporte'
            else:
                return 'Suporte' if strike < current else 'Resistência'

        # Debug detalhado
        print("\nDEBUG - Classificação detalhada de barreiras:")
        for _, row in critical_levels.iterrows():
            strike = float(row['Strike'])
            current = float(self.current_price)
            is_call = row['Tipo'].strip().lower() == 'call'
            moneyness = 'ITM' if is_itm(row, current) else 'OTM'
            barrier = classify_barrier(row)
            print(f"""
    Tipo: {row['Tipo']}
    Strike: {strike:.3f}
    Preço Atual: {current:.3f}
    Moneyness: {moneyness}
    {"Call acima do preço" if is_call and strike > current else "Call abaixo do preço" if is_call else "Put acima do preço" if strike > current else "Put abaixo do preço"}
    Classificação: {barrier}
    OI: {row['OI']}
    Net Gamma Exposure: {row.get('Net_Gamma_Exposure', 'N/A')}
    ------------------------
""")
        
        # Aplica a classificação final dos níveis críticos
        critical_levels.loc[:, 'Barrier_Type'] = critical_levels.apply(classify_barrier, axis=1)

        # Normaliza o score de liquidez
        max_oi = critical_levels['OI'].max()
        critical_levels.loc[:, 'Liquidity_Score'] = critical_levels['OI'] / max_oi

        return critical_levels.sort_values('Liquidity_Score', ascending=False)


