import pandas as pd
import numpy as np
import io

# Função para ler os dados a partir de uma string (pode ser adaptado para leitura de arquivo)
def parse_data(csv_text):
    # Usa separador de ";" e converte números com vírgula como separador decimal
    return pd.read_csv(io.StringIO(csv_text), sep=';', decimal=',')

# Função para extrair o strike a partir do código da opção.
# Exemplo: "H25C005300" -> 5300/100 = 53.00 (ajuste a divisão se necessário)
def extract_strike(code, prefix_length=4):
    try:
        # Remove os primeiros 4 caracteres (ex.: "H25C" ou "H25P") e converte o restante para inteiro
        return int(code[prefix_length:]) / 100
    except Exception:
        return np.nan

# --- Dados de exemplo (substitua as strings abaixo pelos dados completos ou leia de arquivos) ---

calls_csv = r"""Data;Série;Código;Contratos em Aberto;Negócios Realizados;Contratos Negociados;Volume;Preço de Abertura;Preço Mínimo;Preço Máximo;Preço Médio;Último Preço;Variação em Pontos;Prêmio de Referência;Última Oferta de Compra;Última Oferta de Venda
2025-02-05;FV83;F26C007500;3000;;;;;;;;;;70,72;
2025-02-05;FV84;F26C007600;150;;;;;;;;;;63,26;
2025-02-05;FV87;F26C006200;1600;;;;;;;;;;331,88;
2025-02-05;FV8N;F26C005100;500;;;;;;;;;;1030,32;
2025-02-05;FV8S;F26C005300;1000;;;;;;;;;;872,29;
2025-02-05;FV8X;F26C005500;110;;;;;;;;;;724,29;
2025-02-05;FV8Z;F26C005600;200;;;;;;;;;;654,87;
2025-02-05;FV91;F26C005700;1000;;;;;;;;;;588,89;
2025-02-05;FV93;F26C005800;1500;;;;;;;;;;528,02;
2025-02-05;FV94;F26C005850;2000;;;;;;;;;;499,65;
2025-02-05;FV95;F26C005900;2145;;;;;;;;;;472,54;
2025-02-05;FV96;F26C005950;2350;;;;;;;;;;446,33;
2025-02-05;FV97;F26C006000;600;;;;;;;;;;421,39;
2025-02-05;FV98;F26C007000;38150;;;;;;;;;;127,2;
2025-02-05;FV99;F26C006500;3500;1;50;580500;232,2;232,2;232,2;232,2;232,2;;229,99;
2025-02-05;FV9G;F26C006300;900;;;;;;;;;;293,47;
2025-02-05;FV9J;F26C006400;50;;;;;;;;;;259,94;
2025-02-05;FV9N;F26C006800;20;;;;;;;;;;160,43;
2025-02-05;FV9P;F26C006850;10;;;;;;;;;;151,32;
2025-02-05;FW82;F27C007000;150;;;;;;;;;;386,27;
2025-02-05;FW83;F27C006000;165;;;;;;;;;;783,79;
2025-02-05;FW84;F27C006500;1550;;;;;;;;;;554,77;
2025-02-05;FW89;F27C005800;100;;;;;;;;;;895,79;
2025-02-05;FW8V;F27C007150;400;;;;;;;;;;348,56;
2025-02-05;FW8W;F27C007200;35;;;;;;;;;;336,89;
2025-02-05;FW9D;F27C008000;500;;;;;;;;;;199,56;
2025-02-05;FWB1;F27C009000;200;;;;;;;;;;105,81;
2025-02-05;FX85;F28C006000;60;;;;;;;;;;1061,86;
2025-02-05;FX8D;F28C006700;25;;;;;;;;;;743,56;
2025-02-05;FX8F;F28C011000;700;;;;;;;;;;103,24;
2025-02-05;FX8G;F28C008500;700;;;;;;;;;;294,24;
2025-02-05;FX8P;F28C007500;1150;;;;;;;;;;485,08;
2025-02-05;FY88;F29C006300;100;;;;;;;;;;1153,21;
2025-02-05;FY8F;F29C007500;645;;;;;;;;;;705,55;
2025-02-05;FY8N;F29C008000;280;;;;;;;;;;575,26;
2025-02-05;FY8P;F29C008500;500;;;;;;;;;;471,87;
2025-02-05;HT86;H25C005300;35;;;;;;;;;;509,66;
2025-02-05;HT87;H25C005350;250;;;;;;;;;;460,49;
2025-02-05;HT88;H25C005400;100;;;;;;;;;;411,57;
2025-02-05;HT89;H25C005450;25;;;;;;;;;;363,15;
2025-02-05;HT8B;H25C005500;60;;;;;;;;;;315,55;
2025-02-05;HT8D;H25C005600;320;;;;;;;;;;224,85;
2025-02-05;HT8F;H25C005650;20;;;;;;;;;;183,63;
2025-02-05;HT8G;H25C005700;20;;;;;;;;;;146,3;
2025-02-05;HT8J;H25C005750;370;;;;;;;;;;114,14;
2025-02-05;HT8K;H25C006200;3525;1;200;80000;8;8;8;8;8;;7,05;
2025-02-05;HT8L;H25C006250;7840;;;;;;;;;;4,86;
2025-02-05;HT8M;H25C006300;370;1;50;13750;5,5;5,5;5,5;5,5;5,5;;3,19;
2025-02-05;HT8N;H25C006350;75;;;;;;;;;;2,07;
2025-02-05;HT8P;H25C006400;45;;;;;;;;;;1,32;
2025-02-05;HT8R;H25C006500;750;;;;;;;;;;0,49;
2025-02-05;HT93;H25C005850;;1;900;3291255;73,14;73,14;73,14;73,14;73,14;;65,36;
2025-02-05;HT94;H25C005900;1595;1;200;470000;47;47;47;47;47;;48,46;
2025-02-05;HT95;H25C005950;50;;;;;;;;;;35,64;
2025-02-05;HT96;H25C006000;13795;1;200;260000;26;26;26;26;26;;26,1;;40
2025-02-05;HT97;H25C006050;275;1;50;47500;19;19;19;19;19;;19,09;
2025-02-05;HT98;H25C006100;3315;1;300;210000;14;14;14;14;14;;13,97;
2025-02-05;HT99;H25C006150;1150;;;;;;;;;;10,12;
2025-02-05;HT9M;H25C005925;;1;25;51875;41,5;41,5;41,5;41,5;41,5;;41,61;
2025-02-05;HT9P;H25C006025;10;;;;;;;;;;22,31;
2025-02-05;HT9R;H25C006125;105;;;;;;;;;;11,98;
2025-02-05;HT9S;H25C006175;90;;;;;;;;;;8,46;
2025-02-05;HTB3;H25C006600;1302;;;;;;;;;;0,16;
2025-02-05;HTB4;H25C006625;15;;;;;;;;;;0,12;
2025-02-05;JT82;J25C005500;200;;;;;;;;;;355,11;
2025-02-05;JT83;J25C005750;1500;;;;;;;;;;169,15;
2025-02-05;JT84;J25C006000;750;;;;;;;;;;66,63;
2025-02-05;JT85;J25C006250;3500;;;;;;;;;;24,87;
2025-02-05;JT86;J25C006500;985;;;;;;;;;;8,28;
2025-02-05;JT8G;J25C005100;980;;;;;;;;;;733,08;
2025-02-05;JT8J;J25C005200;425;;;;;;;;;;635,61;
2025-02-05;JT8M;J25C005400;100;;;;;;;;;;445,07;
2025-02-05;JT8N;J25C005450;10;;;;;;;;;;399,4;
2025-02-05;JT8Q;J25C005600;325;;;;;;;;;;272,25;
2025-02-05;JT8R;J25C005700;100;;;;;;;;;;200,08;
"""

