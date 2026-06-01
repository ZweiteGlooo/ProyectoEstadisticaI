import base64
import csv
import io
import math
import re
import statistics
import zlib
from collections import Counter


# ============================================================
# Archivo ejecutable independiente
# ============================================================
# Este archivo funciona sin leer ni escribir carpetas como data/, src/ o resultados/.
# Los datos de la encuesta están incorporados dentro del mismo archivo
# en una cadena comprimida para que el profesor pueda ejecutar solo Main_2.py.
#
# Para ejecutarlo:
# python Main_2.py


TITULO_PROYECTO = "Uso de inteligencia artificial generativa en actividades académicas"
POBLACION_OBJETIVO = "Estudiantes encuestados sobre el uso de IA generativa en actividades académicas"
TAMANO_POBLACION = 100
LIMITE_RESPUESTAS_ANALISIS = 100
NIVEL_CONFIANZA = 0.95
VALOR_Z = 1.96
MARGEN_ERROR = 0.05
PROPORCION_ESPERADA = 0.5


# Datos originales del formulario comprimidos dentro del archivo.
# El programa usa estos datos sin pedir un archivo CSV externo.
DATOS_CSV_COMPRIMIDOS = (
    "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"
    "I2x+iIG2v6YPaLe9dZjbHzUF9/+7zs1F"
)


def limpiar_texto(texto):
    # Limpia saltos de línea y espacios repetidos de preguntas y respuestas.
    return re.sub(r"\s+", " ", str(texto).replace("\r", " ").replace("\n", " ")).strip()


def limpiar_nombre_archivo(texto):
    # Convierte el nombre largo de una variable en un nombre válido para guardar archivos.
    texto = limpiar_texto(texto)
    texto = re.sub(r"[^A-Za-z0-9áéíóúÁÉÍÓÚñÑ]+", "_", texto)
    return texto.strip("_")[:80]


def convertir_numero(valor):
    # Convierte un dato a número cuando es posible.
    # Si el dato está vacío o no es numérico, devuelve None.
    try:
        if limpiar_texto(valor) == "":
            return None
        return float(str(valor).replace(",", "."))
    except ValueError:
        return None


def texto_respuestas(cantidad):
    # Mejora la redacción de la salida en singular o plural.
    return f"{cantidad} respuesta" if cantidad == 1 else f"{cantidad} respuestas"


def leer_datos_embebidos():
    # Prepara los datos incorporados en el archivo y los lee como CSV.
    datos_bytes = zlib.decompress(base64.b64decode(DATOS_CSV_COMPRIMIDOS))
    texto_csv = datos_bytes.decode("utf-8")
    lector = csv.DictReader(io.StringIO(texto_csv))
    filas = []

    for fila in lector:
        fila_limpia = {}
        for columna, valor in fila.items():
            fila_limpia[limpiar_texto(columna)] = limpiar_texto(valor)
        filas.append(fila_limpia)

    return filas


def buscar_columna(columnas, palabras_clave):
    # Busca una columna usando palabras clave.
    # Esto evita escribir preguntas largas exactamente igual en muchas partes del código.
    for columna in columnas:
        texto = columna.lower()
        if all(palabra.lower() in texto for palabra in palabras_clave):
            return columna
    return None


def limpiar_y_preparar_datos(filas):
    # Elimina la marca temporal porque no aporta al análisis estadístico.
    # También convierte la escala de dependencia en variable cualitativa ordinal.
    if not filas:
        return []

    columnas = list(filas[0].keys())
    columna_dependencia = buscar_columna(columnas, ["dependencia"])
    columnas_a_eliminar = {"marca temporal", "timestamp", "id"}
    filas_limpias = []

    for fila in filas:
        nueva_fila = {}
        for columna, valor in fila.items():
            if columna.lower() in columnas_a_eliminar:
                continue

            if columna == columna_dependencia:
                numero = convertir_numero(valor)
                nueva_fila[columna] = f"Nivel {int(numero)}" if numero is not None else ""
            else:
                nueva_fila[columna] = valor

        filas_limpias.append(nueva_fila)

    return filas_limpias


def limitar_respuestas(filas):
    # El proyecto trabaja con 100 personas.
    # Si existen más de 100 respuestas, se conservan las primeras 100
    # y se excluyen las respuestas restantes del final.
    total_original = len(filas)
    filas_analizadas = filas[:LIMITE_RESPUESTAS_ANALISIS]
    total_excluido = max(total_original - len(filas_analizadas), 0)
    return filas_analizadas, total_original, total_excluido


def calcular_tamano_muestra(poblacion_finita):
    # Fórmula para población finita:
    # n = (N * Z^2 * p * q) / (e^2 * (N - 1) + Z^2 * p * q)
    q = 1 - PROPORCION_ESPERADA
    numerador = poblacion_finita * (VALOR_Z**2) * PROPORCION_ESPERADA * q
    denominador = (MARGEN_ERROR**2) * (poblacion_finita - 1) + (VALOR_Z**2) * PROPORCION_ESPERADA * q
    return math.ceil(numerador / denominador)


