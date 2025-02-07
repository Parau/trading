"""
Módulo para carregar e preparar os dados
"""
import pandas as pd
import numpy as np
from functools import lru_cache
import datetime

class OptionsDataLoader:
    @staticmethod
    def load_excel(file_path):
        return pd.read_excel(file_path)
    
    @staticmethod
    def extract_strike(code, prefix_length=4):
        try:
            return int(code[prefix_length:]) / 1000
        except Exception:
            return np.nan
    
    @staticmethod
    @lru_cache(maxsize=128)
    def calculate_days_to_expiry(series_code, current_date):
        """
        Calcula dias até o vencimento baseado no código da série
        Ex: H25 = vencimento em março de 2025
        """
        month_codes = {'F': 1, 'G': 2, 'H': 3, 'J': 4, 'K': 5, 'M': 6,
                      'N': 7, 'Q': 8, 'U': 9, 'V': 10, 'X': 11, 'Z': 12}
        
        month = month_codes[series_code[0]]
        year = 2000 + int(series_code[1:3])
        expiry_date = datetime.datetime(year, month, 15)  # Assumindo vencimento no dia 15
        
        return (expiry_date - current_date).days

    def prepare_data(self, calls_file, puts_file, contract_filter="H25"):
        # Lê os arquivos Excel
        df_calls = self.load_excel(calls_file)
        df_puts = self.load_excel(puts_file)
        
        # Filtra pelo contrato específico
        df_calls = df_calls[df_calls['Código'].str.startswith(f"{contract_filter}C")].copy()
        df_puts = df_puts[df_puts['Código'].str.startswith(f"{contract_filter}P")].copy()
        
        # Processa calls e puts
        for df in [df_calls, df_puts]:
            df['Strike'] = df['Código'].apply(lambda x: self.extract_strike(x))
            df['OI'] = pd.to_numeric(df['Contratos em Aberto'], errors='coerce').fillna(0)
            df['Volume'] = pd.to_numeric(df['Contratos Negociados'], errors='coerce').fillna(0)
            df['Último'] = pd.to_numeric(df['Último Preço'], errors='coerce')
            df['Compra'] = pd.to_numeric(df['Última Oferta de Compra'], errors='coerce')
            df['Venda'] = pd.to_numeric(df['Última Oferta de Venda'], errors='coerce')
        
        df_calls['Tipo'] = 'Call'
        df_puts['Tipo'] = 'Put'
        
        return pd.concat([df_calls, df_puts], ignore_index=True)