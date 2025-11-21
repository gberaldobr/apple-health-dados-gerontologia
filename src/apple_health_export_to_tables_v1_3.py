# =============================================================
# Script: apple_health_export_to_tables_v1_3.py
# Projeto: PPP Gerontologia / DISCF / CTI Renato Archer
# Responsável: Germano Beraldo Filho
# Python: 3.9.13
# Execução local simplificada — versão ampliada (Cardíaco, Passos, Sono, Respiração, Energia)
# =============================================================

import os, sys, csv, math, time, threading
from datetime import datetime
from pathlib import Path
import xml.etree.ElementTree as ET

try:
    import pandas as pd
except ImportError:
    pd = None

# -------------------------------------------------------------
# ========== BLOCO A - PROGRESSO E AUDITORIA SIMPLIFICADA ======
# -------------------------------------------------------------

class Spinner:
    def __init__(self, msg="Processando..."):
        self.msg = msg
        self._stop = False
        self._thread = None

    def start(self):
        def spin():
            symbols = "|/-\\"
            i = 0
            while not self._stop:
                sys.stdout.write(f"\r{self.msg} {symbols[i % 4]}")
                sys.stdout.flush()
                i += 1
                time.sleep(0.1)
            sys.stdout.write("\r" + " " * (len(self.msg) + 2) + "\r")

        self._thread = threading.Thread(target=spin, daemon=True)
        self._thread.start()

    def stop(self):
        self._stop = True
        if self._thread:
            self._thread.join()

# -------------------------------------------------------------
# ========== BLOCO B - FUNÇÕES DE LEITURA E AUDITORIA ==========
# -------------------------------------------------------------

def safe_float(x):
    try:
        return float(str(x).replace(",", "."))
    except Exception:
        return math.nan

def parse_date(s):
    if not s:
        return None
    for fmt in ("%Y-%m-%d %H:%M:%S %z", "%Y-%m-%d %H:%M:%S",
                "%Y-%m-%dT%H:%M:%S%z", "%Y-%m-%d"):
        try:
            return datetime.strptime(s, fmt)
        except Exception:
            pass
    return None

def periodo(rows, start="startDate", end="endDate"):
    dmin, dmax = None, None
    for r in rows:
        s = parse_date(r.get(start) or r.get(start.capitalize()))
        e = parse_date(r.get(end) or r.get(end.capitalize())) or s
        if s:
            dmin = s if (dmin is None or s < dmin) else dmin
            dmax = e if (dmax is None or e > dmax) else dmax
    return dmin, dmax

def gerar_auditoria_simplificada(outdir):
    """Cria audit_simplificado.txt com resumo básico"""
    outdir = Path(outdir)
    out_txt = outdir / "audit_simplificado.txt"

    def ler_csv(nome):
        p = outdir / nome
        return list(csv.DictReader(open(p, encoding="utf-8", errors="ignore"))) if p.exists() else []

    master = ler_csv("export_master.csv")
    cardiaco = ler_csv("export_cardiaco.csv")
    passos = ler_csv("export_passos.csv")
    sono = ler_csv("export_sono.csv")
    resp = ler_csv("export_respiracao.csv")
    energia = ler_csv("export_energia.csv")

    lines = [f"Auditoria Simplificada — {datetime.now():%Y-%m-%d %H:%M:%S}", ""]
    lines.append(f"Total de registros (master): {len(master):,}".replace(",", "."))

    # Cardíaco
    if cardiaco:
        vals = [safe_float(r.get("value") or r.get("Value")) for r in cardiaco if r.get("value")]
        vals = [v for v in vals if not math.isnan(v)]
        dmin, dmax = periodo(cardiaco)
        lines.append("\n🩺 Cardíaco:")
        lines.append(f"  Registros: {len(cardiaco):,}".replace(",", "."))
        if dmin and dmax:
            lines.append(f"  Período: {dmin:%d/%m/%Y %H:%M} → {dmax:%d/%m/%Y %H:%M}")
        if vals:
            lines.append(f"  BPM (média/máx/mín): {sum(vals)/len(vals):.1f} / {max(vals):.1f} / {min(vals):.1f}")

    # Passos
    if passos:
        total = sum(safe_float(r.get("value")) for r in passos)
        dmin, dmax = periodo(passos)
        lines.append("\n🚶‍♂️ Passos:")
        lines.append(f"  Registros: {len(passos):,}".replace(",", "."))
        if dmin and dmax:
            lines.append(f"  Período: {dmin:%d/%m/%Y} → {dmax:%d/%m/%Y}")
        lines.append(f"  Total de passos: {int(total):,}".replace(",", "."))
        lines.append(f"  Média por registro: {int(total/len(passos)):,} passos".replace(",", "."))

    # Sono
    if sono:
        dmin, dmax = periodo(sono)
        lines.append("\n😴 Sono:")
        lines.append(f"  Registros: {len(sono):,}".replace(",", "."))
        if dmin and dmax:
            lines.append(f"  Período: {dmin:%d/%m/%Y} → {dmax:%d/%m/%Y}")

    # Respiração
    if resp:
        vals = [safe_float(r.get("value")) for r in resp if r.get("value")]
        vals = [v for v in vals if not math.isnan(v)]
        dmin, dmax = periodo(resp)
        lines.append("\n🌬️ Respiração:")
        lines.append(f"  Registros: {len(resp):,}".replace(",", "."))
        if dmin and dmax:
            lines.append(f"  Período: {dmin:%d/%m/%Y} → {dmax:%d/%m/%Y}")
        if vals:
            lines.append(f"  Média de respirações: {sum(vals)/len(vals):.2f} rpm")

    # Energia
    if energia:
        total = sum(safe_float(r.get("value")) for r in energia if r.get("value"))
        dmin, dmax = periodo(energia)
        lines.append("\n⚡ Energia:")
        lines.append(f"  Registros: {len(energia):,}".replace(",", "."))
        if dmin and dmax:
            lines.append(f"  Período: {dmin:%d/%m/%Y} → {dmax:%d/%m/%Y}")
        lines.append(f"  Energia total: {total:.2f} kcal")

    out_txt.write_text("\n".join(lines), encoding="utf-8")
    print(f"[AUDIT] Gerado: {out_txt}")