def obtener_columnas_cuantitativas(filas):
    # Una columna se considera cuantitativa si todos sus valores válidos son numéricos.
    # La dependencia ya fue convertida a "Nivel X", por eso queda como cualitativa.
    columnas = list(filas[0].keys())
    cuantitativas = []

    for columna in columnas:
        valores_validos = [fila[columna] for fila in filas if fila.get(columna, "") != ""]
        numeros = [convertir_numero(valor) for valor in valores_validos]
        if valores_validos and all(numero is not None for numero in numeros):
            cuantitativas.append(columna)

    return cuantitativas


def obtener_valores_numericos(filas, columna):
    # Extrae una columna como lista de números.
    return [convertir_numero(fila[columna]) for fila in filas if convertir_numero(fila[columna]) is not None]


def obtener_valores_texto(filas, columna):
    # Extrae una columna como lista de categorías no vacías.
    return [fila[columna] for fila in filas if fila.get(columna, "") != ""]


def calcular_cuartil(datos, proporcion):
    # Calcula cuartiles usando interpolación lineal.
    datos_ordenados = sorted(datos)
    posicion = (len(datos_ordenados) - 1) * proporcion
    inferior = math.floor(posicion)
    superior = math.ceil(posicion)

    if inferior == superior:
        return datos_ordenados[inferior]

    peso = posicion - inferior
    return datos_ordenados[inferior] * (1 - peso) + datos_ordenados[superior] * peso


def calcular_asimetria(datos, media, desviacion):
    # Calcula una medida descriptiva de asimetría.
    if len(datos) < 3 or desviacion == 0:
        return 0
    n = len(datos)
    return sum(((x - media) / desviacion) ** 3 for x in datos) / n


def calcular_curtosis(datos, media, desviacion):
    # Calcula curtosis en exceso para describir la forma de la distribución.
    if len(datos) < 4 or desviacion == 0:
        return 0
    n = len(datos)
    return sum(((x - media) / desviacion) ** 4 for x in datos) / n - 3


def interpretar_cv(cv):
    # Clasifica el coeficiente de variación para dar una interpretación clara.
    if cv < 10:
        return "Baja dispersión"
    if cv < 30:
        return "Dispersión moderada"
    return "Alta dispersión"


def analizar_cuantitativas(filas):
    # Calcula medidas descriptivas para variables numéricas.
    columnas_cuantitativas = obtener_columnas_cuantitativas(filas)
    resultados = []

    print("\n2. Resultados: variables cuantitativas")

    for variable in columnas_cuantitativas:
        datos = obtener_valores_numericos(filas, variable)
        if not datos:
            continue

        media = statistics.mean(datos)
        mediana = statistics.median(datos)
        moda = statistics.multimode(datos)
        varianza = statistics.variance(datos) if len(datos) > 1 else 0
        desviacion = statistics.stdev(datos) if len(datos) > 1 else 0
        cv = (desviacion / media) * 100 if media != 0 else 0
        minimo = min(datos)
        maximo = max(datos)
        rango = maximo - minimo
        p10 = calcular_cuartil(datos, 0.10)
        q1 = calcular_cuartil(datos, 0.25)
        q3 = calcular_cuartil(datos, 0.75)
        p90 = calcular_cuartil(datos, 0.90)
        rango_intercuartilico = q3 - q1
        asimetria = calcular_asimetria(datos, media, desviacion)
        curtosis = calcular_curtosis(datos, media, desviacion)
        interpretacion = f"La media es {media:.2f}, la mediana es {mediana:.2f} y la variabilidad se clasifica como {interpretar_cv(cv).lower()}."

        resultados.append(
            {
                "Variable": variable,
                "n válido": len(datos),
                "Media": round(media, 4),
                "Mediana": round(mediana, 4),
                "Moda": ", ".join(f"{valor:.4f}" for valor in moda),
                "Mínimo": round(minimo, 4),
                "Rango": round(rango, 4),
                "Percentil 10": round(p10, 4),
                "Q1": round(q1, 4),
                "P50 o mediana": round(mediana, 4),
                "Q3": round(q3, 4),
                "Percentil 90": round(p90, 4),
                "Rango intercuartílico": round(rango_intercuartilico, 4),
                "Máximo": round(maximo, 4),
                "Varianza muestral": round(varianza, 4),
                "Desviación estándar": round(desviacion, 4),
                "Coeficiente de variación (%)": round(cv, 4),
                "Asimetría": round(asimetria, 4),
                "Curtosis": round(curtosis, 4),
                "Interpretación": interpretacion,
            }
        )

        print(f"\n[{variable}]")
        print(f"  n válido: {len(datos)}")
        print(f"  Media: {media:.2f}")
        print(f"  Mediana: {mediana:.2f}")
        print(f"  Moda: {', '.join(f'{valor:.2f}' for valor in moda)}")
        print(f"  Rango: {rango:.2f}")
        print(f"  Q1: {q1:.2f} | Q3: {q3:.2f} | Rango intercuartílico: {rango_intercuartilico:.2f}")
        print(f"  Percentil 10: {p10:.2f} | Percentil 90: {p90:.2f}")
        print(f"  Desviación estándar: {desviacion:.2f}")
        print(f"  Coeficiente de variación: {cv:.2f}%")
        print(f"  Interpretación: {interpretacion}")

    return resultados


