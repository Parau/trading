//Documentação lightweight-charts:https://tradingview.github.io/lightweight-charts/tutorials/how_to/horizontal-price-scale
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

const TICKER_NAME = 'WDO$';
const API_BASE = 'http://127.0.0.1:5000/api';

export default function DIPage() {
  const [isInitialDataLoaded, setIsInitialDataLoaded] = useState(false);
  const seriesRef = useRef<ISeriesApi<"Candlestick"> | null>(null);
  const lastCandleRef = useRef<ChartData | null>(null);

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
        const price = Number(data[TICKER_NAME].last);
        
        // Convert to milliseconds for compatibility
        const currentTime = new Date().getTime();
        const currentBar = Math.floor(currentTime / (5 * 60 * 1000)) * (5 * 60);

        if (!lastCandleRef.current || lastCandleRef.current.time !== currentBar) {
          // Create a new candle
          const newCandle: ChartData = {
            time: currentBar,
            open: price,
            high: price,
            low: price,
            close: price,
          };
          
          if (seriesRef.current) {
            seriesRef.current.update(newCandle);
            lastCandleRef.current = newCandle;
          }
        } else {
          // Update current candle
          const updatedCandle: ChartData = {
            time: currentBar,
            open: lastCandleRef.current.open,
            high: Math.max(lastCandleRef.current.high, price),
            low: Math.min(lastCandleRef.current.low, price),
            close: price,
          };
          
          if (seriesRef.current) {
            seriesRef.current.update(updatedCandle);
            lastCandleRef.current = updatedCandle;
            
          }
        }
      } catch (error) {
        console.error('Erro ao atualizar dados:', error);
      }
    }

    const intervalId = setInterval(fetchRealtimeData, 2000); // Atualização mais frequente
    return () => clearInterval(intervalId);
  }, [isInitialDataLoaded]);

  return (
    <>
      <HeaderMenu />
      <div style={{ padding: '10px' }}>
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