puts_csv = r"""Data;Série;Código;Contratos em Aberto;Negócios Realizados;Contratos Negociados;Volume;Preço de Abertura;Preço Mínimo;Preço Máximo;Preço Médio;Último Preço;Variação em Pontos;Prêmio de Referência;Última Oferta de Compra;Última Oferta de Venda
2025-02-05;FVD7;F26P006200;35;;;;;;;;;293,15;;;
2025-02-05;FVDG;F26P004800;100;;;;;;;;;7,52;;;
2025-02-05;FVDJ;F26P004900;150;;;;;;;;;11,02;;;
2025-02-05;FVDL;F26P005000;600;;;;;;;;;15,72;;;
2025-02-05;FVDM;F26P005050;1600;;;;;;;;;18,62;;;
2025-02-05;FVDN;F26P005100;850;;;;;;;;;21,94;;;
2025-02-05;FVDP;F26P005150;2850;;;;;;;;;25,72;;;
2025-02-05;FVDQ;F26P005200;200;;;;;;;;;29,99;;;
2025-02-05;FVDV;F26P005400;1050;;;;;;;;;52,94;;;
2025-02-05;FVDX;F26P005500;1250;;;;;;;;;68,51;;;
2025-02-05;FVF2;F26P005750;;3;165;1022950;124,58;119,75;124,58;123,99;119,75;122,04;;;
2025-02-05;FVF3;F26P005800;1250;;;;;;;;;136,68;;;
2025-02-05;FVF4;F26P005850;250;;;;;;;;;152,39;;;
2025-02-05;FVF5;F26P005900;210;;;;;;;;;169,36;;;
2025-02-05;FVF6;F26P005950;10;;;;;;;;;187,22;;;
2025-02-05;FVF7;F26P006000;305;;;;;;;;;206,36;;;
2025-02-05;FVFB;F26P006050;10;;;;;;;;;226,38;;;
2025-02-05;FVFF;F26P006250;360;;;;;;;;;317,52;;;
2025-02-05;FVFH;F26P006350;350;;;;;;;;;369,63;;;
2025-02-05;FVFJ;F26P006400;240;;;;;;;;;397,51;;;
2025-02-05;FWD3;F27P006000;1000;;;;;;;;;165,65;;;
2025-02-05;FWD4;F27P006500;595;;;;;;;;;320,43;;;
2025-02-05;FWD5;F27P005000;200;;;;;;;;;27,69;;;
2025-02-05;FWD9;F27P005800;100;;;;;;;;;124,12;;;
2025-02-05;FWDD;F27P005500;200;;;;;;;;;76,15;;;
2025-02-05;FWGQ;F27P006450;100;;;;;;;;;302,17;;;
2025-02-05;FXDB;F28P006500;400;;;;;;;;;226,45;;;
2025-02-05;FXDG;F28P008500;200;;;;;;;;;1041,61;;;
2025-02-05;FXDP;F28P007500;650;;;;;;;;;560,42;;;
2025-02-05;FYD8;F29P006300;100;;;;;;;;;152,5;;;
2025-02-05;FYDN;F29P008000;200;;;;;;;;;576,03;;;
2025-02-05;FYDP;F29P008500;200;;;;;;;;;767,18;;;
2025-02-05;HTD0;H25P005000;10;;;;;;;;;0;;;
2025-02-05;HTD2;H25P005100;70;;;;;;;;;0,01;;;
2025-02-05;HTD8;H25P005400;10;;;;;;;;;1,34;;;
2025-02-05;HTD9;H25P005450;385;;;;;;;;;2,48;;;
2025-02-05;HTDB;H25P005500;10;;;;;;;;;4,44;;;
2025-02-05;HTDD;H25P005600;15;;;;;;;;;12,87;;;
2025-02-05;HTDF;H25P005650;200;;;;;;;;;21,2;;;
2025-02-05;HTDG;H25P005700;250;;;;;;;;;33,44;;;40
2025-02-05;HTDH;H25P005800;2235;;;;;;;;;73,34;;;
2025-02-05;HTDJ;H25P005750;370;1;900;1980000;44;44;44;44;44;50,83;;;57,88
2025-02-05;HTF0;H25P004850;370;;;;;;;;;0;;;
2025-02-05;HTF3;H25P005850;1510;1;100;534500;106,9;106,9;106,9;106,9;106,9;101,18;;;
2025-02-05;HTF4;H25P005900;1605;;;;;;;;;133,83;;;
2025-02-05;HTF5;H25P005950;60;;;;;;;;;170,58;;;
2025-02-05;HTF6;H25P006000;1115;;;;;;;;;210,6;;;
2025-02-05;HTF8;H25P006100;1020;;;;;;;;;297,59;;;
2025-02-05;HTFK;H25P005825;;1;40;149000;74,5;74,5;74,5;74,5;74,5;86,57;;;
2025-02-05;HTFL;H25P005875;245;;;;;;;;;116,98;;;
2025-02-05;HTFP;H25P006025;30;;;;;;;;;231,59;;;
2025-02-05;HTG4;H25P006625;15;;;;;;;;;804,12;;;
2025-02-05;JTD0;J25P005000;175;;;;;;;;;0,08;;;
2025-02-05;JTD1;J25P005250;100;;;;;;;;;1,69;;;
2025-02-05;JTD2;J25P005500;40;;;;;;;;;15,02;;;
2025-02-05;JTD9;J25P004500;205;;;;;;;;;0;;;
2025-02-05;JTDC;J25P004900;100;;;;;;;;;0,02;;;
2025-02-05;JTDD;J25P004950;450;;;;;;;;;0,04;;;
2025-02-05;JTDF;J25P005050;500;;;;;;;;;0,16;;;
2025-02-05;JTDG;J25P005100;400;;;;;;;;;0,3;;;
2025-02-05;JTDH;J25P005150;135;;;;;;;;;0,56;;;
2025-02-05;JTDK;J25P005300;1850;;;;;;;;;2,76;;;
2025-02-05;JTDM;J25P005400;100;;;;;;;;;6,8;;;
2025-02-05;JTDN;J25P005450;200;;;;;;;;;10,23;;;
2025-02-05;JTDP;J25P005550;175;;;;;;;;;21,65;;;
2025-02-05;JTDQ;J25P005600;30;;;;;;;;;30,33;;;
2025-02-05;JTDR;J25P005700;110;;;;;;;;;56,33;;;
2025-02-05;JTDS;J25P005800;10;;;;;;;;;96,23;;;
2025-02-05;JTDT;J25P005850;400;;;;;;;;;121,29;;;
2025-02-05;JTDV;J25P005900;95;;;;;;;;;150,16;;;
2025-02-05;JTG9;J25P005725;200;;;;;;;;;65,04;;;
"""