# -------------------------------------------------------------
# ========== BLOCO C - PROCESSAMENTO DOS XMLs =================
# -------------------------------------------------------------

def processar_exportacao(indir, outdir, gerar_excel=False):
    indir = Path(indir)
    outdir = Path(outdir)
    outdir.mkdir(exist_ok=True)

    export_xml = list(indir.glob("export*.xml"))[0]
    print(f"[INFO] Lendo: {export_xml.name}")
    root = ET.parse(export_xml).getroot()
    records = [r.attrib for r in root.findall("Record")]

    # Descobre todos os campos de forma dinâmica
    all_fields = set()
    for r in records:
        all_fields.update(r.keys())
    fieldnames = sorted(all_fields)

    # Grava CSV principal
    master_csv = outdir / "export_master.csv"
    with master_csv.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(records)
    print(f"[OK] Gerado: {master_csv}")

    # Domínios principais e suas chaves
    dominios = {
        "cardiaco": "HeartRate",
        "passos": "StepCount",
        "sono": "SleepAnalysis",
        "respiracao": "RespiratoryRate",
        "energia": "ActiveEnergyBurned"
    }

    for nome, chave in dominios.items():
        subset = [r for r in records if chave.lower() in (r.get("type") or "").lower()]
        if subset:
            csv_path = outdir / f"export_{nome}.csv"
            with csv_path.open("w", newline="", encoding="utf-8") as f:
                writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction="ignore")
                writer.writeheader()
                writer.writerows(subset)
            print(f"[OK] Gerado: {csv_path}")

    # Excel opcional
    if gerar_excel and pd:
        df = pd.read_csv(master_csv)
        xlsx_path = outdir / "export_master.xlsx"
        df.to_excel(xlsx_path, index=False)
        print(f"[OK] Gerado: {xlsx_path}")

