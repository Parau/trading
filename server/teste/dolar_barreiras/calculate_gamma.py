import numpy as np
from scipy.stats import norm

def calculate_gamma(S, K, T, r, sigma, option_type="call"):
    d1 = (np.log(S/K) + (r + sigma**2/2)*T) / (sigma*np.sqrt(T))
    gamma = (norm.pdf(d1)) / (S*sigma*np.sqrt(T))
    return gamma

def aggregate_gamma_exposure(df, current_price, days_to_expiry):
    df['Gamma'] = df.apply(lambda row: calculate_gamma(
        S=current_price,
        K=row['Strike'],
        T=days_to_expiry/252,
        r=0.1175,  # Taxa Selic aproximada
        sigma=0.15,  # Volatilidade implícita média do dólar
        option_type=row['Tipo'].lower()
    ) * row['OI'] * 50000, axis=1)  # Multiplicando pelo tamanho do contrato