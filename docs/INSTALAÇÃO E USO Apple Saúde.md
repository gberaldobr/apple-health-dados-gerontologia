# 🛠 INSTALAÇÃO E USO — Apple Saúde → CSV → Excel  
### Projeto: PPP Gerontologia — Extração e Processamento de Dados Apple Saúde  
### Autor: Germano Beraldo (CTI Renato Archer — DISCF/MCTI)  
### Última atualização: 21/11/2025


1. Visão geral
O repositório apple-health-dados-gerontologia contém três scripts principais:
	1.	apple_health_export_to_tables_v1_3.py
	Converte o XML exportado do Apple Saúde em vários arquivos CSV organizados.

	2.	auditar_saude_resumo.py
	Lê os CSVs e gera um resumo numérico (contagens, datas, totais) em texto e planilha.

	3.	audit_to_excel_charts.py
	Gera uma planilha Excel com séries temporais e gráficos das principais métricas.
	O fluxo básico é:
	Exportar dados do iPhone → colocar o XML na pasta do projeto → rodar os scripts na ordem → analisar os arquivos de saída (CSV + Excel).

2. Pré-requisitos
	2.1. Sistema e software
	•	Windows 11 Professional (já confirmado nos testes).
	•	Python 3.11 ou similar instalado (64 bits).
	•	Excel (Microsoft 365 ou equivalente) para abrir as planilhas geradas.
	•	Acesso à internet apenas para a primeira instalação das bibliotecas Python.
	2.2. Ferramentas opcionais
	•	Git (se quiser clonar o repositório; opcional).
	Se não usar Git, pode baixar o projeto como ZIP pelo GitHub.

3. Baixar o projeto
Opção A – via navegador (mais simples)
	1.	Acesse o repositório no GitHub:
	https://github.com/gberaldobr/apple-health-dados-gerontologia
	2.	Clique em Code → Download ZIP.
	3.	Descompacte o ZIP em uma pasta sem acentos, por exemplo:
	C:\Projetos\apple_health_dados_gerontologia

Opção B – via Git (opcional)
	1.	Abra o PowerShell ou Prompt de Comando.
	2.	Vá até a pasta onde deseja guardar o projeto:
	cd C:\Projetos
	3.	Clone o repositório:
	git clone https://github.com/gberaldobr/apple-health-dados-gerontologia.git


4. Criar e ativar o ambiente virtual
	1.	Abra o PowerShell ou Prompt de Comando.
	2.	Vá até a pasta raiz do projeto:
	cd C:\Projetos\apple-health-dados-gerontologia
	3.	Crie o ambiente virtual (apenas na primeira vez):
	python -m venv .venv
	4.	Ative o ambiente virtual:
	.venv\Scripts\activate
	Você saberá que deu certo se aparecer algo como:
	(.venv) C:\Projetos\apple-health-dados-gerontologia>
	Sempre que for usar os scripts em outro dia, basta repetir a etapa 4 (ativar o .venv). Não precisa recriar o ambiente.

5. Instalar as dependências Python
Com o ambiente virtual ativo e dentro da pasta do projeto:
	pip install --upgrade pip
	pip install -r requirements.txt
O arquivo requirements.txt contém as bibliotecas usadas, como:
	•	pandas
	•	matplotlib
	•	openpyxl ou xlsxwriter
	•	python-dateutil
	(e outras auxiliares)
	Essa etapa só precisa ser feita na primeira instalação ou se você mudar de máquina.

6. Estrutura de pastas esperada
A estrutura básica do projeto deve ficar parecida com:
apple-health-dados-gerontologia/
Extração dados de saúde Iphone 15/
├─ .venv/
├─ apple_health_export/
├─ Codificação Python/
├─ relatórios/
├─ Saida/
├─ apple_health_export_to_tables_v1_3.py
├─ audit_to_excel_charts.py
├─ auditar_saude_resumo.py

7. Exportar dados do Apple Saúde (iPhone)
	1.	No iPhone, abra o app Saúde.
	2.	Toque no seu perfil (foto ou ícone no canto superior).
	3.	Role até o final e escolha “Exportar dados de Saúde”.
	4.	Aguarde a preparação do arquivo; será gerado um export.zip.
	5.	Salve o arquivo no iCloud Drive, Arquivos ou envie por AirDrop/E-mail para o PC.
	6.	No Windows, copie o export.zip e descompacte para dentro da pasta do projeto, por exemplo: C:\Projetos\apple-health-dados-gerontologia\apple_health_export		\ .
 
	
