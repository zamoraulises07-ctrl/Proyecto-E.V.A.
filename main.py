import os
import re
import math
import time
import random
import statistics

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import streamlit as st
from google import genai
from google.genai import types

# ==================================================
# CONFIGURACION GENERAL
# ==================================================
st.set_page_config(
    page_title="E.V.A. | Asistente Estadístico",
    page_icon="📊",
    layout="centered",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
    .main-title {
        text-align: center;
        color: #17365D;
        font-size: 2.5rem;
        font-weight: 800;
        margin-bottom: 0;
    }
    .subtitle {
        text-align: center;
        color: #526579;
        margin-top: 5px;
    }
    .project-info {
        background-color: #F0F5FA;
        padding: 16px;
        border-radius: 12px;
        border-left: 5px solid #2471A3;
        margin: 18px 0;
        color: #17365D;
    }
    .footer {
        text-align: center;
        color: #6B7280;
        font-size: 0.85rem;
        margin-top: 30px;
    }
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="main-title">🤖 E.V.A.</div>',
            unsafe_allow_html=True)
st.markdown('<div class="subtitle">Estadístico Virtual Analítico</div>',
            unsafe_allow_html=True)

st.markdown("""
<div class="project-info">
<b>Universidad Mariano Gálvez de Guatemala</b><br>
Facultad de Ingeniería en sistemas<br>
<b>Asignatura:</b> Física II<br>
<b>Integrantes:</b><br>
Jorge Eulises García Zamora<br>
Gerson Antonio Alvarado Sosof<br>
<b>Sección:</b> A
</div>
""", unsafe_allow_html=True)

st.divider()

# ==================================================
# CONFIGURACION DE LA IA (GEMINI)
# ==================================================
INSTRUCCIONES_EVA = """
Tu nombre es E.V.A., siglas de Estadístico Virtual Analítico.

Eres el asistente virtual académico del proyecto E.V.A.,
desarrollado por Jorge Zamora y Gerson Alvarado para la Facultad de
Ingeniería en sistemas de la Universidad Mariano Gálvez de Guatemala,
en la asignatura Física II.

IDENTIDAD:
- Preséntate siempre como E.V.A.
- Nunca digas que no eres E.V.A. ni que eres otro asistente.
- Si te preguntan quién eres, explica brevemente tu nombre
  completo y tu propósito.
- No afirmes ser una persona humana.

FUNCIONES:
- Ayuda con estadística descriptiva, media, mediana, moda,
  varianza, desviación estándar y tablas de frecuencia.
- Explica probabilidad, distribución normal, puntajes Z,
  correlación y regresión lineal.
- Explica la diferencia entre desviación estándar poblacional
  (divide entre n) y muestral (divide entre n-1).
- Apoya con matemáticas, física y análisis de datos.
- Muestra fórmulas, sustituciones, unidades y procedimientos
  cuando sean necesarios, y termina con la respuesta final.
- Comprueba los cálculos cuidadosamente y no inventes datos.

ESTILO:
- Responde en español, con amabilidad y claridad.
- Para saludos y preguntas sencillas, responde brevemente.
- Para problemas académicos, explica los pasos de forma
  ordenada y comprensible.
- Evita introducciones largas y repeticiones innecesarias.
- Si falta información para resolver un problema, pregunta
  únicamente por los datos que necesitas.

IMPORTANTE:
Eres el módulo conversacional de E.V.A. La aplicación tiene
calculadoras exactas en otras secciones (estadística descriptiva,
tablas y gráficas, distribución normal, regresión y práctica).
Puedes recomendarlas cuando el estudiante necesite precisión.
No afirmes que has ejecutado un cálculo en la aplicación si no
lo has hecho. Cuando un cálculo requiera precisión, muestra el
procedimiento matemático verificable.
"""

# Modelos en orden de prioridad. Si uno no existe (404) se pasa al
# siguiente; si está saturado (503) se reintenta con espera creciente.
MODELOS = ["gemini-3.8-flash", "gemini-3.1-flash-lite"]
MAX_REINTENTOS = 2

try:
    api_key = st.secrets.get("GEMINI_API_KEY", "")
except Exception:
    api_key = ""
api_key = api_key or os.getenv("GEMINI_API_KEY", "")


@st.cache_resource
def crear_cliente(clave):
    return genai.Client(api_key=clave)


client = None
if api_key:
    try:
        client = crear_cliente(api_key)
    except Exception:
        client = None


def generar_respuesta(historial):
    """Llama a Gemini con reintentos y modelo de respaldo."""
    if client is None:
        raise RuntimeError(
            "Falta GEMINI_API_KEY en los secretos de la aplicación."
        )
    ultimo_error = RuntimeError("No se obtuvo respuesta")
    for modelo in MODELOS:
        for intento in range(MAX_REINTENTOS):
            try:
                respuesta = client.models.generate_content(
                    model=modelo,
                    contents=historial,
                    config=types.GenerateContentConfig(
                        system_instruction=INSTRUCCIONES_EVA,
                        max_output_tokens=2000,
                        thinking_config=types.ThinkingConfig(
                            thinking_level="low"
                        )
                    )
                )
                if respuesta.text:
                    return respuesta.text
                ultimo_error = RuntimeError("Respuesta vacía")
            except Exception as e:
                ultimo_error = e
                mensaje = str(e)
                if "404" in mensaje or "NOT_FOUND" in mensaje:
                    break
                temporal = any(
                    c in mensaje
                    for c in ("503", "UNAVAILABLE", "429", "500",
                              "overloaded", "RESOURCE_EXHAUSTED")
                )
                if not temporal:
                    raise
                time.sleep(2 ** intento)
    raise ultimo_error


def generar_stream(historial):
    """Genera la respuesta por fragmentos (se muestra mientras se escribe)."""
    if client is None:
        raise RuntimeError(
            "Falta GEMINI_API_KEY en los secretos de la aplicación."
        )
    ultimo_error = RuntimeError("No se obtuvo respuesta")
    for modelo in MODELOS:
        for intento in range(MAX_REINTENTOS):
            emitido = False
            try:
                flujo = client.models.generate_content_stream(
                    model=modelo,
                    contents=historial,
                    config=types.GenerateContentConfig(
                        system_instruction=INSTRUCCIONES_EVA,
                        max_output_tokens=1500,
                        thinking_config=types.ThinkingConfig(
                            thinking_level="low"
                        )
                    )
                )
                for fragmento in flujo:
                    if fragmento.text:
                        emitido = True
                        yield fragmento.text
                if emitido:
                    return
                ultimo_error = RuntimeError("Respuesta vacía")
            except Exception as e:
                if emitido:
                    raise
                ultimo_error = e
                mensaje = str(e)
                if "404" in mensaje or "NOT_FOUND" in mensaje:
                    break
                temporal = any(
                    c in mensaje
                    for c in ("503", "UNAVAILABLE", "429", "500",
                              "overloaded", "RESOURCE_EXHAUSTED")
                )
                if not temporal:
                    raise
                time.sleep(2 ** intento)
    raise ultimo_error


