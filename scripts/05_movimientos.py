# -*- coding: utf-8 -*-
"""
Paso 5: ensamblar movimientos.csv final con equipo_id/categoria_id/proveedor_id/beneficiario,
aplicando todas las reglas de §0, §7 y §9.4 ya documentadas.
"""
import csv, re, unicodedata
from collections import defaultdict

def norm(s):
    s = (s or "").strip().upper()
    s = unicodedata.normalize("NFKD", s).encode("ascii","ignore").decode("ascii")
    return re.sub(r"\s+", " ", s)

# ---- cargar catálogos ----
equipos = {}  # clave_norm -> equipo_id
with open("equipos.csv") as f:
    for row in csv.DictReader(f):
        equipos[norm(row["clave"])] = int(row["equipo_id"])

equipo_alias = {}  # (nombre_en_archivo_norm, archivo_origen) -> equipo_id ; también un mapa laxo solo por nombre
equipo_alias_laxo = {}
with open("equipos_alias.csv") as f:
    for row in csv.DictReader(f):
        equipo_alias[(norm(row["nombre_en_archivo"]), row["archivo_origen"])] = int(row["equipo_id"])
        equipo_alias_laxo[norm(row["nombre_en_archivo"])] = int(row["equipo_id"])

proveedores = {}  # nombre_en_archivo_norm -> proveedor_id
with open("proveedores_alias.csv") as f:
    for row in csv.DictReader(f):
        proveedores[norm(row["nombre_en_archivo"])] = int(row["proveedor_id"])

categorias = {}  # nombre_final -> categoria_id
with open("categorias.csv") as f:
    for row in csv.DictReader(f):
        categorias[row["nombre"]] = int(row["categoria_id"])

CAT_FOLD = {
    "CONSUMIBLES":"CONSUMIBLES","LLANTAS":"LLANTAS","MANGUERAS":"MANGUERAS","PICAS":"CONSUMIBLES",
    "REFACCIONES":"REFACCIONES","WORKFORCE":"MANO DE OBRA","APOYO":"COMIDAS","COMIDAS":"COMIDAS",
    "CONSUMIBLE":"CONSUMIBLES","CANASTA GRUA":"REFACCIONES","PINTURA MG":"REFACCIONES",
    "PINTURA TECHO R4":"REFACCIONES","RENTA COMPRESOR":"RENTA DE EQUIPO","DEUDA":"DEUDA (por confirmar)",
    "EPP":"EPP","GPS":"GPS","HERRAMIENTA":"HERRAMIENTA","LICENCIAS":"LICENCIAS","MANO DE OBRA":"MANO DE OBRA",
    "MANO OBRA":"MANO DE OBRA","PAPELERIA":"PAPELERIA","PASAJE":"PASAJE","PLACAS":"PLACAS",
    "TRAMITES":"TRAMITES","TRASLADOS":"TRASLADOS","TRASLADO":"TRASLADOS","COMBUSTIBLE":"COMBUSTIBLE",
    "E.P.P.":"EPP","M.O. FACTURADA":"MANO DE OBRA","M.O. NO FACTURADA":"MANO DE OBRA",
    "REEMBOLSOS":"REEMBOLSOS (por confirmar)","RENTA":"RENTA DE EQUIPO","SERVICIOS":"SERVICIOS A TERCEROS",
    "OTROS":"VENTA DE ACTIVOS","SVOS INTERNO":"SERVICIO INTERNO (sin costo)","SUELDOS":"SUELDOS","BONOS":"BONOS",
}
GASTO_AJENO = "GASTO AJENO (por reclasificar)"
PRESTAMOS = "PRESTAMOS A TERCEROS"

with open("movimientos_crudo.csv") as f:
    rows = list(csv.DictReader(f))

MESES = {"ENERO":1,"FEBRERO":2,"MARZO":3,"ABRIL":4,"MAYO":5,"JUNIO":6,"JULIO":7,"AGOSTO":8,
         "SEPTIEMBRE":9,"OCTUBRE":10,"NOVIEMBRE":11,"DICIEMBRE":12}

def resolve_equipo(r):
    anio = r["archivo_origen"]
    hoja = r["hoja_origen"]
    if anio == "2026":
        nombre = r.get("equipo_col") or ""
    elif anio == "2025" and hoja in ("COMPRESOR","GRÚA "):
        nombre = r.get("equipo_col") or hoja
    elif anio == "2025" and hoja == "MISCELÁNEOS":
        emp = norm(r.get("empleado_col") or "")
        emp_clean = re.sub(r",.*$", "", emp).strip()  # "F-350, 2007" -> "F-350"
        if emp_clean in equipo_alias_laxo:
            return equipo_alias_laxo[emp_clean], None
        return equipos[norm("GENERALES")], (r.get("empleado_col") or "").strip()
    else:
        nombre = hoja
    key = (norm(nombre), anio)
    if key in equipo_alias:
        return equipo_alias[key], None
    if norm(nombre) in equipo_alias_laxo:
        return equipo_alias_laxo[norm(nombre)], None
    return None, None