# -------------------------------------------------------------
# ========== BLOCO D - PROCESSAMENTO DO CDA (export_cda.xml) ==
# -------------------------------------------------------------
def processar_cda(indir: Path, outdir: Path):
    """Extrai observações do export_cda.xml em cda_master/cardiaco/outros."""
    cda_files = list(indir.glob("*export_cda*.xml"))
    if not cda_files:
        print("[INFO] CDA não encontrado (pulando).")
        return
    cda_xml = cda_files[0]
    print(f"[INFO] Lendo CDA: {cda_xml.name}")

    # CDA costuma vir com namespaces HL7; usamos curinga {*} para ignorar o prefixo
    ns_any = "{*}"
    tree = ET.parse(cda_xml)
    root = tree.getroot()

    rows = []
    # Observações ficam tipicamente em .../structuredBody/component/section/entry/observation
    for obs in root.findall(".//" + ns_any + "observation"):
        r = {}
        code = obs.find(ns_any + "code")
        val  = obs.find(ns_any + "value")
        et   = obs.find(ns_any + "effectiveTime")

        # atributos comuns
        if code is not None:
            r["code"] = code.attrib.get("code")
            r["codeSystem"] = code.attrib.get("codeSystem")
            r["displayName"] = code.attrib.get("displayName")

        # valor pode vir como atributo @value ou texto
        if val is not None:
            r["value"] = val.attrib.get("value") or (val.text or "").strip()
            r["unit"]  = val.attrib.get("unit")

        # datas (HL7 pode ter low/high ou value)
        if et is not None:
            low = et.find(ns_any + "low")
            high = et.find(ns_any + "high")
            if low is not None:
                r["startDate"] = low.attrib.get("value")
            if high is not None:
                r["endDate"] = high.attrib.get("value")
            if not r.get("startDate"):
                r["startDate"] = et.attrib.get("value")
            if not r.get("endDate"):
                r["endDate"] = r.get("startDate")

        # tenta identificar um tipo amigável
        # heurística: se displayName ou code sugerem frequência cardíaca
        tag = (r.get("displayName") or r.get("code") or "").lower()
        if "heart" in tag or "card" in tag or r.get("unit", "").lower() in ("bpm",):
            r["domain"] = "cardiaco"
        else:
            r["domain"] = "outros"

        # guarda tag bruta do elemento (útil para auditoria)
        r["tag"] = obs.tag.split("}")[-1]
        rows.append(r)

    if not rows:
        print("[INFO] CDA sem observações úteis (pulando).")
        return

    # campos dinâmicos
    fieldnames = sorted({k for row in rows for k in row.keys()})

    # master
    cda_master = outdir / "cda_master.csv"
    with cda_master.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames, extrasaction="ignore")
        w.writeheader()
        w.writerows(rows)
    print(f"[OK] Gerado: {cda_master}")

    # divisões simples
    cardiaco = [r for r in rows if r.get("domain") == "cardiaco"]
    outros   = [r for r in rows if r.get("domain") == "outros"]

    if cardiaco:
        p = outdir / "cda_cardiaco.csv"
        with p.open("w", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=fieldnames, extrasaction="ignore")
            w.writeheader()
            w.writerows(cardiaco)
        print(f"[OK] Gerado: {p}")

    if outros:
        p = outdir / "cda_outros.csv"
        with p.open("w", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=fieldnames, extrasaction="ignore")
            w.writeheader()
            w.writerows(outros)
        print(f"[OK] Gerado: {p}")


# -------------------------------------------------------------
# ========== BLOCO E - ROTAS GPX (workout-routes/*.gpx) =======
# -------------------------------------------------------------
def processar_rotas(indir: Path, outdir: Path):
    """Lê todos os GPX (workout-routes) e gera routes_all.csv."""
    gpx_dirs = list(indir.glob("workout-*")) + list(indir.glob("workout*")) + list(indir.glob("routes*"))
    gpx_files = []
    for d in gpx_dirs:
        gpx_files.extend(d.rglob("*.gpx"))
    if not gpx_files:
        # alguns exports usam 'workout-routes'
        gpx_files = list((indir / "workout-routes").rglob("*.gpx"))

    if not gpx_files:
        print("[INFO] GPX não encontrados (pulando).")
        return

    print(f"[INFO] Lendo {len(gpx_files)} arquivo(s) GPX...")
    ns_any = "{*}"
    out_rows = []

    for gpx_path in gpx_files:
        try:
            root = ET.parse(gpx_path).getroot()
        except Exception:
            continue

        # tenta obter um id pelo nome do arquivo/pasta
        workout_id = gpx_path.stem

        # pontos: trk > trkseg > trkpt
        for i, pt in enumerate(root.findall(".//" + ns_any + "trkpt")):
            lat = pt.attrib.get("lat")
            lon = pt.attrib.get("lon")
            ele = None
            time_iso = None
            ele_el = pt.find(ns_any + "ele")
            if ele_el is not None and ele_el.text:
                ele = ele_el.text.strip()
            t_el = pt.find(ns_any + "time")
            if t_el is not None and t_el.text:
                time_iso = t_el.text.strip()

            out_rows.append({
                "workout_id": workout_id,
                "idx": i,
                "lat": lat,
                "lon": lon,
                "ele": ele,
                "time": time_iso,
                "file": str(gpx_path.relative_to(indir))
            })

    if not out_rows:
        print("[INFO] Nenhum ponto GPX válido (pulando).")
        return

    fields = ["workout_id", "idx", "lat", "lon", "ele", "time", "file"]
    routes_csv = outdir / "routes_all.csv"
    with routes_csv.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fields, extrasaction="ignore")
        w.writeheader()
        w.writerows(out_rows)
    print(f"[OK] Gerado: {routes_csv}")

# -------------------------------------------------------------
# ========== EXECUÇÃO DIRETA ==================================
# -------------------------------------------------------------

if __name__ == "__main__":
    base = Path(".")
    pasta_entrada = base / "apple_health_export 30-10-2025"
    pasta_saida = base / "Saida"

    print("[INFO] Iniciando extração local ampliada...")
    print(f"  Entrada: {pasta_entrada}")
    print(f"  Saída:   {pasta_saida}")
    print("")

    sp = Spinner("Processando dados Apple Health")
    sp.start()
    try:
        processar_exportacao(pasta_entrada, pasta_saida, gerar_excel=True)
    finally:
        sp.stop()

    gerar_auditoria_simplificada(pasta_saida)
    print("[OK] Processo finalizado com sucesso.")
