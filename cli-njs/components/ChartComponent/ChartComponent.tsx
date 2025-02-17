//https://github.com/tradingview/lightweight-charts/blob/master/plugin-examples/
import { createChart, ColorType, IChartApi, ISeriesApi } from 'lightweight-charts';
import { useEffect, useRef } from 'react';

interface ChartComponentProps {
  ticker: string;
  onSeriesReady?: (series: ISeriesApi<"Candlestick">) => void;
}

export function ChartComponent({ ticker, onSeriesReady }: ChartComponentProps) {
  const chartContainerRef = useRef<HTMLDivElement>(null);
  const chartRef = useRef<IChartApi | null>(null);
  const seriesRef = useRef<ISeriesApi<"Candlestick"> | null>(null);

  useEffect(() => {
    if (!chartContainerRef.current) return;

    const chartOptions = {
      layout: {
        textColor: 'black',
        background: { type: 'solid', color: 'white' } as const,
      },
      watermark: {
        visible: true,
        fontSize: 96,
        horzAlign: 'center',
        vertAlign: 'center',
        color: 'rgba(0, 0, 0, 0.10)',
        text: ticker,
      },
      timeScale: {
        timeVisible: true,
        secondsVisible: true,
      },
      height: 500,
    };

    console.log('Criando gráfico para', ticker);
    const chart = createChart(chartContainerRef.current, chartOptions);
    const candlestickSeries = chart.addCandlestickSeries({
      upColor: '#26a69a',
      downColor: '#ef5350',
      borderVisible: false,
      wickUpColor: '#26a69a',
      wickDownColor: '#ef5350',

      priceFormat: {
        type: 'price',
        precision: 2,
        minMove: 0.01,
      },
      //////////////////////////////
      lastValueVisible: true,          // Shows the last value
      priceLineVisible: true,         // Shows the price line
      priceLineWidth: 1,
      priceLineColor: '#2196F3',
      priceLineStyle: 2,              // 0 = solid, 1 = dotted, 2 = dashed
      baseLineVisible: true,
      baseLineWidth: 1,
      baseLineColor: '#2196F3',
      baseLineStyle: 0,
      ////////////////////////////
    });

    chartRef.current = chart;
    seriesRef.current = candlestickSeries;

    if (onSeriesReady) {
      onSeriesReady(candlestickSeries);
    }

    chart.timeScale().fitContent();
    chart.timeScale().scrollToPosition(5);

    return () => {
      chart.remove();
    };
  }, [ticker, onSeriesReady]);

  return <div ref={chartContainerRef} />;
}