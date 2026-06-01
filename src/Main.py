import re
import math
from pathlib import Path

import matplotlib

matplotlib.use("Agg")  # Permite guardar gráficos sin abrir ventanas.

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


# =========================
# Configuración del proyecto
# =========================

RUTA_CSV = Path("data") / "Proyecto Estadistica I (Respuestas) - Respuestas de formulario 1.csv"
CARPETA_RESULTADOS = Path("resultados_proyecto")

TITULO_PROYECTO = "Uso de inteligencia artificial generativa en actividades académicas"
POBLACION_OBJETIVO = "Estudiantes encuestados sobre el uso de IA generativa en actividades académicas"
TAMANO_POBLACION = 100
LIMITE_RESPUESTAS_ANALISIS = 100
NIVEL_CONFIANZA = 0.95
VALOR_Z = 1.96
MARGEN_ERROR = 0.05
PROPORCION_ESPERADA = 0.5


def limpiar_nombre_archivo(texto):
    # Esta función toma el nombre de una variable y lo adapta para poder usarlo
    # como nombre de archivo. Por ejemplo, elimina signos raros y espacios.
    texto = str(texto).strip()
    texto = re.sub(r"[^A-Za-z0-9áéíóúÁÉÍÓÚñÑ]+", "_", texto)
    return texto.strip("_")[:80]


def limpiar_texto(texto):
    # Esta función limpia textos del formulario.
    # Sirve para quitar saltos de línea, retornos de carro y espacios repetidos.
    return re.sub(r"\s+", " ", str(texto).replace("\r", " ").replace("\n", " ")).strip()


def texto_respuestas(cantidad):
    # Esta función solo mejora la redacción de las salidas.
    # Si hay 1 respuesta escribe "respuesta"; si hay más, escribe "respuestas".
    return f"{cantidad} respuesta" if cantidad == 1 else f"{cantidad} respuestas"


def limpiar_dataframe(df):
    # Se hace una copia del DataFrame para no modificar directamente los datos originales.
    df = df.copy()

    # Se limpian los nombres de las columnas porque algunas preguntas del formulario
    # traen saltos de línea o espacios innecesarios.
    df.columns = [limpiar_texto(col) for col in df.columns]

    # Se limpian las respuestas de texto. Esto evita que una misma categoría se cuente
    # como distinta solo por tener espacios o saltos de línea.
    for columna in df.select_dtypes(include=["object", "string"]).columns:
        df[columna] = df[columna].map(limpiar_texto)
        df[columna] = df[columna].replace({"nan": np.nan, "None": np.nan, "": np.nan})

    # Se eliminan columnas de identificación o fecha que no aportan al análisis estadístico.
    columnas_id = [col for col in df.columns if col.lower() in {"id", "marca temporal", "timestamp"}]
    return df.drop(columns=columnas_id, errors="ignore")


def clasificar_dependencia_como_cualitativa(df):
    # Según la corrección del profesor, la escala de dependencia de 1 a 10
    # se debe analizar como variable cualitativa ordinal.
    # Por eso se transforma cada número en una categoría: "Nivel 1", "Nivel 2", etc.
    df = df.copy()
    columna_dependencia = buscar_columna(df, ["dependencia"])

    if columna_dependencia:
        valores = pd.to_numeric(df[columna_dependencia], errors="coerce")
        df[columna_dependencia] = valores.map(lambda valor: f"Nivel {int(valor)}" if pd.notna(valor) else np.nan)

    return df


def limitar_respuestas(df):
    # El proyecto debe trabajar con una población de 100 personas.
    # Si el archivo trae más respuestas, se conservan las primeras 100 filas
    # y se excluyen las respuestas adicionales del final del archivo.
    total_original = len(df)
    if total_original > LIMITE_RESPUESTAS_ANALISIS:
        df = df.head(LIMITE_RESPUESTAS_ANALISIS).copy()
    return df, total_original, max(total_original - len(df), 0)


def guardar_tabla(df, nombre_archivo):
    # Guarda las tablas del análisis en archivos CSV.
    # La codificación utf-8-sig ayuda a que Excel muestre bien tildes y ñ.
    ruta = CARPETA_RESULTADOS / nombre_archivo
    df.to_csv(ruta, index=False, encoding="utf-8-sig")
    return ruta


def calcular_tamano_muestra(poblacion_finita):
    # Fórmula para población finita:
    # n = (N * Z^2 * p * q) / (e^2 * (N - 1) + Z^2 * p * q)
    q = 1 - PROPORCION_ESPERADA
    numerador = poblacion_finita * (VALOR_Z**2) * PROPORCION_ESPERADA * q
    denominador = (MARGEN_ERROR**2) * (poblacion_finita - 1) + (VALOR_Z**2) * PROPORCION_ESPERADA * q
    return math.ceil(numerador / denominador)


def crear_histograma(datos, variable):
    # El histograma permite observar la distribución de una variable cuantitativa.
    # Muestra en qué rangos se concentran más los datos.
    plt.figure(figsize=(8, 5))
    plt.hist(datos, bins="auto", color="#2F6F73", edgecolor="white")
    plt.title(f"Distribución de {variable}")
    plt.xlabel("Valor observado")
    plt.ylabel("Frecuencia")
    plt.tight_layout()
    ruta = CARPETA_RESULTADOS / f"histograma_{limpiar_nombre_archivo(variable)}.png"
    plt.savefig(ruta, dpi=160)
    plt.close()
    return ruta


def crear_boxplot(datos, variable):
    # El diagrama de caja resume mediana, cuartiles, dispersión y posibles valores atípicos.
    # Es útil para comparar qué tan concentrados o dispersos están los datos.
    plt.figure(figsize=(8, 4))
    plt.boxplot(datos, vert=False, patch_artist=True, boxprops={"facecolor": "#D9A441"})
    plt.title(f"Diagrama de caja de {variable}")
    plt.xlabel("Valor observado")
    plt.tight_layout()
    ruta = CARPETA_RESULTADOS / f"boxplot_{limpiar_nombre_archivo(variable)}.png"
    plt.savefig(ruta, dpi=160)
    plt.close()
    return ruta