def analizar_cualitativas(filas):
    # Calcula frecuencias absolutas y porcentajes para variables cualitativas.
    columnas_cuantitativas = set(obtener_columnas_cuantitativas(filas))
    columnas_cualitativas = [columna for columna in filas[0].keys() if columna not in columnas_cuantitativas]
    resultados = []

    print("\n3. Resultados: variables cualitativas")

    for variable in columnas_cualitativas:
        datos = obtener_valores_texto(filas, variable)
        if not datos:
            continue

        frecuencias = dict(Counter(datos).most_common())
        moda = next(iter(frecuencias))

        print(f"\n[{variable}]")
        print(f"  n válido: {len(datos)}")
        print(f"  Categoría más frecuente: {moda} ({texto_respuestas(frecuencias[moda])})")
        print("  Tabla de frecuencias:")

        for categoria, frecuencia in frecuencias.items():
            porcentaje = frecuencia / len(datos) * 100
            resultados.append(
                {
                    "Variable": variable,
                    "Categoría": categoria,
                    "Frecuencia absoluta": frecuencia,
                    "Frecuencia relativa": round(frecuencia / len(datos), 4),
                    "Porcentaje": round(porcentaje, 2),
                }
            )
            print(f"    {categoria}: {texto_respuestas(frecuencia)} ({porcentaje:.2f}%)")

    return resultados


def calcular_probabilidades(filas):
    # Calcula probabilidades descriptivas de eventos importantes de la encuesta.
    columnas = list(filas[0].keys())
    col_trabajos = buscar_columna(columnas, ["10", "trabajos"])
    col_dependencia = buscar_columna(columnas, ["dependencia"])
    col_verifica = buscar_columna(columnas, ["verificar"])
    col_ia = buscar_columna(columnas, ["ia", "regularidad"])
    col_accion = buscar_columna(columnas, ["acción", "principal"])
    col_promedio = buscar_columna(columnas, ["promedio"])
    resultados = []

    print("\n2. Resultados: probabilidades descriptivas de la encuesta")

    if col_trabajos:
        datos = obtener_valores_numericos(filas, col_trabajos)
        favorables = sum(1 for valor in datos if valor >= 7)
        resultados.append(crear_evento("Usar IA generativa en 7 o más de cada 10 trabajos académicos", favorables, len(datos)))

    if col_dependencia:
        datos = []
        for fila in filas:
            coincidencia = re.search(r"\d+", fila.get(col_dependencia, ""))
            if coincidencia:
                datos.append(int(coincidencia.group()))
        favorables = sum(1 for valor in datos if valor >= 8)
        resultados.append(crear_evento("Calificar la dependencia de IA como alta (8 a 10)", favorables, len(datos)))

    if col_verifica:
        datos = obtener_valores_texto(filas, col_verifica)
        favorables = sum(1 for valor in datos if valor.lower() in {"siempre", "casi siempre"})
        resultados.append(crear_evento("Verificar información de la IA en fuentes externas", favorables, len(datos)))

    if col_ia:
        datos = obtener_valores_texto(filas, col_ia)
        ia_principal = Counter(datos).most_common(1)[0][0]
        favorables = sum(1 for valor in datos if valor == ia_principal)
        resultados.append(crear_evento(f"Usar principalmente {ia_principal}", favorables, len(datos)))

    if col_trabajos:
        generar_distribucion_discreta(filas, col_trabajos)

    if col_accion and col_verifica and col_promedio:
        generar_probabilidad_condicional(filas, col_accion, col_verifica, col_promedio)

    generar_probabilidades_adicionales(filas)
    generar_temas_adicionales_curso(filas)

    for fila in resultados:
        print(f"  P({fila['Evento']}) = {fila['Probabilidad']:.4f} ({fila['Porcentaje']:.2f}%, {fila['Casos favorables']}/{fila['Total válido']})")

    return resultados


def generar_distribucion_discreta(filas, columna):
    # Distribución discreta: valores posibles, frecuencias y probabilidades.
    datos = obtener_valores_numericos(filas, columna)
    conteos = dict(sorted(Counter(datos).items()))
    total = sum(conteos.values())
    acumulada = 0
    resultados = []

    print("\n2.1 Distribución de probabilidad discreta")
    print(f"Variable discreta usada: {columna}")

    for valor, frecuencia in conteos.items():
        acumulada += frecuencia
        probabilidad = frecuencia / total
        probabilidad_acumulada = acumulada / total
        resultados.append(
            {
                "xi": valor,
                "Frecuencia absoluta": frecuencia,
                "Probabilidad fi": round(probabilidad, 4),
                "Frecuencia acumulada": acumulada,
                "Probabilidad acumulada Fi": round(probabilidad_acumulada, 4),
            }
        )
        print(f"  x={valor:g}: P(X=x)={probabilidad:.4f}, F(x)={probabilidad_acumulada:.4f}")

    return resultados


