from analysis import OptionsAnalysis

if __name__ == "__main__":
  analyzer = OptionsAnalysis(5.80, "H25", '../calls.csv', '../puts.csv' )
  pd = analyzer.getOptionsData()
  print(pd[['Strike', 'OI', 'Tipo']])