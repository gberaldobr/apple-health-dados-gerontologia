import pandas as pd
from pathlib import Path
import warnings

# ---------------------------------------------------------
# Configuração básica: usa apenas a pasta local e "Saida"
# ---------------------------------------------------------

BASE_DIR = Path(__file__).resolve().parent
SAIDA_DIR = BASE_DIR / "Saida"
SAIDA_DIR.mkdir(exist_ok=True)

OUTPUT_XLSX = SAIDA_DIR / "timeseries_resumo.xlsx"

# Silenciar avisos chatos de parsing
warnings.filterwarnings(
    "ignore",
    message="Could not infer format, so each element will be parsed individually, falling back to `dateutil`."
)
warnings.filterwarnings("ignore", category=pd.errors.DtypeWarning)

# ---------------------------------------------------------
# Métricas quantitativas (1 linha por dia após agregação)
# ---------------------------------------------------------
QUANTITY_METRICS = [
    {
        "name": "Passos",
        "csv": "export_passos.csv",
        "type_filter": "HKQuantityTypeIdentifierStepCount",
        "agg": "sum",  # soma de passos por dia
        "y_label": "Passos (contagem por dia)",
    },
    {
        "name": "Respiração",
        "csv": "export_respiracao.csv",
        "type_filter": "HKQuantityTypeIdentifierRespiratoryRate",
        "agg": "mean",  # média da taxa respiratória
        "y_label": "Respirações/min (média diária)",
    },
    {
        "name": "Energia ativa",
        "csv": "export_energia.csv",
        "type_filter": "HKQuantityTypeIdentifierActiveEnergyBurned",
        "agg": "sum",  # kcal por dia
        "y_label": "Energia ativa (Cal/dia)",
    },
    {
        "name": "FC média",
        "csv": "export_cardiaco.csv",
        "type_filter": "HKQuantityTypeIdentifierHeartRate",
        "agg": "mean",
        "y_label": "Frequência cardíaca (bpm – média diária)",
    },
    {
        "name": "FC repouso",
        "csv": "export_cardiaco.csv",
        "type_filter": "HKQuantityTypeIdentifierRestingHeartRate",
        "agg": "mean",
        "y_label": "FC de repouso (bpm – média diária)",
    },
    {
        "name": "FC caminhada",
        "csv": "export_cardiaco.csv",
        "type_filter": "HKQuantityTypeIdentifierWalkingHeartRateAverage",
        "agg": "mean",
        "y_label": "FC caminhando (bpm – média diária)",
    },
    {
        "name": "HRV SDNN",
        "csv": "export_cardiaco.csv",
        "type_filter": "HKQuantityTypeIdentifierHeartRateVariabilitySDNN",
        "agg": "mean",
        "y_label": "Variabilidade FC SDNN (ms – média diária)",
    },
]

# ---------------------------------------------------------
# Métrica de sono (duração em horas por dia)
# ---------------------------------------------------------
SLEEP_METRIC = {
    "name": "Sono",
    "csv": "export_sono.csv",
    "y_label": "Horas de sono (h/dia, episódios marcados como 'Asleep')",
}


def load_quantity_metric(cfg: dict) -> pd.DataFrame:
    """
    Lê o CSV da métrica, filtra pelo tipo (coluna 'type'),
    agrega por dia (soma ou média) e devolve DF: ['data', name]
    """
    csv_path = SAIDA_DIR / cfg["csv"]
    if not csv_path.exists():
        print(f"[AVISO] Arquivo não encontrado para '{cfg['name']}': {csv_path}")
        return pd.DataFrame(columns=["data", cfg["name"]])

    print(f"[INFO] Lendo {csv_path.name} para métrica '{cfg['name']}'")
    df = pd.read_csv(csv_path, low_memory=False)

    # filtra pelo tipo, se houver
    type_filter = cfg.get("type_filter")
    if type_filter and "type" in df.columns:
        df = df[df["type"] == type_filter]

    if df.empty:
        print(f"[AVISO] Nenhum dado após filtro de tipo para '{cfg['name']}'.")
        return pd.DataFrame(columns=["data", cfg["name"]])

    # converte datas e valores
    df["data"] = pd.to_datetime(df["startDate"], errors="coerce").dt.date
    df["valor"] = pd.to_numeric(df["value"], errors="coerce")

    df = df.dropna(subset=["data", "valor"])
    if df.empty:
        print(f"[AVISO] Nenhum dado válido em '{cfg['name']}' depois da limpeza.")
        return pd.DataFrame(columns=["data", cfg["name"]])

    # agrega por dia
    if cfg["agg"] == "sum":
        serie = df.groupby("data")["valor"].sum()
    else:
        serie = df.groupby("data")["valor"].mean()

    out = serie.reset_index()
    out.columns = ["data", cfg["name"]]
    return out


