import { useEffect, useRef } from 'react';
import * as am5 from '@amcharts/amcharts5';
import * as am5xy from '@amcharts/amcharts5/xy';
import * as am5stock from '@amcharts/amcharts5/stock';
import am5themes_Animated from '@amcharts/amcharts5/themes/Animated';
import { Container, Title, Paper } from '@mantine/core';
import { HeaderMenu } from '../components/HeaderMenu/HeaderMenu';

const TICKER_NAME = 'WDO$';
const API_BASE = 'http://127.0.0.1:5000/api';

export default function DolarPage() {
  const chartRef = useRef<am5.Root | null>(null);

  useEffect(() => {
    // Create root element
    const root = am5.Root.new('chartdiv');
    chartRef.current = root;

    const myTheme = am5.Theme.new(root);
    myTheme.rule('Grid', ['scrollbar', 'minor']).setAll({
      visible: false
    });

    root.setThemes([am5themes_Animated.new(root), myTheme]);

    // Create stock chart
    const stockChart = root.container.children.push(
      am5stock.StockChart.new(root, {
        paddingRight: 0
      })
    );

    root.numberFormatter.set('numberFormat', '#,###.00');

    // Create main panel
    const mainPanel = stockChart.panels.push(
      am5stock.StockPanel.new(root, {
        wheelY: 'zoomX',
        panX: true,
        panY: true
      })
    );

    // Create axes
    const valueAxis = mainPanel.yAxes.push(
      am5xy.ValueAxis.new(root, {
        renderer: am5xy.AxisRendererY.new(root, { pan: 'zoom' }),
        extraMin: 0.1,
        tooltip: am5.Tooltip.new(root, {}),
        numberFormat: '#,###.00',
        extraTooltipPrecision: 2
      })
    );

    const dateAxis = mainPanel.xAxes.push(
      am5xy.GaplessDateAxis.new(root, {
        extraMax: 0.1,
        baseInterval: { timeUnit: 'minute', count: 5 }, // Changed to 5 minutes
        renderer: am5xy.AxisRendererX.new(root, {
          pan: 'zoom',
          minorGridEnabled: true
        }),
        tooltip: am5.Tooltip.new(root, {})
      })
    );

    // Create series
    const valueSeries = mainPanel.series.push(
      am5xy.CandlestickSeries.new(root, {
        name: 'DOLAR',
        clustered: false,
        valueXField: 'Date',
        valueYField: 'Close',
        highValueYField: 'High',
        lowValueYField: 'Low',
        openValueYField: 'Open',
        calculateAggregates: true,
        xAxis: dateAxis,
        yAxis: valueAxis,
        legendValueText:
        "open: [bold]{openValueY}[/] high: [bold]{highValueY}[/] low: [bold]{lowValueY}[/] close: [bold]{valueY}[/]",
        legendRangeValueText: ""
      })
    );

    // Add cursor
    mainPanel.set(
      'cursor',
      am5xy.XYCursor.new(root, {
        yAxis: valueAxis,
        xAxis: dateAxis,
        snapToSeries: [valueSeries],
        snapToSeriesBy: 'y!'
      })
    );

    // Add current value indicator
    const currentValueDataItem = valueAxis.createAxisRange(valueAxis.makeDataItem({ value: 0 }));
    const currentLabel = currentValueDataItem.get("label");
    if (currentLabel) {
      currentLabel.setAll({
        fill: am5.color(0xffffff),
        background: am5.Rectangle.new(root, { fill: am5.color(0x000000) })
      });
    }

    const currentGrid = currentValueDataItem.get("grid");
    if (currentGrid) {
      currentGrid.setAll({ strokeOpacity: 0.5, strokeDasharray: [2, 5] });
    }

    // Add stock legend
    const valueLegend = mainPanel.plotContainer.children.push(
      am5stock.StockLegend.new(root, {
        stockChart: stockChart
      })
    );

    // Set main value series
    stockChart.set("stockSeries", valueSeries);
    valueLegend.data.setAll([valueSeries]);

    // Add scrollbar
    const scrollbar = mainPanel.set(
      "scrollbarX",
      am5xy.XYChartScrollbar.new(root, {
        orientation: "horizontal",
        height: 50
      })
    );
    stockChart.toolsContainer.children.push(scrollbar);

    const sbDateAxis = scrollbar.chart.xAxes.push(
      am5xy.GaplessDateAxis.new(root, {
        extraMax: 0.1,
        baseInterval: { timeUnit: 'minute', count: 5 }, // Changed to 5 minutes
        renderer: am5xy.AxisRendererX.new(root, {
          minorGridEnabled: true
        })
      })
    );

    const sbValueAxis = scrollbar.chart.yAxes.push(
      am5xy.ValueAxis.new(root, {
        renderer: am5xy.AxisRendererY.new(root, {})
      })
    );

    const sbSeries = scrollbar.chart.series.push(
      am5xy.LineSeries.new(root, {
        valueYField: "Close",
        valueXField: "Date",
        xAxis: sbDateAxis,
        yAxis: sbValueAxis
      })
    );

    sbSeries.fills.template.setAll({
      visible: true,
      fillOpacity: 0.3
    });

    // Replace generateChartData with API fetch
    const fetchHistoricalData = async () => {
      try {
        const response = await fetch(
          `${API_BASE}/historical-ticker-data?tickerName=${TICKER_NAME}`
        );
        const historicalData = await response.json();
        
        // Transform API data to match chart format
        const chartData = historicalData.map(item => ({
          Date: item.time * 1000, // Convert to milliseconds
          Close: item.close,
          Open: item.open,
          High: item.high,
          Low: item.low,
          Volume: item.volume
        }));

        // Set data to both series
        valueSeries.data.setAll(chartData);
        sbSeries.data.setAll(chartData);
      } catch (error) {
        console.error('Error fetching historical data:', error);
      }
    };

    // Call the fetch function instead of generating random data
    fetchHistoricalData();

    // Update data periodically with real-time data
    const intervalId = setInterval(async () => {
      try {
        const response = await fetch(`${API_BASE}/last-ticker-data?tickerName=${TICKER_NAME}`);
        const data = await response.json();
        const currentPrice = data[TICKER_NAME].last;
        
        // Use client's local time instead of server time
        const currentTime = new Date().getTime();
        const currentBar = Math.floor(currentTime / (5 * 60 * 1000)) * (5 * 60 * 1000);

        const lastDataObject = valueSeries.data.getIndex(valueSeries.data.length - 1);
        if (lastDataObject) {
          if (currentBar > lastDataObject.Date) {
            // Create new 5-minute candle aligned to local time boundaries
            const newData = {
              Date: currentBar,
              Close: currentPrice,
              Open: currentPrice,
              Low: currentPrice,
              High: currentPrice,
              Volume: data[TICKER_NAME].volume || 0
            };
            valueSeries.data.push(newData);
            sbSeries.data.push(newData);
          } else {
            // Update current candle
            const updatedData = {
              ...lastDataObject,
              Close: currentPrice,
              High: Math.max(currentPrice, lastDataObject.High),
              Low: Math.min(currentPrice, lastDataObject.Low),
              Volume: (data[TICKER_NAME].volume || 0) + (lastDataObject.Volume || 0)
            };
            valueSeries.data.setIndex(valueSeries.data.length - 1, updatedData);
            sbSeries.data.setIndex(sbSeries.data.length - 1, updatedData);
          }

          // Update current value indicator
          if (currentLabel) {
            currentValueDataItem.animate({
              key: "value",
              to: currentPrice,
              duration: 500,
              easing: am5.ease.out(am5.ease.cubic)
            });
            currentLabel.set("text", stockChart.getNumberFormatter().format(currentPrice));
            const bg = currentLabel.get("background");
            if (bg) {
              bg.set("fill", root.interfaceColors.get(
                currentPrice < lastDataObject.Open ? "negative" : "positive"
              ));
            }
          }
        }
      } catch (error) {
        console.error('Error fetching real-time data:', error);
      }
    }, 1000);

    // Cleanup
    return () => {
      clearInterval(intervalId);
      root.dispose();
    };
  }, []);

  return (
    <>
      <HeaderMenu />
      <Container size="xl">
        <Title order={2} mb="md">Dólar Chart</Title>
        <Paper shadow="xs" p="md">
          <div id="chartdiv" style={{ width: '100%', height: '500px' }}></div>
        </Paper>
      </Container>
    </>
  );
}
