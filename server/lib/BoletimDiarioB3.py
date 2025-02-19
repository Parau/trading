## Exemplo endereço download Resumo Estatístico do dia 03/02/2025 e 31/01/2025
# https://arquivos.b3.com.br/bdi/download/bdi/2025-02-03/BDI_03-1_20250203.pdf
# https://arquivos.b3.com.br/bdi/download/bdi/2025-02-03/BDI_03-1_20250131.pdf
# Boletim diário do mercado
# https://www.b3.com.br/pt_br/market-data-e-indices/servicos-de-dados/market-data/consultas/boletim-diario/boletim-diario-do-mercado/
## Estrutura pra captura dos valores de dólar
# DOL: Dólar Comercial (Contrato = US$ 50.000,00; Cotação = R$/US$ 1.000,00)
# Mercado de Opções Sobre Disponível - Compra
# DOL: Dólar Comercial (Contrato = US$ 50.000,00; Cotação = R$/US$ 1.000,00)
# Mercado de Opções Sobre Disponível - Venda
# WDO: Dólar Míni
# Mercado de Opções - Compra
# WDO: Dólar Míni
# Mercado de Opções - Venda
## Extração de dados escolhido o PyMuPDF por suportar também outros tipos de arquivo.
# https://pymupdf.readthedocs.io/

import fitz  # PyMuPDF
import pandas as pd
import numpy as np
from typing import List, Tuple
import re
import glob
import os

def extract_date_from_header(doc) -> str:
    """Extract date from the first page header"""
    first_page = doc[0]
    text = first_page.get_text()
    
    # Pattern to match dates like "31 DE JANEIRO DE 2025"
    pattern = r'REFERENTE A .+? - (\d{2} DE [A-ZÇ]+ DE \d{4})'
    match = re.search(pattern, text)
    
    if match:
        date_str = match.group(1)
        # Convert Portuguese month names to numbers
        month_map = {
            'JANEIRO': '01', 'FEVEREIRO': '02', 'MARÇO': '03', 'ABRIL': '04',
            'MAIO': '05', 'JUNHO': '06', 'JULHO': '07', 'AGOSTO': '08',
            'SETEMBRO': '09', 'OUTUBRO': '10', 'NOVEMBRO': '11', 'DEZEMBRO': '12'
        }
        
        # Extract day, month and year
        day = date_str.split()[0]
        month = next(v for k, v in month_map.items() if k in date_str)
        year = date_str.split()[-1]
        
        # Format as YYYY-MM-DD
        return f"{year}-{month}-{day}"
    return None

