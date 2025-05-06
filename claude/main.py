import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import json
import datetime
from dateutil.relativedelta import relativedelta
from scipy import stats
import seaborn as sns
from tqdm import tqdm


# Función para cargar los datos
def cargar_datos(ruta_archivo):
    with open(ruta_archivo, 'r', encoding='utf-8') as file:
        datos = json.load(file)
    return datos


# Función para preparar los datos en un DataFrame
def preparar_dataframe(datos):
    registros = []

    for periodo in datos:
        fecha = periodo['fecha']
        for categoria in periodo['datos']:
            registros.append({
                'fecha': fecha,
                'categoria': categoria['categoria'],
                'ponderado': categoria['ponderado'],
                'mensual': categoria['mensual']
            })

    df = pd.DataFrame(registros)
    df['fecha'] = pd.to_datetime(df['fecha'])
    return df


# Función para simular la inflación futura usando Monte Carlo
def simulacion_montecarlo(df, categoria, num_simulaciones=1000, periodos_proyeccion=12):
    # Filtrar datos por categoría
    datos_categoria = df[df['categoria'] == categoria].copy()

    if len(datos_categoria) < 2:
        print(f"Advertencia: Datos insuficientes para la categoría {categoria}")
        return None

    # Calcular estadísticas de la distribución histórica
    media = datos_categoria['mensual'].mean()
    desv_est = datos_categoria['mensual'].std()

    # Si la desviación estándar es cero o muy pequeña, asigna un valor mínimo
    if desv_est < 0.01:
        desv_est = 0.01

    # Fecha del último dato disponible
    ultima_fecha = datos_categoria['fecha'].max()

    # Crear fechas para la proyección
    fechas_proyeccion = [ultima_fecha + relativedelta(months=i + 1) for i in range(periodos_proyeccion)]

    # Realizar simulaciones de Monte Carlo
    simulaciones = []

    for _ in range(num_simulaciones):
        # Generar valores aleatorios según una distribución normal
        variaciones_mensuales = np.random.normal(media, desv_est, periodos_proyeccion)

        # Calcular inflación acumulada (comenzando desde 100)
        indice_base = 100
        indices = [indice_base]

        for var in variaciones_mensuales:
            nuevo_indice = indices[-1] * (1 + var / 100)
            indices.append(nuevo_indice)

        indices = indices[1:]  # Eliminar el valor base inicial

        # Almacenar resultados
        proyeccion = pd.DataFrame({
            'fecha': fechas_proyeccion,
            'indice': indices,
            'variacion_mensual': variaciones_mensuales
        })

        simulaciones.append(proyeccion)

    return simulaciones


# Función para calcular estadísticas de las simulaciones
def calcular_estadisticas(simulaciones):
    if simulaciones is None:
        return None

    # Obtener todas las fechas únicas de proyección
    fechas = simulaciones[0]['fecha'].unique()
    estadisticas = []

    for fecha in fechas:
        valores = [sim.loc[sim['fecha'] == fecha, 'indice'].values[0] for sim in simulaciones]

        estadistica = {
            'fecha': fecha,
            'media': np.mean(valores),
            'mediana': np.median(valores),
            'percentil_5': np.percentile(valores, 5),
            'percentil_25': np.percentile(valores, 25),
            'percentil_75': np.percentile(valores, 75),
            'percentil_95': np.percentile(valores, 95)
        }


        estadisticas.append(estadistica)

    return pd.DataFrame(estadisticas)


# Función para visualizar resultados
def visualizar_proyeccion(estadisticas, categoria, ponderado):
    if estadisticas is None:
        print(f"No hay datos suficientes para visualizar la categoría {categoria}")
        return

    plt.figure(figsize=(12, 6))

    # Graficar la mediana
    plt.plot(estadisticas['fecha'], estadisticas['mediana'], 'b-', label='Mediana')

    # Graficar intervalos de confianza
    plt.fill_between(estadisticas['fecha'],
                     estadisticas['percentil_25'],
                     estadisticas['percentil_75'],
                     color='blue', alpha=0.2, label='Rango intercuartílico (25%-75%)')

    plt.fill_between(estadisticas['fecha'],
                     estadisticas['percentil_5'],
                     estadisticas['percentil_95'],
                     color='blue', alpha=0.1, label='Intervalo de confianza (5%-95%)')

    plt.title(f'Proyección de Inflación: {categoria} (Ponderación: {ponderado}%)')
    plt.xlabel('Fecha')
    plt.ylabel('Índice (Base 100)')
    plt.grid(True, linestyle='--', alpha=0.7)
    plt.legend()

    # Formatear fechas en el eje x
    plt.gcf().autofmt_xdate()

    plt.tight_layout()
    plt.show()