def generar_probabilidad_condicional(filas, col_accion, col_verifica, col_promedio):
    # Probabilidad condicional:
    # P(A|B) = P(A y B) / P(B)
    # A: tener promedio menor o igual a 3.8.
    # B1: copiar y pegar directamente.
    # B2: nunca verificar fuentes.
    promedio_bajo = []
    copia_pega = []
    nunca_verifica = []

    for fila in filas:
        promedio = convertir_numero(fila.get(col_promedio, ""))
        accion = fila.get(col_accion, "").lower()
        verifica = fila.get(col_verifica, "").lower()

        promedio_bajo.append(promedio is not None and promedio <= 3.8)
        copia_pega.append("copiar y pegar directamente" in accion)
        nunca_verifica.append(verifica == "nunca")

    interseccion_copia = [a and b for a, b in zip(promedio_bajo, copia_pega)]
    interseccion_nunca = [a and b for a, b in zip(promedio_bajo, nunca_verifica)]
    total_copia = sum(copia_pega)
    total_nunca = sum(nunca_verifica)
    prob_bajo_dado_copia = sum(interseccion_copia) / total_copia if total_copia else 0
    prob_bajo_dado_nunca = sum(interseccion_nunca) / total_nunca if total_nunca else 0

    resultados = [
        {
            "Probabilidad condicional": "P(promedio <= 3.8 | copia y pega directamente)",
            "Casos intersección": sum(interseccion_copia),
            "Casos condición": total_copia,
            "Resultado": round(prob_bajo_dado_copia, 4),
            "Porcentaje": round(prob_bajo_dado_copia * 100, 2),
        },
        {
            "Probabilidad condicional": "P(promedio <= 3.8 | nunca verifica fuentes)",
            "Casos intersección": sum(interseccion_nunca),
            "Casos condición": total_nunca,
            "Resultado": round(prob_bajo_dado_nunca, 4),
            "Porcentaje": round(prob_bajo_dado_nunca * 100, 2),
        },
    ]

    print("\n2.2 Probabilidad condicional")
    for fila in resultados:
        print(f"  {fila['Probabilidad condicional']} = {fila['Resultado']:.4f} ({fila['Porcentaje']:.2f}%)")

    return resultados


def generar_probabilidades_adicionales(filas):
    # Probabilidades complementarias, conjuntas, condicionales inversas,
    # binomial y riesgo por programa académico.
    columnas = list(filas[0].keys())
    col_accion = buscar_columna(columnas, ["acción", "principal"])
    col_verifica = buscar_columna(columnas, ["verificar"])
    col_trabajos = buscar_columna(columnas, ["10", "trabajos"])
    col_dependencia = buscar_columna(columnas, ["dependencia"])
    col_promedio = buscar_columna(columnas, ["promedio"])
    col_programa = buscar_columna(columnas, ["programa"])
    total = len(filas)

    if not (col_accion and col_verifica and col_trabajos and col_dependencia and col_promedio) or total == 0:
        print("\n2.4 Probabilidades adicionales")
        print("No se encontraron todas las variables necesarias para este cálculo.")
        return []

    copia_pega = []
    nunca_verifica = []
    uso_severo = []
    dependencia_alta = []
    promedio_bajo = []
    programas = []

    for fila in filas:
        accion = fila.get(col_accion, "").lower()
        verifica = fila.get(col_verifica, "").lower()
        trabajos = convertir_numero(fila.get(col_trabajos, ""))
        promedio = convertir_numero(fila.get(col_promedio, ""))
        coincidencia = re.search(r"\d+", fila.get(col_dependencia, ""))
        dependencia = int(coincidencia.group()) if coincidencia else None

        copia_pega.append("copiar y pegar directamente" in accion)
        nunca_verifica.append(verifica == "nunca")
        uso_severo.append(trabajos is not None and trabajos >= 7)
        dependencia_alta.append(dependencia is not None and dependencia >= 8)
        promedio_bajo.append(promedio is not None and promedio <= 3.8)
        programas.append(fila.get(col_programa, "") if col_programa else "")

    uso_riesgoso = [a or b or c for a, b, c in zip(copia_pega, nunca_verifica, uso_severo)]
    p_riesgo = sum(uso_riesgoso) / total
    p_no_riesgo = 1 - p_riesgo
    conjunta_copia_bajo = sum(a and b for a, b in zip(copia_pega, promedio_bajo)) / total
    conjunta_nunca_bajo = sum(a and b for a, b in zip(nunca_verifica, promedio_bajo)) / total
    conjunta_uso_dep = sum(a and b for a, b in zip(uso_severo, dependencia_alta)) / total
    total_bajo = sum(promedio_bajo)
    p_copia_dado_bajo = sum(a and b for a, b in zip(copia_pega, promedio_bajo)) / total_bajo if total_bajo else 0
    p_nunca_dado_bajo = sum(a and b for a, b in zip(nunca_verifica, promedio_bajo)) / total_bajo if total_bajo else 0

    n_binomial = 5
    p_exactamente_3 = math.comb(n_binomial, 3) * (p_riesgo**3) * ((1 - p_riesgo) ** (n_binomial - 3))
    p_al_menos_3 = sum(
        math.comb(n_binomial, k) * (p_riesgo**k) * ((1 - p_riesgo) ** (n_binomial - k))
        for k in range(3, n_binomial + 1)
    )

    resultados = [
        ("P(uso riesgoso)", p_riesgo),
        ("P(no uso riesgoso)", p_no_riesgo),
        ("P(copia y pega y promedio <= 3.8)", conjunta_copia_bajo),
        ("P(nunca verifica y promedio <= 3.8)", conjunta_nunca_bajo),
        ("P(uso en 7+ trabajos y dependencia alta)", conjunta_uso_dep),
        ("P(copia y pega | promedio <= 3.8)", p_copia_dado_bajo),
        ("P(nunca verifica | promedio <= 3.8)", p_nunca_dado_bajo),
        ("P(exactamente 3 de 5 con uso riesgoso)", p_exactamente_3),
        ("P(al menos 3 de 5 con uso riesgoso)", p_al_menos_3),
    ]

    print("\n2.4 Probabilidades adicionales")
    for nombre, probabilidad in resultados:
        print(f"  {nombre} = {probabilidad:.4f} ({probabilidad * 100:.2f}%)")

    if col_programa:
        grupos = {}
        for programa, riesgo in zip(programas, uso_riesgoso):
            if programa not in grupos:
                grupos[programa] = {"total": 0, "riesgo": 0}
            grupos[programa]["total"] += 1
            grupos[programa]["riesgo"] += int(riesgo)

        resumen = []
        for programa, valores in grupos.items():
            probabilidad = valores["riesgo"] / valores["total"]
            resumen.append((programa, valores["riesgo"], valores["total"], probabilidad))
        resumen.sort(key=lambda fila: fila[3], reverse=True)

        print("\n2.5 Probabilidad de uso riesgoso por programa")
        for programa, riesgo, total_programa, probabilidad in resumen:
            print(f"  P(uso riesgoso | {programa}) = {probabilidad:.4f} ({probabilidad * 100:.2f}%, {riesgo}/{total_programa})")

    return resultados


