
import os
import streamlit as st
from google import genai

# Configuración de la aplicación
st.set_page_config(
    page_title="Proyecto E.V.A.",
    page_icon="🤖",
    layout="centered"
)

st.title("🤖 Proyecto E.V.A.")
st.write("Asistente inteligente conectado con Google Gemini.")
st.caption("Estadística, matemáticas y asistencia académica")

# Obtener la clave API
try:
    api_key = st.secrets.get("GEMINI_API_KEY", "")
except Exception:
    api_key = ""

api_key = api_key or os.getenv("GEMINI_API_KEY", "")

if not api_key:
    st.error(
        "No se encontró GEMINI_API_KEY. "
        "Configúrala en Settings > Secrets de Streamlit Cloud."
    )
    st.stop()

# Crear el cliente de Gemini
client = genai.Client(api_key=api_key)

# Mantener el historial de la conversación
if "messages" not in st.session_state:
    st.session_state.messages = []

# Mostrar los mensajes anteriores
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Entrada del usuario
prompt = st.chat_input("Escribe tu mensaje para E.V.A...")

if prompt:
    st.session_state.messages.append(
        {"role": "user", "content": prompt}
    )

    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner("E.V.A. está pensando..."):
            try:
                response = client.models.generate_content(
                    model="gemini-3.8-flash",
                    contents=prompt,
                )

                answer = response.text

                if not answer:
                    answer = "Gemini no devolvió texto. Intenta de nuevo."

                st.markdown(answer)

                st.session_state.messages.append(
                    {"role": "assistant", "content": answer}
                )

            except Exception as e:
                st.error(
                    "No se pudo obtener una respuesta de Gemini."
                )
                st.caption(
                    f"Detalle técnico: {type(e).__name__}: {e}"
                )