# Función principal
def main(ruta_archivo, num_simulaciones=1000, periodos_proyeccion=12):
    # Cargar y preparar datos
    datos = cargar_datos(ruta_archivo)
    df = preparar_dataframe(datos)

    # Obtener categorías únicas
    categorias = df['categoria'].unique()

    # Resultados para todas las categorías
    resultados = {}

    print(f"Realizando {num_simulaciones} simulaciones para {len(categorias)} categorías...")

    for categoria in tqdm(categorias):
        # Obtener la última ponderación para esta categoría
        ultima_fecha = df[df['categoria'] == categoria]['fecha'].max()
        ponderado = df[(df['categoria'] == categoria) & (df['fecha'] == ultima_fecha)]['ponderado'].values[0]

        # Realizar simulación
        simulaciones = simulacion_montecarlo(df, categoria, num_simulaciones, periodos_proyeccion)

        # Calcular estadísticas
        estadisticas = calcular_estadisticas(simulaciones)

        if estadisticas is not None:
            resultados[categoria] = {
                'ponderado': ponderado,
                'estadisticas': estadisticas
            }

    # Visualizar resultados para cada categoría
    for categoria, datos in resultados.items():
        visualizar_proyeccion(datos['estadisticas'], categoria, datos['ponderado'])

    # Calcular la inflación general ponderada
    calcular_inflacion_general(resultados)

    return resultados


# Función para calcular la inflación general ponderada
def calcular_inflacion_general(resultados):
    if not resultados:
        print("No hay resultados para calcular la inflación general")
        return

    # Obtener las fechas comunes a todas las categorías
    fechas = resultados[list(resultados.keys())[0]]['estadisticas']['fecha'].tolist()

    # Inicializar DataFrame para la inflación general
    inflacion_general = pd.DataFrame({
        'fecha': fechas,
        'mediana': np.zeros(len(fechas)),
        'percentil_5': np.zeros(len(fechas)),
        'percentil_25': np.zeros(len(fechas)),
        'percentil_75': np.zeros(len(fechas)),
        'percentil_95': np.zeros(len(fechas))
    })

    # Calcular la suma total de ponderaciones para normalizar
    suma_ponderaciones = sum(datos['ponderado'] for datos in resultados.values())

    # Calcular la inflación ponderada
    for categoria, datos in resultados.items():
        peso = datos['ponderado'] / suma_ponderaciones
        estadisticas = datos['estadisticas']

        for col in ['mediana', 'percentil_5', 'percentil_25', 'percentil_75', 'percentil_95']:
            inflacion_general[col] += estadisticas[col] * peso

    # Visualizar la inflación general
    plt.figure(figsize=(12, 6))

    plt.plot(inflacion_general['fecha'], inflacion_general['mediana'], 'r-', linewidth=2, label='Mediana')

    plt.fill_between(inflacion_general['fecha'],
                     inflacion_general['percentil_25'],
                     inflacion_general['percentil_75'],
                     color='red', alpha=0.2, label='Rango intercuartílico (25%-75%)')

    plt.fill_between(inflacion_general['fecha'],
                     inflacion_general['percentil_5'],
                     inflacion_general['percentil_95'],
                     color='red', alpha=0.1, label='Intervalo de confianza (5%-95%)')

    plt.title('Proyección de Inflación General Ponderada')
    plt.xlabel('Fecha')
    plt.ylabel('Índice (Base 100)')
    plt.grid(True, linestyle='--', alpha=0.7)
    plt.legend()

    plt.gcf().autofmt_xdate()
    plt.tight_layout()
    plt.show()

    return inflacion_general


# Ejecutar el programa si se ejecuta directamente este script
if __name__ == "__main__":
    # Configuración
    ruta_archivo = "output.json"  # Ruta al archivo JSON
    num_simulaciones = 5000  # Número de simulaciones de Monte Carlo
    periodos_proyeccion = 24  # Número de meses a proyectar

    # Ejecutar simulación
    resultados = main(ruta_archivo, num_simulaciones, periodos_proyeccion)