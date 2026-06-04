# -*- coding: utf-8 -*-
"""
Created on Fri May  8 20:51:48 2026

@author: claude.ai
"""

"""
build_html.py
Lee data/basicos.csv e data/indicadores.csv e inyecta los valores
en src/index.html, escribiendo el resultado en index.html (raíz).

Estructura esperada de los CSVs:

  basicos.csv
  ┌──────────────────────────────┬───────────┬────────────┐
  │ cargo                        │ basico    │ fecha      │
  ├──────────────────────────────┼───────────┼────────────┤
  │ Ayudante de Primera          │ 221392.92 │ 2026-04-01 │
  │ Jefe de Trabajos Prácticos   │ 265009.91 │ 2026-04-01 │
  │ Profesor Adjunto             │ 308578.79 │ 2026-04-01 │
  └──────────────────────────────┴───────────┴────────────┘

  indicadores.csv
  ┌───────────────────────────────┬────────────┬────────────┐
  │ indicador                     │ valor      │ fecha      │
  ├───────────────────────────────┼────────────┼────────────┤
  │ Tipo de cambio minorista      │ 1416.84    │ 2026-04-30 │
  │ Garantia Salarial             │ 308641.98  │ 2026-02-01 │
  └───────────────────────────────┴────────────┴────────────┘
"""

import csv
import sys
from datetime import datetime
from pathlib import Path

# ── Rutas ──────────────────────────────────────────────────────────────────

ROOT        = Path(__file__).parent.parent
DATA_DIR    = ROOT / "data"
TEMPLATE    = ROOT / "src" / "index.html"
OUTPUT      = ROOT / "dist" / "index.html"


BASICOS_CSV     = DATA_DIR / "basicos.csv"
INDICADORES_CSV = DATA_DIR / "indicadores.csv"

# Nombre exacto de la columna "indicador" en indicadores.csv
KEY_TC          = "Tipo de cambio minorista"
KEY_GARANTIA    = "Garantía Salarial"
KEY_CBT         = "Canasta Básica"
KEY_RIPTE       = "RIPTE"



def leer_basicos(path: Path) -> tuple[dict[str, float], list[str]]:
    """Devuelve ({cargo: basico}, [fechas]) leyendo la última fila por cargo."""
    basicos: dict[str, float] = {}
    fechas:  list[str]        = []
    with open(path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            cargo  = row["cargo"].strip()
            valor  = float(row["basico"].strip())
            fecha  = row["fecha"].strip()
            basicos[cargo] = valor  # sobreescribe → queda la última entrada
            fechas.append(fecha)
    return basicos, fechas



def leer_indicadores(path: Path) -> dict[str, tuple[float, str]]:
    """Devuelve {indicador: (valor, fecha)}."""
    indicadores: dict[str, tuple[float, str]] = {}
    with open(path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            nombre = row["indicador"].strip()
            valor  = float(row["valor"].strip())
            fecha  = row["fecha"].strip()
            indicadores[nombre] = (valor, fecha)
    return indicadores


def fecha_legible(fecha_iso: str) -> str:
    """'2026-04-01' → 'Abril 2026'."""
    MESES = [
        "Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio",
        "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"
    ]
    try:
        dt = datetime.strptime(fecha_iso, "%Y-%m-%d")
        m = MESES[dt.month - 1]
        return m + f" {dt.year}"
    except ValueError:
        return fecha_iso


def build() -> None:
    # ── Leer datos ─────────────────────────────────────────────────────────
    if not BASICOS_CSV.exists():
        sys.exit(f"[ERROR] No se encontró {BASICOS_CSV}")
    if not INDICADORES_CSV.exists():
        sys.exit(f"[ERROR] No se encontró {INDICADORES_CSV}")
    if not TEMPLATE.exists():
        sys.exit(f"[ERROR] No se encontró {TEMPLATE}")

    basicos, fechas_basicos = leer_basicos(BASICOS_CSV)
    indicadores  = leer_indicadores(INDICADORES_CSV)

    # Siempre incluir "Ninguno" con valor 0
    basicos["Ninguno"] = 0.0

    # ── Extraer indicadores ────────────────────────────────────────────────
    if KEY_TC not in indicadores:
        sys.exit(f"[ERROR] '{KEY_TC}' no encontrado en {INDICADORES_CSV}")
    if KEY_GARANTIA not in indicadores:
        sys.exit(f"[ERROR] '{KEY_GARANTIA}' no encontrado en {INDICADORES_CSV}")
    if KEY_CBT not in indicadores:
        sys.exit(f"[ERROR] '{KEY_CBT}' no encontrado en {INDICADORES_CSV}")
    if KEY_RIPTE not in indicadores:
        sys.exit(f"[ERROR] '{KEY_RIPTE}' no encontrado en {INDICADORES_CSV}")

    tipo_de_cambio, _           = indicadores[KEY_TC]
    garantia, _                 = indicadores[KEY_GARANTIA]
    canasta_basica, fecha_cbt   = indicadores[KEY_CBT]
    ripte, fecha_ripte          = indicadores[KEY_RIPTE]
    

    # Fecha de datos: la más reciente entre todos los básicos
    fecha_datos_iso  = max(fechas_basicos)
    fecha_datos_str  = fecha_legible(fecha_datos_iso)
    
    # Fechas de indicadores
    fecha_cbt_str   = fecha_legible(fecha_cbt)
    fecha_ripte_str = fecha_legible(fecha_ripte)

    # ── Serializar BASICOS como JSON inline para JS ────────────────────────
    # Formato: { "Cargo": valor, ... }  con 2 decimales
    basicos_js_lines = []
    for cargo, valor in basicos.items():
        basicos_js_lines.append(f'      "{cargo}": {valor:.2f},')
    # Quitar la coma del último elemento
    basicos_js_lines[-1] = basicos_js_lines[-1].rstrip(",")
    basicos_js = "{\n" + "\n".join(basicos_js_lines) + "\n    }"

    # ── Reemplazar placeholders en el template ─────────────────────────────
    html = TEMPLATE.read_text(encoding="utf-8")

    replacements = {
        "__BASICOS__":          basicos_js,
        "__TIPO_DE_CAMBIO__":   f"{tipo_de_cambio:.2f}",
        "__GARANTIA_SALARIAL__":f"{garantia:.2f}",
        "__CANASTA_BASICA__":   f"{canasta_basica:.2f}",
        "__RIPTE__":            f"{ripte:.2f}",
        "__FECHA_DATOS__":      fecha_datos_str,
        "__FECHA_CBT__":        fecha_cbt_str,
        "__FECHA_RIPTE__":      fecha_ripte_str
    }

    for placeholder, value in replacements.items():
        if placeholder not in html:
            print(f"[WARN] Placeholder '{placeholder}' no encontrado en el template.")
        html = html.replace(placeholder, value)

    OUTPUT.write_text(html, encoding="utf-8")
    print(f"[OK] {OUTPUT} generado correctamente.")
    print(f"     Básicos:          {len(basicos) - 1} cargos")
    print(f"     Tipo de cambio:   $ {tipo_de_cambio:,.2f} ARS/USD")
    print(f"     Garantía salarial:$ {garantia:,.2f}")
    print(f"     Canasta Básica:   $ {canasta_basica:,.2f}")
    print(f"     RIPTE:            $ {ripte:,.2f}")
    print(f"     Fecha de datos:   {fecha_datos_str}")
    print(f"     Fecha de CBT:     {fecha_cbt_str}")
    print(f"     Fecha de RIPTE:   {fecha_ripte_str}")


if __name__ == "__main__":
    build()