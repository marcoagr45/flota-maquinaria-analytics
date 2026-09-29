# -*- coding: utf-8 -*-
"""
Anonimiza los catálogos y movimientos para publicación en GitHub (Fase 6).

Criterio confirmado por Marco (29/09/2026): los PROVEEDORES EXTERNOS (talleres, mecánicos,
refaccionarias) conservan su nombre real — trabajan bajo su propio nombre como parte de su oficio
(recomendación de boca en boca), y no hay ningún dato sensible de la empresa en eso. Lo que se
protege es información INTERNA de la empresa:
 - Nómina (SUELDOS, BONOS): se excluye por completo, no solo se oculta.
 - Personal interno identificado por nombre (empleados, no proveedores externos) y los
   beneficiarios de préstamos/anticipos internos: se sustituyen por un marcador genérico,
   tanto en las columnas dedicadas como en el texto libre de `concepto`/`medio_pago` donde
   aparecían mencionados.
 - Folios fiscales reales: se sustituyen por una bandera booleana `tiene_factura` (se conserva
   la señal analítica sin exponer el folio).
 - No hay números de serie en este dataset (equipos.csv no los captura), nada que quitar ahí.

Este script toma como entrada el `movimientos.csv`/`proveedores.csv` COMPLETOS (con sueldos,
nombres reales y folios), que viven solo en el control interno de la empresa — no en este
repositorio. Ejecutarlo regenera la carpeta `data/` publicada aquí a partir de ese archivo privado.
"""
import csv
import os
import re

SRC = os.environ.get("MG_DATA_SRC", "/home/claude/work")
OUT = os.environ.get("MG_DATA_OUT", "/home/claude/work/anon_build/data")
os.makedirs(OUT, exist_ok=True)


def read_csv(name):
    with open(f"{SRC}/{name}", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def write_csv(name, rows, fieldnames):
    with open(f"{OUT}/{name}", "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        for r in rows:
            w.writerow(r)


equipos = read_csv("equipos.csv")
categorias = read_csv("categorias.csv")
proveedores = read_csv("proveedores.csv")
movimientos = read_csv("movimientos.csv")

# --- Personal interno de la empresa (NO proveedores externos) confirmado en el proyecto ---
# Cada entrada es (patrón regex case-insensitive con límite de palabra, marcador de reemplazo).
PERSONAL_INTERNO = [
    (r"\bREYES\s+HUMBERTO\s+TEPAL\s+CHAN\b", "[ENCARGADO INTERNO]"),
    (r"\bREYES\s+TEPAL\b", "[EMPLEADO INTERNO]"),
    (r"\bMANUEL\s+G[ÜU]EMEZ\b", "[BENEFICIARIO INTERNO]"),
    (r"\bMARCO\s+G[ÜU]EMEZ\b", "[BENEFICIARIO INTERNO]"),
    (r"\bNEHEM[IÍ]AS\b", "[BENEFICIARIO INTERNO]"),
    (r"\bALONSO\s+CANUL\b", "[EMPLEADO INTERNO]"),
    (r"\bFRANCISCO\s+CHIM\b", "[EMPLEADO INTERNO]"),
    (r"\bGUADALUPE\s+GABRIEL\s+CAAMAL\s+CHI\b", "[EMPLEADO INTERNO]"),
    # Coincidencias sueltas ya confirmadas por el proyecto como referencia a personal interno
    # (p.ej. "REYES" en "DILIGENCIAS MAQUINARIA REYES" = Reyes Tepal; "MG" = marcador interno).
    (r"\bREYES\b", "[EMPLEADO INTERNO]"),
    (r"\bMG\b", "[INTERNO]"),
]


def redactar_interno(texto):
    if not texto:
        return texto
    out = texto
    for patron, marcador in PERSONAL_INTERNO:
        out = re.sub(patron, marcador, out, flags=re.IGNORECASE)
    return out


# --- Proveedores: se conservan reales; solo se enmascara al personal interno que quedó
#     registrado como "proveedor_id" por un asunto de captura, no porque sea un proveedor real ---
PROVEEDOR_INTERNO_IDS = set()
proveedores_anon = []
for p in proveedores:
    nombre = p["nombre_normalizado"]
    nombre_redactado = redactar_interno(nombre)
    if nombre_redactado != nombre:
        PROVEEDOR_INTERNO_IDS.add(p["proveedor_id"])
        proveedores_anon.append({"proveedor_id": p["proveedor_id"], "nombre_normalizado": nombre_redactado, "es_persona_fisica": "TRUE"})
    else:
        proveedores_anon.append({"proveedor_id": p["proveedor_id"], "nombre_normalizado": nombre, "es_persona_fisica": "FALSE"})

write_csv("proveedores.csv", proveedores_anon, ["proveedor_id", "nombre_normalizado", "es_persona_fisica"])
write_csv("equipos.csv", equipos, list(equipos[0].keys()))
write_csv("categorias.csv", categorias, list(categorias[0].keys()))

# --- Categorías de nómina a excluir por completo ---
cat_nomina_ids = {c["categoria_id"] for c in categorias if c["grupo"] == "nomina"}

movimientos_anon = []
excluidos_nomina = 0
concepto_redactado_n = 0
for m in movimientos:
    if m["categoria_id"] in cat_nomina_ids:
        excluidos_nomina += 1
        continue
    row = dict(m)

    ben = row.get("beneficiario", "").strip()
    if ben:
        row["beneficiario"] = redactar_interno(ben)

    concepto_orig = row.get("concepto", "")
    concepto_nuevo = redactar_interno(concepto_orig)
    if concepto_nuevo != concepto_orig:
        concepto_redactado_n += 1
    row["concepto"] = concepto_nuevo

    row["medio_pago"] = redactar_interno(row.get("medio_pago", ""))

    factura = m.get("factura", "").strip().upper()
    sin_folio_valores = {"SIN FACTURA", "N/A", "S/N", "", "POR CONFIRMAR"}
    row["tiene_factura"] = "FALSE" if factura in sin_folio_valores else "TRUE"
    row.pop("factura", None)
    movimientos_anon.append(row)

fieldnames_mov = [k for k in movimientos[0].keys() if k != "factura"]
fieldnames_mov.insert(fieldnames_mov.index("medio_pago"), "tiene_factura")
write_csv("movimientos.csv", movimientos_anon, fieldnames_mov)

print(f"Proveedores marcados como personal interno (no proveedor real): {len(PROVEEDOR_INTERNO_IDS)}")
print(f"Movimientos de nómina excluidos: {excluidos_nomina}")
print(f"Filas de concepto/medio_pago con redacción de personal interno: {concepto_redactado_n}")
print(f"Movimientos publicados: {len(movimientos_anon)} (de {len(movimientos)} originales)")

with open(os.path.join(OUT, "..", "REPORTE_ANONIMIZACION.md"), "w", encoding="utf-8") as f:
    f.write("# Reporte de anonimización (revisión interna, no se publica)\n\n")
    f.write("Criterio: proveedores externos conservan su nombre real; solo se enmascara personal interno.\n\n")
    f.write("## Proveedores marcados como personal interno\n\n")
    for p in proveedores:
        if p["proveedor_id"] in PROVEEDOR_INTERNO_IDS:
            f.write(f"- id {p['proveedor_id']}: {p['nombre_normalizado']}\n")
    f.write(f"\n## Movimientos de nómina excluidos: {excluidos_nomina}\n")
    f.write(f"\n## Filas con redacción en concepto/medio_pago: {concepto_redactado_n}\n")
