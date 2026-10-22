import streamlit as st
import numpy as np
import math
import statistics
import matplotlib.pyplot as plt

# Configuración de la página
st.set_page_config(
    page_title="Estadístico Virtual Analítico E.V.A.",
    page_icon="📊",
    layout="wide"
)

# ---------------------------------------------------------
# ENCABEZADO E INFORMACIÓN DEL PROYECTO (Requisito 7)
# ---------------------------------------------------------
st.title("📊 Estadístico Virtual Analítico E.V.A.")
st.subheader("Universidad Mariano Gálvez de Guatemala")
st.markdown("""
**Facultad de Ingeniería** | **Asignatura:** Física II  
**Integrantes:**  
Jorge Eulises García Zamora.   
Gerson Antonio Alvarado Sosof.

**Sección:** [A]
---
""")

# Menú lateral para navegación
modulo = st.sidebar.selectbox(
    "Selecciona un Módulo del Asistente:",
    [
        "1. Ejemplo de Prueba Oficial",
        "2. Estadística Descriptiva y Datos Experimentales",
        "3. Tablas de Frecuencia y Gráficas",
        "4. Probabilidad y Distribución Normal",
        "5. Relación entre Variables (Regresión)",
        "6. Interpretaciones Teóricas",
        "7. Generador de Prácticas (10 Ejercicios)"
    ]
)

# Función auxiliar para convertir texto a lista de flotantes con manejo de errores
def parse_input_data(data_str):
    try:
        clean_str = data_str.replace(";", ",").replace(" ", ",")
        tokens = [t for t in clean_str.split(",") if t.strip() != ""]
        values = [float(t) for t in tokens]
        if len(values) == 0:
            return None, "⚠️ Error: No ingresaste ningún número válido."
        return values, None
    except ValueError:
        return None, "⚠️ Error de entrada: Asegúrate de ingresar únicamente números separados por comas."

# ---------------------------------------------------------
# MÓDULO 1: EJEMPLO DE PRUEBA OFICIAL (Sección 4)
# ---------------------------------------------------------
if modulo == "1. Ejemplo de Prueba Oficial":
    st.header("📌 Caso de Prueba Oficial")
    st.write("**Problema de evaluación:** Con mediciones de corriente (A): `2.1, 2.3, 2.2, 2.4, 2.0`; calcula media, desviación estándar muestral e interpreta.")
    
    if st.button("🚀 Ejecutar Caso de Prueba"):
        datos = [2.1, 2.3, 2.2, 2.4, 2.0]
        n = len(datos)
        suma = sum(datos)
        media = suma / n
        
        sq_diffs = [(x - media) ** 2 for x in datos]
        suma_sq_diffs = sum(sq_diffs)
        var_muestral = suma_sq_diffs / (n - 1)
        desv_muestral = math.sqrt(var_muestral)
        
        st.success("✅ **Cálculo Realizado con Éxito**")
        
        col1, col2 = st.columns(2)
        with col1:
            st.write("### 1. Media Aritmética (x̄)")
            st.latex(r"\bar{x} = \frac{\sum x_i}{n}")
            st.write(f"**Sustitución:** ({' + '.join(map(str, datos))}) / {n}")
            st.write(f"**Procedimiento:** {suma:.2f} / {n}")
            st.write(f"**Resultado Final:** **{media:.4f} A**")
            
        with col2:
            st.write("### 2. Desviación Estándar Muestral (s)")
            st.latex(r"s = \sqrt{\frac{\sum (x_i - \bar{x})^2}{n - 1}}")
            st.write(f"**Suma de diferencias al cuadrado:** {suma_sq_diffs:.4f}")
            st.write(f"**Varianza Muestral (s²):** {suma_sq_diffs:.4f} / {n - 1} = {var_muestral:.4f}")
            st.write(f"**Resultado Final:** **{desv_muestral:.4f} A**")
            
        st.info(f"**Interpretación Física:** La corriente eléctrica promedio medida en el circuito es de **{media:.2f} Amperios**. La dispersión o variación promedio de las mediciones respecto al valor central es de **±{desv_muestral:.4f} Amperios**, lo que indica una alta precisión en la toma de datos experimentales.")