def crear_grafico_barras(frecuencias, variable):
    # El gráfico de barras se usa para variables cualitativas.
    # Compara visualmente cuántas respuestas tuvo cada categoría.
    plt.figure(figsize=(10, 5))
    frecuencias.plot(kind="bar", color="#7A4E9B", edgecolor="white")
    plt.title(f"Frecuencia de {variable}")
    plt.xlabel("Categoría")
    plt.ylabel("Frecuencia absoluta")
    plt.xticks(rotation=35, ha="right")
    plt.tight_layout()
    ruta = CARPETA_RESULTADOS / f"barras_{limpiar_nombre_archivo(variable)}.png"
    plt.savefig(ruta, dpi=160)
    plt.close()
    return ruta


def interpretar_cv(cv):
    # El coeficiente de variación permite comparar la dispersión relativa.
    # Se clasifica para que la salida no sea solo numérica sino también interpretativa.
    if pd.isna(cv):
        return "No interpretable"
    if cv < 10:
        return "Baja dispersión"
    if cv < 30:
        return "Dispersión moderada"
    return "Alta dispersión"


def analizar_cuantitativas(df):
    # En esta función se analizan las variables cuantitativas.
    # Se calculan medidas de tendencia central, dispersión y forma de la distribución.
    resultados = []

    # Pandas identifica como cuantitativas las columnas numéricas.
    # La variable de dependencia ya fue transformada antes, por eso no aparece aquí.
    numericas = df.select_dtypes(include=[np.number])

    print("\n2. Resultados: variables cuantitativas")
    if numericas.empty:
        print("No se encontraron variables cuantitativas para analizar.")
        return pd.DataFrame(resultados)

    for variable in numericas.columns:
        # Se eliminan valores vacíos para que las medidas se calculen solo con datos válidos.
        datos = numericas[variable].dropna()
        if datos.empty:
            print(f"\n[{variable}] Sin datos válidos.")
            continue

        # Medidas de tendencia central.
        media = datos.mean()
        mediana = datos.median()
        moda = datos.mode()

        # Medidas de dispersión y posición.
        varianza = datos.var(ddof=1)
        desviacion = datos.std(ddof=1)
        cv = (desviacion / media) * 100 if media != 0 else np.nan
        q1 = datos.quantile(0.25)
        q3 = datos.quantile(0.75)
        p10 = datos.quantile(0.10)
        p90 = datos.quantile(0.90)
        minimo = datos.min()
        maximo = datos.max()
        rango = maximo - minimo
        rango_intercuartilico = q3 - q1
        curtosis = datos.kurtosis()
        asimetria = datos.skew()

        # Para cada variable cuantitativa se generan dos gráficos:
        # histograma y diagrama de caja.
        ruta_histograma = crear_histograma(datos, variable)
        ruta_boxplot = crear_boxplot(datos, variable)

        # Esta interpretación breve ayuda a sustentar el resultado en la presentación.
        interpretacion = (
            f"La media es {media:.2f}, la mediana es {mediana:.2f} y la variabilidad se clasifica como "
            f"{interpretar_cv(cv).lower()}."
        )

        # Se guarda una fila por variable en la tabla de resumen cuantitativo.
        resultados.append(
            {
                "Variable": variable,
                "n válido": int(datos.count()),
                "Media": round(media, 4),
                "Mediana": round(mediana, 4),
                "Moda": ", ".join([f"{valor:.4f}" for valor in moda]) if not moda.empty else "Sin moda",
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
                "Coeficiente de variación (%)": round(cv, 4) if not pd.isna(cv) else "Indefinido",
                "Asimetría": round(asimetria, 4),
                "Curtosis": round(curtosis, 4),
                "Interpretación": interpretacion,
                "Histograma": str(ruta_histograma),
                "Boxplot": str(ruta_boxplot),
            }
        )

        # Salida en consola para presentar los resultados principales.
        print(f"\n[{variable}]")
        print(f"  n válido: {datos.count()}")
        print(f"  Media: {media:.2f}")
        print(f"  Mediana: {mediana:.2f}")
        print(f"  Moda: {', '.join([f'{valor:.2f}' for valor in moda]) if not moda.empty else 'Sin moda'}")
        print(f"  Rango: {rango:.2f}")
        print(f"  Q1: {q1:.2f} | Q3: {q3:.2f} | Rango intercuartílico: {rango_intercuartilico:.2f}")
        print(f"  Percentil 10: {p10:.2f} | Percentil 90: {p90:.2f}")
        print(f"  Desviación estándar: {desviacion:.2f}")
        print(f"  Coeficiente de variación: {cv:.2f}%" if not pd.isna(cv) else "  Coeficiente de variación: indefinido")
        print(f"  Interpretación: {interpretacion}")
        print("  Gráficos generados.")

    # Además de imprimir resultados, se guarda una tabla completa para anexos o presentación.
    tabla = pd.DataFrame(resultados)
    guardar_tabla(tabla, "resumen_variables_cuantitativas.csv")
    return tabla


