import QuantLib as ql
from datetime import datetime, timedelta
import numpy as np
from scipy.optimize import minimize
from dataclasses import dataclass
from typing import Optional

@dataclass
class CopomMeeting:
    """
    Estrutura de dados para representar uma reunião do COPOM.
    
    Attributes:
        date: Data da reunião
        rate_change: Mudança esperada na taxa (em pontos percentuais)
                    None significa que a taxa precisa ser otimizada
    """
    date: datetime
    rate_change: Optional[float] = None

def datetime_to_qldate(dt):
    """Converte datetime para QuantLib Date."""
    return ql.Date(dt.day, dt.month, dt.year)

def qldate_to_datetime(qldate):
    """Converte QuantLib Date para datetime."""
    return datetime(qldate.year(), qldate.month(), qldate.dayOfMonth())

def get_next_business_day(date, calendar):
    """Retorna o próximo dia útil após uma data específica."""
    ql_date = datetime_to_qldate(date)
    next_business_day = calendar.adjust(ql_date + 1, ql.Following)
    return qldate_to_datetime(next_business_day)

def get_copom_meetings():
    """
    Define as reuniões do COPOM com possíveis estimativas de mudança na taxa.
    rate_change pode ser None (para ser otimizado) ou um valor específico.
    """
    meetings = [
        CopomMeeting(datetime(2020, 10, 28)),  # Exemplo: None significa que será otimizado
        CopomMeeting(datetime(2020, 12, 9)),  # Exemplo: aumento de 0.5 p.p.
        CopomMeeting(datetime(2021, 1, 20), rate_change=0.25),
        CopomMeeting(datetime(2021, 3, 17), rate_change=0.50),
        CopomMeeting(datetime(2021, 5, 5), rate_change=0.50),
        CopomMeeting(datetime(2021, 6, 16), rate_change=0.50),
        CopomMeeting(datetime(2021, 8, 4), rate_change=0.750),
        CopomMeeting(datetime(2021, 9, 22), rate_change=1.0),
        CopomMeeting(datetime(2021, 10, 27), rate_change=1.00),
        CopomMeeting(datetime(2021, 12, 8), rate_change=0.25),
        CopomMeeting(datetime(2022, 2, 2)),
        CopomMeeting(datetime(2022, 3, 16)),
        CopomMeeting(datetime(2022, 5, 4)),
        CopomMeeting(datetime(2022, 6, 15)),
        CopomMeeting(datetime(2022, 8, 3)),
        CopomMeeting(datetime(2022, 9, 21)),
        CopomMeeting(datetime(2022, 10, 26)),
        CopomMeeting(datetime(2022, 12, 7))
    ]
    return meetings

def get_effective_dates(meetings, start_date, end_date):
    """
    Obtém as datas efetivas das mudanças de taxa, considerando o dia útil seguinte.
    Filtra as datas dentro do período de interesse.
    """
    brazil_calendar = ql.Brazil()
    
    # Converte as datas das reuniões para datas efetivas
    effective_dates = [get_next_business_day(m.date, brazil_calendar) for m in meetings]
    
    # Filtra as datas dentro do período
    valid_meetings = []
    valid_dates = []
    
    for meeting, date in zip(meetings, effective_dates):
        if start_date <= date <= end_date:
            valid_meetings.append(meeting)
            valid_dates.append(date)
    
    return [start_date] + valid_dates + [end_date], valid_meetings

def calculate_du252_rate(rates, dates, brazil_calendar):
    """Calcula a taxa média usando a convenção DU252."""
    if len(rates) != len(dates):
        raise ValueError("Número de taxas deve ser igual ao número de datas")
    
    daily_factors = [(1 + rate/100) ** (1/252) for rate in rates]
    accumulated_factor = 1
    total_du = 0
    
    for i in range(len(dates)-1):
        business_days = 0
        current_date = datetime_to_qldate(dates[i])
        end_date = datetime_to_qldate(dates[i+1])
        
        while current_date < end_date:
            if brazil_calendar.isBusinessDay(current_date):
                business_days += 1
            current_date = current_date + 1
        
        accumulated_factor *= daily_factors[i] ** business_days
        total_du += business_days
    
    avg_rate = (accumulated_factor ** (252/total_du) - 1) * 100
    return avg_rate, total_du