# ==================================================
# UTILIDADES
# ==================================================
def fmt(x, d=4):
    """Formatea un número sin ceros sobrantes."""
    if x is None:
        return "—"
    if isinstance(x, (int, np.integer)):
        return str(int(x))
    x = float(x)
    if x != 0 and abs(x) < 1e-3:
        return f"{x:.3e}"
    if abs(x - round(x)) < 1e-12 and abs(x) < 1e12:
        return str(int(round(x)))
    return f"{x:.{d}f}".rstrip("0").rstrip(".")


def leer_datos(texto, minimo=1, nombre="datos"):
    """Convierte un texto en lista de números. Devuelve (datos, error)."""
    if not texto or not texto.strip():
        return None, (f"No ingresaste {nombre}. Escribe al menos "
                      f"{minimo} valor(es) numérico(s).")
    tokens = [t for t in re.split(r"[\s;,]+", texto.strip()) if t]
    valores, malos = [], []
    for t in tokens:
        try:
            v = float(t)
            if math.isnan(v) or math.isinf(v):
                raise ValueError
            valores.append(v)
        except ValueError:
            malos.append(t)
    if malos:
        return None, (
            "Hay valores que no son números: " + ", ".join(malos[:5]) +
            ". Usa punto como separador decimal (ej. 2.5) y separa los "
            "datos con comas, espacios o saltos de línea."
        )
    if len(valores) < minimo:
        return None, (f"Se necesitan al menos {minimo} datos en "
                      f"{nombre} y recibí {len(valores)}.")
    return valores, None


def lista_txt(valores, maximo=10):
    if len(valores) <= maximo:
        return ", ".join(fmt(v) for v in valores)
    return (", ".join(fmt(v) for v in valores[:6]) + ", …, " +
            ", ".join(fmt(v) for v in valores[-2:]))


def suma_txt(terminos, maximo=10):
    if len(terminos) <= maximo:
        return " + ".join(terminos)
    return " + ".join(terminos[:6]) + " + \\dots + " + \
        " + ".join(terminos[-2:])


def cdf_normal(z):
    return 0.5 * (1 + math.erf(z / math.sqrt(2)))


def pdf_normal(x, mu, sigma):
    return (np.exp(-0.5 * ((x - mu) / sigma) ** 2) /
            (sigma * math.sqrt(2 * math.pi)))


# ==================================================
# ESTADISTICA DESCRIPTIVA
# ==================================================
def calcular_desc(datos, muestral=True):
    n = len(datos)
    media = sum(datos) / n
    mediana = statistics.median(datos)
    modas = statistics.multimode(datos)
    amodal = len(modas) == len(set(datos))
    ss = sum((x - media) ** 2 for x in datos)
    gl = n - 1 if muestral else n
    var = ss / gl if gl > 0 else None
    sd = math.sqrt(var) if var is not None else None
    return {
        "n": n, "media": media, "mediana": mediana,
        "modas": [] if amodal else sorted(modas),
        "amodal": amodal, "minimo": min(datos), "maximo": max(datos),
        "rango": max(datos) - min(datos), "ss": ss, "gl": gl,
        "var": var, "sd": sd,
        "ee": (sd / math.sqrt(n)) if sd is not None else None,
    }


def texto_interpretacion(r, muestral, unidad):
    u = f" {unidad}" if unidad else ""
    lineas = []
    if r["sd"] is not None:
        a = r["media"] - r["sd"]
        b = r["media"] + r["sd"]
        lineas.append(
            f"Los datos se concentran alrededor de **{fmt(r['media'])}{u}** "
            f"y se desvían en promedio **{fmt(r['sd'])}{u}** de ese valor. "
            f"El intervalo x̄ ± s va de {fmt(a)} a {fmt(b)}{u}."
        )
        if r["media"] != 0:
            cv = r["sd"] / abs(r["media"]) * 100
            if cv < 10:
                nivel = "baja (los datos son muy consistentes)"
            elif cv < 30:
                nivel = "moderada"
            else:
                nivel = "alta (los datos están muy dispersos)"
            lineas.append(
                f"El coeficiente de variación es {fmt(cv, 2)} %, "
                f"una variabilidad {nivel}."
            )
        if abs(r["media"] - r["mediana"]) > 0.1 * r["sd"]:
            lado = "derecha" if r["media"] > r["mediana"] else "izquierda"
            lineas.append(
                f"La media y la mediana difieren; la distribución "
                f"podría tener cierta asimetría hacia la {lado}."
            )
        else:
            lineas.append(
                "La media y la mediana son cercanas, lo que sugiere "
                "una distribución aproximadamente simétrica."
            )
    if muestral:
        lineas.append(
            "Se usó la **desviación estándar muestral** (divide entre "
            "n − 1) porque los datos se consideran una muestra de un "
            "conjunto mayor de mediciones posibles."
        )
    else:
        lineas.append(
            "Se usó la **desviación estándar poblacional** (divide "
            "entre n) porque los datos representan a toda la población."
        )
    return lineas