def extract_options_tables(pdf_path: str, output_path: str, file:str, header: str = "Mercado de Opções Sobre Disponível - Compra", finish: str = "DOL: Dólar Comercial" ) -> str:
    doc = fitz.open(pdf_path)
    table_data: List[List[str]] = []

    # Get date from first page
    reference_date = extract_date_from_header(doc)
    print("Data de referência:", reference_date)

    capture_table = False
    # Updated column names matching the actual PDF structure
    columns = [
        'Série', 'Código', 'Contratos em Aberto', 'Negócios Realizados',
        'Contratos Negociados', 'Volume', 'Preço de Abertura', 'Preço Mínimo',
        'Preço Máximo', 'Preço Médio', 'Último Preço', 'Variação em Pontos',
        'Prêmio de Referência', 'Última Oferta de Compra', 'Última Oferta de Venda'
    ]
    finish_table = False
    first_title = False
    for page in doc:
        blocks = page.get_text("blocks")
        
        for block in blocks:
            text = block[4].strip()
            
            if not first_title:
              if "DOL: Dólar Comercial" in text: 
                  print("achei titulo 1:", text)
                  first_title = True
                  capture_table = False
                  finish_table = False
                  continue
            else:
              if header in text:  #exemplo "Mercado de Opções Sobre Disponível - Compra"
                  print("achei titulo 2:", text)
                  capture_table = True
                  finish_table = False
                  continue
                
            if capture_table and (finish in text):  #título que indica que encerrou encerrou a tabela
                capture_table = False
                finish_table = True
                print("Fim da tabela")
                break
                
            if capture_table:
                # Split the line and process all columns
                row = text.split()
                
                # Validate if this is a data row (should have numbers)
                if len(row) >= len(columns) and any(re.match(r'\d', item) for item in row):
                    table_data.append(row[:len(columns)])  # Take all columns
                #else:
                #    print("desconsiderado:", text)
        if finish_table:
            break
    

    df = pd.DataFrame(table_data, columns=columns)

    numeric_columns = [
        'Contratos em Aberto', 'Negócios Realizados', 'Contratos Negociados',
        'Volume', 'Preço de Abertura', 'Preço Mínimo', 'Preço Máximo',
        'Preço Médio', 'Último Preço', 'Variação em Pontos', 'Prêmio de Referência',
        'Última Oferta de Compra', 'Última Oferta de Venda'
    ]

    for col in numeric_columns:
      # Substituir caracteres especiais no final dos números por nada
      column = df[col].str.replace(r'[^\d,.-]', '', regex=True)
      # Substituir vírgulas por pontos e converter para numérico
      column = column.str.replace(',', '') #.str.replace(',', '.')
      # Substituir valores vazios ou "-" por NaN
      column = column.replace('-', np.nan)
      df[col] =  pd.to_numeric(column, errors='coerce')

    # Acrescenta a coluna de data de referência
    df.insert(0, 'Data', reference_date)  # Insert 'Data' as first column with reference_date value
    
    output_filename = f"{output_path}{reference_date}_{file}.csv"
    #df.to_excel(output_filename, index=False)
    df.to_csv(output_filename, index=False, encoding='utf-8-sig', sep=';')
    
    doc.close()
    return output_filename

def GenerateCSVOptionsDolar():
    pathTo = "./data/opcoes_dolar/"
    pathFrom = "./data/_para_processar/"

    # Print the absolute paths
    print(f"Current working directory: {os.getcwd()}")

    # Look for all BDI files in the pathFrom directory
    #print(f"Path busca arquivos: {os.path.join(pathFrom, 'BDI_03-1_*.pdf')}")
    bdi_files = glob.glob(os.path.join(pathFrom, "BDI_03-1_*.pdf"))
    
    for pdf_file in bdi_files:
        print(f"Processing {pdf_file}...")
        try:
            # Extract options tables for both calls and puts
            extract_options_tables(pdf_file, pathTo, "DOL_OP_Call", "Mercado de Opções Sobre Disponível - Compra")
            extract_options_tables(pdf_file, pathTo, "DOL_OP_Put", "Mercado de Opções Sobre Disponível - Venda", "WDO: Dólar Míni")
            
            # Move file to processed folder after successful processing
            processed_dir = os.path.join(pathFrom, 'arquivos_processados')
            if not os.path.exists(processed_dir):
                os.makedirs(processed_dir)
            os.rename(pdf_file, os.path.join(processed_dir, os.path.basename(pdf_file)))
            #print(f"Successfully moved {pdf_file} to processed folder")
            
        except Exception as e:
            print(f"Erro processando o arquivo {pdf_file}: {str(e)}")
    return 


# Use para teste e modificações rodando diretamente no console python e não no sistema servidor
# python BoletimDiarioB3.py
if __name__ == "__main__":
    #pdf_file = "BDI_03-1_20250131.pdf"
    #pdf_file = "BDI_03-1_20250204.pdf" 
    #pdf_file = "BDI_03-1_20250203.pdf" 
    
    ##
    #pdf_file = "BDI_03-1_20250213.pdf" 
    #output_file = extract_options_tables(pdf_file, "_DOL_OP_Compra.xlsx", "Mercado de Opções Sobre Disponível - Compra")
    #output_file = extract_options_tables(pdf_file, "_DOL_OP_Venda.xlsx", "Mercado de Opções Sobre Disponível - Venda", "WDO: Dólar Míni")
    os.chdir('E:/dev/trading/server/')
    GenerateCSVOptionsDolar()