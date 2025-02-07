from sklearn.cluster import DBSCAN
import numpy as np

def analyze_strike_clusters(df):
    # Prepara os dados para clustering
    X = np.array(df[['Strike', 'OI']]).reshape(-1, 2)
    
    # Normaliza os dados
    X_normalized = (X - X.mean(axis=0)) / X.std(axis=0)
    
    # Aplica DBSCAN
    clustering = DBSCAN(eps=0.3, min_samples=2).fit(X_normalized)
    
    df['Cluster'] = clustering.labels_
    return df