def mostrar_desc(datos, muestral=True, unidad="", comparar=False):
    n = len(datos)
    r = calcular_desc(datos, muestral)
    u = f" {unidad}" if unidad else ""
    sim = "s" if muestral else "\\sigma"
    nombre_sd = "muestral" if muestral else "poblacional"

    if muestral and n < 2:
        st.warning("Con un solo dato no se puede calcular la desviación "
                   "estándar muestral (n − 1 = 0). Agrega más mediciones.")

    filas = [
        ("n (cantidad de datos)", str(n)),
        ("Media", fmt(r["media"]) + u),
        ("Mediana", fmt(r["mediana"]) + u),
        ("Moda", "No hay moda (todos los valores son distintos)"
         if r["amodal"] else ", ".join(fmt(m) for m in r["modas"]) + u),
        ("Mínimo / Máximo", f"{fmt(r['minimo'])} / {fmt(r['maximo'])}{u}"),
        ("Rango", fmt(r["rango"]) + u),
        (f"Varianza {nombre_sd}", fmt(r["var"]) +
         (f" {unidad}²" if unidad and r["var"] is not None else "")),
        (f"Desviación estándar {nombre_sd}", fmt(r["sd"]) +
         (u if r["sd"] is not None else "")),
    ]
    st.markdown("#### Resultados")
    st.dataframe(pd.DataFrame(filas, columns=["Medida", "Valor"]),
                 hide_index=True)

    st.markdown("#### Procedimiento")

    # 1. Media
    st.markdown("**1) Media aritmética**")
    terminos = [fmt(x) for x in datos]
    st.latex(r"\bar{x}=\frac{\sum x_i}{n}=\frac{" + suma_txt(terminos) +
             "}{" + str(n) + "}=\\frac{" + fmt(sum(datos)) + "}{" +
             str(n) + "}=" + fmt(r["media"]) +
             (r"\ \text{" + unidad + "}" if unidad else ""))

    # 2. Mediana
    st.markdown("**2) Mediana**")
    orden = sorted(datos)
    st.write("Datos ordenados: " + lista_txt(orden))
    if n % 2 == 1:
        pos = (n + 1) // 2
        st.write(f"n = {n} es impar: la mediana es el dato de la "
                 f"posición (n+1)/2 = {pos}.")
    else:
        p1, p2 = n // 2, n // 2 + 1
        st.write(f"n = {n} es par: la mediana es el promedio de los "
                 f"datos en las posiciones {p1} y {p2}: "
                 f"({fmt(orden[p1 - 1])} + {fmt(orden[p2 - 1])}) / 2.")
    st.latex(r"\text{Mediana}=" + fmt(r["mediana"]))

    # 3. Moda
    st.markdown("**3) Moda**")
    if r["amodal"]:
        st.write("Ningún valor se repite, por lo tanto no hay moda.")
    else:
        veces = datos.count(r["modas"][0])
        st.write("Valor(es) que más se repiten: "
                 + ", ".join(fmt(m) for m in r["modas"])
                 + f" (aparece {veces} veces).")

    # 4. Rango
    st.markdown("**4) Rango**")
    st.latex(r"R=x_{max}-x_{min}=" + fmt(r["maximo"]) + "-" +
             (fmt(r["minimo"]) if r["minimo"] >= 0
              else "(" + fmt(r["minimo"]) + ")") + "=" + fmt(r["rango"]))

    # 5. Varianza y desviación estándar
    st.markdown(f"**5) Varianza y desviación estándar {nombre_sd}**")
    divisor = "n-1" if muestral else "n"
    if r["var"] is not None:
        sq = ["(" + fmt(x) + "-" + fmt(r["media"]) + ")^2" for x in datos]
        st.latex(sim + r"^2=\frac{\sum (x_i-\bar{x})^2}{" + divisor +
                 r"}=\frac{" + suma_txt(sq) + "}{" + str(r["gl"]) +
                 "}=\\frac{" + fmt(r["ss"]) + "}{" + str(r["gl"]) +
                 "}=" + fmt(r["var"]))
        st.latex(sim + r"=\sqrt{" + sim + "^2}=\\sqrt{" +
                 fmt(r["var"]) + "}=" + fmt(r["sd"]) +
                 (r"\ \text{" + unidad + "}" if unidad else ""))
        with st.expander("Ver tabla de desviaciones"):
            tabla = pd.DataFrame({
                "xᵢ": [fmt(x) for x in datos],
                "xᵢ − x̄": [fmt(x - r["media"]) for x in datos],
                "(xᵢ − x̄)²": [fmt((x - r["media"]) ** 2) for x in datos],
            })
            st.dataframe(tabla, hide_index=True)
    else:
        st.info("No se puede calcular con un solo dato.")

    # 6. Incertidumbre
    if muestral and r["ee"] is not None:
        st.markdown("**6) Resultado de la medición (datos experimentales)**")
        st.latex(r"u=\frac{s}{\sqrt{n}}=\frac{" + fmt(r["sd"]) +
                 r"}{\sqrt{" + str(n) + "}}=" + fmt(r["ee"]))
        st.success(
            f"Resultado: x̄ ± s/√n = ({fmt(r['media'])} ± "
            f"{fmt(r['ee'])}){u}"
        )

    if comparar and n >= 2:
        r2 = calcular_desc(datos, not muestral)
        otro = "poblacional" if muestral else "muestral"
        st.info(
            f"Comparación: la desviación estándar {otro} sería "
            f"{fmt(r2['sd'])}{u}, frente a {fmt(r['sd'])}{u} de la "
            f"{nombre_sd}. La muestral es mayor porque divide entre "
            f"n − 1, lo que corrige la subestimación al trabajar con "
            f"una muestra."
        )

    st.markdown("#### Interpretación")
    for linea in texto_interpretacion(r, muestral, unidad):
        st.write("• " + linea)
    return r


# ==================================================
# TABLAS DE FRECUENCIA Y GRAFICAS
# ==================================================
def mostrar_frecuencias(datos, k=0, unidad=""):
    n = len(datos)
    if len(set(datos)) < 2:
        st.warning("Todos los datos son iguales; se necesitan al menos "
                   "dos valores distintos para armar intervalos.")
        return
    if n < 4:
        st.warning("Se recomiendan al menos 4 datos para una tabla de "
                   "frecuencias útil.")
    if k <= 0:
        k = int(math.ceil(1 + 3.322 * math.log10(n)))
        st.caption(f"Número de clases por la regla de Sturges: "
                   f"k = 1 + 3.322·log₁₀({n}) ≈ {k}")
    mn, mx = min(datos), max(datos)
    ancho = (mx - mn) / k
    bordes = [mn + i * ancho for i in range(k + 1)]
    conteos, _ = np.histogram(datos, bins=bordes)

    st.write(f"Rango = {fmt(mx)} − {fmt(mn)} = {fmt(mx - mn)}; "
             f"ancho de clase = {fmt(mx - mn)} / {k} = {fmt(ancho)}")

    filas, acum = [], 0
    for i in range(k):
        fi = int(conteos[i])
        acum += fi
        cierre = "]" if i == k - 1 else ")"
        filas.append({
            "Intervalo": f"[{fmt(bordes[i])}, {fmt(bordes[i + 1])}{cierre}",
            "Marca de clase": fmt((bordes[i] + bordes[i + 1]) / 2),
            "fi": fi,
            "fr": fmt(fi / n),
            "%": fmt(fi / n * 100, 2),
            "Fi": acum,
        })
    st.dataframe(pd.DataFrame(filas), hide_index=True)

    fig, ax = plt.subplots(1, 2, figsize=(9, 3.6))
    ax[0].hist(datos, bins=bordes, edgecolor="white", color="#2471A3")
    ax[0].set_title("Histograma")
    ax[0].set_xlabel("Valor" + (f" ({unidad})" if unidad else ""))
    ax[0].set_ylabel("Frecuencia")
    ax[1].boxplot(datos, vert=True)
    ax[1].set_title("Diagrama de caja")
    ax[1].set_ylabel("Valor" + (f" ({unidad})" if unidad else ""))
    fig.tight_layout()
    st.pyplot(fig)
    plt.close(fig)

    q1, q3 = np.percentile(datos, [25, 75])
    st.write(f"Cuartiles: Q1 = {fmt(q1)}, Q3 = {fmt(q3)}, "
             f"rango intercuartílico = {fmt(q3 - q1)}.")
    st.write("• Interpretación: las barras más altas indican los "
             "intervalos donde se concentran los datos; la caja contiene "
             "el 50 % central de las observaciones.")