def analizar_cualitativas(df):
    # En esta función se analizan las variables cualitativas.
    # Para estas variables no se calculan medias, sino frecuencias y porcentajes.
    resultados = []

    # Se toman como cualitativas las columnas no numéricas.
    categoricas = df.select_dtypes(exclude=[np.number])

    print("\n3. Resultados: variables cualitativas")
    if categoricas.empty:
        print("No se encontraron variables cualitativas para analizar.")
        return pd.DataFrame(resultados)

    for variable in categoricas.columns:
        # Se eliminan respuestas vacías antes de contar categorías.
        datos = categoricas[variable].dropna()
        if datos.empty:
            print(f"\n[{variable}] Sin datos válidos.")
            continue

        # value_counts calcula la frecuencia absoluta de cada categoría.
        frecuencias = datos.value_counts()
        ruta_barras = crear_grafico_barras(frecuencias, variable)
        moda = frecuencias.index[0]

        print(f"\n[{variable}]")
        print(f"  n válido: {datos.count()}")
        print(f"  Categoría más frecuente: {moda} ({texto_respuestas(frecuencias.iloc[0])})")
        print("  Tabla de frecuencias:")

        for categoria, frecuencia in frecuencias.items():
            # La frecuencia relativa se obtiene dividiendo cada frecuencia entre el total válido.
            porcentaje = (frecuencia / datos.count()) * 100
            resultados.append(
                {
                    "Variable": variable,
                    "Categoría": categoria,
                    "Frecuencia absoluta": int(frecuencia),
                    "Frecuencia relativa": round(frecuencia / datos.count(), 4),
                    "Porcentaje": round(porcentaje, 2),
                    "Gráfico": str(ruta_barras),
                }
            )
            print(f"    {categoria}: {texto_respuestas(frecuencia)} ({porcentaje:.2f}%)")

    # Se guarda una tabla con todas las frecuencias cualitativas.
    tabla = pd.DataFrame(resultados)
    guardar_tabla(tabla, "frecuencias_variables_cualitativas.csv")
    return tabla


def buscar_columna(df, palabras_clave):
    # Busca columnas usando palabras clave.
    # Esto evita depender de escribir preguntas largas exactamente igual en varias partes.
    for columna in df.columns:
        texto = columna.lower()
        if all(palabra.lower() in texto for palabra in palabras_clave):
            return columna
    return None


def calcular_probabilidades(df):
    # Esta función calcula probabilidades simples a partir de eventos del proyecto.
    # Cada probabilidad se calcula como:
    # casos favorables / total de respuestas válidas.
    resultados = []

    # Se localizan las columnas necesarias usando palabras clave de cada pregunta.
    col_trabajos = buscar_columna(df, ["10", "trabajos"])
    col_dependencia = buscar_columna(df, ["dependencia"])
    col_verifica = buscar_columna(df, ["verificar"])
    col_ia = buscar_columna(df, ["ia", "regularidad"])
    col_accion = buscar_columna(df, ["acción", "principal"])
    col_promedio = buscar_columna(df, ["promedio"])

    print("\n2. Resultados: probabilidades descriptivas de la encuesta")

    if col_trabajos:
        # Evento: estudiantes que usan IA en 7 o más de cada 10 trabajos.
        datos = df[col_trabajos].dropna()
        evento = datos >= 7
        resultados.append(
            {
                "Evento": "Usar IA generativa en 7 o más de cada 10 trabajos académicos",
                "Casos favorables": int(evento.sum()),
                "Total válido": int(datos.count()),
                "Probabilidad": round(evento.mean(), 4),
                "Porcentaje": round(evento.mean() * 100, 2),
            }
        )

    if col_dependencia:
        # La dependencia se maneja como cualitativa ordinal ("Nivel 8", por ejemplo).
        # Para calcular la probabilidad del evento 8 a 10, se extrae temporalmente el número.
        datos = pd.to_numeric(
            df[col_dependencia].astype(str).str.extract(r"(\d+)")[0],
            errors="coerce",
        ).dropna()
        evento = datos >= 8
        resultados.append(
            {
                "Evento": "Calificar la dependencia de IA como alta (8 a 10)",
                "Casos favorables": int(evento.sum()),
                "Total válido": int(datos.count()),
                "Probabilidad": round(evento.mean(), 4),
                "Porcentaje": round(evento.mean() * 100, 2),
            }
        )

    if col_verifica:
        # Evento: estudiantes que verifican la información siempre o casi siempre.
        datos = df[col_verifica].dropna().astype(str)
        patron = datos.str.lower().str.contains("siempre|casi siempre|sí|si", regex=True)
        resultados.append(
            {
                "Evento": "Verificar información de la IA en fuentes externas",
                "Casos favorables": int(patron.sum()),
                "Total válido": int(datos.count()),
                "Probabilidad": round(patron.mean(), 4),
                "Porcentaje": round(patron.mean() * 100, 2),
            }
        )

    if col_ia:
        # Evento: usar la IA generativa más frecuente en la muestra.
        datos = df[col_ia].dropna()
        ia_principal = datos.mode().iloc[0]
        evento = datos == ia_principal
        resultados.append(
            {
                "Evento": f"Usar principalmente {ia_principal}",
                "Casos favorables": int(evento.sum()),
                "Total válido": int(datos.count()),
                "Probabilidad": round(evento.mean(), 4),
                "Porcentaje": round(evento.mean() * 100, 2),
            }
        )

    if col_trabajos:
        generar_distribucion_discreta(df, col_trabajos)

    if col_accion and col_verifica and col_promedio:
        generar_probabilidad_condicional(df, col_accion, col_verifica, col_promedio)

    generar_probabilidades_adicionales(df)
    generar_temas_adicionales_curso(df)

    # Si no se encontró ninguna columna esperada, se informa y se evita crear una tabla vacía.
    tabla = pd.DataFrame(resultados)
    if tabla.empty:
        print("No se pudieron calcular probabilidades porque faltan variables esperadas.")
        return tabla

    # Se imprimen las probabilidades en formato fácil de leer.
    for _, fila in tabla.iterrows():
        print(
            f"  P({fila['Evento']}) = {fila['Probabilidad']:.4f} "
            f"({fila['Porcentaje']:.2f}%, {fila['Casos favorables']}/{fila['Total válido']})"
        )

    # Se guarda la tabla de probabilidades para usarla como soporte de la presentación.
    guardar_tabla(tabla, "probabilidades_descriptivas.csv")
    return tabla


