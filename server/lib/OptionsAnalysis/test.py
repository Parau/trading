from analysis import OptionsAnalysis

if __name__ == "__main__":

  current_price = 5.70  # Exemplo hipotético
  contract_filter = "H25"  # Insira os filtros de contrato conforme necessário

  analyzer = OptionsAnalysis(current_price, contract_filter, 
            'E:/dev/trading/server/data/opcoes_dolar/2025-02-18_DOL_OP_Call.csv',
            'E:/dev/trading/server/data/opcoes_dolar/2025-02-18_DOL_OP_Put.csv' )
  
  ## Apenas imprime as puts e calls
  #pd = analyzer.getOptionsData()
  #print(pd[['Strike', 'OI', 'Tipo']])

  # Calcular exposição de gamma (substitua "3" pelo número de dias até o vencimento)
  df_with_gamma = analyzer.calculate_gamma_exposure(days_to_expiry=3)
  print("DataFrame com Gamma Exposure calculado:")
  print(df_with_gamma.head())


  # Detectar níveis críticos
  critical_levels = analyzer.detect_critical_levels()
  print("\nNíveis críticos detectados:")
  print(critical_levels)
