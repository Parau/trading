"""
Módulo principal de análise
"""
import numpy as np
import pandas as pd
from scipy.stats import norm
from sklearn.cluster import DBSCAN

try:
    # This will work when the module is imported as part of a package (e.g., used in the server application)
    from .data_loader import OptionsDataLoader
except ImportError:
    # This will work when the script is run directly (e.g., during testing in the console)
    from data_loader import OptionsDataLoader

try:
    from .config import *  # Changeg to relative import
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
        
    def calculate_gamma(self, S, K, T, r, sigma, option_type="call"):
        """Calcula o gamma para uma opção"""
        d1 = (np.log(S/K) + (r + sigma**2/2)*T) / (sigma*np.sqrt(T))
        gamma = (norm.pdf(d1)) / (S*sigma*np.sqrt(T))
        return gamma
    
    def calculate_gamma_exposure(self, days_to_expiry):
        """Calcula exposição total de gamma"""
        # Converte os valores para numérico para garantir cálculos corretos
        self.df['Strike'] = pd.to_numeric(self.df['Strike'], errors='coerce')
        
        # Calcula gamma linha por linha
        gamma_values = []
        for _, row in self.df.iterrows():
            try:
                gamma = self.calculate_gamma(
                    S=float(self.current_price),
                    K=float(row['Strike']),
                    T=float(days_to_expiry)/252,
                    r=SELIC_RATE,
                    sigma=DEFAULT_VOLATILITY,
                    option_type=row['Tipo'].lower()
                ) * float(row['OI']) * CONTRACT_SIZE
            except (ValueError, TypeError):
                gamma = 0
            gamma_values.append(gamma)
        
        # Atribui os valores calculados à nova coluna
        self.df['Gamma'] = gamma_values
        
        return self.df
    
    def analyze_strike_clusters(self):
        """Análise de clusters de strikes"""
        X = np.array(self.df[['Strike', 'OI']]).reshape(-1, 2)
        X_normalized = (X - X.mean(axis=0)) / X.std(axis=0)
        
        clustering = DBSCAN(eps=DBSCAN_EPS, min_samples=DBSCAN_MIN_SAMPLES).fit(X_normalized)
        self.df['Cluster'] = clustering.labels_
        
        return self.df
    
    def calculate_volume_profile(self):
        """Calcula o perfil de volume"""
        price_levels = pd.IntervalIndex.from_arrays(
            self.df['Strike'] - 0.025,
            self.df['Strike'] + 0.025
        )
        
        return self.df.groupby(pd.cut(self.df['Strike'], price_levels))['OI'].sum()
    
    def calculate_liquidity_score(self):
        """Calcula score de liquidez"""
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
        Detecta níveis críticos considerando puts e calls separadamente
        """
        # Calcula o peso do OI separadamente para puts e calls
        self.df['OI_Weight'] = self.df.groupby('Tipo')['OI'].transform(lambda x: x / x.sum())
        
        print("\nDEBUG - Análise de níveis críticos:", self.df)

        # Identifica níveis com alta concentração
        mask = self.df['OI_Weight'] > self.df.groupby('Tipo')['OI_Weight'].transform(
            lambda x: x.mean() + x.std()
        )
        
        # Cria uma cópia explícita
        critical_levels = self.df[mask].copy()
        
        def is_itm(row, current_price):
            """
            Determina se a opção está ITM:
            Call ITM: Strike < Preço Atual
            Put ITM: Strike > Preço Atual
            """
            strike = float(row['Strike'])
            current = float(current_price)
            if row['Tipo'] == 'Call':
                return strike < current
            else:  # Put
                return strike > current
                
        def classify_barrier(row):
            """
            Classifica barreiras baseado no tipo de opção e posição:
            
            Para Calls:
            - OTM (Strike > Preço) -> Resistência (pressão vendedora no strike)
            - ITM (Strike < Preço) -> Suporte (pressão compradora para manter ITM)
            
            Para Puts:
            - OTM (Strike < Preço) -> Suporte      <- Esta é a correção principal
            - ITM (Strike > Preço) -> Resistência
            """
            strike = float(row['Strike'])
            current = float(self.current_price)
            is_call = row['Tipo'] == 'Call'
            
            # Nova lógica mais clara
            if is_call:
                # Call acima do preço -> Resistência
                return 'Resistência' if strike > current else 'Suporte'
            else:
                # Put abaixo do preço -> Suporte
                return 'Suporte' if strike < current else 'Resistência'
        
        # Debug detalhado
        print("\nDEBUG - Classificação detalhada de barreiras:")
        for _, row in critical_levels.iterrows():
            strike = float(row['Strike'])
            current = float(self.current_price)
            is_call = row['Tipo'] == 'Call'
            moneyness = 'ITM' if is_itm(row, current) else 'OTM'
            barrier = classify_barrier(row)
            
            print(f"""
    Tipo: {row['Tipo']}
    Strike: {strike:.3f}
    Preço Atual: {current:.3f}
    Moneyness: {moneyness}
    {'Call acima do preço' if is_call and strike > current else 'Call abaixo do preço' if is_call else 'Put acima do preço' if strike > current else 'Put abaixo do preço'}
    Classificação: {barrier}
    OI: {row['OI']}
    ------------------------""")
        
        # Aplica classificação
        critical_levels.loc[:, 'Barrier_Type'] = critical_levels.apply(classify_barrier, axis=1)
        
        # Normaliza score de liquidez
        max_oi = critical_levels['OI'].max()
        critical_levels.loc[:, 'Liquidity_Score'] = critical_levels['OI'] / max_oi
        
        return critical_levels.sort_values('Liquidity_Score', ascending=False)