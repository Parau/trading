"""
Configurações e constantes do sistema
"""
import datetime

# Configurações gerais
SELIC_RATE = 0.1175  # Taxa Selic aproximada
DEFAULT_VOLATILITY = 0.15  # Volatilidade implícita média do dólar
CONTRACT_SIZE = 50000  # Tamanho do contrato de dólar futuro
CURRENT_DATE = datetime.datetime(2025, 2, 7, 12, 16, 28)

# Configurações de clustering
DBSCAN_EPS = 0.3
DBSCAN_MIN_SAMPLES = 2

# Configurações de cache
CACHE_EXPIRY = 3600  # 1 hora em segundos

# Pesos para cálculo de scores
OI_WEIGHT = 0.7
SPREAD_WEIGHT = 0.3