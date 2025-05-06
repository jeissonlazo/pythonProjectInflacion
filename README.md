# Simulador de Inflación con Monte Carlo

Este proyecto implementa un simulador de inflación utilizando el método de Monte Carlo para proyectar tendencias inflacionarias futuras basadas en datos históricos.

## Descripción

El sistema analiza datos históricos de inflación por categorías y utiliza técnicas de simulación de Monte Carlo para generar proyecciones probabilísticas de la inflación futura. El proyecto está diseñado para:

- Cargar datos históricos de inflación desde archivos JSON
- Simular múltiples escenarios futuros usando técnicas de Monte Carlo
- Calcular estadísticas sobre las proyecciones (mediana, percentiles)
- Visualizar los resultados con intervalos de confianza
- Generar una proyección general ponderada basada en el peso de cada categoría

## Requisitos

```
numpy
pandas
matplotlib
scipy
seaborn
tqdm
python-dateutil
```

Puede instalar todas las dependencias con:

```bash
pip install -r requirements.txt
```

## Estructura de datos

El programa espera un archivo JSON con la siguiente estructura:

```json
[
  {
    "fecha": "YYYY-MM-DD",
    "datos": [
      {
        "categoria": "Nombre de categoría",
        "ponderado": 25.5,
        "mensual": 1.2
      },
      {
        "categoria": "Otra categoría",
        "ponderado": 12.3,
        "mensual": 0.8
      }
    ]
  }
]
```

Donde:
- `fecha`: Fecha del período
- `categoria`: Nombre de la categoría de productos/servicios
- `ponderado`: Peso porcentual de la categoría en el índice general
- `mensual`: Variación porcentual mensual para ese período

## Uso

Para ejecutar la simulación, modifique las variables de configuración al final del archivo `main.py`:

```python
if __name__ == "__main__":
    # Configuración
    ruta_archivo = "data/output.json"  # Ruta al archivo JSON
    num_simulaciones = 5000  # Número de simulaciones de Monte Carlo
    periodos_proyeccion = 24  # Número de meses a proyectar

    # Ejecutar simulación
    resultados = main(ruta_archivo, num_simulaciones, periodos_proyeccion)
```

Luego, ejecute:

```bash
python main.py
```

## Funcionamiento

1. **Carga de datos**: Lee los datos históricos de inflación desde un archivo JSON.
2. **Preparación**: Convierte los datos a un DataFrame de pandas para su análisis.
3. **Simulación**: Para cada categoría:
   - Calcula estadísticas de la distribución histórica (media, desviación estándar)
   - Genera múltiples simulaciones aleatorias siguiendo una distribución normal
   - Calcula índices acumulados para cada simulación
4. **Estadísticas**: Calcula mediana, percentiles y otros estadísticos de las simulaciones.
5. **Visualización**: Genera gráficos para cada categoría y un gráfico ponderado general.

## Metodología de Monte Carlo

El método de Monte Carlo implementado:

1. Utiliza la distribución histórica de variaciones mensuales para caracterizar cada categoría
2. Genera N trayectorias aleatorias para cada categoría
3. Construye intervalos de confianza basados en los percentiles de las simulaciones
4. Combina las categorías según su ponderación para generar la proyección general

## Personalización

Puede modificar los siguientes parámetros:
- `num_simulaciones`: Cantidad de simulaciones aleatorias (mayor número = resultados más estables)
- `periodos_proyeccion`: Cantidad de meses a proyectar hacia el futuro
- `ruta_archivo`: Ubicación del archivo JSON con los datos históricos

## Licencia

[MIT](https://choosealicense.com/licenses/mit/)