def generar_distribucion_discreta(df, columna):
    # Esta sección sigue la idea de distribución de probabilidad discreta:
    # valores posibles, frecuencia absoluta, frecuencia relativa y frecuencia acumulada.
    datos = df[columna].dropna()
    conteos = datos.value_counts().sort_index()
    total = conteos.sum()
    acumulada = 0
    filas = []

    print("\n2.1 Distribución de probabilidad discreta")
    print(f"Variable discreta usada: {columna}")

    for valor, frecuencia in conteos.items():
        acumulada += frecuencia
        probabilidad = frecuencia / total
        probabilidad_acumulada = acumulada / total
        filas.append(
            {
                "xi": valor,
                "Frecuencia absoluta": int(frecuencia),
                "Probabilidad fi": round(probabilidad, 4),
                "Frecuencia acumulada": int(acumulada),
                "Probabilidad acumulada Fi": round(probabilidad_acumulada, 4),
            }
        )
        print(f"  x={valor}: P(X=x)={probabilidad:.4f}, F(x)={probabilidad_acumulada:.4f}")

    guardar_tabla(pd.DataFrame(filas), "distribucion_discreta_trabajos_ia.csv")


def generar_probabilidad_condicional(df, col_accion, col_verifica, col_promedio):
    # Esta sección aplica P(A|B) = P(A y B) / P(B).
    # A: tener promedio menor o igual a 3.8.
    # B1: copiar y pegar directamente.
    # B2: nunca verificar fuentes.
    promedio = pd.to_numeric(df[col_promedio], errors="coerce")
    accion = df[col_accion].astype(str).str.lower()
    verifica = df[col_verifica].astype(str).str.lower()

    promedio_bajo = promedio <= 3.8
    copia_pega = accion.str.contains("copiar y pegar directamente", regex=False)
    nunca_verifica = verifica.eq("nunca")

    interseccion_copia = promedio_bajo & copia_pega
    interseccion_nunca = promedio_bajo & nunca_verifica

    total_copia = copia_pega.sum()
    total_nunca = nunca_verifica.sum()
    prob_bajo_dado_copia = interseccion_copia.sum() / total_copia if total_copia else 0
    prob_bajo_dado_nunca = interseccion_nunca.sum() / total_nunca if total_nunca else 0

    filas = [
        {
            "Probabilidad condicional": "P(promedio <= 3.8 | copia y pega directamente)",
            "Casos intersección": int(interseccion_copia.sum()),
            "Casos condición": int(total_copia),
            "Resultado": round(prob_bajo_dado_copia, 4),
            "Porcentaje": round(prob_bajo_dado_copia * 100, 2),
        },
        {
            "Probabilidad condicional": "P(promedio <= 3.8 | nunca verifica fuentes)",
            "Casos intersección": int(interseccion_nunca.sum()),
            "Casos condición": int(total_nunca),
            "Resultado": round(prob_bajo_dado_nunca, 4),
            "Porcentaje": round(prob_bajo_dado_nunca * 100, 2),
        },
    ]

    print("\n2.2 Probabilidad condicional")
    for fila in filas:
        print(f"  {fila['Probabilidad condicional']} = {fila['Resultado']:.4f} ({fila['Porcentaje']:.2f}%)")

    guardar_tabla(pd.DataFrame(filas), "probabilidad_condicional.csv")


