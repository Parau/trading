import sys
from pathlib import Path# Changed to relative import
sys.path.append(str(Path(__file__).parent.parent))  # Add parent directory to path

from analysis import OptionsAnalysis
from B3.Calendario import DolarOption
from datetime import datetime

if __name__ == "__main__":

  current_price = 5.70  # Exemplo hipotético
  contract_filter = "H25"  # Exemplo de série

  # Compute days_to_expiry using DolarOption:
  option = DolarOption(contract_filter)
  exp_date_str = option.get_expiration_date()
  if exp_date_str == "Série não encontrada":
      print("Série não encontrada")
      days_to_expiry = 0
  else:
      exp_date = datetime.strptime(exp_date_str, "%d/%m/%Y").date()
      today = datetime.now().date()  # Use system's current date
      days_to_expiry = (exp_date - today).days
      print(f"Days to expiry for {contract_filter}: {days_to_expiry}")

  analyzer = OptionsAnalysis(current_price, contract_filter, 
            'E:/dev/trading/server/data/opcoes_dolar/2025-02-18_DOL_OP_Call.csv',
            'E:/dev/trading/server/data/opcoes_dolar/2025-02-18_DOL_OP_Put.csv' )
  
  # Calcular exposição de gamma com days_to_expiry calculado
  df_with_gamma = analyzer.calculate_gamma_exposure(days_to_expiry=days_to_expiry)
  print("DataFrame com Gamma Exposure calculado:")
  print(df_with_gamma.head())
  df_with_gamma.to_excel('gamma_exposure.xlsx', index=False)

  # Detectar níveis críticos
  critical_levels = analyzer.detect_critical_levels()
  print("\nNíveis críticos detectados:")
  print(critical_levels)
  critical_levels.to_excel('critical_levels.xlsx', index=False)