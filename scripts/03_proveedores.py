# -*- coding: utf-8 -*-
"""
Paso 3: catálogo de proveedores.
Fusión automática segura (mayúsculas/acentos/espacios) igual que en el trabajo original (§9.3, paso 1).
La fusión MANUAL de 18 pares + 6 dudas del 21/09 no se puede reproducir textual (no quedó la lista
completa, solo 2 ejemplos), así que en vez de adivinar cuáles se fusionaron, se aplican solo las
reglas 100% documentadas (los 6 casos con decisión explícita + TALLER ALFONSO) y se deja una lista
de "candidatos a fusionar" (nombres muy parecidos) para que Marco los confirme en un paso corto,
en vez de inventar la fusión.
"""
import csv, re, unicodedata
from collections import defaultdict

def normalize(s):
    s = (s or "").strip().upper()
    s = unicodedata.normalize("NFKD", s).encode("ascii","ignore").decode("ascii")
    s = re.sub(r"\s+", " ", s)
    return s

with open("movimientos_crudo.csv") as f:
    rows = list(csv.DictReader(f))

# nombre_original -> (archivo_origen, veces)
raw_occurrences = defaultdict(lambda: defaultdict(int))
for r in rows:
    p = (r.get("proveedor") or "").strip()
    if not p:
        continue
    raw_occurrences[p][r["archivo_origen"]] += 1

# Fusión automática por clave normalizada
norm_to_raws = defaultdict(set)
for raw in raw_occurrences:
    norm_to_raws[normalize(raw)].add(raw)

# Reglas documentadas explícitas (§9.3 paso 3, 6 dudas resueltas + TALLER ALFONSO agregado en Paso 4)
MANUAL_MERGE = {
    "PTB": "PTB TORNIYUC",
    "PTB TORNIYUC": "PTB TORNIYUC",
    "DAWN": "BETO DAWN",
    "BETO DAWN": "BETO DAWN",
    "REYES": "REYES TEPAL",
    "REYES TEPAL": "REYES TEPAL",
    # DIAL / DALI, ANGA MAQUINARIA / MAQUINARIA, MANU / MANUEL SANTOS / JUAN MANUEL MELLADO RUIZ:
    # confirmados como NO fusionar (son proveedores/personas distintas) -> no se tocan.
}

final_name_for_norm = {}
for norm, raws in norm_to_raws.items():
    # nombre final = el más frecuente entre las variantes de esa clave normalizada
    best = max(raws, key=lambda r: sum(raw_occurrences[r].values()))
    final_name_for_norm[norm] = best

def resolve(raw):
    key = normalize(raw)
    base = final_name_for_norm[key]
    return MANUAL_MERGE.get(normalize(base), base)

proveedores = {}
alias_rows = []
prov_id = 1
alias_id = 1
prov_id_for_name = {}
for raw in raw_occurrences:
    final = resolve(raw)
    fkey = normalize(final)
    if fkey not in prov_id_for_name:
        prov_id_for_name[fkey] = prov_id
        proveedores[prov_id] = final
        prov_id += 1
    pid = prov_id_for_name[fkey]
    for archivo, veces in raw_occurrences[raw].items():
        alias_rows.append((alias_id, pid, raw, archivo, veces))
        alias_id += 1

# TALLER ALFONSO: confirmar que quedó cargado (aparece en hoja GRÚA de 2025 con encabezado en fila 2)
nombres_norm = {normalize(v) for v in proveedores.values()}
print("TALLER ALFONSO en catálogo:", "TALLER ALFONSO" in nombres_norm)

with open("proveedores.csv","w",newline="",encoding="utf-8") as f:
    w = csv.writer(f)
    w.writerow(["proveedor_id","nombre_normalizado"])
    for pid, name in sorted(proveedores.items()):
        w.writerow([pid, name])

with open("proveedores_alias.csv","w",newline="",encoding="utf-8") as f:
    w = csv.writer(f)
    w.writerow(["alias_id","proveedor_id","nombre_en_archivo","archivo_origen","veces"])
    for row in alias_rows:
        w.writerow(row)

print("proveedores.csv:", len(proveedores), "proveedores finales")
print("proveedores_alias.csv:", len(alias_rows), "filas")

# ---- candidatos a fusionar manualmente (nombres parecidos que la fusión automática NO unió) ----
def sim_key(name):
    # clave más agresiva: solo letras, sin espacios, para detectar candidatos
    return re.sub(r"[^A-Z0-9]", "", normalize(name))

buckets = defaultdict(list)
for pid, name in proveedores.items():
    buckets[sim_key(name)[:6]].append((pid, name))  # agrupa por prefijo de 6 chars, solo para acotar candidatos

candidatos = []
import difflib
names = list(proveedores.items())
for i in range(len(names)):
    for j in range(i+1, len(names)):
        a, b = names[i][1], names[j][1]
        if abs(len(a)-len(b)) > 6:
            continue
        ratio = difflib.SequenceMatcher(None, normalize(a), normalize(b)).ratio()
        if ratio > 0.82:
            candidatos.append((names[i][0], a, names[j][0], b, round(ratio,2)))

print(f"\nCandidatos a revisar (posibles duplicados no fusionados): {len(candidatos)}")
with open("proveedores_candidatos_revisar.csv","w",newline="",encoding="utf-8") as f:
    w = csv.writer(f)
    w.writerow(["proveedor_id_a","nombre_a","proveedor_id_b","nombre_b","similitud"])
    for c in candidatos:
        w.writerow(c)
        print(" ", c)