# ==================================================
# DISTRIBUCION NORMAL
# ==================================================
M_MENOR = "P(X < a)"
M_MAYOR = "P(X > a)"
M_ENTRE = "P(a < X < b)"
M_Z = "Puntaje Z de un valor"
MODOS_NORMAL = [M_MENOR, M_MAYOR, M_ENTRE, M_Z]


def mostrar_normal(mu, sigma, modo, a, b=None, unidad=""):
    if sigma <= 0:
        st.error("La desviación estándar σ debe ser mayor que 0.")
        return
    u = f" {unidad}" if unidad else ""
    if modo == M_ENTRE and (b is None or a >= b):
        st.error("Para P(a < X < b) se necesita que a sea menor que b.")
        return

    st.latex(r"Z=\frac{X-\mu}{\sigma}")
    za = (a - mu) / sigma
    st.latex(r"z_a=\frac{" + fmt(a) + "-" + (fmt(mu) if mu >= 0
             else "(" + fmt(mu) + ")") + "}{" + fmt(sigma) + "}=" +
             fmt(za, 4))

    x = np.linspace(mu - 4 * sigma, mu + 4 * sigma, 500)
    y = pdf_normal(x, mu, sigma)
    fig, ax = plt.subplots(figsize=(8, 3.4))
    ax.plot(x, y, color="#17365D")
    ax.set_xlabel("X" + (f" ({unidad})" if unidad else ""))
    ax.set_ylabel("Densidad")

    if modo == M_MENOR:
        p = cdf_normal(za)
        st.latex(r"P(X<" + fmt(a) + r")=P(Z<" + fmt(za, 2) +
                 r")=\Phi(" + fmt(za, 2) + ")=" + fmt(p, 4))
        m = x <= a
        resultado = (f"P(X < {fmt(a)}{u}) = {fmt(p, 4)} "
                     f"({fmt(p * 100, 2)} %)")
    elif modo == M_MAYOR:
        p = 1 - cdf_normal(za)
        st.latex(r"P(X>" + fmt(a) + r")=1-\Phi(" + fmt(za, 2) +
                 ")=1-" + fmt(cdf_normal(za), 4) + "=" + fmt(p, 4))
        m = x >= a
        resultado = (f"P(X > {fmt(a)}{u}) = {fmt(p, 4)} "
                     f"({fmt(p * 100, 2)} %)")
    elif modo == M_ENTRE:
        zb = (b - mu) / sigma
        st.latex(r"z_b=\frac{" + fmt(b) + "-" + (fmt(mu) if mu >= 0
                 else "(" + fmt(mu) + ")") + "}{" + fmt(sigma) + "}=" +
                 fmt(zb, 4))
        p = cdf_normal(zb) - cdf_normal(za)
        st.latex(r"P(" + fmt(a) + "<X<" + fmt(b) + ")=\\Phi(" +
                 fmt(zb, 2) + ")-\\Phi(" + fmt(za, 2) + ")=" +
                 fmt(cdf_normal(zb), 4) + "-" + fmt(cdf_normal(za), 4) +
                 "=" + fmt(p, 4))
        m = (x >= a) & (x <= b)
        ax.axvline(b, color="#C0392B", linestyle="--")
        resultado = (f"P({fmt(a)}{u} < X < {fmt(b)}{u}) = {fmt(p, 4)} "
                     f"({fmt(p * 100, 2)} %)")
    else:
        p = None
        m = None
        resultado = (f"z = {fmt(za, 4)}: el valor {fmt(a)}{u} está a "
                     f"{fmt(abs(za), 2)} desviaciones estándar "
                     f"{'por encima' if za > 0 else 'por debajo'} de la "
                     f"media." if za != 0 else
                     "z = 0: el valor coincide con la media.")

    if m is not None:
        ax.fill_between(x, y, where=m, color="#2471A3", alpha=0.35)
    ax.axvline(a, color="#C0392B", linestyle="--")
    ax.axvline(mu, color="gray", linestyle=":")
    fig.tight_layout()
    st.pyplot(fig)
    plt.close(fig)

    st.success("Respuesta: " + resultado)
    if p is not None:
        st.caption("Φ(z) = ½·[1 + erf(z/√2)]; el mismo valor se obtiene "
                   "con la tabla normal estándar.")
        st.write(f"• Interpretación: si X sigue una distribución normal "
                 f"con μ = {fmt(mu)}{u} y σ = {fmt(sigma)}{u}, "
                 f"aproximadamente el {fmt(p * 100, 1)} % de los valores "
                 f"cae en la región sombreada.")
    else:
        if abs(za) > 2:
            st.write("• Interpretación: |z| > 2 indica un valor poco "
                     "común (fuera del ≈ 95 % central).")
        else:
            st.write("• Interpretación: |z| ≤ 2 indica un valor dentro "
                     "de lo habitual (dentro del ≈ 95 % central).")


# ==================================================
# CORRELACION Y REGRESION
# ==================================================
def calcular_regresion(x, y):
    n = len(x)
    mx, my = sum(x) / n, sum(y) / n
    sxx = sum((xi - mx) ** 2 for xi in x)
    syy = sum((yi - my) ** 2 for yi in y)
    sxy = sum((xi - mx) * (yi - my) for xi, yi in zip(x, y))
    if sxx == 0:
        return None
    m = sxy / sxx
    b = my - m * mx
    r = sxy / math.sqrt(sxx * syy) if syy > 0 else None
    return {"n": n, "mx": mx, "my": my, "sxx": sxx, "syy": syy,
            "sxy": sxy, "m": m, "b": b, "r": r}


def texto_fuerza(r):
    ar = abs(r)
    if ar >= 0.9:
        fuerza = "muy fuerte"
    elif ar >= 0.7:
        fuerza = "fuerte"
    elif ar >= 0.4:
        fuerza = "moderada"
    elif ar >= 0.2:
        fuerza = "débil"
    else:
        fuerza = "muy débil o nula"
    sentido = "positiva" if r > 0 else "negativa"
    return fuerza, sentido