def load_sleep_metric(cfg: dict) -> pd.DataFrame:
    """
    Calcula horas de sono por dia:
    - usa startDate e endDate
    - considera apenas linhas em que "value" contém "Asleep"
    - soma a duração em horas por dia
    """
    csv_path = SAIDA_DIR / cfg["csv"]
    if not csv_path.exists():
        print(f"[AVISO] Arquivo não encontrado para '{cfg['name']}': {csv_path}")
        return pd.DataFrame(columns=["data", cfg["name"]])

    print(f"[INFO] Lendo {csv_path.name} para métrica de sono '{cfg['name']}'")
    df = pd.read_csv(csv_path, low_memory=False)

    if df.empty:
        print(f"[AVISO] CSV de sono vazio.")
        return pd.DataFrame(columns=["data", cfg["name"]])

    df["start"] = pd.to_datetime(df["startDate"], errors="coerce")
    df["end"] = pd.to_datetime(df["endDate"], errors="coerce")
    df = df.dropna(subset=["start", "end"])

    # mantém apenas episódios "Asleep" (dormindo)
    df = df[df["value"].astype(str).str.contains("Asleep")]
    if df.empty:
        print(f"[AVISO] Nenhum episódio 'Asleep' encontrado em sono.")
        return pd.DataFrame(columns=["data", cfg["name"]])

    df["dur_h"] = (df["end"] - df["start"]).dt.total_seconds() / 3600.0
    df["data"] = df["start"].dt.date

    serie = df.groupby("data")["dur_h"].sum()
    out = serie.reset_index()
    out.columns = ["data", cfg["name"]]
    return out


def main():
    # carrega todas as séries
    series_dict = {}
    ylabels = {}

    for cfg in QUANTITY_METRICS:
        df_metric = load_quantity_metric(cfg)
        series_dict[cfg["name"]] = df_metric
        ylabels[cfg["name"]] = cfg["y_label"]

    df_sono = load_sleep_metric(SLEEP_METRIC)
    series_dict[SLEEP_METRIC["name"]] = df_sono
    ylabels[SLEEP_METRIC["name"]] = SLEEP_METRIC["y_label"]

    if not any(not df.empty for df in series_dict.values()):
        print("[ERRO] Nenhuma série com dados válidos. Verifique os CSVs em 'Saida/'.")
        return

    print(f"[INFO] Gerando Excel em: {OUTPUT_XLSX}")

    with pd.ExcelWriter(OUTPUT_XLSX, engine="xlsxwriter") as writer:
        workbook = writer.book

        for name, df in series_dict.items():
            sheet_name = name[:31]
            df_sorted = df.sort_values("data")
            df_sorted.to_excel(writer, sheet_name=sheet_name, index=False)
            ws = writer.sheets[sheet_name]

            n_rows = len(df_sorted)
            if n_rows == 0:
                continue

            chart = workbook.add_chart({"type": "line"})
            chart.add_series(
                {
                    "name": name,
                    "categories": [sheet_name, 1, 0, n_rows, 0],
                    "values": [sheet_name, 1, 1, n_rows, 1],
                }
            )

            chart.set_title({"name": name})
            chart.set_x_axis({"name": "Data"})
            chart.set_y_axis({"name": ylabels.get(name, "Valor")})
            chart.set_legend({"position": "none"})
            chart.set_size({"width": 720, "height": 400})

            ws.insert_chart("D2", chart)

    print(f"[OK] Arquivo criado com sucesso: {OUTPUT_XLSX}")


if __name__ == "__main__":
    main()
