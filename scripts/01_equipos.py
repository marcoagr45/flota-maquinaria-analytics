# -*- coding: utf-8 -*-
"""
Paso 1: catálogo de equipos + alias, reconstruido desde cero (28/09/2026)
Sigue exactamente las decisiones ya documentadas en CONTEXTO_PROYECTO_MAQUINARIA.md §9.1
No se inventan equipos nuevos ni bajas nuevas: se transcribe lo ya confirmado por Marco.
"""
import pandas as pd

# equipo_id, clave, descripcion, tipo, es_centro_costo, activo
# Orden: activos operativos 2026 primero, luego bajas/especiales de 2024, luego agregados 21/09.
EQUIPOS = [
    (1,  "COMPRESOR",       "Compresor Ingersoll Rand XP375", "compresor",     False, True),
    (2,  "KODIAK",          "Grúa Kodiak (Hiab)",              "grua",          False, True),
    (3,  "R1",              "Retroexcavadora Case 580M",       "retroexcavadora", False, True),
    (4,  "R4",              "Retroexcavadora John Deere 310J", "retroexcavadora", False, True),
    (5,  "Z2",              "Zanjadora Vermeer RTX1250",        "zanjadora",     False, True),
    (6,  "Z3",              "Zanjadora Vermeer RTX1250",        "zanjadora",     False, True),
    (7,  "F-350",           "Camión F-350",                     "vehiculo",      False, True),
    (8,  "BRAZO ART.",      "Brazo articulado / Grúa Hiab",     "grua",          False, True),
    (9,  "ATTITUDE",        "Vehículo Attitude",                "vehiculo",      False, True),
    (10, "CH-3500",         "Chevrolet 3500",                   "vehiculo",      False, True),
    (11, "DRILL",           "Perforadora Drill",                "perforadora",   False, True),
    (12, "SAVEIRO 01",      "Saveiro 01",                       "vehiculo",      False, True),
    (13, "SAVEIRO 02",      "Saveiro 02",                       "vehiculo",      False, True),
    (14, "NISSAN 69",       "Nissan 69",                        "vehiculo",      False, True),
    (15, "NISSAN 70",       "Nissan 70",                        "vehiculo",      False, True),
    (16, "VAN HIACE",       "Van Hiace",                        "vehiculo",      False, True),
    (17, "GENERADOR",       "Generador",                        "generador",     False, True),
    (18, "MARCH 02",        "March 02",                         "vehiculo",      False, True),
    (19, "MOTOBOMBA",       "Motobomba",                        "bomba",         False, True),
    (20, "GENERALES",       "Centro de costo general (no es equipo)", "centro_costo", True, True),
    # Bajas confirmadas (existen en 2024, ya no operan, pero tienen movimientos históricos)
    (21, "Z1",              "Zanjadora Z1 (dada de baja)",      "zanjadora",     False, False),
    (22, "R2",              "Retroexcavadora R2 (dada de baja)", "retroexcavadora", False, False),
    (23, "R3",              "Retroexcavadora R3 (dada de baja)", "retroexcavadora", False, False),
    (24, "SILVERADO",       "Silverado (dada de baja)",         "vehiculo",      False, False),
    (25, "FORD 2006",       "Ford 2006 (dado de baja)",         "vehiculo",      False, False),
    (26, "FORD 2007",       "Ford 2007 (dado de baja)",         "vehiculo",      False, False),
    (27, "RIO",             "Río (dado de baja)",               "vehiculo",      False, False),
    (28, "TORNADO",         "Tornado (dado de baja)",           "vehiculo",      False, False),
    (29, "MAZDA",           "Mazda (abandonado, no operativo)", "vehiculo",      False, False),
    # Activos pero con poco/nulo movimiento en 2024 (confirmados activos por Marco 21/09)
    (30, "SANTA FE",        "Santa Fe",                          "vehiculo",      False, True),
    (31, "CAMPER CHICO",    "Camper chico",                      "vehiculo",      False, True),
    (32, "CAMPER GRANDE",   "Camper grande",                     "vehiculo",      False, True),
    (33, "HONDA VTX",       "Motocicleta Honda VTX",             "vehiculo",      False, True),
    (34, "SPORTAGE",        "Sportage",                          "vehiculo",      False, True),
    (35, "HERRAMIENTA MENOR","Herramienta menor (bolsa 2024)",   "herramienta",   False, False),
    (36, "MARCH 01",        "March 01",                          "vehiculo",      False, True),
]

equipos = pd.DataFrame(EQUIPOS, columns=["equipo_id","clave","descripcion","tipo","es_centro_costo","activo"])
equipos.to_csv("equipos.csv", index=False)
print("equipos.csv:", len(equipos), "filas")