8. Execução dos scripts (ordem recomendada)
Abra o PowerShell na pasta do projeto e ative o ambiente virtual:
	cd C:\Projetos\apple-health-dados-gerontologia
	.venv\Scripts\activate
	
	8.1. Passo 1 – Converter o XML em CSV
	Script: apple_health_export_to_tables_v1_3.py
	Esse script:
	•	procura o arquivo de exportação do Apple Saúde (XML),
	•	lê os registros, e
	•	gera arquivos CSV separados por tipo de métrica.
	Comando (a partir da raiz do projeto):
		python src\apple_health_export_to_tables_v1_3.py
	Ao final, você deverá ver na pasta do projeto arquivos como:
	•	export_passos.csv
	•	export_respiracao.csv
	•	export_energia.csv
	•	export_cardiaco.csv
	•	export_sono.csv
	•	export_master.csv (consolidação geral)
	Se os CSVs forem gerados em outra pasta (por exemplo, Saida/), basta verificar o log do script; ele informa o caminho completo.

	8.2. Passo 2 – Gerar resumo numérico (auditoria)
	Script: auditar_saude_resumo.py
	Esse script:
	•	lê os CSVs gerados no passo 1,
	•	calcula contagem de registros, datas mínima e máxima, totais e estatísticas simples,
	•	gera um arquivo texto de auditoria e, em alguns casos, uma planilha de resumo.
	Comando:
		python src\auditar_saude_resumo.py

	Saídas esperadas (em Saida/ ou na pasta atual, conforme a versão):
	•	audit_simplificado.txt
	(resumo em formato texto, fácil de ler e anexar a relatórios)
	•	opcionalmente: audit_resumo_graficos.xlsx
	(dependendo da versão utilizada)
________________________________________
	8.3. Passo 3 – Gerar planilha com séries temporais e gráficos
	Script: audit_to_excel_charts.py
	Esse script:
	•	lê os CSVs de cada métrica (passos, respiração, energia, cardíaco, sono, etc.),
	•	agrupa os dados por dia,
	•	monta uma planilha Excel com:
	o	abas individuais por métrica,
	o	gráficos de linhas ao longo do tempo.
	Comando:
	python src\audit_to_excel_charts.py


	Saída principal:
	•	Saida\timeseries_resumo.xlsx
		Dentro dessa planilha você deve encontrar abas como:
		•	Passos
		•	Respiração
		•	Energia
		•	Cardíaco
		•	Sono
		•	(e eventualmente outras, conforme as métricas disponíveis nos CSVs)

9. Verificando os resultados
	1.	Abra o arquivo:
	Saida\timeseries_resumo.xlsx
	Navegue pelas abas individuais e:
	2.	verifique se o eixo X (datas) está coerente,
	a.	confira se os valores médios, totais e picos fazem sentido,
	b.	observe possíveis valores muito fora da curva (outliers) — esses ainda não são filtrados pelo Processo e Técnica.
	3.	Abra também o audit_simplificado.txt para ter uma visão rápida da quantidade de dados por métrica e período coberto.

10. Problemas comuns e como resolver
	10.1. Python não é reconhecido
	Mensagem:
		'python' is not recognized as an internal or external command...
	•	Verifique se o Python foi instalado com a opção “Add python.exe to PATH”.
	•	Se não, reinstale o Python marcando essa opção ou use:
		py -3 -m venv .venv


	10.2. Erro de biblioteca não encontrada (ex.: ModuleNotFoundError: 'pandas')
	•	Certifique-se de que o ambiente virtual está ativo ((.venv) aparecendo no prompt).
	•	Rode novamente:
	•	pip install -r requirements.txt

	10.3. Erros relacionados a datas (UserWarning: Could not infer format…)
	Isso geralmente é apenas um aviso do pandas sobre o formato de datas; o script tenta interpretar cada registro.
	Se a planilha final foi gerada normalmente, você pode ignorar o aviso.

	10.4. Problemas com caminhos de pasta (acentos / espaços)
	•	Prefira caminhos sem acentos e caracteres especiais, por exemplo:
		C:\Projetos\apple-health-dados-gerontologia\

11. Execução resumida (checklist rápido)
	Sempre que você for rodar a análise completa:
	1.	Exportar dados do Apple Saúde no iPhone → obter export.zip.
	2.	Copiar o ZIP para a pasta do projeto → descompactar → deixar o .xml acessível.
	3.	Abrir PowerShell na pasta do projeto.
	4.	Ativar o ambiente virtual: 
		.venv\Scripts\activate

	5.	Rodar na sequência:
		python src\apple_health_export_to_tables_v1_3.py
		python src\auditar_saude_resumo.py
		python src\audit_to_excel_charts.py
		Abrir os arquivos em Saida/:
	6.	audit_simplificado.txt
	7.	timeseries_resumo.xlsx


	8.	Rodar na sequência:



---

## 12. Aviso sobre uso de IA

Este documento foi elaborado com auxílio de ferramentas de IA (ChatGPT – OpenAI) sob supervisão técnica humana.

---

## 13. Contato

Germano Beraldo  
DISCF – CTI Renato Archer – MCTI  
Campinas/SP – Brasil
gberaldobr@gmail.com
