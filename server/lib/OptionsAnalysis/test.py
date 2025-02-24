import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))  # Add parent directory to path

from analysis import OptionsAnalysis
from B3.Calendario import DolarOption
from datetime import datetime
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np  # Added numpy import

if __name__ == "__main__":
    current_price = 5.70  
    contract_filter = "H25" 

    # Compute days_to_expiry using DolarOption:
    option = DolarOption(contract_filter)
    exp_date_str = option.get_expiration_date()
    if exp_date_str == "Série não encontrada":
        print("Série não encontrada")
        days_to_expiry = 0
    else:
        exp_date = datetime.strptime(exp_date_str, "%d/%m/%Y").date()
        today = datetime.now().date()
        days_to_expiry = (exp_date - today).days
        print(f"Days to expiry for {contract_filter}: {days_to_expiry}")

    analyzer = OptionsAnalysis(current_price, contract_filter, 
              'E:/dev/trading/server/data/opcoes_dolar/2025-02-19_DOL_OP_Call.csv',
              'E:/dev/trading/server/data/opcoes_dolar/2025-02-19_DOL_OP_Put.csv')
    
    # Calculate gamma exposure
    df_with_gamma = analyzer.calculate_gamma_exposure(days_to_expiry=days_to_expiry)
    print("DataFrame com Gamma Exposure calculado:")
    print(df_with_gamma.head())
    df_with_gamma.to_excel('gamma_exposure.xlsx', index=False)

    # Detect critical levels and analyze clusters
    critical_levels = analyzer.detect_critical_levels()
    df_with_clusters = analyzer.analyze_strike_clusters()
    print("\nNíveis críticos detectados:")
    print(critical_levels)
    critical_levels.to_excel('critical_levels.xlsx', index=False)

    # Set figure style
    plt.style.use('default')  # Using default style instead of seaborn
    
    # 1. Bar Chart of Net Gamma Exposure
    plt.figure(figsize=(12, 6))
    colors = ['red' if x < 0 else 'green' for x in df_with_gamma['Net_Gamma_Exposure']]
    plt.bar(df_with_gamma['Strike'], df_with_gamma['Net_Gamma_Exposure'], color=colors, alpha=0.7)
    plt.axhline(y=0, color='black', linestyle='-', alpha=0.3)
    plt.axvline(x=current_price, color='blue', linestyle='--', label='Current Price')
    plt.title('Net Gamma Exposure by Strike Price', fontsize=12, pad=15)
    plt.xlabel('Strike Price', fontsize=10)
    plt.ylabel('Net Gamma Exposure', fontsize=10)
    plt.legend(fontsize=10)
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig('gamma_exposure_bar.png', dpi=300, bbox_inches='tight')
    plt.close()

    ### 2. Area Chart with Support/Resistance Zones
    plt.figure(figsize=(12, 6))
    exposure_df = df_with_gamma.groupby('Strike')['Net_Gamma_Exposure'].sum().reset_index()
    exposure_df = exposure_df.sort_values('Strike')  # Sort by Strike for proper line plot
    
    # Plot filled areas
    plt.fill_between(exposure_df['Strike'], 
                    exposure_df['Net_Gamma_Exposure'], 
                    0, 
                    where=(exposure_df['Net_Gamma_Exposure'] >= 0),
                    color='green', 
                    alpha=0.3, 
                    label='Resistance Zone')
    plt.fill_between(exposure_df['Strike'], 
                    exposure_df['Net_Gamma_Exposure'], 
                    0, 
                    where=(exposure_df['Net_Gamma_Exposure'] <= 0),
                    color='red', 
                    alpha=0.3, 
                    label='Support Zone')
    
    # Plot line with markers
    plt.plot(exposure_df['Strike'], 
             exposure_df['Net_Gamma_Exposure'], 
             'k.-',  # Added dot marker
             alpha=0.7,
             markersize=4)
             
    # Add vertical grid lines at each strike
    plt.gca().set_xticks(exposure_df['Strike'])
    plt.grid(True, which='major', axis='both', alpha=0.3)
    plt.grid(True, which='minor', axis='both', alpha=0.1)
    
    # Rotate x-axis labels for better readability
    plt.xticks(rotation=90)
    
    # Current price line
    plt.axvline(x=current_price, color='blue', linestyle='--', label='Current Price')
    
    plt.title('Gamma Exposure Profile with Support/Resistance Zones', fontsize=12, pad=15)
    plt.xlabel('Strike Price', fontsize=10)
    plt.ylabel('Net Gamma Exposure', fontsize=10)
    plt.legend(fontsize=10)
    
    # Adjust layout to prevent label cutoff
    plt.tight_layout()
    plt.savefig('gamma_exposure_area.png', dpi=300, bbox_inches='tight')
    plt.close()

    # 3. Scatter Plot with Cluster Overlay
    plt.figure(figsize=(12, 6))
    scatter = plt.scatter(df_with_clusters['Strike'], 
                         df_with_clusters['Net_Gamma_Exposure'],
                         c=df_with_clusters['Cluster'], 
                         cmap='viridis',
                         s=100 * df_with_clusters['OI'] / df_with_clusters['OI'].max(),
                         alpha=0.6)
    plt.axhline(y=0, color='black', linestyle='-', alpha=0.3)
    plt.axvline(x=current_price, color='blue', linestyle='--', label='Current Price')
    plt.colorbar(scatter, label='Cluster')
    plt.title('Gamma Exposure Clusters', fontsize=12, pad=15)
    plt.xlabel('Strike Price', fontsize=10)
    plt.ylabel('Net Gamma Exposure', fontsize=10)
    plt.legend(fontsize=10)
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig('gamma_exposure_clusters.png', dpi=300, bbox_inches='tight')
    plt.close()

    # 4. Strike Clusters Analysis with Call/Put Color Distinction
    plt.figure(figsize=(12, 6))
    
    # Separate calls and puts
    calls = df_with_clusters[df_with_clusters['Tipo'] == 'Call']
    puts = df_with_clusters[df_with_clusters['Tipo'] == 'Put']
    
    # Create color maps for each type
    call_clusters = calls['Cluster'].unique()
    put_clusters = puts['Cluster'].unique()
    
    # Generate green colors for calls and red colors for puts
    call_colors = plt.cm.Greens(np.linspace(0.3, 0.9, len(call_clusters)))
    put_colors = plt.cm.Reds(np.linspace(0.3, 0.9, len(put_clusters)))
    
    # Plot Calls
    for cluster, color in zip(call_clusters, call_colors):
        mask = (calls['Cluster'] == cluster)
        cluster_data = calls[mask]
        sizes = 100 * cluster_data['OI'] / df_with_clusters['OI'].max()
        
        plt.scatter(cluster_data['Strike'], 
                   cluster_data['OI'],
                   c=[color],
                   s=sizes,
                   alpha=0.6,
                   marker='o',
                   label=f'Call Cluster {cluster}')
    
    # Plot Puts
    for cluster, color in zip(put_clusters, put_colors):
        mask = (puts['Cluster'] == cluster)
        cluster_data = puts[mask]
        sizes = 100 * cluster_data['OI'] / df_with_clusters['OI'].max()
        
        plt.scatter(cluster_data['Strike'], 
                   cluster_data['OI'],
                   c=[color],
                   s=sizes,
                   alpha=0.6,
                   marker='s',  # Square marker for puts
                   label=f'Put Cluster {cluster}')

    # Add vertical line for current price
    plt.axvline(x=current_price, color='blue', linestyle='--', 
                label=f'Current Price ({current_price})')
    
    # Customize the plot
    plt.title('Strike Price Clusters Analysis (Calls vs Puts)', fontsize=12, pad=15)
    plt.xlabel('Strike Price', fontsize=10)
    plt.ylabel('Open Interest', fontsize=10)
    plt.legend(fontsize=8, bbox_to_anchor=(1.05, 1), loc='upper left')
    plt.grid(True, alpha=0.3)
    
    # Add strike price labels
    plt.xticks(df_with_clusters['Strike'].unique(), rotation=90)
    
    # Adjust layout to prevent label cutoff
    plt.tight_layout()
    plt.savefig('strike_clusters_analysis.png', dpi=300, bbox_inches='tight')
    plt.close()