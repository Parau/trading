"""
Código principal que integra todos os módulos
"""
from data_loader import OptionsDataLoader
from analysis import OptionsAnalysis
from visualization import OptionsVisualizer
import pandas as pd
import numpy as np
from config import *

def main(calls_file, puts_file, current_price, contract_filter="H25"):
    # Carrega e prepara os dados
    loader = OptionsDataLoader()
    df = loader.prepare_data(calls_file, puts_file, contract_filter)
    
    # Instancia o analisador
    analyzer = OptionsAnalysis(df, current_price)
    
    # Calcula dias até o vencimento
    days_to_expiry = loader.calculate_days_to_expiry(contract_filter, CURRENT_DATE)
    
    # Executa análises
    df = analyzer.calculate_gamma_exposure(days_to_expiry)
    df = analyzer.analyze_strike_clusters()
    df = analyzer.calculate_liquidity_score()
    
    # Detecta níveis críticos
    critical_levels = analyzer.detect_critical_levels()
    
    # Cria visualizações
    visualizer = OptionsVisualizer(df, current_price)
    barrier_plot = visualizer.plot_barrier_analysis()
    volume_profile = visualizer.plot_volume_profile()
    
    # Exibe resultados
    print("\n=== Análise de Barreiras de Liquidez ===")
    print("\nNíveis Críticos Detectados:")
    print(critical_levels[['Strike', 'OI', 'Barrier_Type', 'Liquidity_Score', 'Tipo']].to_string(index=False))
    
    print("\nCluster Analysis:")
    cluster_summary = df.groupby('Cluster').agg({
        'Strike': ['count', 'mean'],
        'OI': 'sum'
    }).round(2)
    print(cluster_summary)
    
    # Mostra os gráficos
    barrier_plot.show()
    volume_profile.show()
    
    return df, critical_levels

if __name__ == "__main__":
    # Define os caminhos para os arquivos Excel
    calls_file = "calls.xlsx"  # ajuste o caminho conforme necessário
    puts_file = "puts.xlsx"    # ajuste o caminho conforme necessário
    current_price = 5.791
    
    df, critical_levels = main(calls_file, puts_file, current_price)