def resolve_proveedor_beneficiario(r):
    prov_raw = (r.get("proveedor") or "").strip()
    if norm(prov_raw) == "MAQUINARIA":
        beneficiario = (r.get("empleado_col") or "").strip()
        return None, beneficiario if beneficiario else "POR CONFIRMAR"
    pid = proveedores.get(norm(prov_raw))
    return pid, None

def resolve_categoria(r):
    anio = r["archivo_origen"]
    raw = (r.get("categoria_col") if anio == "2026" else r.get("tipo")) or ""
    rawn = norm(raw)
    if rawn == "CANALIZACIONES":
        prov = norm(r.get("proveedor") or "")
        concepto = norm(r.get("concepto") or "")
        if prov == "MAQUINARIA" and "PRESTAMO" in concepto:
            return categorias[PRESTAMOS]
        return categorias[GASTO_AJENO]
    final = CAT_FOLD.get(rawn)
    if final is None:
        return None
    return categorias[final]

out_rows = []
sin_equipo = 0
sin_categoria = 0
mov_id = 1
for r in rows:
    equipo_id, beneficiario_equipo = resolve_equipo(r)
    proveedor_id, beneficiario_prov = resolve_proveedor_beneficiario(r)
    beneficiario = beneficiario_prov or beneficiario_equipo
    categoria_id = resolve_categoria(r)
    if equipo_id is None:
        sin_equipo += 1
    if categoria_id is None:
        sin_categoria += 1

    anio = r["archivo_origen"]
    if anio == "2026":
        fecha = r.get("fecha_completa")
        fecha = fecha.split(" ")[0] if fecha else None
    else:
        dia = r.get("dia")
        mes = MESES.get((r.get("mes") or "").strip().upper())
        anio_num = r.get("anio")
        try:
            fecha = f"{int(anio_num):04d}-{mes:02d}-{int(float(dia)):02d}" if mes and dia else None
        except Exception:
            fecha = None

    total = r.get("neto") or r.get("bruto")
    try:
        total = round(float(total), 4) if total not in (None, "") else None
    except Exception:
        total = None
    subtotal = r.get("importe") or r.get("bruto")
    try:
        subtotal = round(float(subtotal),4) if subtotal not in (None,"") else None
    except Exception:
        subtotal = None
    iva = r.get("iva")
    try:
        iva = round(float(iva),4) if iva not in (None,"") else None
    except Exception:
        iva = None

    factura_raw = (r.get("factura") or "").strip()
    if not factura_raw or norm(factura_raw) in ("S/N","N/A","SIN FACTURA"):
        factura = "SIN FACTURA" if not factura_raw else factura_raw.upper()
    else:
        factura = factura_raw

    out_rows.append({
        "movimiento_id": mov_id,
        "fecha": fecha or "POR CONFIRMAR",
        "anio_origen": anio,
        "equipo_id": equipo_id if equipo_id is not None else "",
        "categoria_id": categoria_id if categoria_id is not None else "",
        "proveedor_id": proveedor_id if proveedor_id is not None else "",
        "beneficiario": beneficiario or "",
        "concepto": (r.get("concepto") or "").strip(),
        "cantidad": r.get("cantidad") or "",
        "unidad": (r.get("unidad") or "").strip(),
        "precio_unitario": r.get("importe") or "",
        "subtotal": subtotal if subtotal is not None else "",
        "iva": iva if iva is not None else "",
        "total": total if total is not None else "",
        "factura": factura,
        "medio_pago": (r.get("medio_pago") or "POR CONFIRMAR").strip() or "POR CONFIRMAR",
        "es_reconstruido": "FALSE",
        "archivo_origen": anio,
        "hoja_origen": r["hoja_origen"],
    })
    mov_id += 1

fields = list(out_rows[0].keys())
with open("movimientos.csv","w",newline="",encoding="utf-8") as f:
    w = csv.DictWriter(f, fieldnames=fields)
    w.writeheader()
    for row in out_rows:
        w.writerow(row)

print("movimientos.csv:", len(out_rows), "filas (esperado 1738 antes de SUELDOS reconstruido)")
print("sin equipo_id resuelto:", sin_equipo)
print("sin categoria_id resuelto:", sin_categoria)

por_anio = defaultdict(lambda: [0,0.0])
for r in out_rows:
    por_anio[r["anio_origen"]][0]+=1
    try:
        por_anio[r["anio_origen"]][1]+=float(r["total"])
    except Exception:
        pass
for a,(n,t) in sorted(por_anio.items()):
    print(a, n, round(t,2))
