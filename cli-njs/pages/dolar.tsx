import { useEffect, useRef } from 'react';
import * as am5 from '@amcharts/amcharts5';
import * as am5xy from '@amcharts/amcharts5/xy';
import * as am5stock from '@amcharts/amcharts5/stock';
import am5themes_Animated from '@amcharts/amcharts5/themes/Animated';
import { Container, Title, Paper } from '@mantine/core';
import { HeaderMenu } from '../components/HeaderMenu/HeaderMenu';
import am5locales_pt_BR from "@amcharts/amcharts5/locales/pt_BR";

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

    root.locale = am5locales_pt_BR;
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
    const closePriceAxis = mainPanel.yAxes.push(
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
        //calculateAggregates: true,
        xAxis: dateAxis,
        yAxis: closePriceAxis,
        legendValueText:
        "open: [bold]{openValueY}[/] high: [bold]{highValueY}[/] low: [bold]{lowValueY}[/] close: [bold]{valueY}[/]",
        legendRangeValueText: ""
      })
    );

    // Add cursor
    mainPanel.set(
      'cursor',
      am5xy.XYCursor.new(root, {
        yAxis: closePriceAxis,
        xAxis: dateAxis,
        snapToSeries: [valueSeries],
        snapToSeriesBy: 'y!'
      })
    );

    // Add current value indicator
    const currentValueDataItem = closePriceAxis.createAxisRange(closePriceAxis.makeDataItem({ value: 0 }));
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

    // Create options panel
    const optionsPanel = stockChart.panels.push(
      am5stock.StockPanel.new(root, {
        wheelY: "zoomX",
        panX: true,
        height: 200
      })
    );

    // Create value axis (x-axis for horizontal bars)
    const optionsVolumeAxis = optionsPanel.xAxes.push(
      am5xy.ValueAxis.new(root, {
        renderer: am5xy.AxisRendererX.new(root, {  inversed: true, opposite: true }),
        numberFormat: '#,###.00',
        calculateTotals: true
      })
    );

    // Create category axis (y-axis for strikes)
    const optionsStrikeAxis = optionsPanel.yAxes.push(
      am5xy.CategoryAxis.new(root, {
        categoryField: "Strike",
        renderer: am5xy.AxisRendererY.new(root, {
          // Remove inversed: true to show lower values at bottom
          cellStartLocation: 0.1,
          cellEndLocation: 0.9
        }),
        tooltip: am5.Tooltip.new(root, {})
      })
    );

    // Create series for calls
    const callsSeries = optionsPanel.series.push(
      am5xy.ColumnSeries.new(root, {
        name: "Calls",
        //clustered: false,
        xAxis: optionsVolumeAxis,
        yAxis: optionsStrikeAxis,
        // Swap valueXField and valueYField for horizontal bars
        valueYField: "Close",
        valueXField: "OI",
        categoryYField: "Close",
        fill: am5.color(0x00ff00),
        stroke: am5.color(0x00ff00)
      })
    );

    // Create series for puts
    const putsSeries = optionsPanel.series.push(
      am5xy.ColumnSeries.new(root, {
        name: "Puts",
        xAxis: optionsVolumeAxis,
        yAxis: optionsStrikeAxis,
        // Swap valueXField and valueYField for horizontal bars
        valueYField: "Close",
        valueXField: "OI",
        categoryYField: "Close",
        fill: am5.color(0xff0000),
        stroke: am5.color(0xff0000)
      })
    );

    // Add legend
    const optionsLegend = optionsPanel.plotContainer.children.push(
      am5stock.StockLegend.new(root, {
        stockChart: stockChart
      })
    );
    optionsLegend.data.setAll([callsSeries, putsSeries]);

    // Fetch and set options data
    const fetchOptionsData = async () => {
      try {
        const response = await fetch(`${API_BASE}/dolar-options`);
        const data = await response.json();
        
        // Transform strikes to match dolar price scale (multiply by 1000)
        const calls = data.options
          .filter(opt => opt.Tipo === 'Call')
          .map(opt => ({ ...opt}));
        
        const puts = data.options
          .filter(opt => opt.Tipo === 'Put')
          .map(opt => ({ ...opt }));

        // Set data to series
        calls.forEach(call => call.Close = call.Strike * 1000); //para usas o mesmo eixo Y da série do candle
        puts.forEach(puts => puts.Close = puts.Strike * 1000); //para usas o mesmo eixo Y da série do candle
        //console.log(calls);

        callsSeries.data.setAll(calls);
        putsSeries.data.setAll(puts);
        
        // Set all unique strikes as categories (must also multiply strikes here)
        const strikes = [...new Set(data.options.map(opt => opt.Strike * 1000))].sort((a, b) => a - b);
        optionsStrikeAxis.data.setAll(strikes.map(strike => ({ Strike: strike })));
      } catch (error) {
        console.error('Error fetching options data:', error);
      }
    };

    // Initial fetch and periodic updates
    fetchOptionsData();

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