def mostrar_regresion(x, y, x_pred=None, nx="x", ny="y"):
    if len(x) != len(y):
        st.error(f"Las listas deben tener la misma cantidad de datos: "
                 f"X tiene {len(x)} y Y tiene {len(y)}.")
        return
    if len(x) < 2:
        st.error("Se necesitan al menos 2 pares de datos.")
        return
    if len(x) < 3:
        st.warning("Con solo 2 puntos la recta siempre ajusta "
                   "perfectamente; usa 3 o más para un análisis real.")
    r = calcular_regresion(x, y)
    if r is None:
        st.error("Todos los valores de X son iguales: no se puede "
                 "ajustar una recta (Σ(x − x̄)² = 0).")
        return

    st.latex(r"\bar{x}=" + fmt(r["mx"]) + r",\quad \bar{y}=" +
             fmt(r["my"]))
    st.latex(r"m=\frac{\sum (x_i-\bar{x})(y_i-\bar{y})}"
             r"{\sum (x_i-\bar{x})^2}=\frac{" + fmt(r["sxy"]) + "}{" +
             fmt(r["sxx"]) + "}=" + fmt(r["m"]))
    st.latex(r"b=\bar{y}-m\,\bar{x}=" + fmt(r["my"]) + "-(" +
             fmt(r["m"]) + ")(" + fmt(r["mx"]) + ")=" + fmt(r["b"]))
    signo = "+" if r["b"] >= 0 else "-"
    st.latex(r"\hat{y}=" + fmt(r["m"]) + "x" + signo + fmt(abs(r["b"])))

    if r["r"] is not None:
        st.latex(r"r=\frac{\sum (x_i-\bar{x})(y_i-\bar{y})}"
                 r"{\sqrt{\sum (x_i-\bar{x})^2\,\sum (y_i-\bar{y})^2}}"
                 r"=\frac{" + fmt(r["sxy"]) + r"}{\sqrt{" +
                 fmt(r["sxx"]) + r"\cdot " + fmt(r["syy"]) + "}}=" +
                 fmt(r["r"]))
        st.latex(r"r^2=" + fmt(r["r"] ** 2))
    else:
        st.warning("Todos los valores de Y son iguales: r no está "
                   "definido (la pendiente es 0).")

    with st.expander("Ver tabla de cálculo"):
        tabla = pd.DataFrame({
            nx: [fmt(v) for v in x],
            ny: [fmt(v) for v in y],
            f"{nx} − x̄": [fmt(v - r["mx"]) for v in x],
            f"{ny} − ȳ": [fmt(v - r["my"]) for v in y],
            "Producto": [fmt((a - r["mx"]) * (c - r["my"]))
                         for a, c in zip(x, y)],
        })
        st.dataframe(tabla, hide_index=True)

    fig, ax = plt.subplots(figsize=(8, 3.6))
    ax.scatter(x, y, color="#2471A3", label="Datos", zorder=3)
    xs = np.linspace(min(x), max(x) if x_pred is None
                     else max(max(x), x_pred), 100)
    ax.plot(xs, r["m"] * xs + r["b"], color="#C0392B",
            label="Recta ajustada")
    if x_pred is not None:
        ax.scatter([x_pred], [r["m"] * x_pred + r["b"]],
                   color="green", marker="*", s=160, zorder=4,
                   label="Predicción")
    ax.set_xlabel(nx)
    ax.set_ylabel(ny)
    ax.legend()
    ax.grid(alpha=0.3)
    fig.tight_layout()
    st.pyplot(fig)
    plt.close(fig)

    if x_pred is not None:
        yp = r["m"] * x_pred + r["b"]
        st.success(f"Predicción: para {nx} = {fmt(x_pred)}, "
                   f"ŷ = {fmt(r['m'])}({fmt(x_pred)}) "
                   f"{signo} {fmt(abs(r['b']))} = {fmt(yp)}")
        if x_pred < min(x) or x_pred > max(x):
            st.warning("El valor está fuera del rango de los datos "
                       "(extrapolación): la predicción es menos confiable.")

    st.markdown("#### Interpretación")
    st.write(f"• Por cada unidad que aumenta {nx}, {ny} "
             f"{'aumenta' if r['m'] > 0 else 'disminuye'} en promedio "
             f"{fmt(abs(r['m']))} unidades.")
    if r["r"] is not None:
        fuerza, sentido = texto_fuerza(r["r"])
        st.write(f"• r = {fmt(r['r'], 4)}: correlación lineal {fuerza} "
                 f"y {sentido}. El modelo explica el "
                 f"{fmt(r['r'] ** 2 * 100, 1)} % de la variación de {ny}.")
        st.write("• Correlación no implica causalidad.")


# ==================================================
# EJEMPLOS RESUELTOS (10)
# ==================================================
EJEMPLOS = [
    {"titulo": "1. Corriente eléctrica (prueba del proyecto)",
     "enunciado": "Con mediciones de corriente (A): 2.1, 2.3, 2.2, 2.4, "
                  "2.0; calcula la media y la desviación estándar "
                  "muestral e interpreta.",
     "tipo": "desc", "datos": [2.1, 2.3, 2.2, 2.4, 2.0],
     "muestral": True, "unidad": "A"},
    {"titulo": "2. Tiempo de caída libre",
     "enunciado": "Un cronómetro registró estos tiempos de caída (s): "
                  "0.45, 0.47, 0.44, 0.46, 0.48, 0.45. Calcula las "
                  "medidas descriptivas y el resultado de la medición.",
     "tipo": "desc", "datos": [0.45, 0.47, 0.44, 0.46, 0.48, 0.45],
     "muestral": True, "unidad": "s"},
    {"titulo": "3. Calificaciones de todo un grupo (población)",
     "enunciado": "Las calificaciones de los 8 estudiantes de un grupo "
                  "son: 70, 85, 90, 85, 60, 75, 85, 95. Calcula media, "
                  "mediana, moda, rango y desviación poblacional.",
     "tipo": "desc", "datos": [70, 85, 90, 85, 60, 75, 85, 95],
     "muestral": False, "unidad": "pts"},
    {"titulo": "4. Varilla: desviación muestral vs poblacional",
     "enunciado": "Se midió la longitud de una varilla (cm): 25.1, 25.3, "
                  "24.9, 25.0, 25.2, 25.4. Calcula s y compárala con σ "
                  "para explicar la diferencia.",
     "tipo": "desc", "datos": [25.1, 25.3, 24.9, 25.0, 25.2, 25.4],
     "muestral": True, "unidad": "cm", "comparar": True},
    {"titulo": "5. Tabla de frecuencias e histograma",
     "enunciado": "Con los datos 12, 15, 15, 18, 20, 22, 22, 22, 25, 28, "
                  "30, 31 construye una tabla de frecuencias con 4 "
                  "clases y su histograma.",
     "tipo": "frec",
     "datos": [12, 15, 15, 18, 20, 22, 22, 22, 25, 28, 30, 31], "k": 4},
    {"titulo": "6. Resistores: P(X > 108 Ω)",
     "enunciado": "La resistencia de cierto lote de resistores sigue una "
                  "normal con μ = 100 Ω y σ = 5 Ω. ¿Qué probabilidad "
                  "hay de que un resistor supere 108 Ω?",
     "tipo": "normal", "mu": 100, "sigma": 5, "modo": M_MAYOR,
     "a": 108, "unidad": "Ω"},
    {"titulo": "7. Estaturas: P(160 < X < 180)",
     "enunciado": "Las estaturas de un grupo son normales con μ = 170 cm "
                  "y σ = 8 cm. ¿Qué porcentaje mide entre 160 y 180 cm?",
     "tipo": "normal", "mu": 170, "sigma": 8, "modo": M_ENTRE,
     "a": 160, "b": 180, "unidad": "cm"},
    {"titulo": "8. Puntaje Z de una calificación",
     "enunciado": "En un examen, μ = 70 y σ = 8. Calcula el puntaje Z "
                  "de un estudiante que obtuvo 82 e interpreta.",
     "tipo": "normal", "mu": 70, "sigma": 8, "modo": M_Z,
     "a": 82, "unidad": "pts"},
    {"titulo": "9. Horas de estudio vs calificación",
     "enunciado": "Horas de estudio (X): 1, 2, 3, 4, 5, 6. "
                  "Calificación (Y): 55, 60, 64, 70, 75, 82. Calcula la "
                  "recta de regresión, r y predice la nota con 7 horas.",
     "tipo": "regr", "x": [1, 2, 3, 4, 5, 6],
     "y": [55, 60, 64, 70, 75, 82], "x_pred": 7,
     "nx": "Horas", "ny": "Nota"},
    {"titulo": "10. Ley de Ohm: voltaje vs corriente",
     "enunciado": "Se midió la corriente I (A) para distintos voltajes "
                  "V (V): V = 1, 2, 3, 4, 5; I = 0.11, 0.19, 0.32, 0.39, "
                  "0.52. Ajusta I en función de V y predice I a 6 V. "
                  "La resistencia es R = 1/m.",
     "tipo": "regr", "x": [1, 2, 3, 4, 5],
     "y": [0.11, 0.19, 0.32, 0.39, 0.52], "x_pred": 6,
     "nx": "V (V)", "ny": "I (A)"},
]