def generar_probabilidades_adicionales(df):
    # Integra probabilidades complementarias, conjuntas, condicionales inversas,
    # binomial y riesgo por programa académico.
    col_accion = buscar_columna(df, ["acción", "principal"])
    col_verifica = buscar_columna(df, ["verificar"])
    col_trabajos = buscar_columna(df, ["10", "trabajos"])
    col_dependencia = buscar_columna(df, ["dependencia"])
    col_promedio = buscar_columna(df, ["promedio"])
    col_programa = buscar_columna(df, ["programa"])
    total = len(df)

    if not (col_accion and col_verifica and col_trabajos and col_dependencia and col_promedio) or total == 0:
        print("\n2.4 Probabilidades adicionales")
        print("No se encontraron todas las variables necesarias para este cálculo.")
        return pd.DataFrame()

    accion = df[col_accion].astype(str).str.lower()
    verifica = df[col_verifica].astype(str).str.lower()
    trabajos = pd.to_numeric(df[col_trabajos], errors="coerce")
    dependencia = pd.to_numeric(df[col_dependencia].astype(str).str.extract(r"(\d+)")[0], errors="coerce")
    promedio = pd.to_numeric(df[col_promedio], errors="coerce")

    copia_pega = accion.str.contains("copiar y pegar directamente", regex=False)
    nunca_verifica = verifica.eq("nunca")
    uso_severo = trabajos >= 7
    dependencia_alta = dependencia >= 8
    promedio_bajo = promedio <= 3.8
    uso_riesgoso = copia_pega | nunca_verifica | uso_severo

    p_riesgo = uso_riesgoso.mean()
    p_no_riesgo = 1 - p_riesgo
    conjunta_copia_bajo = (copia_pega & promedio_bajo).mean()
    conjunta_nunca_bajo = (nunca_verifica & promedio_bajo).mean()
    conjunta_uso_dep = (uso_severo & dependencia_alta).mean()
    p_copia_dado_bajo = (copia_pega & promedio_bajo).sum() / promedio_bajo.sum() if promedio_bajo.sum() else 0
    p_nunca_dado_bajo = (nunca_verifica & promedio_bajo).sum() / promedio_bajo.sum() if promedio_bajo.sum() else 0

    n_binomial = 5
    p_exactamente_3 = math.comb(n_binomial, 3) * (p_riesgo**3) * ((1 - p_riesgo) ** (n_binomial - 3))
    p_al_menos_3 = sum(
        math.comb(n_binomial, k) * (p_riesgo**k) * ((1 - p_riesgo) ** (n_binomial - k))
        for k in range(3, n_binomial + 1)
    )

    filas = [
        {"Tipo": "Complementaria", "Evento": "P(uso riesgoso)", "Probabilidad": round(p_riesgo, 4), "Porcentaje": round(p_riesgo * 100, 2)},
        {"Tipo": "Complementaria", "Evento": "P(no uso riesgoso)", "Probabilidad": round(p_no_riesgo, 4), "Porcentaje": round(p_no_riesgo * 100, 2)},
        {"Tipo": "Conjunta", "Evento": "P(copia y pega y promedio <= 3.8)", "Probabilidad": round(conjunta_copia_bajo, 4), "Porcentaje": round(conjunta_copia_bajo * 100, 2)},
        {"Tipo": "Conjunta", "Evento": "P(nunca verifica y promedio <= 3.8)", "Probabilidad": round(conjunta_nunca_bajo, 4), "Porcentaje": round(conjunta_nunca_bajo * 100, 2)},
        {"Tipo": "Conjunta", "Evento": "P(uso en 7+ trabajos y dependencia alta)", "Probabilidad": round(conjunta_uso_dep, 4), "Porcentaje": round(conjunta_uso_dep * 100, 2)},
        {"Tipo": "Condicional inversa", "Evento": "P(copia y pega | promedio <= 3.8)", "Probabilidad": round(p_copia_dado_bajo, 4), "Porcentaje": round(p_copia_dado_bajo * 100, 2)},
        {"Tipo": "Condicional inversa", "Evento": "P(nunca verifica | promedio <= 3.8)", "Probabilidad": round(p_nunca_dado_bajo, 4), "Porcentaje": round(p_nunca_dado_bajo * 100, 2)},
        {"Tipo": "Binomial", "Evento": "P(exactamente 3 de 5 con uso riesgoso)", "Probabilidad": round(p_exactamente_3, 4), "Porcentaje": round(p_exactamente_3 * 100, 2)},
        {"Tipo": "Binomial", "Evento": "P(al menos 3 de 5 con uso riesgoso)", "Probabilidad": round(p_al_menos_3, 4), "Porcentaje": round(p_al_menos_3 * 100, 2)},
    ]

    print("\n2.4 Probabilidades adicionales")
    for fila in filas:
        print(f"  {fila['Evento']} = {fila['Probabilidad']:.4f} ({fila['Porcentaje']:.2f}%)")

    if col_programa:
        datos_programa = pd.DataFrame({"Programa": df[col_programa], "Uso riesgoso": uso_riesgoso})
        riesgo_programa = (
            datos_programa.groupby("Programa")
            .agg(Estudiantes=("Uso riesgoso", "count"), Casos_riesgo=("Uso riesgoso", "sum"), Probabilidad=("Uso riesgoso", "mean"))
            .reset_index()
            .sort_values("Probabilidad", ascending=False)
        )
        riesgo_programa["Porcentaje"] = (riesgo_programa["Probabilidad"] * 100).round(2)

        print("\n2.5 Probabilidad de uso riesgoso por programa")
        for _, fila in riesgo_programa.iterrows():
            print(
                f"  P(uso riesgoso | {fila['Programa']}) = {fila['Probabilidad']:.4f} "
                f"({fila['Porcentaje']:.2f}%, {int(fila['Casos_riesgo'])}/{int(fila['Estudiantes'])})"
            )

        guardar_tabla(riesgo_programa, "probabilidad_riesgo_por_programa.csv")

    resultados = pd.DataFrame(filas)
    guardar_tabla(resultados, "probabilidades_adicionales.csv")
    return resultados