# equipos_alias: nombre_en_archivo -> clave real, por archivo de origen
# Cubre los nombres de hoja/columna reales encontrados en los 3 Excel + los casos especiales documentados en §9.1
ALIAS = [
    # (nombre_en_archivo, clave, archivo_origen, hoja_origen)
    ("XP375","COMPRESOR","2024","XP375"), ("COMPRESOR","COMPRESOR","2025","COMPRESOR"), ("COMPRESOR","COMPRESOR","2026","REGISTRO"),
    ("GRUA HIAB","KODIAK","2024","GRUA HIAB"), ("GRUA FASSI","BRAZO ART.","2024","GRUA FASSI"), ("GRÚA ","KODIAK","2025","GRÚA "), ("KODIAK","KODIAK","2026","REGISTRO"),
    ("R1","R1","2024","R1"), ("RETRO 1","R1","2025","RETRO 1"), ("R1","R1","2026","REGISTRO"),
    ("RETRO 2","R2","2025","RETRO 2"),
    ("R4","R4","2024","R4"), ("RETRO 4","R4","2025","RETRO 4"), ("R4","R4","2026","REGISTRO"),
    ("Z2","Z2","2024","Z2"), ("Z2","Z2","2025","Z2"), ("Z2","Z2","2026","REGISTRO"),
    ("Z3","Z3","2024","Z3"), ("Z3","Z3","2025","Z3"), ("Z3","Z3","2026","REGISTRO"),
    ("F-350","F-350","2025","COMPRESOR(col EQUIPO)"), ("F-350","F-350","2026","REGISTRO"),
    ("GRÚA HIAB (col EQUIPO)","BRAZO ART.","2025","GRÚA "), ("BRAZO ART.","BRAZO ART.","2026","REGISTRO"),
    ("CAMIÓN KODIAK","KODIAK","2025","GRÚA "),
    ("ATTITUDE","ATTITUDE","2024","ATTITUDE"), ("ATTITUDE","ATTITUDE","2025","ATTITUDE"), ("ATTITUDE","ATTITUDE","2026","REGISTRO"),
    ("CHEVROLET 3500","CH-3500","2025","CHEVROLET 3500"), ("CH-3500","CH-3500","2026","REGISTRO"),
    ("DRILL","DRILL","2024","DRILL"), ("DRILL","DRILL","2026","REGISTRO"),
    ("SAVEIRO 1","SAVEIRO 01","2024","SAVEIRO 1"), ("SAVEIRO 1","SAVEIRO 01","2025","SAVEIRO 1"), ("SAVEIRO 01","SAVEIRO 01","2026","REGISTRO"),
    ("SAVEIRO 2","SAVEIRO 02","2024","SAVEIRO 2"), ("SAVEIRO 2","SAVEIRO 02","2025","SAVEIRO 2"), ("SAVEIRO 02","SAVEIRO 02","2026","REGISTRO"),
    ("NISSAN 69","NISSAN 69","2024","NISSAN 69"), ("NISSAN 69","NISSAN 69","2026","REGISTRO"),
    ("NISSAN 70","NISSAN 70","2024","NISSAN 70"), ("NISSAN 70","NISSAN 70","2026","REGISTRO"),
    ("VAN","VAN HIACE","2024","VAN"), ("VAN HIACE","VAN HIACE","2025","VAN HIACE"), ("VAN HIACE","VAN HIACE","2026","REGISTRO"),
    ("GENERADOR EVANS 5500","GENERADOR","2024","GENERADOR EVANS 5500"), ("GENERADOR VALSI 6000","GENERADOR","2024","GENERADOR VALSI 6000"),
    ("GENERADOR EVANS 8500","GENERADOR","2024","GENERADOR EVANS 8500"), ("GENERADOR","GENERADOR","2026","REGISTRO"),
    ("MARCH 2","MARCH 02","2024","MARCH 2"), ("MARCH 02","MARCH 02","2025","MARCH 02"), ("MARCH 02","MARCH 02","2026","REGISTRO"),
    ("BOMBA AGUA","MOTOBOMBA","2024","BOMBA AGUA"), ("MOTOBOMBA","MOTOBOMBA","2026","REGISTRO"),
    ("GENERALES","GENERALES","2026","REGISTRO"),
    ("Z1","Z1","2024","Z1"), ("R2","R2","2024","R2"), ("R3","R3","2024","R3"),
    ("SILVERADO","SILVERADO","2024","SILVERADO"), ("FORD 2006","FORD 2006","2024","FORD 2006"), ("FORD 2007","FORD 2007","2024","FORD 2007"),
    ("RIO","RIO","2024","RIO"), ("TORNADO","TORNADO","2024","TORNADO"), ("MAZDA","MAZDA","2024","MAZDA"),
    ("SANTA FE","SANTA FE","2024","SANTA FE"), ("CAMPER GRANDE","CAMPER GRANDE","2024","CAMPER GRANDE"),
    ("CAMPER CHICO","CAMPER CHICO","2024","CAMPER CHICO"), ("HONDA VTX","HONDA VTX","2024","HONDA VTX"),
    ("SPORTAGE","SPORTAGE","2024","SPORTAGE"), ("MARCH 1","MARCH 01","2024","MARCH 1"),
    ("MISCELÁNEOS","GENERALES","2025","MISCELÁNEOS"),
]
alias_rows = []
alias_id = 1
clave_to_id = dict(zip(equipos["clave"], equipos["equipo_id"]))
for nombre, clave, archivo, hoja in ALIAS:
    alias_rows.append((alias_id, clave_to_id[clave], nombre, archivo, hoja))
    alias_id += 1
equipos_alias = pd.DataFrame(alias_rows, columns=["alias_id","equipo_id","nombre_en_archivo","archivo_origen","hoja_origen"])
equipos_alias.to_csv("equipos_alias.csv", index=False)
print("equipos_alias.csv:", len(equipos_alias), "filas")