def mostrar_ejemplo(e):
    st.markdown("**Enunciado:** " + e["enunciado"])
    st.markdown("---")
    if e["tipo"] == "desc":
        mostrar_desc(e["datos"], e["muestral"], e.get("unidad", ""),
                     e.get("comparar", False))
    elif e["tipo"] == "frec":
        mostrar_frecuencias(e["datos"], e.get("k", 0))
    elif e["tipo"] == "normal":
        mostrar_normal(e["mu"], e["sigma"], e["modo"], e["a"],
                       e.get("b"), e.get("unidad", ""))
    elif e["tipo"] == "regr":
        mostrar_regresion(e["x"], e["y"], e.get("x_pred"),
                          e.get("nx", "x"), e.get("ny", "y"))
        if e["nx"].startswith("V"):
            r = calcular_regresion(e["x"], e["y"])
            if r and r["m"] != 0:
                st.info(f"Resistencia: R = 1/m = 1/{fmt(r['m'])} = "
                        f"{fmt(1 / r['m'], 3)} Ω")


# ==================================================
# GENERADOR DE PRACTICAS CON RETROALIMENTACION
# ==================================================
TEMAS = [
    "Media aritmética",
    "Mediana",
    "Desviación estándar muestral",
    "Puntaje Z",
    "Probabilidad normal P(X < x)",
    "Pendiente de la recta de regresión",
    "Coeficiente de correlación r",
]