def generar_temas_adicionales_curso(df):
    # Esta sección integra temas vistos en clase que no siempre aparecen
    # de forma directa en una encuesta: conteo, Bayes y distribuciones discretas modelo.
    col_accion = buscar_columna(df, ["acción", "principal"])
    col_verifica = buscar_columna(df, ["verificar"])
    col_trabajos = buscar_columna(df, ["10", "trabajos"])
    col_dependencia = buscar_columna(df, ["dependencia"])
    col_promedio = buscar_columna(df, ["promedio"])
    col_programa = buscar_columna(df, ["programa"])
    col_ia = buscar_columna(df, ["ia", "regularidad"])
    total = len(df)

    print("\n2.6 Temas adicionales del curso")
    filas = []

    if col_programa and col_ia:
        programas = df[col_programa].dropna().unique()
        herramientas = df[col_ia].dropna().unique()
        cantidad_ia = len(herramientas)
        combinaciones_ia = math.comb(cantidad_ia, 3) if cantidad_ia >= 3 else 0
        permutaciones_ia = math.perm(cantidad_ia, 3) if cantidad_ia >= 3 else 0
        regla_producto = len(programas) * cantidad_ia

        print("\nTécnicas de conteo")
        print(f"  Regla del producto: {len(programas)} programas x {cantidad_ia} IAs = {regla_producto} perfiles posibles.")
        print(f"  Combinaciones: C({cantidad_ia}, 3) = {combinaciones_ia} formas de escoger 3 IAs sin orden.")
        print(f"  Permutaciones: P({cantidad_ia}, 3) = {permutaciones_ia} formas de ordenar 3 IAs.")

        filas.extend(
            [
                {"Tema": "Conteo", "Cálculo": "Regla del producto", "Resultado": regla_producto},
                {"Tema": "Conteo", "Cálculo": f"C({cantidad_ia}, 3)", "Resultado": combinaciones_ia},
                {"Tema": "Conteo", "Cálculo": f"P({cantidad_ia}, 3)", "Resultado": permutaciones_ia},
            ]
        )

    if col_accion and col_verifica and col_trabajos and col_dependencia and col_promedio and total:
        accion = df[col_accion].astype(str).str.lower()
        verifica = df[col_verifica].astype(str).str.lower()
        trabajos = pd.to_numeric(df[col_trabajos], errors="coerce")
        dependencia = pd.to_numeric(df[col_dependencia].astype(str).str.extract(r"(\d+)")[0], errors="coerce")
        promedio = pd.to_numeric(df[col_promedio], errors="coerce")

        copia_pega = accion.str.contains("copiar y pegar directamente", regex=False)
        nunca_verifica = verifica.eq("nunca")
        promedio_bajo = promedio <= 3.8
        uso_riesgoso = copia_pega | nunca_verifica | (trabajos >= 7)
        dependencia_alta = dependencia >= 8

        p_bajo = promedio_bajo.mean()
        p_copia = copia_pega.mean()
        p_nunca = nunca_verifica.mean()
        p_bajo_dado_copia = (promedio_bajo & copia_pega).sum() / copia_pega.sum() if copia_pega.sum() else 0
        p_bajo_dado_nunca = (promedio_bajo & nunca_verifica).sum() / nunca_verifica.sum() if nunca_verifica.sum() else 0
        p_copia_dado_bajo_bayes = (p_bajo_dado_copia * p_copia / p_bajo) if p_bajo else 0
        p_nunca_dado_bajo_bayes = (p_bajo_dado_nunca * p_nunca / p_bajo) if p_bajo else 0

        print("\nTeorema de Bayes")
        print(f"  P(copia y pega | promedio <= 3.8) = {p_copia_dado_bajo_bayes:.4f} ({p_copia_dado_bajo_bayes * 100:.2f}%)")
        print(f"  P(nunca verifica | promedio <= 3.8) = {p_nunca_dado_bajo_bayes:.4f} ({p_nunca_dado_bajo_bayes * 100:.2f}%)")

        p_riesgo = uso_riesgoso.mean()
        n_grupo = 5
        casos_riesgo = int(uso_riesgoso.sum())
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

        filas.extend(
            [
                {"Tema": "Bayes", "Cálculo": "P(copia y pega | promedio <= 3.8)", "Resultado": round(p_copia_dado_bajo_bayes, 4)},
                {"Tema": "Bayes", "Cálculo": "P(nunca verifica | promedio <= 3.8)", "Resultado": round(p_nunca_dado_bajo_bayes, 4)},
                {"Tema": "Hipergeométrica", "Cálculo": "P(X=3) en n=5 sin reemplazo", "Resultado": round(p_hipergeometrica, 4)},
                {"Tema": "Poisson", "Cálculo": f"P(X=3), lambda={lambda_poisson:.2f}", "Resultado": round(p_poisson_3, 4)},
            ]
        )

        p_riesgo_dado_dep_alta = (uso_riesgoso & dependencia_alta).sum() / dependencia_alta.sum() if dependencia_alta.sum() else 0
        print("\nProbabilidad condicional adicional")
        print(f"  P(uso riesgoso | dependencia alta) = {p_riesgo_dado_dep_alta:.4f} ({p_riesgo_dado_dep_alta * 100:.2f}%)")
        filas.append({"Tema": "Condicional", "Cálculo": "P(uso riesgoso | dependencia alta)", "Resultado": round(p_riesgo_dado_dep_alta, 4)})

    if filas:
        guardar_tabla(pd.DataFrame(filas), "temas_adicionales_curso.csv")


def analizar_uso_riesgoso(df):
    # Un estudiante queda en uso riesgoso si cumple al menos una condición crítica.
    col_accion = buscar_columna(df, ["acción", "principal"])
    col_verifica = buscar_columna(df, ["verificar"])
    col_trabajos = buscar_columna(df, ["10", "trabajos"])
    total = len(df)

    if not (col_accion and col_verifica and col_trabajos) or total == 0:
        print("\nUso riesgoso")
        print("No se encontraron todas las variables necesarias para este cálculo.")
        return pd.DataFrame()

    condicion_copiar = df[col_accion].astype(str).str.lower().str.contains("copiar y pegar directamente", regex=False)
    condicion_no_verifica = df[col_verifica].astype(str).str.lower().eq("nunca")
    condicion_uso_severo = pd.to_numeric(df[col_trabajos], errors="coerce") >= 7
    uso_riesgoso = condicion_copiar | condicion_no_verifica | condicion_uso_severo

    resultados = pd.DataFrame(
        [
            {
                "Indicador": "Copiar y pegar directamente",
                "Casos": int(condicion_copiar.sum()),
                "Porcentaje": round(condicion_copiar.mean() * 100, 2),
            },
            {
                "Indicador": "Nunca verifica fuentes",
                "Casos": int(condicion_no_verifica.sum()),
                "Porcentaje": round(condicion_no_verifica.mean() * 100, 2),
            },
            {
                "Indicador": "Usa IA en 7 o más de cada 10 trabajos",
                "Casos": int(condicion_uso_severo.sum()),
                "Porcentaje": round(condicion_uso_severo.mean() * 100, 2),
            },
            {
                "Indicador": "Uso riesgoso (al menos una condición)",
                "Casos": int(uso_riesgoso.sum()),
                "Porcentaje": round(uso_riesgoso.mean() * 100, 2),
            },
        ]
    )

    print("\nUso riesgoso")
    for _, fila in resultados.iterrows():
        print(f"  {fila['Indicador']}: {fila['Casos']}/{total} ({fila['Porcentaje']:.2f}%)")

    guardar_tabla(resultados, "uso_riesgoso.csv")
    return resultados


