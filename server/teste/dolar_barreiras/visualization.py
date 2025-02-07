"""
Módulo de visualização
"""
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots

import matplotlib.pyplot as plt
import numpy as np

class OptionsVisualizer:
    def __init__(self, df, current_price):
        self.df = df
        self.current_price = current_price
    
    def plot_barrier_analysis(self):
        """Plot principal de análise de barreiras"""
        fig = make_subplots(rows=2, cols=1, shared_xaxes=True,
                           vertical_spacing=0.05,
                           subplot_titles=('Open Interest', 'Gamma Exposure'))
        
        # OI de Calls
        fig.add_trace(
            go.Bar(
                x=self.df[self.df['Tipo'] == 'Call']['Strike'],
                y=self.df[self.df['Tipo'] == 'Call']['OI'],
                name='Calls OI',
                marker_color='green',
                opacity=0.6
            ),
            row=1, col=1
        )
        
        # OI de Puts
        fig.add_trace(
            go.Bar(
                x=self.df[self.df['Tipo'] == 'Put']['Strike'],
                y=self.df[self.df['Tipo'] == 'Put']['OI'],
                name='Puts OI',
                marker_color='red',
                opacity=0.6
            ),
            row=1, col=1
        )
        
        # Gamma Exposure
        fig.add_trace(
            go.Scatter(
                x=self.df['Strike'],
                y=self.df['Gamma'],
                name='Gamma Exposure',
                line=dict(color='blue')
            ),
            row=2, col=1
        )
        
        # Linha de preço atual
        fig.add_vline(x=self.current_price, line_dash="dash", line_color="black")
        
        fig.update_layout(
            title='Análise de Barreiras de Liquidez',
            showlegend=True,
            height=800
        )
        
        return fig
    
    def plot_volume_profile(self):

        # Separa o volume profile por tipo de opção
        calls_profile = self.df[self.df['Tipo'] == 'Call'].groupby('Strike')['OI'].sum()
        puts_profile = self.df[self.df['Tipo'] == 'Put'].groupby('Strike')['OI'].sum()
        
        fig = go.Figure()
        
        # Adiciona barras para Calls (azul)
        fig.add_trace(go.Bar(
            x=calls_profile.values,
            y=calls_profile.index,
            orientation='h',
            name='Calls',
            marker_color='rgba(0, 121, 255, 0.7)'  # Azul semi-transparente
        ))
        
        # Adiciona barras para Puts (vermelho)
        fig.add_trace(go.Bar(
            x=puts_profile.values,
            y=puts_profile.index,
            orientation='h',
            name='Puts',
            marker_color='rgba(255, 0, 0, 0.7)'  # Vermelho semi-transparente
        ))
        
        # Adiciona linha do preço atual
        fig.add_hline(
            y=self.current_price,
            line_dash="dash",
            line_color="green",
            annotation_text=f"Preço Atual: {self.current_price:.3f}"
        )
        
        # Configuração do layout
        fig.update_layout(
            title={
                'text': 'Perfil de Volume por Strike',
                'x': 0.5,
                'xanchor': 'center'
            },
            yaxis_title='Strike',
            xaxis_title='Open Interest',
            barmode='group',  # Agrupa as barras lado a lado
            showlegend=True,
            # Adiciona informações de data e usuário
            annotations=[
                dict(
                    text=f"Data: 2025-02-07 15:49:10<br>Usuário: Parau",
                    xref="paper",
                    yref="paper",
                    x=0.02,
                    y=0.98,
                    showarrow=False,
                    font=dict(size=10)
                )
            ]
        )
        
        return fig
'''
    def plot_volume_profile(self):
        """Plot do perfil de volume"""
        volume_profile = self.df.groupby('Strike')['OI'].sum()
        
        fig = go.Figure()
        fig.add_trace(go.Bar(
            x=volume_profile.values,
            y=volume_profile.index,
            orientation='h',
            name='Volume Profile'
        ))
        
        fig.update_layout(
            title='Perfil de Volume por Strike',
            yaxis_title='Strike',
            xaxis_title='Volume Total'
        )
        
        return fig
'''