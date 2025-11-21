# Apple Health – Dados para Gerontologia

Scripts em Python para ler e organizar os metadados do Apple Saúde (Apple Health),
gerando arquivos CSV estruturados e uma planilha Excel com séries temporais diárias.

Projeto desenvolvido no contexto da PPP Gerontologia – CTI Renato Archer  
Processo SEI: 01241.000186/2025-93

## Como funciona

- Leitura do arquivo `export.xml` exportado pelo app Saúde do iPhone.
- Conversão para CSVs separados por tipo de dado (passos, respiração, energia, sono etc.).
- Geração de uma planilha `timeseries_resumo.xlsx` com:
  - uma aba por métrica principal;
  - valores agregados por dia;
  - gráficos de linha para visualização ao longo do tempo.

## Scripts principais

- `apple_health_export_to_tables_v1_3.py` – converte o `export.xml` em CSVs.
- `auditar_saude_resumo.py` – faz um resumo/auditoria simples dos dados.
- `audit_to_excel_charts.py` – gera a planilha Excel com séries temporais e gráficos.

> Observação: este projeto não faz limpeza nem filtragem dos dados.  
> Ele apenas organiza e agrega os valores; o tratamento estatístico é feito depois.

## Requisitos

- Python 3.9 ou superior
- Pacotes: `pandas` e `xlsxwriter`
