
import os
import streamlit as st
from google import genai
from google.genai import types

# --------------------------------------------------
# CONFIGURACION GENERAL
# --------------------------------------------------
st.set_page_config(
    page_title="E.V.A. | Asistente Estadístico",
    page_icon="📊",
    layout="centered",
    initial_sidebar_state="expanded"
)

# --------------------------------------------------
# IDENTIDAD VISUAL
# --------------------------------------------------
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
    }
    .footer {
        text-align: center;
        color: #6B7280;
        font-size: 0.85rem;
        margin-top: 30px;
    }
</style>
""", unsafe_allow_html=True)

st.markdown(
    '<div class="main-title">🤖 E.V.A.</div>',
    unsafe_allow_html=True
)
st.markdown(
    '<div class="subtitle">'
    'Estadístico Virtual Analítico'
    '</div>',
    unsafe_allow_html=True
)

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

# --------------------------------------------------
# CONFIGURACION DEL ASISTENTE
# --------------------------------------------------
INSTRUCCIONES_EVA = """
Tu nombre es E.V.A., siglas de Estadístico Virtual Analítico.

Eres el asistente virtual académico del proyecto E.V.A.,
desarrollado por Jorge Zamora para la Facultad de Ingeniería en sistemas de la
Universidad Mariano Gálvez de Guatemala, en la asignatura
Física II.

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
- Apoya con matemáticas, física y análisis de datos.
- Muestra fórmulas, sustituciones, unidades y procedimientos
  cuando sean necesarios.
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
Eres el módulo conversacional de E.V.A. No afirmes que has
ejecutado un cálculo en la aplicación si no lo has hecho.
Cuando un cálculo requiera precisión, muestra el
procedimiento matemático verificable.
"""

# --------------------------------------------------
# CLAVE API
# --------------------------------------------------
try:
    api_key = st.secrets.get("GEMINI_API_KEY", "")
except Exception:
    api_key = ""

api_key = api_key or os.getenv("GEMINI_API_KEY", "")

if not api_key:
    st.error(
        "Falta GEMINI_API_KEY. Configúrala en los secretos "
        "de tu aplicación en Streamlit Cloud."
    )
    st.stop()

# Crear el cliente una sola vez por sesión de caché
@st.cache_resource
def crear_cliente(clave):
    return genai.Client(api_key=clave)

try:
    client = crear_cliente(api_key)
except Exception as e:
    st.error(f"No se pudo inicializar Gemini: {e}")
    st.stop()

# --------------------------------------------------
# HISTORIAL DEL CHAT
# --------------------------------------------------
if "messages" not in st.session_state:
    st.session_state.messages = []

# Barra lateral
with st.sidebar:
    st.header("📊 Proyecto E.V.A.")
    st.write("Estadística, matemáticas y Física II.")

    if st.button("🗑️ Nueva conversación", use_container_width=True):
        st.session_state.messages = []
        st.rerun()

    st.caption("Desarrollado para la Facultad de Ingeniería.")
    st.caption("Universidad Mariano Gálvez de Guatemala.")

# Mensaje inicial
if not st.session_state.messages:
    with st.chat_message("assistant", avatar="🤖"):
        st.markdown(
            "¡Hola! Soy **E.V.A.**, tu Estadístico Virtual "
            "Analítico. 📊\n\n"
            "Puedo ayudarte con estadística, probabilidad, "
            "matemáticas y Física II. ¿Qué problema resolvemos hoy?"
        )

# Mostrar conversación previa
for mensaje in st.session_state.messages:
    avatar = "🤖" if mensaje["role"] == "assistant" else "🧑‍🎓"
    with st.chat_message(mensaje["role"], avatar=avatar):
        st.markdown(mensaje["content"])

# --------------------------------------------------
# GENERACION DE RESPUESTAS
# --------------------------------------------------
prompt = st.chat_input("Escribe tu pregunta para E.V.A....")

if prompt:
    st.session_state.messages.append({
        "role": "user",
        "content": prompt
    })

    with st.chat_message("user", avatar="🧑‍🎓"):
        st.markdown(prompt)

    # Convertir el historial al formato de Gemini.
    # Gemini utiliza "model" en lugar de "assistant".
    historial = []
    for mensaje in st.session_state.messages:
        historial.append({
            "role": (
                "model"
                if mensaje["role"] == "assistant"
                else "user"
            ),
            "parts": [{"text": mensaje["content"]}]
        })

    with st.chat_message("assistant", avatar="🤖"):
        with st.spinner("E.V.A. está preparando tu respuesta..."):
            try:
                respuesta = client.models.generate_content(
                    model="gemini-3.8-flash",
                    contents=historial,
                    config=types.GenerateContentConfig(
                        system_instruction=INSTRUCCIONES_EVA,
                        temperature=0.4,
                        max_output_tokens=1200,
                        thinking_config=types.ThinkingConfig(
                            thinking_level="low"
                        )
                    )
                )

                texto = respuesta.text

                if not texto:
                    texto = (
                        "No pude generar una respuesta esta vez. "
                        "Por favor, intenta de nuevo."
                    )

                st.markdown(texto)

                st.session_state.messages.append({
                    "role": "assistant",
                    "content": texto
                })

            except Exception as e:
                st.error(
                    "No se pudo generar la respuesta. "
                    "Comprueba la conexión, el modelo y la cuota de API."
                )
                st.caption(f"Detalle técnico: {type(e).__name__}: {e}")

st.markdown("""
<div class="footer">
E.V.A. · Estadístico Virtual Analítico<br>
Proyecto académico · Física II
</div>
""", unsafe_allow_html=True)
