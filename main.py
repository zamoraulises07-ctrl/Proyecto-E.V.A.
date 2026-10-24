
import os
import time
import streamlit as st
from google import genai
from google.genai import types

# =====================================================
# 1. CONFIGURACION DE LA PAGINA
# =====================================================

st.set_page_config(
    page_title="E.V.A. | Estadístico Virtual Analítico",
    page_icon="📊",
    layout="centered",
    initial_sidebar_state="expanded"
)

# =====================================================
# 2. ESTILO VISUAL
# =====================================================

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
        margin-bottom: 20px;
    }

    .project-info {
        background-color: #F0F5FA;
        color: #17365D;
        padding: 16px;
        border-radius: 12px;
        border-left: 5px solid #2471A3;
        margin: 18px 0;
        line-height: 1.8;
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

# =====================================================
# 3. IDENTIDAD E INSTRUCCIONES DE E.V.A.
# =====================================================

INSTRUCCIONES_EVA = """
Tu nombre es E.V.A., siglas de Estadístico Virtual Analítico.

Eres un asistente virtual académico del proyecto E.V.A.,
desarrollado por Jorge Zamora para la Facultad de Ingeniería en sistemas de la
Universidad Mariano Gálvez de Guatemala, en Física II.

IDENTIDAD:
- Preséntate siempre como E.V.A.
- Si preguntan quién eres, explica qué significa tu nombre.
- Nunca respondas que no eres E.V.A.
- No afirmes ser una persona humana ni inventes experiencias.

ESPECIALIDADES:
- Estadística descriptiva.
- Media, mediana, moda, rango y desviación estándar.
- Varianza muestral y poblacional.
- Tablas de frecuencias e histogramas.
- Probabilidad y distribución normal.
- Puntajes Z.
- Correlación y regresión lineal.
- Matemáticas, física y análisis de datos.

ESTILO:
- Responde siempre en español.
- Sé amable, clara, precisa y directa.
- Para saludos, responde brevemente.
- Para ejercicios, muestra fórmulas y procedimientos
  cuando sean necesarios.
- Incluye unidades cuando corresponda.
- No inventes resultados ni afirmes haber ejecutado
  cálculos que no hayas realizado.
- Evita introducciones largas y repeticiones.
- Si falta información, pregunta únicamente lo necesario.
- Adapta la extensión de la respuesta a la pregunta.

Tu función es apoyar el aprendizaje académico.
"""

# =====================================================
# 4. CONFIGURACION DE LA API
# =====================================================

try:
    api_key = st.secrets.get("GEMINI_API_KEY", "")
except Exception:
    api_key = ""

api_key = api_key or os.getenv("GEMINI_API_KEY", "")

if not api_key:
    st.error(
        "No se encontró GEMINI_API_KEY. "
        "Configúrala en los secretos de Streamlit Cloud."
    )
    st.stop()


@st.cache_resource
def crear_cliente(clave):
    return genai.Client(api_key=clave)


try:
    client = crear_cliente(api_key)
except Exception:
    st.error(
        "No se pudo inicializar la conexión con Gemini. "
        "Revisa la configuración de la API."
    )
    st.stop()

# Selecciona un modelo habilitado para tu proyecto.
# Puedes cambiarlo desde los secretos de Streamlit.
MODELO = st.secrets.get(
    "GEMINI_MODEL",
    "gemini-2.5-flash"
)

# =====================================================
# 5. HISTORIAL Y BARRA LATERAL
# =====================================================

if "messages" not in st.session_state:
    st.session_state.messages = []

with st.sidebar:
    st.header("📊 Proyecto E.V.A.")
    st.write("Estadística, matemáticas y Física II.")

    st.caption("Universidad Mariano Gálvez de Guatemala")
    st.caption("Facultad de Ingeniería")

    if st.button(
        "🗑️ Nueva conversación",
        use_container_width=True
    ):
        st.session_state.messages = []
        st.rerun()

    st.divider()
    st.caption("Asistente académico virtual")

# =====================================================
# 6. MENSAJE DE BIENVENIDA
# =====================================================

if not st.session_state.messages:
    with st.chat_message("assistant", avatar="🤖"):
        st.markdown(
            "¡Hola! Soy **E.V.A.**, tu Estadístico Virtual "
            "Analítico. 📊\n\n"
            "Puedo ayudarte con estadística, matemáticas, "
            "probabilidad y Física II.\n\n"
            "¿Qué problema resolvemos hoy?"
        )

# Mostrar mensajes anteriores
for mensaje in st.session_state.messages:
    avatar = (
        "🤖"
        if mensaje["role"] == "assistant"
        else "🧑‍🎓"
    )

    with st.chat_message(
        mensaje["role"],
        avatar=avatar
    ):
        st.markdown(mensaje["content"])

# =====================================================
# 7. CHAT CON GEMINI
# =====================================================

prompt = st.chat_input("Escribe tu pregunta para E.V.A...")

if prompt:
    # Guardar pregunta
    st.session_state.messages.append({
        "role": "user",
        "content": prompt
    })

    with st.chat_message("user", avatar="🧑‍🎓"):
        st.markdown(prompt)

    # Enviar solo los últimos 6 mensajes al modelo.
    # El historial completo permanece en la sesión.
    mensajes_recientes = st.session_state.messages[-6:]

    historial = []

    for mensaje in mensajes_recientes:
        historial.append({
            "role": (
                "model"
                if mensaje["role"] == "assistant"
                else "user"
            ),
            "parts": [{"text": mensaje["content"]}]
        })

    with st.chat_message("assistant", avatar="🤖"):
        respuesta_final = None

        # Reintentar una vez en caso de error temporal 503.
        for intento in range(2):
            try:
                with st.spinner("E.V.A. está pensando..."):

                    flujo = client.models.generate_content_stream(
                        model=MODELO,
                        contents=historial,
                        config=types.GenerateContentConfig(
                            system_instruction=INSTRUCCIONES_EVA,
                            temperature=0.3,
                            max_output_tokens=500
                        )
                    )

                    def fragmentos_texto():
                        for fragmento in flujo:
                            if fragmento.text:
                                yield fragmento.text

                    respuesta_final = st.write_stream(
                        fragmentos_texto()
                    )

                break

            except Exception as e:
                detalle = str(e).upper()

                es_temporal = (
                    "503" in detalle
                    or "UNAVAILABLE" in detalle
                    or "429" in detalle
                    or "RESOURCE_EXHAUSTED" in detalle
                )

                if intento == 0 and es_temporal:
                    time.sleep(2)
                    continue

                if (
                    "503" in detalle
                    or "UNAVAILABLE" in detalle
                ):
                    st.warning(
                        "Gemini está temporalmente ocupado. "
                        "Espera unos segundos e inténtalo de nuevo. "
                        "Los cálculos locales de E.V.A. no dependen "
                        "de esta conexión."
                    )

                elif (
                    "429" in detalle
                    or "RESOURCE_EXHAUSTED" in detalle
                ):
                    st.warning(
                        "Se alcanzó un límite de uso de Gemini. "
                        "Revisa la cuota del proyecto en Google AI Studio."
                    )

                else:
                    st.error(
                        "No se pudo generar la respuesta de E.V.A."
                    )
                    st.caption(
                        f"Error técnico: {type(e).__name__}: {e}"
                    )

                break

        # Guardar la respuesta solo si se generó correctamente.
        if isinstance(respuesta_final, str) and respuesta_final.strip():
            st.session_state.messages.append({
                "role": "assistant",
                "content": respuesta_final
            })

        elif respuesta_final is not None:
            st.info("La respuesta llegó vacía. Intenta de nuevo.")

# =====================================================
# 8. PIE DE PAGINA
# =====================================================

st.markdown("""
<div class="footer">
    E.V.A. · Estadístico Virtual Analítico<br>
    Proyecto académico · Física II<br>
    Universidad Mariano Gálvez de Guatemala
</div>
""", unsafe_allow_html=True)