def analizar_ia_y_dependencia(df):
    # Relaciona la IA usada con la dependencia reportada por los estudiantes.
    col_ia = buscar_columna(df, ["ia", "regularidad"])
    col_dependencia = buscar_columna(df, ["dependencia"])

    if not (col_ia and col_dependencia):
        print("\nIA utilizada y dependencia")
        print("No se encontraron todas las variables necesarias para este cálculo.")
        return pd.DataFrame()

    datos = df[[col_ia, col_dependencia]].copy()
    datos["Dependencia numérica"] = pd.to_numeric(
        datos[col_dependencia].astype(str).str.extract(r"(\d+)")[0],
        errors="coerce",
    )
    datos = datos.dropna(subset=[col_ia, "Dependencia numérica"])

    resumen = (
        datos.groupby(col_ia)
        .agg(
            Estudiantes=("Dependencia numérica", "count"),
            Dependencia_promedio=("Dependencia numérica", "mean"),
            Dependencia_alta=("Dependencia numérica", lambda valores: (valores >= 8).mean() * 100),
        )
        .reset_index()
        .sort_values(["Dependencia_promedio", "Dependencia_alta"], ascending=False)
    )

    resumen["Dependencia_promedio"] = resumen["Dependencia_promedio"].round(2)
    resumen["Dependencia_alta"] = resumen["Dependencia_alta"].round(2)

    print("\nIA utilizada y dependencia")
    for _, fila in resumen.iterrows():
        print(
            f"  {fila[col_ia]}: dependencia promedio {fila['Dependencia_promedio']:.2f}, "
            f"dependencia alta {fila['Dependencia_alta']:.2f}% "
            f"({int(fila['Estudiantes'])} estudiantes)"
        )

    if not resumen.empty:
        fila_mayor = resumen.iloc[0]
        print(
            f"\nLa IA que más se conecta con mayor dependencia promedio es {fila_mayor[col_ia]} "
            f"({fila_mayor['Dependencia_promedio']:.2f})."
        )

    guardar_tabla(resumen, "ia_y_dependencia.csv")
    return resumen


def preparar_condiciones_riesgo(df):
    # Centraliza las tres condiciones del índice de riesgo para reutilizarlas.
    col_accion = buscar_columna(df, ["acción", "principal"])
    col_verifica = buscar_columna(df, ["verificar"])
    col_trabajos = buscar_columna(df, ["10", "trabajos"])

    if not (col_accion and col_verifica and col_trabajos):
        return None, None, None, None

    condicion_copiar = df[col_accion].astype(str).str.lower().str.contains("copiar y pegar directamente", regex=False)
    condicion_no_verifica = df[col_verifica].astype(str).str.lower().eq("nunca")
    condicion_uso_severo = pd.to_numeric(df[col_trabajos], errors="coerce") >= 7
    indice_riesgo = condicion_copiar.astype(int) + condicion_no_verifica.astype(int) + condicion_uso_severo.astype(int)
    return condicion_copiar, condicion_no_verifica, condicion_uso_severo, indice_riesgo


def analizar_indice_riesgo(df):
    # Índice de riesgo: 0 a 3 según cuántas condiciones críticas cumple el estudiante.
    _, _, _, indice_riesgo = preparar_condiciones_riesgo(df)
    total = len(df)

    if indice_riesgo is None or total == 0:
        print("\nÍndice de riesgo")
        print("No se encontraron todas las variables necesarias para este cálculo.")
        return pd.DataFrame()

    conteos = indice_riesgo.value_counts().sort_index()
    etiquetas = {
        0: "0 condiciones",
        1: "1 condición",
        2: "2 condiciones",
        3: "3 condiciones",
    }
    filas = []

    print("\nÍndice de riesgo")
    for nivel in range(4):
        casos = int(conteos.get(nivel, 0))
        porcentaje = casos / total * 100
        filas.append({"Nivel": etiquetas[nivel], "Casos": casos, "Porcentaje": round(porcentaje, 2)})
        print(f"  {etiquetas[nivel]}: {casos}/{total} ({porcentaje:.2f}%)")

    resultados = pd.DataFrame(filas)
    guardar_tabla(resultados, "indice_riesgo.csv")
    return resultados


def analizar_riesgo_por_programa(df):
    # Compara el porcentaje de uso riesgoso entre programas académicos.
    col_programa = buscar_columna(df, ["programa"])
    _, _, _, indice_riesgo = preparar_condiciones_riesgo(df)
    total_muestra = len(df)

    if not col_programa or indice_riesgo is None or total_muestra == 0:
        print("\nUso riesgoso por programa académico")
        print("No se encontraron todas las variables necesarias para este cálculo.")
        return pd.DataFrame()

    datos = df[[col_programa]].copy()
    datos["Uso riesgoso"] = indice_riesgo >= 1
    resumen = (
        datos.groupby(col_programa)
        .agg(
            Estudiantes=("Uso riesgoso", "count"),
            Casos_riesgo=("Uso riesgoso", "sum"),
            Porcentaje_riesgo=("Uso riesgoso", lambda valores: valores.mean() * 100),
        )
        .reset_index()
    )
    resumen["Porcentaje_de_las_100_respuestas"] = resumen["Estudiantes"] / total_muestra * 100
    resumen = resumen.sort_values(
        ["Porcentaje_de_las_100_respuestas", "Porcentaje_riesgo"],
        ascending=False,
    )
    resumen = resumen[[col_programa, "Estudiantes", "Porcentaje_de_las_100_respuestas", "Casos_riesgo", "Porcentaje_riesgo"]]
    resumen["Porcentaje_de_las_100_respuestas"] = resumen["Porcentaje_de_las_100_respuestas"].round(2)
    resumen["Porcentaje_riesgo"] = resumen["Porcentaje_riesgo"].round(2)

    print("\nUso riesgoso por programa académico")
    for _, fila in resumen.iterrows():
        print(
            f"  {fila[col_programa]}: {int(fila['Estudiantes'])}/{total_muestra} respuestas "
            f"({fila['Porcentaje_de_las_100_respuestas']:.2f}% de la muestra); "
            f"riesgo {int(fila['Casos_riesgo'])}/{int(fila['Estudiantes'])} ({fila['Porcentaje_riesgo']:.2f}%)"
        )

    guardar_tabla(resumen, "riesgo_por_programa.csv")
    return resumen