def generar_temas_adicionales_curso(filas):
    # Esta sección integra técnicas de conteo, Bayes y distribuciones discretas modelo.
    columnas = list(filas[0].keys())
    col_accion = buscar_columna(columnas, ["acción", "principal"])
    col_verifica = buscar_columna(columnas, ["verificar"])
    col_trabajos = buscar_columna(columnas, ["10", "trabajos"])
    col_dependencia = buscar_columna(columnas, ["dependencia"])
    col_promedio = buscar_columna(columnas, ["promedio"])
    col_programa = buscar_columna(columnas, ["programa"])
    col_ia = buscar_columna(columnas, ["ia", "regularidad"])
    total = len(filas)

    print("\n2.6 Temas adicionales del curso")

    if col_programa and col_ia:
        programas = sorted(set(obtener_valores_texto(filas, col_programa)))
        herramientas = sorted(set(obtener_valores_texto(filas, col_ia)))
        cantidad_ia = len(herramientas)
        combinaciones_ia = math.comb(cantidad_ia, 3) if cantidad_ia >= 3 else 0
        permutaciones_ia = math.perm(cantidad_ia, 3) if cantidad_ia >= 3 else 0
        regla_producto = len(programas) * cantidad_ia

        print("\nTécnicas de conteo")
        print(f"  Regla del producto: {len(programas)} programas x {cantidad_ia} IAs = {regla_producto} perfiles posibles.")
        print(f"  Combinaciones: C({cantidad_ia}, 3) = {combinaciones_ia} formas de escoger 3 IAs sin orden.")
        print(f"  Permutaciones: P({cantidad_ia}, 3) = {permutaciones_ia} formas de ordenar 3 IAs.")

    if col_accion and col_verifica and col_trabajos and col_dependencia and col_promedio and total:
        copia_pega = []
        nunca_verifica = []
        uso_severo = []
        dependencia_alta = []
        promedio_bajo = []

        for fila in filas:
            accion = fila.get(col_accion, "").lower()
            verifica = fila.get(col_verifica, "").lower()
            trabajos = convertir_numero(fila.get(col_trabajos, ""))
            promedio = convertir_numero(fila.get(col_promedio, ""))
            coincidencia = re.search(r"\d+", fila.get(col_dependencia, ""))
            dependencia = int(coincidencia.group()) if coincidencia else None

            copia_pega.append("copiar y pegar directamente" in accion)
            nunca_verifica.append(verifica == "nunca")
            uso_severo.append(trabajos is not None and trabajos >= 7)
            dependencia_alta.append(dependencia is not None and dependencia >= 8)
            promedio_bajo.append(promedio is not None and promedio <= 3.8)

        uso_riesgoso = [a or b or c for a, b, c in zip(copia_pega, nunca_verifica, uso_severo)]
        total_bajo = sum(promedio_bajo)
        total_copia = sum(copia_pega)
        total_nunca = sum(nunca_verifica)
        p_bajo = total_bajo / total
        p_copia = total_copia / total
        p_nunca = total_nunca / total
        p_bajo_dado_copia = sum(a and b for a, b in zip(promedio_bajo, copia_pega)) / total_copia if total_copia else 0
        p_bajo_dado_nunca = sum(a and b for a, b in zip(promedio_bajo, nunca_verifica)) / total_nunca if total_nunca else 0
        p_copia_dado_bajo_bayes = (p_bajo_dado_copia * p_copia / p_bajo) if p_bajo else 0
        p_nunca_dado_bajo_bayes = (p_bajo_dado_nunca * p_nunca / p_bajo) if p_bajo else 0

        print("\nTeorema de Bayes")
        print(f"  P(copia y pega | promedio <= 3.8) = {p_copia_dado_bajo_bayes:.4f} ({p_copia_dado_bajo_bayes * 100:.2f}%)")
        print(f"  P(nunca verifica | promedio <= 3.8) = {p_nunca_dado_bajo_bayes:.4f} ({p_nunca_dado_bajo_bayes * 100:.2f}%)")

        p_riesgo = sum(uso_riesgoso) / total
        n_grupo = 5
        casos_riesgo = sum(uso_riesgoso)
        p_hipergeometrica = (
            math.comb(casos_riesgo, 3) * math.comb(total - casos_riesgo, n_grupo - 3) / math.comb(total, n_grupo)
            if total >= n_grupo and casos_riesgo >= 3 and total - casos_riesgo >= n_grupo - 3
            else 0
        )
        lambda_poisson = n_grupo * p_riesgo
        p_poisson_3 = math.exp(-lambda_poisson) * (lambda_poisson**3) / math.factorial(3)

        print("\nDistribuciones discretas modelo")
        print(f"  Hipergeométrica: P(exactamente 3 riesgosos en una muestra de 5 sin reemplazo) = {p_hipergeometrica:.4f} ({p_hipergeometrica * 100:.2f}%)")
        print(f"  Poisson: con lambda={lambda_poisson:.2f}, P(X=3) = {p_poisson_3:.4f} ({p_poisson_3 * 100:.2f}%)")

        total_dep_alta = sum(dependencia_alta)
        p_riesgo_dado_dep_alta = sum(a and b for a, b in zip(uso_riesgoso, dependencia_alta)) / total_dep_alta if total_dep_alta else 0
        print("\nProbabilidad condicional adicional")
        print(f"  P(uso riesgoso | dependencia alta) = {p_riesgo_dado_dep_alta:.4f} ({p_riesgo_dado_dep_alta * 100:.2f}%)")