# --- Processamento dos Dados ---

# Lê os dados
df_calls = parse_data(calls_csv)
df_puts  = parse_data(puts_csv)

# Filtra apenas as opções do contrato futuro H25
df_calls = df_calls[df_calls['Código'].str.startswith("H25C")].copy()
df_puts  = df_puts[df_puts['Código'].str.startswith("H25P")].copy()

# Extrai o strike a partir do código
df_calls['Strike'] = df_calls['Código'].apply(lambda x: extract_strike(x, prefix_length=4))
df_puts['Strike']  = df_puts['Código'].apply(lambda x: extract_strike(x, prefix_length=4))

# Converte "Contratos em Aberto" para numérico (open interest)
df_calls['OI'] = pd.to_numeric(df_calls['Contratos em Aberto'], errors='coerce').fillna(0)
df_puts['OI']  = pd.to_numeric(df_puts['Contratos em Aberto'], errors='coerce').fillna(0)

# Função para normalizar os valores de open interest em um score de 1 a 10
def normalize_strength(oi_series):
    min_oi = oi_series.min()
    max_oi = oi_series.max()
    if max_oi == min_oi:
        return pd.Series(np.ones(len(oi_series)))
    # Normalização simples: transforma o intervalo [min, max] para [1, 10]
    return 1 + 9 * (oi_series - min_oi) / (max_oi - min_oi)

# Calcula o score de barreira (Barrier Strength) para calls e puts
df_calls['Barrier_Strength'] = normalize_strength(df_calls['OI'])
df_puts['Barrier_Strength']  = normalize_strength(df_puts['OI'])

# Cria uma coluna para identificar o tipo da opção
df_calls['Tipo'] = 'Call'
df_puts['Tipo']  = 'Put'

# Junta os resultados de calls e puts em um único DataFrame
df_barriers = pd.concat([
    df_calls[['Strike', 'OI', 'Barrier_Strength', 'Tipo']],
    df_puts[['Strike', 'OI', 'Barrier_Strength', 'Tipo']]
], ignore_index=True)

# Ordena pelo valor do strike
df_barriers.sort_values(by='Strike', inplace=True)

# Exibe a tabela final com as barreiras de liquidez
print("Tabela de Barreiras de Liquidez para H25:")
print(df_barriers.to_string(index=False, formatters={
    'Strike': '{:.2f}'.format,
    'OI': '{:.0f}'.format,
    'Barrier_Strength': '{:.2f}'.format
}))
