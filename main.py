import numpy as np
import matplotlib.pyplot as plt

# Parámetros de la simulación
lado_bosque = 100  # El bosque es un cuadrado de 100x100 metros
radio_incendio = 30  # Radio del incendio
centro_incendio = (50, 50)  # Centro del incendio
num_puntos = 10000  # Número de puntos aleatorios

# Generar puntos aleatorios dentro del bosque
x_puntos = np.random.uniform(0, lado_bosque, num_puntos)
y_puntos = np.random.uniform(0, lado_bosque, num_puntos)

# Calcular la distancia de cada punto al centro del incendio
distancias = np.sqrt((x_puntos - centro_incendio[0])**2 + (y_puntos - centro_incendio[1])**2)

# Determinar si los puntos están dentro del área quemada (círculo)
puntos_quemados = distancias <= radio_incendio

# Estimar área afectada
area_total = lado_bosque ** 2
proporcion_quemada = np.sum(puntos_quemados) / num_puntos
area_quemada_estimada = proporcion_quemada * area_total

# Cálculo teórico del área (para comparar)
area_quemada_real = np.pi * (radio_incendio ** 2)

# Mostrar resultados
print(f"Área total del bosque: {area_total:.2f} m²")
print(f"Área quemada estimada (Monte Carlo): {area_quemada_estimada:.2f} m²")
print(f"Área quemada real (cálculo exacto): {area_quemada_real:.2f} m²")
print(f"Error relativo: {abs(area_quemada_estimada - area_quemada_real) / area_quemada_real * 100:.2f}%")

# Gráfica
plt.figure(figsize=(8, 8))
plt.scatter(x_puntos[~puntos_quemados], y_puntos[~puntos_quemados], color='green', s=1, label='Zona no quemada')
plt.scatter(x_puntos[puntos_quemados], y_puntos[puntos_quemados], color='red', s=1, label='Zona quemada')
circle = plt.Circle(centro_incendio, radio_incendio, color='blue', fill=False, linestyle='--', label='Área teórica incendio')
plt.gca().add_artist(circle)
plt.title('Simulación de incendio forestal con Monte Carlo')
plt.xlabel('X (m)')
plt.ylabel('Y (m)')
plt.xlim(0, lado_bosque)
plt.ylim(0, lado_bosque)
plt.legend()
plt.grid(True)
plt.show()