def analizar_uso_riesgoso(filas):
    # Un estudiante queda en uso riesgoso si cumple al menos una condición crítica.
    columnas = list(filas[0].keys())
    col_accion = buscar_columna(columnas, ["acción", "principal"])
    col_verifica = buscar_columna(columnas, ["verificar"])
    col_trabajos = buscar_columna(columnas, ["10", "trabajos"])
    total = len(filas)

    if not (col_accion and col_verifica and col_trabajos) or total == 0:
        print("\nUso riesgoso")
        print("No se encontraron todas las variables necesarias para este cálculo.")
        return []

    total_copiar = 0
    total_no_verifica = 0
    total_uso_severo = 0
    total_riesgoso = 0

    for fila in filas:
        accion = fila.get(col_accion, "").lower()
        verifica = fila.get(col_verifica, "").lower()
        trabajos = convertir_numero(fila.get(col_trabajos, ""))

        condicion_copiar = "copiar y pegar directamente" in accion
        condicion_no_verifica = verifica == "nunca"
        condicion_uso_severo = trabajos is not None and trabajos >= 7
        condicion_riesgosa = condicion_copiar or condicion_no_verifica or condicion_uso_severo

        total_copiar += int(condicion_copiar)
        total_no_verifica += int(condicion_no_verifica)
        total_uso_severo += int(condicion_uso_severo)
        total_riesgoso += int(condicion_riesgosa)

    indicadores = [
        ("Copiar y pegar directamente", total_copiar),
        ("Nunca verifica fuentes", total_no_verifica),
        ("Usa IA en 7 o más de cada 10 trabajos", total_uso_severo),
        ("Uso riesgoso (al menos una condición)", total_riesgoso),
    ]

    print("\nUso riesgoso")
    resultados = []
    for nombre, casos in indicadores:
        porcentaje = casos / total * 100
        resultados.append({"Indicador": nombre, "Casos": casos, "Porcentaje": round(porcentaje, 2)})
        print(f"  {nombre}: {casos}/{total} ({porcentaje:.2f}%)")

    return resultados


def analizar_ia_y_dependencia(filas):
    # Relaciona la IA usada con la dependencia reportada por los estudiantes.
    columnas = list(filas[0].keys())
    col_ia = buscar_columna(columnas, ["ia", "regularidad"])
    col_dependencia = buscar_columna(columnas, ["dependencia"])

    if not (col_ia and col_dependencia):
        print("\nIA utilizada y dependencia")
        print("No se encontraron todas las variables necesarias para este cálculo.")
        return []

    grupos = {}
    for fila in filas:
        ia = fila.get(col_ia, "")
        coincidencia = re.search(r"\d+", fila.get(col_dependencia, ""))
        if not ia or not coincidencia:
            continue

        dependencia = int(coincidencia.group())
        if ia not in grupos:
            grupos[ia] = []
        grupos[ia].append(dependencia)

    resumen = []
    for ia, valores in grupos.items():
        dependencia_promedio = statistics.mean(valores)
        dependencia_alta = sum(1 for valor in valores if valor >= 8) / len(valores) * 100
        resumen.append(
            {
                "IA": ia,
                "Estudiantes": len(valores),
                "Dependencia promedio": round(dependencia_promedio, 2),
                "Dependencia alta": round(dependencia_alta, 2),
            }
        )

    resumen.sort(key=lambda fila: (fila["Dependencia promedio"], fila["Dependencia alta"]), reverse=True)

    print("\nIA utilizada y dependencia")
    for fila in resumen:
        print(
            f"  {fila['IA']}: dependencia promedio {fila['Dependencia promedio']:.2f}, "
            f"dependencia alta {fila['Dependencia alta']:.2f}% "
            f"({fila['Estudiantes']} estudiantes)"
        )

    if resumen:
        fila_mayor = resumen[0]
        print(
            f"\nLa IA que más se conecta con mayor dependencia promedio es {fila_mayor['IA']} "
            f"({fila_mayor['Dependencia promedio']:.2f})."
        )

    return resumen