# ---------------------------------------------------------
# MÓDULO 2: ESTADÍSTICA DESCRIPTIVA Y DATOS EXPERIMENTALES
# ---------------------------------------------------------
elif modulo == "2. Estadística Descriptiva y Datos Experimentales":
    st.header("📈 Estadística Descriptiva y Análisis Experimental")
    
    input_str = st.text_input("Ingresa los datos separados por comas:", "45.2, 46.0, 44.8, 45.5, 46.2, 45.0, 45.8")
    unidad = st.text_input("Unidad de medida (ej. N, V, A, m, kg):", "N")
    
    if st.button("Calcular Parámetros"):
        data, err = parse_input_data(input_str)
        if err:
            st.error(err)
        else:
            n = len(data)
            suma_val = sum(data)
            media = np.mean(data)
            mediana = np.median(data)
            
            # Limpiamos la unidad para que sea un texto corto y seguro
            unidad_str = unidad.strip() if len(unidad.strip()) < 6 else ""
            
            try:
                moda = statistics.mode(data)
                moda_str = f"{moda:.4f} {unidad_str}"
            except statistics.StatisticsError:
                moda_str = "No hay moda única"
                
            rango = np.ptp(data)
            var_m = np.var(data, ddof=1) if n > 1 else 0
            std_m = np.std(data, ddof=1) if n > 1 else 0
            var_p = np.var(data, ddof=0)
            std_p = np.std(data, ddof=0)
            
            st.markdown("### Resultados y Procedimiento Paso a Paso")
            st.write(f"**Cantidad de datos (n):** {n}")
            st.write(f"**Suma total ($\sum x_i$):** {suma_val:.4f} {unidad_str}")
            
            c1, c2, c3 = st.columns(3)
            c1.metric("Media (x̄)", f"{media:.4f} {unidad_str}")
            c2.metric("Mediana", f"{mediana:.4f} {unidad_str}")
            c3.metric("Moda", moda_str)
            
            st.markdown("---")
            st.write("#### Medidas de Dispersión")
            st.write(f"* **Rango:** {rango:.4f} {unidad_str}")
            st.write(f"* **Varianza Muestral ($s^2$):** {var_m:.4f} {unidad_str}²")
            st.write(f"* **Desviación Estándar Muestral ($s$):** {std_m:.4f} {unidad_str}")
            st.write(f"* **Desviación Estándar Poblacional ($\sigma$):** {std_p:.4f} {unidad_str}")

# ---------------------------------------------------------
# MÓDULO 3: TABLAS DE FRECUENCIAS Y GRÁFICAS
# ---------------------------------------------------------
elif modulo == "3. Tablas de Frecuencia y Gráficas":
    st.header("📊 Tablas de Frecuencias e Histogramas")
    input_str = st.text_area("Ingresa los datos para la tabla de frecuencias:", "5, 8, 10, 12, 15, 18, 20, 22, 25, 28, 30, 32, 35, 38, 40")
    
    if st.button("Generar Tabla y Gráficas"):
        data, err = parse_input_data(input_str)
        if err:
            st.error(err)
        else:
            fig, ax = plt.subplots(1, 2, figsize=(12, 4))
            ax[0].hist(data, bins='auto', color='#1f77b4', edgecolor='black', alpha=0.7)
            ax[0].set_title("Histograma de Frecuencias")
            ax[0].set_xlabel("Valores")
            ax[0].set_ylabel("Frecuencia Absoluta")
            
            ax[1].boxplot(data, vert=False)
            ax[1].set_title("Diagrama de Dispersión / Caja (Boxplot)")
            st.pyplot(fig)

# ---------------------------------------------------------
# MÓDULO 4: PROBABILIDAD Y DISTRIBUCIÓN NORMAL
# ---------------------------------------------------------
elif modulo == "4. Probabilidad y Distribución Normal":
    st.header("🎲 Distribución Normal Z")
    st.write("Calcula la probabilidad acumulada $P(X \le x)$ para una variable normal con Media ($\mu$) y Desviación ($\sigma$).")
    
    col1, col2, col3 = st.columns(3)
    mu = col1.number_input("Media (μ):", value=100.0)
    sigma = col2.number_input("Desviación Estándar (σ):", value=15.0, min_value=0.0001)
    x_val = col3.number_input("Valor X a evaluar:", value=115.0)
    
    if st.button("Calcular Probabilidad"):
        z = (x_val - mu) / sigma
        # Cálculo de probabilidad normal usando la función de error matemática (math.erf) nativa
        prob = 0.5 * (1.0 + math.erf(z / math.sqrt(2.0)))
        
        st.latex(r"Z = \frac{X - \mu}{\sigma}")
        st.write(f"**Sustitución:** Z = ({x_val} - {mu}) / {sigma}")
        st.write(f"**Puntaje Z:** **{z:.4f}**")
        st.write(f"**Probabilidad $P(X \le {x_val})$:** **{prob*100:.2f}%** ({prob:.4f})")

