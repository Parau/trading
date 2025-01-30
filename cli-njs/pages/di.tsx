import { HeaderMenu } from '../components/HeaderMenu/HeaderMenu';
import { ChartComponent } from '../components/ChartComponent/ChartComponent';
import { useEffect, useState, useRef } from 'react';
import { ISeriesApi } from 'lightweight-charts';

interface ChartData {
  time: number;
  open: number;
  high: number;
  low: number;
  close: number;
}

const TICKER_NAME = 'DI1N26';
const API_BASE = 'http://127.0.0.1:5000/api';

export default function DIPage() {
  const [isInitialDataLoaded, setIsInitialDataLoaded] = useState(false);
  const seriesRef = useRef<ISeriesApi<"Candlestick"> | null>(null);

  // Carregar dados históricos
  useEffect(() => {
    async function fetchHistoricalData() {
      if (!seriesRef.current) return;
      
      try {
        const response = await fetch(
          `${API_BASE}/historical-ticker-data?tickerName=${TICKER_NAME}`
        );
        const data = await response.json();
        if (Array.isArray(data)) {
          seriesRef.current.setData(data);
          setIsInitialDataLoaded(true);
        }
      } catch (error) {
        console.error('Erro ao carregar dados históricos:', error);
        setIsInitialDataLoaded(true); // Mesmo com erro, permitir continuar
      }
    }

    if (seriesRef.current) {
      fetchHistoricalData();
    }
  }, [seriesRef.current]); // Adicionar seriesRef.current como dependência

  // Atualizar com dados em tempo real
  useEffect(() => {
    if (!isInitialDataLoaded) return;

    async function fetchRealtimeData() {
      try {
        const response = await fetch(
          `${API_BASE}/last-ticker-data?tickerName=${TICKER_NAME}`
        );
        const data = await response.json();
        
        if (data[TICKER_NAME] && seriesRef.current) {
          seriesRef.current.update({
            time: data[TICKER_NAME].time,
            open: Number(data[TICKER_NAME].last),
            high: Number(data[TICKER_NAME].last),
            low: Number(data[TICKER_NAME].last),
            close: Number(data[TICKER_NAME].last)
          });
        }
      } catch (error) {
        console.error('Erro ao atualizar dados:', error);
      }
    }

    const intervalId = setInterval(fetchRealtimeData, 2000);
    return () => clearInterval(intervalId);
  }, [isInitialDataLoaded]);

  return (
    <>
      <HeaderMenu />
      <div style={{ padding: '20px' }}>
        <ChartComponent 
          ticker={TICKER_NAME} 
          onSeriesReady={(series) => {
            seriesRef.current = series;
          }} 
        />
        {!isInitialDataLoaded && <div>Carregando...</div>}
      </div>
    </>
  );
}