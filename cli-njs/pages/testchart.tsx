import { useLayoutEffect } from 'react';
import { Container, Text } from '@mantine/core';
import * as am5 from '@amcharts/amcharts5';
import * as am5xy from '@amcharts/amcharts5/xy';
import am5themes_Animated from '@amcharts/amcharts5/themes/Animated';

export default function TestChart() {
	useLayoutEffect(() => {
		// Create root and set theme
		const root = am5.Root.new("chartdiv");
		root.setThemes([am5themes_Animated.new(root)]);
		
		// Create an XYChart with two X axes and one shared Y axis
		const chart = root.container.children.push(
			am5xy.XYChart.new(root, {
				layout: root.verticalLayout,
				paddingRight: 20
			})
		);
		
		// DateAxis for candlestick series (X-axis on bottom)
		const dateAxis = chart.xAxes.push(
			am5xy.DateAxis.new(root, {
				maxDeviation: 0.5,
				baseInterval: { timeUnit: "day", count: 1 },
				renderer: am5xy.AxisRendererX.new(root, { minGridDistance: 50 })
			})
		);
		
		// Secondary ValueAxis for volume (X-axis on top/right)
		const volumeAxis = chart.xAxes.push(
			am5xy.ValueAxis.new(root, {
				renderer: am5xy.AxisRendererX.new(root, { opposite: true }),
				min: 0,
				extraMax: 0.1,
				numberFormatter: root.numberFormatter
			})
		);
		
		// Shared price axis (Y-axis)
		const priceAxis = chart.yAxes.push(
			am5xy.ValueAxis.new(root, {
				renderer: am5xy.AxisRendererY.new(root, {})
			})
		);
		
		// Create candlestick series using the DateAxis and priceAxis
		const candleSeries = chart.series.push(
			am5xy.CandlestickSeries.new(root, {
				name: "Candles",
				xAxis: dateAxis,
				yAxis: priceAxis,
				valueXField: "date",
				openValueYField: "open",
				valueYField: "close",
				lowValueYField: "low",
				highValueYField: "high",
				tooltip: am5.Tooltip.new(root, { labelText: "O:{openValueY}\nH:{highValueY}\nL:{lowValueY}\nC:{valueY}" })
			})
		);
		
		// Create static candlestick data
		const candleData = [
			{ date: new Date(2023, 9, 1).getTime(), open: 100, high: 110, low: 90, close: 105 },
			{ date: new Date(2023, 9, 2).getTime(), open: 105, high: 115, low: 95, close: 110 },
			{ date: new Date(2023, 9, 3).getTime(), open: 110, high: 120, low: 100, close: 115 },
			{ date: new Date(2023, 9, 4).getTime(), open: 115, high: 125, low: 105, close: 120 }
		];
		candleSeries.data.setAll(candleData);
		
		// Create volume series using the volumeAxis (X) and shared priceAxis (Y).
		const volumeSeries = chart.series.push(
			am5xy.ColumnSeries.new(root, {
				name: "Volume",
				xAxis: volumeAxis,
				yAxis: priceAxis,
				valueXField: "volume",
				valueYField: "price",
				tooltip: am5.Tooltip.new(root, { labelText: "Volume: {valueX}" })
			})
		);
		
		 // Set rotation on columns to display horizontal bars.
		volumeSeries.columns.template.setAll({
			rotation: -90,
			centerY: am5.percent(50)
		});
		
		// Create static volume data derived from candlestick close prices and random volumes.
		const volumeData = candleData.map(item => ({
			price: item.close,
			volume: Math.round(Math.random() * 5000) + 1000
		}));
		volumeSeries.data.setAll(volumeData);
		
		// Optional: animate in
		chart.appear(1000, 100);
		
		return () => {
			root.dispose();
		};
	}, []);
	
	return (
		<Container size="md" py="xl">
			<Text size="xl" fw={700} ta="center">
				Financial Chart with Volume Profile
			</Text>
			<div id="chartdiv" style={{ width: '100%', height: '500px' }}></div>
		</Container>
	);
}