def optimize_copom_rates(initial_rate, target_rate, dates, meetings):
    """
    Otimiza as taxas do COPOM, respeitando as estimativas fornecidas.
    Apenas as reuniões sem estimativas (rate_change=None) serão otimizadas.
    """
    brazil_calendar = ql.Brazil()
    
    # Identificamos quais posições precisam ser otimizadas
    unknown_positions = [i for i, m in enumerate(meetings) if m.rate_change is None]
    known_changes = [m.rate_change for m in meetings if m.rate_change is not None]
    
    def objective_function(x):
        # Reconstrói o vetor completo de variações
        all_changes = []
        x_index = 0
        for meeting in meetings:
            if meeting.rate_change is None:
                all_changes.append(x[x_index])
                x_index += 1
            else:
                all_changes.append(meeting.rate_change)
        
        # Calcula as taxas resultantes
        rates = [initial_rate]
        current_rate = initial_rate
        for change in all_changes:
            current_rate += change
            rates.append(current_rate)
        
        # Adiciona a última taxa (igual à anterior) para o período final
        rates.append(rates[-1])
        
        avg_rate, _ = calculate_du252_rate(rates, dates, brazil_calendar)
        return abs(avg_rate - target_rate)
    
    # Define limites para os aumentos baseado na posição no ciclo
    n_unknown = len(unknown_positions)
    bounds = []
    for pos in unknown_positions:
        if pos < len(meetings) // 3:
            bounds.append((0, 0.75))
        elif pos < 2 * len(meetings) // 3:
            bounds.append((0.25, 1.0))
        else:
            bounds.append((0, 0.5))
    
    # Otimiza apenas as posições desconhecidas
    initial_guess = [0.5] * n_unknown
    result = minimize(objective_function, initial_guess, bounds=bounds, method='SLSQP')
    
    # Reconstrói o vetor completo de taxas
    final_rates = [initial_rate]
    current_rate = initial_rate
    x_index = 0
    for meeting in meetings:
        if meeting.rate_change is None:
            change = result.x[x_index]
            x_index += 1
        else:
            change = meeting.rate_change
        current_rate += change
        final_rates.append(current_rate)
    
    # Adiciona a última taxa para o período final
    final_rates.append(final_rates[-1])
    
    return final_rates

# Parâmetros iniciais
initial_cdi = 1.90
target_rate = 5.05
start_date = datetime(2020, 10, 30)
end_date = datetime(2023, 1, 2)

# Obtém as reuniões e datas efetivas
meetings = get_copom_meetings()
dates, valid_meetings = get_effective_dates(meetings, start_date, end_date)

# Calcula as taxas otimizadas
optimal_rates = optimize_copom_rates(initial_cdi, target_rate, dates, valid_meetings)

# Imprime os resultados
print("\nProjeção de taxas do COPOM:")
print("Data Efetiva    Taxa (%)    Variação (p.p.)    Origem")
print("-" * 65)
prev_rate = optimal_rates[0]
for date, rate, meeting in zip(dates[:-1], optimal_rates[:-1], [None] + valid_meetings):
    variation = rate - prev_rate
    origin = "Estimativa" if meeting and meeting.rate_change is not None else "Otimização"
    print(f"{date.strftime('%d/%m/%Y')}   {rate:.2f}        {variation:+.2f}           {origin}")
    prev_rate = rate

# Calcula estatísticas finais
brazil_calendar = ql.Brazil()
avg_rate, total_du = calculate_du252_rate(optimal_rates, dates, brazil_calendar)
print(f"\nResultados Finais:")
print(f"Taxa média resultante: {avg_rate:.2f}% a.a.")
print(f"Taxa alvo (DI Futuro): {target_rate:.2f}% a.a.")
print(f"Total de dias úteis no período: {total_du}")

# Estatísticas dos ajustes
variations = [optimal_rates[i+1] - optimal_rates[i] for i in range(len(optimal_rates)-1)]
print(f"\nEstatísticas dos ajustes:")
print(f"Maior aumento: {max(variations):.2f} p.p.")
print(f"Menor aumento: {min(variations):.2f} p.p.")
print(f"Aumento médio: {sum(variations)/len(variations):.2f} p.p.")