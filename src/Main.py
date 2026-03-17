import os
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')  # Usa un backend no interactivo para evitar errores con interfaces gráficas
import matplotlib.pyplot as plt


def process_csv(file_path):

    # Verifica si el archivo existe en la ruta indicada
    if not os.path.exists(file_path):
        print(f"Error: The file '{file_path}' does not exist.")
        return

    # Intenta leer el archivo CSV
    try:
        df = pd.read_csv(file_path)
    except Exception as e:
        print(f"Error reading the CSV file: {e}")
        return

    # Contador de personas encuestadas 
    print(f"Total de personas encuestadas: {len(df)}")

    # Limpia los nombres de las columnas:
    # elimina retornos de carro, saltos de línea y espacios en blanco
    df.columns = [str(col).replace('\r', '').replace('\n', '').strip() for col in df.columns]

    # Limpia las columnas de tipo texto:
    # convierte a string, elimina saltos de línea y espacios laterales
    for col in df.select_dtypes(include=['object', 'string']).columns:
        df[col] = df[col].astype(str).str.replace(r'[\r\n]', '', regex=True).str.strip()

    # Elimina la columna ID si existe, ya que normalmente no aporta al análisis estadístico
    if 'ID' in df.columns:
        df = df.drop(columns=['ID'])

    # Selecciona únicamente las columnas numéricas
    numeric_df = df.select_dtypes(include=[np.number])

    # Si no existen columnas numéricas, termina la función
    if numeric_df.empty:
        print("No numeric columns found in the CSV to calculate statistics.")
        return

    print(f"Loaded '{file_path}' successfully.")
    print(f"Found {len(numeric_df.columns)} numeric variables to analyze.")
    print("--- Variables cuantitativas ---")

    # Crea un directorio de salida para guardar los boxplots
    # El nombre de la carpeta se forma con el nombre base del CSV + "_plots"
    base_name = os.path.splitext(os.path.basename(file_path))[0]
    plots_dir = f"{base_name}_plots"
    os.makedirs(plots_dir, exist_ok=True)
    print(f"Box plots will be saved in the directory: {plots_dir}")

    # Recorre cada columna numérica para calcular sus estadísticas
    for column in numeric_df.columns:
        print(f"\n[{column}]")

        # Elimina valores nulos antes del análisis
        col_data = numeric_df[column].dropna()

        # Si después de eliminar nulos no quedan datos válidos, se omite la columna
        if col_data.empty:
            print("  No hay datos disponibles.")
            continue

        # Media aritmética
        mean = col_data.mean()
        print(f"  Media Aritmética:            {mean:.4f}")

        # Mediana
        median = col_data.median()
        print(f"  Mediana:                    {median:.4f}")

        # Moda
        mode_series = col_data.mode()
        if not mode_series.empty:
            modes = ", ".join([f"{m:.4f}" for m in mode_series])
            print(f"  Moda:                      {modes}")
        else:
            print("  Moda:                      N/A")

        # Varianza muestral
        # pandas usa ddof=1 por defecto, lo cual corresponde a varianza muestral
        variance = col_data.var()
        print(f"  Varianza muestral:           {variance:.4f}")

        # Desviación estándar muestral
        std_dev = col_data.std()
        print(f"  Desviación estándar:        {std_dev:.4f}")

        # Coeficiente de variación
        # Se valida que la media no sea 0 para evitar división por cero
        if mean != 0:
            cv = (std_dev / mean) * 100
            print(f"  Coeficiente de variación:   {cv:.4f}%")
        else:
            print("  Coeficiente de variación:   Indefinido (La media es igual a 0)")

        # Curtosis
        # Mide el grado de concentración de los datos en comparación con una distribución normal
        kurtosis = col_data.kurtosis()
        if pd.isna(kurtosis):
            print("  Coeficiente de kurtosis:    Not enough data")
        else:
            print(f"  Coeficiente de kurtosis:    {kurtosis:.4f}")

        # Generación del boxplot
        plt.figure(figsize=(6, 4))
        plt.boxplot(col_data, vert=False, patch_artist=True)
        plt.title(f'Box Plot de {column}')
        plt.xlabel('Valores')

        # Limpia el nombre de la columna para usarlo de forma segura como nombre de archivo
        safe_col_name = "".join([c if c.isalnum() else "_" for c in str(column)])
        plot_filename = os.path.join(plots_dir, f"boxplot_{safe_col_name}.png")

        # Ajusta márgenes, guarda la imagen y cierra la figura
        plt.tight_layout()
        plt.savefig(plot_filename)
        plt.close()

        print(f"  Box plot guardado en:         {plot_filename}")

        # Nota:
        # La generación de gráficos de frecuencia fue eliminada según la solicitud original

    # Selecciona las columnas no numéricas para análisis categórico
    categorical_df = df.select_dtypes(exclude=[np.number])

    if not categorical_df.empty:
        print("\n--- Variables cualitativas ---")

        for column in categorical_df.columns:
            print(f"\n[{column}]")

            # Elimina valores nulos
            col_data = categorical_df[column].dropna()

            if col_data.empty:
                print("  No hay datos disponibles.")
                continue

            # Moda de la variable categórica
            mode_series = col_data.mode()
            if not mode_series.empty:
                modes = ", ".join([str(m) for m in mode_series])
                print(f"  Moda:                      {modes}")
            else:
                print("  Moda:                      N/A")

            # Frecuencias absolutas
            value_counts = col_data.value_counts()
            print("  Frecuencias:")
            for val, count in value_counts.items():
                print(f"    {val}: n_i = {count} / h_i = {round(count/len(df),2)}")


# Construye la ruta del archivo CSV a procesar
path = os.path.join("data", "dataset.csv")

# Llama a la función principal para procesar el archivo
process_csv(path)