def generar_ejercicio(tema):
    ej = {"id": random.randint(1, 10 ** 9), "tema": tema,
          "alternativas": [], "contado": False}

    if tema == "Media aritmética":
        n = random.randint(5, 8)
        d = [random.randint(10, 50) for _ in range(n)]
        v = sum(d) / n
        ej.update(
            enunciado="Calcula la **media aritmética** de: " +
                      ", ".join(map(str, d)),
            respuesta=v, tol=0.01,
            solucion=f"$\\bar{{x}}=\\frac{{{sum(d)}}}{{{n}}}={fmt(v)}$")

    elif tema == "Mediana":
        n = random.choice([5, 6, 7, 8])
        d = random.sample(range(5, 60), n)
        o = sorted(d)
        v = statistics.median(d)
        ej.update(
            enunciado="Calcula la **mediana** de: " +
                      ", ".join(map(str, d)),
            respuesta=v, tol=0.01,
            solucion="Ordenados: " + ", ".join(map(str, o)) +
                     f". Mediana = {fmt(v)}.")
        sin_orden = d[n // 2] if n % 2 else (d[n // 2 - 1] + d[n // 2]) / 2
        if abs(sin_orden - v) > 0.01:
            ej["alternativas"].append(
                (sin_orden, "Tomaste el valor central sin ordenar "
                            "primero los datos de menor a mayor."))

    elif tema == "Desviación estándar muestral":
        n = random.randint(5, 6)
        d = [random.randint(10, 40) for _ in range(n)]
        r = calcular_desc(d, True)
        rp = calcular_desc(d, False)
        ej.update(
            enunciado="Calcula la **desviación estándar muestral** de: " +
                      ", ".join(map(str, d)) +
                      " (redondea a 2 decimales).",
            respuesta=r["sd"], tol=0.011,
            solucion=(f"$\\bar{{x}}={fmt(r['media'])}$; "
                      f"$\\sum(x_i-\\bar{{x}})^2={fmt(r['ss'])}$; "
                      f"$s^2=\\frac{{{fmt(r['ss'])}}}{{{n - 1}}}="
                      f"{fmt(r['var'])}$; $s={fmt(r['sd'])}$"))
        ej["alternativas"].append(
            (rp["sd"], "Dividiste entre n en lugar de n − 1 "
                       "(eso es la desviación poblacional)."))
        ej["alternativas"].append(
            (r["var"], "Diste la varianza; falta sacar la raíz "
                       "cuadrada."))

    elif tema == "Puntaje Z":
        mu = random.randint(50, 80)
        sg = random.randint(4, 10)
        z = random.choice([-2, -1.5, -1, -0.5, 0.5, 1, 1.5, 2, 2.5])
        x = mu + sg * z
        v = (x - mu) / sg
        ej.update(
            enunciado=(f"Una variable tiene μ = {mu} y σ = {sg}. "
                       f"Calcula el **puntaje Z** de X = {fmt(x)}."),
            respuesta=v, tol=0.011,
            solucion=(f"$z=\\frac{{x-\\mu}}{{\\sigma}}="
                      f"\\frac{{{fmt(x)}-{mu}}}{{{sg}}}={fmt(v)}$"))
        ej["alternativas"].append(
            (-v, "El signo está invertido: la fórmula es (x − μ)/σ."))
        ej["alternativas"].append(
            (x - mu, "Olvidaste dividir entre σ."))

    elif tema == "Probabilidad normal P(X < x)":
        mu = random.randint(50, 100)
        sg = random.randint(4, 12)
        z = random.choice([-1.5, -1, -0.5, 0.5, 1, 1.5, 2])
        x = mu + sg * z
        zz = (x - mu) / sg
        p = cdf_normal(zz)
        ej.update(
            enunciado=(f"X sigue una normal con μ = {mu} y σ = {sg}. "
                       f"Calcula **P(X < {fmt(x)})** (como decimal, "
                       f"4 decimales)."),
            respuesta=p, tol=0.005,
            solucion=(f"$z=\\frac{{{fmt(x)}-{mu}}}{{{sg}}}={fmt(zz)}$; "
                      f"$P(X<{fmt(x)})=\\Phi({fmt(zz)})={fmt(p)}$"))
        ej["alternativas"].append(
            (1 - p, "Calculaste el área a la derecha, P(X > x). "
                    "Se pedía P(X < x)."))

    elif tema in ("Pendiente de la recta de regresión",
                  "Coeficiente de correlación r"):
        n = random.randint(5, 6)
        x = list(range(1, n + 1))
        m0 = random.randint(2, 6)
        b0 = random.randint(10, 40)
        y = [b0 + m0 * xi + random.randint(-3, 3) for xi in x]
        r = calcular_regresion(x, y)
        datos_txt = (f"X: {', '.join(map(str, x))}; "
                     f"Y: {', '.join(map(str, y))}")
        if tema.startswith("Pendiente"):
            ej.update(
                enunciado=("Calcula la **pendiente m** de la recta de "
                           f"regresión con los datos {datos_txt} "
                           "(2 decimales)."),
                respuesta=r["m"], tol=0.011,
                solucion=(f"$\\bar{{x}}={fmt(r['mx'])}$, "
                          f"$\\bar{{y}}={fmt(r['my'])}$; "
                          f"$m=\\frac{{{fmt(r['sxy'])}}}"
                          f"{{{fmt(r['sxx'])}}}={fmt(r['m'])}$"))
            ej["alternativas"].append(
                (r["b"], "Diste el intercepto b; se pedía la "
                         "pendiente m."))
        else:
            ej.update(
                enunciado=("Calcula el **coeficiente de correlación r** "
                           f"con los datos {datos_txt} (3 decimales)."),
                respuesta=r["r"], tol=0.011,
                solucion=(f"$r=\\frac{{{fmt(r['sxy'])}}}"
                          f"{{\\sqrt{{{fmt(r['sxx'])}\\cdot"
                          f"{fmt(r['syy'])}}}}}={fmt(r['r'])}$"))
            ej["alternativas"].append(
                (r["r"] ** 2, "Diste r²; falta sacar la raíz "
                              "cuadrada para obtener r."))

    # Solo se conservan los errores típicos que se distinguen de la
    # respuesta correcta (si quedan muy cerca, serían ambiguos).
    ej["alternativas"] = [
        (alt, msg) for alt, msg in ej["alternativas"]
        if alt is not None and abs(alt - ej["respuesta"]) > 2 * ej["tol"]
    ]
    return ej


def evaluar_respuesta(ej, texto):
    """Devuelve (ok, mensaje)."""
    if not texto or not texto.strip():
        return None, "Escribe un número antes de comprobar."
    try:
        v = float(texto.strip().replace(",", "."))
    except ValueError:
        return None, ("Eso no parece un número. Escribe solo la cifra, "
                      "por ejemplo 12.5")
    if abs(v - ej["respuesta"]) <= ej["tol"]:
        return True, "¡Correcto! 🎉 Tu respuesta coincide con la solución."
    for alt, msg in ej["alternativas"]:
        if alt is not None and abs(v - alt) <= ej["tol"]:
            return False, "Casi: " + msg
    return False, ("No coincide. Revisa tu procedimiento paso a paso; "
                   "abajo puedes ver la solución.")


def seccion_practica():
    st.subheader("🎯 Práctica con retroalimentación")
    st.write("Elige un tema, genera un ejercicio nuevo, escribe tu "
             "respuesta y E.V.A. la revisará.")

    if "ej" not in st.session_state:
        st.session_state.ej = None
        st.session_state.aciertos = 0
        st.session_state.intentos = 0
        st.session_state.resultado = None

    tema = st.selectbox("Tema", TEMAS)
    if st.button("🎲 Generar ejercicio nuevo"):
        st.session_state.ej = generar_ejercicio(tema)
        st.session_state.resultado = None

    ej = st.session_state.ej
    if ej is None:
        st.info("Pulsa «Generar ejercicio nuevo» para comenzar.")
    else:
        st.markdown(f"**Tema:** {ej['tema']}")
        st.markdown(ej["enunciado"])
        resp = st.text_input("Tu respuesta", key=f"resp_{ej['id']}")
        if st.button("✅ Comprobar"):
            ok, msg = evaluar_respuesta(ej, resp)
            st.session_state.resultado = (ok, msg)
            if ok is not None and not ej["contado"]:
                ej["contado"] = True
                st.session_state.intentos += 1
                if ok:
                    st.session_state.aciertos += 1

        res = st.session_state.resultado
        if res is not None:
            ok, msg = res
            if ok is True:
                st.success(msg)
            elif ok is False:
                st.error(msg)
            else:
                st.warning(msg)
        with st.expander("Ver solución paso a paso"):
            st.markdown(ej["solucion"])
            st.markdown(f"**Respuesta final:** {fmt(ej['respuesta'])}")

    st.caption(f"Puntaje: {st.session_state.aciertos} correctos de "
               f"{st.session_state.intentos} ejercicios intentados.")


# ==================================================
# SECCIONES DE LA APLICACION
# ==================================================
def seccion_descriptiva():
    st.subheader("📐 Estadística descriptiva y datos experimentales")
    st.write("Ingresa tus mediciones separadas por comas, espacios o "
             "saltos de línea (usa punto decimal).")
    texto = st.text_area("Datos", value="2.1, 2.3, 2.2, 2.4, 2.0",
                         key="desc_datos")
    c1, c2 = st.columns(2)
    tipo = c1.radio("Tipo de desviación estándar",
                    ["Muestral (n − 1)", "Poblacional (n)"],
                    key="desc_tipo")
    unidad = c2.text_input("Unidad (opcional)", value="A",
                           key="desc_unidad")
    datos, err = leer_datos(texto, minimo=1)
    if err:
        st.error(err)
        return
    muestral = tipo.startswith("Muestral")
    r = mostrar_desc(datos, muestral, unidad.strip(), comparar=True)

    st.markdown("---")
    if st.button("🤖 Pedir interpretación ampliada a E.V.A. (IA)"):
        if client is None:
            st.warning("La IA no está configurada (falta GEMINI_API_KEY).")
            return
        pregunta = (
            f"Datos: {lista_txt(datos, 30)} {unidad}. Media = "
            f"{fmt(r['media'])}, mediana = {fmt(r['mediana'])}, "
            f"desviación estándar {'muestral' if muestral else 'poblacional'}"
            f" = {fmt(r['sd'])}. Interpreta estos resultados en un "
            f"contexto de mediciones físicas, en máximo 6 líneas."
        )
        with st.spinner("E.V.A. está redactando la interpretación..."):
            try:
                st.info(generar_respuesta(
                    [{"role": "user", "parts": [{"text": pregunta}]}]))
            except Exception as e:
                st.error("No se pudo obtener la interpretación de la IA. "
                         "Los resultados calculados arriba siguen siendo "
                         "válidos.")
                st.caption(f"Detalle técnico: {type(e).__name__}: {e}")


def seccion_tablas():
    st.subheader("📊 Tablas de frecuencia y gráficas")
    texto = st.text_area(
        "Datos", key="frec_datos",
        value="12, 15, 15, 18, 20, 22, 22, 22, 25, 28, 30, 31")
    c1, c2 = st.columns(2)
    k = c1.number_input("Número de clases (0 = automático)", min_value=0,
                        max_value=30, value=0, step=1, key="frec_k")
    unidad = c2.text_input("Unidad (opcional)", key="frec_unidad")
    datos, err = leer_datos(texto, minimo=2)
    if err:
        st.error(err)
        return
    mostrar_frecuencias(datos, int(k), unidad.strip())


def seccion_normal():
    st.subheader("🔔 Probabilidad y distribución normal")
    c1, c2 = st.columns(2)
    mu = c1.number_input("Media μ", value=100.0, key="n_mu")
    sigma = c2.number_input("Desviación estándar σ", value=5.0,
                            key="n_sigma")
    modo = st.selectbox("¿Qué deseas calcular?", MODOS_NORMAL,
                        key="n_modo")
    c3, c4 = st.columns(2)
    a = c3.number_input("Valor a" if modo != M_Z else "Valor X",
                        value=108.0, key="n_a")
    b = None
    if modo == M_ENTRE:
        b = c4.number_input("Valor b", value=115.0, key="n_b")
    unidad = st.text_input("Unidad (opcional)", key="n_unidad")
    mostrar_normal(mu, sigma, modo, a, b, unidad.strip())


def seccion_regresion():
    st.subheader("📈 Correlación y regresión lineal")
    c1, c2 = st.columns(2)
    tx = c1.text_area("Valores de X", value="1, 2, 3, 4, 5, 6",
                      key="r_x")
    ty = c2.text_area("Valores de Y", value="55, 60, 64, 70, 75, 82",
                      key="r_y")
    c3, c4, c5 = st.columns(3)
    nx = c3.text_input("Nombre de X", value="x", key="r_nx")
    ny = c4.text_input("Nombre de Y", value="y", key="r_ny")
    pred = c5.text_input("Predecir para X = (opcional)", key="r_pred")
    x, ex = leer_datos(tx, minimo=2, nombre="X")
    y, ey = leer_datos(ty, minimo=2, nombre="Y")
    if ex:
        st.error(ex)
        return
    if ey:
        st.error(ey)
        return
    x_pred = None
    if pred.strip():
        try:
            x_pred = float(pred.strip().replace(",", "."))
        except ValueError:
            st.warning("El valor a predecir no es un número; se ignorará.")
    mostrar_regresion(x, y, x_pred, nx.strip() or "x", ny.strip() or "y")


def seccion_ejemplos():
    st.subheader("📝 Ejercicios de ejemplo resueltos")
    titulos = [e["titulo"] for e in EJEMPLOS]
    elegido = st.selectbox("Elige un ejemplo", titulos, key="ej_sel")
    mostrar_ejemplo(EJEMPLOS[titulos.index(elegido)])


def seccion_chat():
    st.subheader("💬 Chat con E.V.A. (IA)")
    if client is None:
        st.warning("El chat con IA no está disponible: falta "
                   "GEMINI_API_KEY en los secretos de la aplicación. "
                   "Las demás secciones funcionan con normalidad.")
        return

    if "messages" not in st.session_state:
        st.session_state.messages = []

    if not st.session_state.messages:
        with st.chat_message("assistant", avatar="🤖"):
            st.markdown(
                "¡Hola! Soy **E.V.A.**, tu Estadístico Virtual "
                "Analítico. 📊\n\nPuedo ayudarte con estadística, "
                "probabilidad, matemáticas y Física II. ¿Qué problema "
                "resolvemos hoy?"
            )

    for mensaje in st.session_state.messages:
        avatar = "🤖" if mensaje["role"] == "assistant" else "🧑‍🎓"
        with st.chat_message(mensaje["role"], avatar=avatar):
            st.markdown(mensaje["content"])

    prompt = st.chat_input("Escribe tu pregunta para E.V.A....")
    if prompt:
        st.session_state.messages.append(
            {"role": "user", "content": prompt})
        with st.chat_message("user", avatar="🧑‍🎓"):
            st.markdown(prompt)

        # Solo los últimos mensajes: menos texto = respuesta más rápida
        historial = [
            {"role": "model" if m["role"] == "assistant" else "user",
             "parts": [{"text": m["content"]}]}
            for m in st.session_state.messages[-9:]
        ]
        with st.chat_message("assistant", avatar="🤖"):
            try:
                texto = st.write_stream(generar_stream(historial))
                st.session_state.messages.append(
                    {"role": "assistant", "content": texto})
            except Exception as e:
                st.error("No se pudo generar la respuesta. Los "
                         "servidores de Gemini pueden estar "
                         "saturados; espera unos segundos e "
                         "intenta de nuevo.")
                st.caption(
                    f"Detalle técnico: {type(e).__name__}: {e}")


# ==================================================
# BARRA LATERAL Y NAVEGACION
# ==================================================
with st.sidebar:
    st.header("📊 Proyecto E.V.A.")
    st.write("Estadística, matemáticas y Física II.")
    if st.button("🗑️ Reiniciar chat"):
        st.session_state.messages = []
        st.rerun()
    st.caption("Desarrollado para la Facultad de Ingeniería.")
    st.caption("Universidad Mariano Gálvez de Guatemala.")

SECCIONES = {
    "📐 Descriptiva": seccion_descriptiva,
    "📊 Tablas y gráficas": seccion_tablas,
    "🔔 Normal": seccion_normal,
    "📈 Regresión": seccion_regresion,
    "📝 Ejemplos": seccion_ejemplos,
    "🎯 Práctica": seccion_practica,
    "💬 Chat IA": seccion_chat,
}

elegida = st.radio("Módulo", list(SECCIONES.keys()), horizontal=True,
                   label_visibility="collapsed", key="modulo")
st.write("")
try:
    SECCIONES[elegida]()
except Exception as e:
    st.error("Ocurrió un error inesperado al procesar los datos. "
             "Revisa que los valores ingresados sean correctos.")
    st.caption(f"Detalle técnico: {type(e).__name__}: {e}")

st.markdown("""
<div class="footer">
E.V.A. · Estadístico Virtual Analítico<br>
Proyecto académico · Física II
</div>
""", unsafe_allow_html=True)
