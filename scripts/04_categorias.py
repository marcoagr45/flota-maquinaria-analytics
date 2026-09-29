# -*- coding: utf-8 -*-
"""
Paso 4: catálogo de categorías, aplicando las reglas ya documentadas en §9.2 y §9.4.
"""
import csv, re, unicodedata
from collections import defaultdict, Counter

def norm(s):
    s = (s or "").strip().upper()
    s = unicodedata.normalize("NFKD", s).encode("ascii","ignore").decode("ascii")
    return re.sub(r"\s+", " ", s)

# valor crudo normalizado -> (nombre_categoria_final, tipo INGRESO/EGRESO, grupo)
FOLD = {
    # 2024
    "CONSUMIBLES":("CONSUMIBLES","EGRESO","operativo"),
    "LLANTAS":("LLANTAS","EGRESO","operativo"),
    "MANGUERAS":("MANGUERAS","EGRESO","operativo"),
    "PICAS":("CONSUMIBLES","EGRESO","operativo"),               # doc: PICAS -> CONSUMIBLES
    "REFACCIONES":("REFACCIONES","EGRESO","operativo"),
    "WORKFORCE":("MANO DE OBRA","EGRESO","operativo"),
    # 2025
    "APOYO":("COMIDAS","EGRESO","operativo"),                    # doc: APOYO -> COMIDAS
    "COMIDAS":("COMIDAS","EGRESO","operativo"),
    "CONSUMIBLE":("CONSUMIBLES","EGRESO","operativo"),
    "CANASTA GRUA":("REFACCIONES","EGRESO","operativo"),
    "PINTURA MG":("REFACCIONES","EGRESO","operativo"),
    "PINTURA TECHO R4":("REFACCIONES","EGRESO","operativo"),
    "RENTA COMPRESOR":("RENTA DE EQUIPO","INGRESO","operativo"),
    "DEUDA":("DEUDA (por confirmar)","EGRESO","por_confirmar"),
    "EPP":("EPP","EGRESO","operativo"),
    "GPS":("GPS","EGRESO","operativo"),
    "HERRAMIENTA":("HERRAMIENTA","EGRESO","operativo"),
    "LICENCIAS":("LICENCIAS","EGRESO","operativo"),
    "MANO DE OBRA":("MANO DE OBRA","EGRESO","operativo"),
    "MANO OBRA":("MANO DE OBRA","EGRESO","operativo"),
    "PAPELERIA":("PAPELERIA","EGRESO","operativo"),
    "PASAJE":("PASAJE","EGRESO","operativo"),
    "PLACAS":("PLACAS","EGRESO","operativo"),
    "TRAMITES":("TRAMITES","EGRESO","operativo"),
    "TRASLADOS":("TRASLADOS","EGRESO","operativo"),
    # CANALIZACIONES se resuelve fila por fila (GASTO AJENO / PRESTAMOS A TERCEROS), no aquí
    # 2026 CATEGORÍA
    "COMBUSTIBLE":("COMBUSTIBLE","EGRESO","operativo"),
    "E.P.P.":("EPP","EGRESO","operativo"),
    "M.O. FACTURADA":("MANO DE OBRA","EGRESO","operativo"),      # supuesto: se pliega a MANO DE OBRA (por confirmar)
    "M.O. NO FACTURADA":("MANO DE OBRA","EGRESO","operativo"),   # supuesto: idem
    "REEMBOLSOS":("REEMBOLSOS (por confirmar)","EGRESO","por_confirmar"),
    "RENTA":("RENTA DE EQUIPO","INGRESO","operativo"),
    "SERVICIOS":("SERVICIOS A TERCEROS","INGRESO","operativo"),
    "OTROS":("VENTA DE ACTIVOS","INGRESO","no_operativo"),
    "SVOS INTERNO":("SERVICIO INTERNO (sin costo)","EGRESO","informativo"),
    "SUELDOS":("SUELDOS","EGRESO","nomina"),
    "BONOS":("BONOS","EGRESO","nomina"),
    "TRASLADO":("TRASLADOS","EGRESO","operativo"),
}
# categorías nuevas por la sección 0 (CANALIZACIONES dividido)
GASTO_AJENO = ("GASTO AJENO (por reclasificar)","EGRESO","por_reclasificar")
PRESTAMOS = ("PRESTAMOS A TERCEROS","EGRESO","no_operativo")

with open("movimientos_crudo.csv") as f:
    rows = list(csv.DictReader(f))

cat_final_set = {}
for key,val in FOLD.items():
    cat_final_set[val[0]] = val
cat_final_set[GASTO_AJENO[0]] = GASTO_AJENO
cat_final_set[PRESTAMOS[0]] = PRESTAMOS

# valores crudos no cubiertos por FOLD (se listan para no inventar nada silenciosamente)
crudos_no_mapeados = Counter()
for r in rows:
    anio = r["archivo_origen"]
    if anio == "2026":
        raw = norm(r.get("categoria_col") or "")
    else:
        raw = norm(r.get("tipo") or "")
    if raw == "CANALIZACIONES":
        continue  # se resuelve por fila
    if raw not in FOLD:
        crudos_no_mapeados[raw] += 1

if crudos_no_mapeados:
    print("VALORES CRUDOS SIN REGLA (revisar):")
    for k,v in crudos_no_mapeados.items():
        print(" ", repr(k), v)

# asignar categoria_id
categorias = {}
cid = 1
for name, (n, tipo, grupo) in sorted(cat_final_set.items()):
    categorias[name] = (cid, tipo, grupo)
    cid += 1

with open("categorias.csv","w",newline="",encoding="utf-8") as f:
    w = csv.writer(f)
    w.writerow(["categoria_id","nombre","tipo","grupo"])
    for name,(cid_,tipo,grupo) in categorias.items():
        w.writerow([cid_, name, tipo, grupo])

# categorias_alias: valor crudo -> categoria final, por archivo
alias_rows = []
aid = 1
seen = set()
for r in rows:
    anio = r["archivo_origen"]
    raw_orig = (r.get("categoria_col") if anio=="2026" else r.get("tipo")) or ""
    raw = norm(raw_orig)
    if raw == "CANALIZACIONES" or not raw:
        continue
    key = (raw, anio)
    if key in seen or raw not in FOLD:
        continue
    seen.add(key)
    final_name = FOLD[raw][0]
    alias_rows.append((aid, categorias[final_name][0], raw_orig.strip(), anio))
    aid += 1

with open("categorias_alias.csv","w",newline="",encoding="utf-8") as f:
    w = csv.writer(f)
    w.writerow(["alias_id","categoria_id","nombre_en_archivo","archivo_origen"])
    for row in alias_rows:
        w.writerow(row)

print("\ncategorias.csv:", len(categorias), "categorías finales")
print("categorias_alias.csv:", len(alias_rows), "filas")