# ---------------------------------------------------------
# MÓDULO 5: RELACIÓN ENTRE VARIABLES (REGRESIÓN)
# ---------------------------------------------------------
elif modulo == "5. Relación entre Variables (Regresión)":
    st.header("📉 Correlación y Regresión Lineal Simple")
    
    str_x = st.text_input("Valores de Variable X (separados por coma):", "1, 2, 3, 4, 5")
    str_y = st.text_input("Valores de Variable Y (separados por coma):", "2, 4, 5, 4, 5")
    
    if st.button("Calcular Regresión Lineal"):
        x, err_x = parse_input_data(str_x)
        y, err_y = parse_input_data(str_y)
        
        if err_x or err_y:
            st.error("Error en el formato de entrada de X o Y.")
        elif len(x) != len(y):
            st.error("⚠️ Error: El número de datos en X debe ser igual al número de datos en Y.")
        else:
            x_arr = np.array(x)
            y_arr = np.array(y)
            n = len(x_arr)
            
            # Cálculo de regresión lineal por mínimos cuadrados usando NumPy puro
            m = (n * np.sum(x_arr * y_arr) - np.sum(x_arr) * np.sum(y_arr)) / (n * np.sum(x_arr**2) - (np.sum(x_arr))**2)
            b = (np.sum(y_arr) - m * np.sum(x_arr)) / n
            r_value = np.corrcoef(x_arr, y_arr)[0, 1]
            
            st.write(f"**Ecuación de la recta de regresión:** $y = {m:.4f}x + {b:.4f}$")
            st.write(f"**Coeficiente de Correlación (r):** **{r_value:.4f}**")
            st.write(f"**Coeficiente de Determinación ($R^2$):** **{r_value**2:.4f}**")
            
            fig, ax = plt.subplots()
            ax.scatter(x_arr, y_arr, color='red', label='Datos')
            ax.plot(x_arr, m * x_arr + b, color='blue', label='Línea de Regresión')
            ax.set_xlabel("X")
            ax.set_ylabel("Y")
            ax.legend()
            st.pyplot(fig)

# ---------------------------------------------------------
# MÓDULO 6: INTERPRETACIONES TEÓRICAS (Requisito 3)
# ---------------------------------------------------------
elif modulo == "6. Interpretaciones Teóricas":
    st.header("📚 Guía Teórica de Interpretación")
    st.markdown(r"""
    ### Diferencia entre Desviación Estándar Poblacional ($\sigma$) y Muestral ($s$)
    
    * **Desviación Estándar Poblacional ($\sigma$):** Se calcula cuando se poseen los datos de **absolutamente todos** los elementos del universo de estudio. Su fórmula divide la suma de cuadrados entre $N$.
    $$\sigma = \sqrt{\frac{\sum (x_i - \mu)^2}{N}}$$
      
    * **Desviación Estándar Muestral ($s$):** Se calcula cuando se trabaja con un **subconjunto (muestra)** representativo. Se divide entre $n - 1$ (Corrección de Bessel) para corregir el sesgo y no subestimar la variabilidad real de la población.
    $$s = \sqrt{\frac{\sum (x_i - \bar{x})^2}{n - 1}}$$
    """)

# ---------------------------------------------------------
# MÓDULO 7: GENERADOR DE PRÁCTICAS CON RETROALIMENTACIÓN (Requisito 5)
# ---------------------------------------------------------
elif modulo == "7. Generador de Prácticas (10 Ejercicios)":
    st.header("📝 Módulo de Prácticas y Evaluación Autónoma")
    
    ejercicios = [
        {"pregunta": "1. Dado el conjunto [4, 8, 6, 5, 3], ¿cuál es la media aritmética?", "respuesta": 5.2},
        {"pregunta": "2. ¿Cuál es la mediana del conjunto [10, 2, 5, 8, 12]?", "respuesta": 8.0},
        {"pregunta": "3. En el conjunto [1, 2, 2, 3, 4], ¿cuál es la moda?", "respuesta": 2.0},
        {"pregunta": "4. Calcula el rango del conjunto [15, 3, 22, 8, 19].", "respuesta": 19.0},
        {"pregunta": "5. Si n=5 y la suma de datos es 45, ¿cuál es la media?", "respuesta": 9.0},
        {"pregunta": "6. ¿Cuál es el valor Z si X=80, μ=70 y σ=5?", "respuesta": 2.0},
        {"pregunta": "7. En un conjunto de datos idénticos [7, 7, 7], ¿cuál es la desviación estándar?", "respuesta": 0.0},
        {"pregunta": "8. Si r = 0.9, ¿cuál es el coeficiente de determinación R²?", "respuesta": 0.81},
        {"pregunta": "9. Para una muestra de n=10, ¿por cuánto se divide para calcular la varianza muestral s²?", "respuesta": 9.0},
        {"pregunta": "10. ¿Cuál es la mediana del conjunto par [2, 4, 6, 8]?", "respuesta": 5.0}
    ]
    
    score = 0
    for idx, ej in enumerate(ejercicios):
        ans = st.number_input(ej["pregunta"], key=f"q_{idx}", value=0.0)
        if math.isclose(ans, ej["respuesta"], abs_tol=0.01):
            st.success("✨ ¡Correcto!")
            score += 1
        elif ans != 0.0:
            st.error(f"❌ Incorrecto. La respuesta exacta es {ej['respuesta']}")
            
    st.write(f"### Tu Puntuación: {score} / 10")