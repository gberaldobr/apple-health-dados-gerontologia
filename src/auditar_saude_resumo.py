import re
from pathlib import Path
import pandas as pd

# ---------------------------------------------------------
# Configurações de caminho
# ---------------------------------------------------------

# Pasta onde o script está
BASE_DIR = Path(__file__).resolve().parent

# Arquivo de entrada (gerado pelo auditar_saude_resumo.py)
AUDIT_FILE = BASE_DIR / "Saida" / "audit_simplificado.txt"

# Arquivo de saída (Excel com tabela + gráfico)
OUTPUT_XLSX = BASE_DIR / "Saida" / "audit_resumo_graficos.xlsx"


# ---------------------------------------------------------
# Mapeamento de nomes HK -> nomes amigáveis para o gráfico
# ---------------------------------------------------------

MAPEAMENTO_NOMES = {
    "HKQuantityTypeIdentifierStepCount": "Passos",
    "HKQuantityTypeIdentifierRespiratoryRate": "Respiração",
    "HKQuantityTypeIdentifierActiveEnergyBurned": "Energia ativa",
    "HKQuantityTypeIdentifierDistanceWalkingRunning": "Distância percorrida",
    "HKQuantityTypeIdentifierBasalEnergyBurned": "Energia basal",
    "HKQuantityTypeIdentifierRunningSpeed": "Corrida – Velocidade",
    "HKQuantityTypeIdentifierPhysicalEffort": "Esforço físico",
    "HKCategoryTypeIdentifierSleepAnalysis": "Sono",
    "HKQuantityTypeIdentifierRunningPower": "Corrida – Potência",
}


def normalizar_nome(metrica: str) -> str:
    """
    Converte o texto original da coluna 'metrica' em um nome amigável
    para o gráfico (Passos, Respiração, Sono, etc.).
    """
    if metrica is None:
        return ""

    # Remove espaços extras e traços iniciais
    metrica = metrica.strip().strip("- ").strip()

    # Se for um identificador HK conhecido, troca pelo nome amigável
    if metrica in MAPEAMENTO_NOMES:
        return MAPEAMENTO_NOMES[metrica]

    # Mantém "Registros" como está (se ainda existisse)
    if metrica.lower() == "registros":
        return "Registros"

    # Caso não esteja no dicionário, devolve o original (fallback)
    return metrica


# ---------------------------------------------------------
# Parsing do audit_simplificado.txt
# ---------------------------------------------------------

def parse_audit_file(path: Path):
    """
    Lê o audit_simplificado.txt e separa linhas em:
    - métricas numéricas (para gráfico)
    - informações textuais (para referência)

    Formato esperado das linhas numéricas:
      'Label: valor' ou 'Label = valor'
    """
    numeric_rows = []
    text_rows = []

    if not path.exists():
        raise FileNotFoundError(f"Arquivo não encontrado: {path}")

    with path.open("r", encoding="utf-8", errors="ignore") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue  # pula linhas em branco

            # Padrão "label: valor" ou "label = valor"
            m = re.match(r"^(.*?)[=:]\s*(.+)$", line)
            if not m:
                # linha sem separador claro -> só texto
                text_rows.append({"chave": "", "descricao": line})
                continue

            label = m.group(1).strip()
            value_str = m.group(2).strip()

            # tenta converter para número (float)
            value_str_std = value_str.replace(",", ".")
            try:
                value_num = float(value_str_std)
                numeric_rows.append({"metrica": label, "valor": value_num})
            except ValueError:
                # não é numérico -> trata como texto
                text_rows.append({"chave": label, "descricao": value_str})

    df_numeric = pd.DataFrame(numeric_rows)
    df_text = pd.DataFrame(text_rows)

    return df_numeric, df_text


# ---------------------------------------------------------
# Geração do Excel + gráfico
# ---------------------------------------------------------

def build_excel_with_charts(df_numeric: pd.DataFrame,
                            df_text: pd.DataFrame,
                            out_path: Path):
    """
    Gera um arquivo Excel com:
    - Aba 'Resumo_numerico': tabela de métricas + gráfico de barras
    - Aba 'Resumo_textual': linhas descritivas do audit_simplificado
    """
    with pd.ExcelWriter(out_path, engine="xlsxwriter") as writer:
        # Aba numérica
        sheet_num = "Resumo_numerico"
        df_numeric.to_excel(writer, index=False, sheet_name=sheet_num)

        # Aba textual (se houver)
        if not df_text.empty:
            sheet_txt = "Resumo_textual"
            df_text.to_excel(writer, index=False, sheet_name=sheet_txt)

        workbook = writer.book
        worksheet_num = writer.sheets[sheet_num]

        # Só cria gráfico se houver dados numéricos
        if not df_numeric.empty:
            chart = workbook.add_chart({"type": "column"})

            # Linhas de dados começam em linha 1 (linha 0 = cabeçalho)
            num_rows = len(df_numeric)

            # Série de dados
            chart.add_series({
                "name": "Valores",
                "categories": [sheet_num, 1, 0, num_rows, 0],  # col A: metrica
                "values":     [sheet_num, 1, 1, num_rows, 1],  # col B: valor
            })

            chart.set_title({"name": "Resumo numérico – audit_simplificado"})
            chart.set_x_axis({"name": "Métrica"})
            chart.set_y_axis({"name": "Valor"})
            chart.set_legend({"position": "none"})
            chart.set_size({"width": 720, "height": 480})

            # Insere o gráfico, por exemplo em D2
            worksheet_num.insert_chart("D2", chart)


# ---------------------------------------------------------
# Função principal
# ---------------------------------------------------------

def main():
    print(f"Lendo arquivo de auditoria: {AUDIT_FILE}")
    df_numeric, df_text = parse_audit_file(AUDIT_FILE)

    # Aplica nomes amigáveis nas métricas
    if not df_numeric.empty:
        df_numeric["metrica"] = df_numeric["metrica"].apply(normalizar_nome)

        # Remove linhas genéricas 'Registros' se existirem,
        # para evitar barras duplicadas/sem contexto no gráfico.
        df_numeric = df_numeric[df_numeric["metrica"] != "Registros"].reset_index(drop=True)

    print("\nResumo numérico (já normalizado):")
    print(df_numeric if not df_numeric.empty else "  (nenhuma métrica numérica identificada)")

    print("\nResumo textual:")
    print(df_text if not df_text.empty else "  (nenhuma linha textual identificada)")

    print(f"\nGerando Excel com gráficos em: {OUTPUT_XLSX}")
    build_excel_with_charts(df_numeric, df_text, OUTPUT_XLSX)
    print("Concluído.")


if __name__ == "__main__":
    main()