def obtener_indice_riesgo(filas):
    # Devuelve una lista con puntaje 0 a 3 por estudiante.
    columnas = list(filas[0].keys())
    col_accion = buscar_columna(columnas, ["acción", "principal"])
    col_verifica = buscar_columna(columnas, ["verificar"])
    col_trabajos = buscar_columna(columnas, ["10", "trabajos"])

    if not (col_accion and col_verifica and col_trabajos):
        return None

    indices = []
    for fila in filas:
        accion = fila.get(col_accion, "").lower()
        verifica = fila.get(col_verifica, "").lower()
        trabajos = convertir_numero(fila.get(col_trabajos, ""))

        condicion_copiar = "copiar y pegar directamente" in accion
        condicion_no_verifica = verifica == "nunca"
        condicion_uso_severo = trabajos is not None and trabajos >= 7
        indices.append(int(condicion_copiar) + int(condicion_no_verifica) + int(condicion_uso_severo))

    return indices


def analizar_indice_riesgo(filas):
    # Índice de riesgo: 0 a 3 según cuántas condiciones críticas cumple el estudiante.
    indices = obtener_indice_riesgo(filas)
    total = len(filas)

    if indices is None or total == 0:
        print("\nÍndice de riesgo")
        print("No se encontraron todas las variables necesarias para este cálculo.")
        return []

    conteos = Counter(indices)
    etiquetas = {
        0: "0 condiciones",
        1: "1 condición",
        2: "2 condiciones",
        3: "3 condiciones",
    }
    resultados = []

    print("\nÍndice de riesgo")
    for nivel in range(4):
        casos = conteos.get(nivel, 0)
        porcentaje = casos / total * 100
        resultados.append({"Nivel": etiquetas[nivel], "Casos": casos, "Porcentaje": round(porcentaje, 2)})
        print(f"  {etiquetas[nivel]}: {casos}/{total} ({porcentaje:.2f}%)")

    return resultados


def analizar_riesgo_por_programa(filas):
    # Compara el porcentaje de uso riesgoso entre programas académicos.
    columnas = list(filas[0].keys())
    col_programa = buscar_columna(columnas, ["programa"])
    indices = obtener_indice_riesgo(filas)
    total_muestra = len(filas)

    if not col_programa or indices is None or total_muestra == 0:
        print("\nUso riesgoso por programa académico")
        print("No se encontraron todas las variables necesarias para este cálculo.")
        return []

    grupos = {}
    for fila, indice in zip(filas, indices):
        programa = fila.get(col_programa, "")
        if programa not in grupos:
            grupos[programa] = {"total": 0, "riesgo": 0}
        grupos[programa]["total"] += 1
        grupos[programa]["riesgo"] += int(indice >= 1)

    resumen = []
    for programa, valores in grupos.items():
        porcentaje = valores["riesgo"] / valores["total"] * 100
        porcentaje_muestra = valores["total"] / total_muestra * 100
        resumen.append(
            {
                "Programa": programa,
                "Estudiantes": valores["total"],
                "Porcentaje de las 100 respuestas": round(porcentaje_muestra, 2),
                "Casos riesgo": valores["riesgo"],
                "Porcentaje riesgo": round(porcentaje, 2),
            }
        )

    resumen.sort(key=lambda fila: (fila["Porcentaje de las 100 respuestas"], fila["Porcentaje riesgo"]), reverse=True)

    print("\nUso riesgoso por programa académico")
    for fila in resumen:
        print(
            f"  {fila['Programa']}: {fila['Estudiantes']}/{total_muestra} respuestas "
            f"({fila['Porcentaje de las 100 respuestas']:.2f}% de la muestra); "
            f"riesgo {fila['Casos riesgo']}/{fila['Estudiantes']} ({fila['Porcentaje riesgo']:.2f}%)"
        )

    return resumen


def analizar_dependencia_por_accion(filas):
    # Compara la dependencia promedio según la acción principal al usar IA.
    columnas = list(filas[0].keys())
    col_accion = buscar_columna(columnas, ["acción", "principal"])
    col_dependencia = buscar_columna(columnas, ["dependencia"])

    if not (col_accion and col_dependencia):
        print("\nDependencia por acción principal")
        print("No se encontraron todas las variables necesarias para este cálculo.")
        return []

    grupos = {}
    for fila in filas:
        accion = fila.get(col_accion, "")
        coincidencia = re.search(r"\d+", fila.get(col_dependencia, ""))
        if not accion or not coincidencia:
            continue

        dependencia = int(coincidencia.group())
        if accion not in grupos:
            grupos[accion] = []
        grupos[accion].append(dependencia)

    resumen = []
    for accion, valores in grupos.items():
        dependencia_promedio = statistics.mean(valores)
        dependencia_alta = sum(1 for valor in valores if valor >= 8) / len(valores) * 100
        resumen.append(
            {
                "Acción": accion,
                "Estudiantes": len(valores),
                "Dependencia promedio": round(dependencia_promedio, 2),
                "Dependencia alta": round(dependencia_alta, 2),
            }
        )

    resumen.sort(key=lambda fila: (fila["Dependencia promedio"], fila["Dependencia alta"]), reverse=True)

    print("\nDependencia por acción principal")
    for fila in resumen:
        print(
            f"  {fila['Acción']}: dependencia promedio {fila['Dependencia promedio']:.2f}, "
            f"dependencia alta {fila['Dependencia alta']:.2f}% "
            f"({fila['Estudiantes']} estudiantes)"
        )

    return resumen