def analizar_dependencia_por_accion(df):
    # Compara la dependencia promedio según la acción principal al usar IA.
    col_accion = buscar_columna(df, ["acción", "principal"])
    col_dependencia = buscar_columna(df, ["dependencia"])

    if not (col_accion and col_dependencia):
        print("\nDependencia por acción principal")
        print("No se encontraron todas las variables necesarias para este cálculo.")
        return pd.DataFrame()

    datos = df[[col_accion, col_dependencia]].copy()
    datos["Dependencia numérica"] = pd.to_numeric(
        datos[col_dependencia].astype(str).str.extract(r"(\d+)")[0],
        errors="coerce",
    )
    datos = datos.dropna(subset=[col_accion, "Dependencia numérica"])

    resumen = (
        datos.groupby(col_accion)
        .agg(
            Estudiantes=("Dependencia numérica", "count"),
            Dependencia_promedio=("Dependencia numérica", "mean"),
            Dependencia_alta=("Dependencia numérica", lambda valores: (valores >= 8).mean() * 100),
        )
        .reset_index()
        .sort_values(["Dependencia_promedio", "Dependencia_alta"], ascending=False)
    )
    resumen["Dependencia_promedio"] = resumen["Dependencia_promedio"].round(2)
    resumen["Dependencia_alta"] = resumen["Dependencia_alta"].round(2)

    print("\nDependencia por acción principal")
    for _, fila in resumen.iterrows():
        print(
            f"  {fila[col_accion]}: dependencia promedio {fila['Dependencia_promedio']:.2f}, "
            f"dependencia alta {fila['Dependencia_alta']:.2f}% "
            f"({int(fila['Estudiantes'])} estudiantes)"
        )

    guardar_tabla(resumen, "dependencia_por_accion.csv")
    return resumen


def imprimir_metodologia(total_original, total_excluido, total_analizado):
    # Imprime la metodología, el cálculo formal de muestra y la comparación solicitada.
    muestra_ideal = calcular_tamano_muestra(total_original)
    brecha = total_analizado - muestra_ideal

    print("\n1. Metodología y población")
    print(f"Población objetivo: {POBLACION_OBJETIVO}.")
    print(f"Muestra de trabajo definida para el proyecto: {TAMANO_POBLACION} personas.")
    print(f"Respuestas encontradas en el archivo original: {total_original}.")
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
    # Esta función construye conclusiones automáticas y las guarda en un archivo de texto.
    # No las imprime en consola porque se pidió quitarlas del output.
    conclusiones = []

    if not tabla_cuantitativa.empty:
        # Se identifica la variable cuantitativa con mayor coeficiente de variación.
        fila_mayor_cv = tabla_cuantitativa.sort_values("Coeficiente de variación (%)", ascending=False).iloc[0]
        conclusiones.append(
            "La variable con mayor dispersión relativa fue "
            f"'{fila_mayor_cv['Variable']}', lo cual indica diferencias importantes entre los estudiantes."
        )

    if not tabla_probabilidades.empty:
        # Se identifica el evento con mayor probabilidad dentro de los eventos calculados.
        fila_mayor_prob = tabla_probabilidades.sort_values("Probabilidad", ascending=False).iloc[0]
        conclusiones.append(
            f"El evento con mayor probabilidad fue: {fila_mayor_prob['Evento']} "
            f"({fila_mayor_prob['Porcentaje']:.2f}%)."
        )

    conclusiones.append(
        "Las tablas y gráficos generados permiten sustentar los resultados descriptivos solicitados en la rúbrica."
    )

    # El archivo queda disponible para redactar o apoyar la presentación final.
    ruta = CARPETA_RESULTADOS / "conclusiones.txt"
    ruta.write_text("\n".join(conclusiones), encoding="utf-8")


def procesar_proyecto():
    # Esta es la función principal del programa.
    # Organiza todo el flujo: leer datos, limpiarlos, analizarlos y guardar resultados.
    print("============================================================")
    print(f"PROYECTO: {TITULO_PROYECTO}")
    print("============================================================")

    # Se valida que el archivo de datos exista antes de intentar leerlo.
    if not RUTA_CSV.exists():
        print(f"Error: no se encontró el archivo de datos en '{RUTA_CSV}'.")
        return

    # Se crea la carpeta donde quedarán tablas, gráficos y conclusiones.
    CARPETA_RESULTADOS.mkdir(parents=True, exist_ok=True)

    # Se lee el archivo CSV con las respuestas del formulario.
    try:
        df_original = pd.read_csv(RUTA_CSV)
    except Exception as error:
        print(f"Error al leer el archivo CSV: {error}")
        return

    # Primero se limpian los datos.
    df_limpio = limpiar_dataframe(df_original)

    # Después se ajusta la clasificación de la variable dependencia
    # para tratarla como cualitativa ordinal, según la indicación del profesor.
    df_limpio = clasificar_dependencia_como_cualitativa(df_limpio)

    # Finalmente se limita el análisis a 100 respuestas, como pide el proyecto.
    df_limpio, total_original, total_excluido = limitar_respuestas(df_limpio)

    # El menú queda en ciclo hasta que el usuario elija salir.
    while True:
        opcion = mostrar_menu()

        if opcion == "1":
            imprimir_metodologia(total_original, total_excluido, len(df_limpio))
            tabla_cuantitativa = analizar_cuantitativas(df_limpio)
            analizar_cualitativas(df_limpio)
            generar_conclusiones(tabla_cuantitativa, pd.DataFrame())
            print("\nAnálisis finalizado correctamente.")
        elif opcion == "2":
            imprimir_metodologia(total_original, total_excluido, len(df_limpio))
            calcular_probabilidades(df_limpio)
            print("\nAnálisis finalizado correctamente.")
        elif opcion == "3":
            imprimir_metodologia(total_original, total_excluido, len(df_limpio))
            analizar_uso_riesgoso(df_limpio)
            analizar_indice_riesgo(df_limpio)
            analizar_riesgo_por_programa(df_limpio)
            analizar_ia_y_dependencia(df_limpio)
            analizar_dependencia_por_accion(df_limpio)
            print("\nAnálisis finalizado correctamente.")
        elif opcion == "4":
            print("Programa finalizado.")
            return
        else:
            print("Opción no válida. Seleccione una opción del menú.")


if __name__ == "__main__":
    procesar_proyecto()