def crear_evento(nombre, favorables, total):
    # Crea una fila estándar para la tabla de probabilidades.
    probabilidad = favorables / total if total else 0
    return {
        "Evento": nombre,
        "Casos favorables": favorables,
        "Total válido": total,
        "Probabilidad": round(probabilidad, 4),
        "Porcentaje": round(probabilidad * 100, 2),
    }


def imprimir_metodologia(total_original, total_excluido, total_analizado):
    # Muestra la información general de la población usada.
    muestra_ideal = calcular_tamano_muestra(total_original)
    brecha = total_analizado - muestra_ideal

    print("\n1. Metodología y población")
    print(f"Población objetivo: {POBLACION_OBJETIVO}.")
    print(f"Muestra de trabajo definida para el proyecto: {TAMANO_POBLACION} personas.")
    print(f"Respuestas incorporadas en este archivo: {total_original}.")
    print(f"Respuestas usadas en el análisis: {total_analizado}.")
    print(f"Respuestas excluidas por límite del proyecto: {total_excluido}.")
    print("\nEstimación técnica del tamaño de muestra")
    print(f"Nivel de confianza: {NIVEL_CONFIANZA * 100:.0f}%")
    print(f"Valor Z: {VALOR_Z}")
    print(f"Margen de error: {MARGEN_ERROR * 100:.0f}%")
    print(f"Proporción esperada: {PROPORCION_ESPERADA:.2f}")
    print(f"Población finita usada en la corrección: {total_original} registros recolectados.")
    print(f"Tamaño de muestra estimado con corrección finita: {muestra_ideal} registros.")
    print(f"Brecha entre muestra real y muestra estimada: {brecha:+d} registros.")
    print(
        "Tipo de selección aplicado: muestreo sistemático por orden de registro, "
        "conservando los primeros 100 registros completos y excluyendo los registros finales adicionales."
    )
    print(
        "Representatividad: la muestra real supera el tamaño estimado, por lo que mantiene una base suficiente "
        "para describir el grupo encuestado; la generalización debe limitarse al contexto de estudiantes evaluado."
    )


def mostrar_menu():
    # Menú principal solicitado para separar descriptiva y probabilidad.
    print("\nSeleccione el tipo de análisis que desea ejecutar:")
    print("1. Estadística descriptiva")
    print("2. Probabilidad")
    print("3. Análisis")
    print("4. Salir")
    opcion = input("Digite una opción y presione Enter: ").strip()
    return opcion


def generar_conclusiones(tabla_cuantitativa, tabla_probabilidades):
    # Genera conclusiones para apoyar la interpretación de los resultados.
    conclusiones = []

    if tabla_cuantitativa:
        mayor_cv = max(tabla_cuantitativa, key=lambda fila: fila["Coeficiente de variación (%)"])
        conclusiones.append(
            f"La variable con mayor dispersión relativa fue '{mayor_cv['Variable']}', "
            "lo cual indica diferencias importantes entre los estudiantes."
        )

    if tabla_probabilidades:
        mayor_probabilidad = max(tabla_probabilidades, key=lambda fila: fila["Probabilidad"])
        conclusiones.append(
            f"El evento con mayor probabilidad fue: {mayor_probabilidad['Evento']} "
            f"({mayor_probabilidad['Porcentaje']:.2f}%)."
        )

    conclusiones.append("Los resultados permiten sustentar el análisis descriptivo solicitado.")
    return conclusiones


def procesar_proyecto():
    # Función principal: descomprime datos, limpia y ejecuta el análisis elegido.
    print("============================================================")
    print(f"PROYECTO: {TITULO_PROYECTO}")
    print("============================================================")

    filas_originales = leer_datos_embebidos()
    filas_limpias = limpiar_y_preparar_datos(filas_originales)
    filas_analizadas, total_original, total_excluido = limitar_respuestas(filas_limpias)

    while True:
        opcion = mostrar_menu()

        if opcion == "1":
            imprimir_metodologia(total_original, total_excluido, len(filas_analizadas))
            tabla_cuantitativa = analizar_cuantitativas(filas_analizadas)
            analizar_cualitativas(filas_analizadas)
            generar_conclusiones(tabla_cuantitativa, [])
            print("\nAnálisis finalizado correctamente.")
        elif opcion == "2":
            imprimir_metodologia(total_original, total_excluido, len(filas_analizadas))
            calcular_probabilidades(filas_analizadas)
            print("\nAnálisis finalizado correctamente.")
        elif opcion == "3":
            imprimir_metodologia(total_original, total_excluido, len(filas_analizadas))
            analizar_uso_riesgoso(filas_analizadas)
            analizar_indice_riesgo(filas_analizadas)
            analizar_riesgo_por_programa(filas_analizadas)
            analizar_ia_y_dependencia(filas_analizadas)
            analizar_dependencia_por_accion(filas_analizadas)
            print("\nAnálisis finalizado correctamente.")
        elif opcion == "4":
            print("Programa finalizado.")
            return
        else:
            print("Opción no válida. Seleccione una opción entre 1 y 4.")


if __name__ == "__main__":
    procesar_proyecto()
