import os
import streamlit as st
from google import genai

# Configuración de la página de Streamlit
st.set_page_config(page_title="Proyecto E.V.A.", page_icon="🤖")

st.title("🤖 Proyecto E.V.A.")
st.write("Asistente inteligente conectado con Google Gemini.")

# Obtener la API Key desde los secretos de Streamlit Cloud o variables de entorno
api_key = st.secrets.get("GEMINI_API_KEY") or os.getenv("GEMINI_API_KEY")

if not api_key:
    st.error("⚠️ Falta configurar la GEMINI_API_KEY en los secretos de Streamlit Cloud.")
else:
    try:
        # Inicializar el cliente oficial moderno de Google GenAI
        client = genai.Client(api_key=api_key)

        # Inicializar historial de chat en la sesión
        if "messages" not in st.session_state:
            st.session_state.messages = []

        # Mostrar historial en pantalla
        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])

        # Entrada de texto del usuario
        if prompt := st.chat_input("Escribe tu mensaje para E.V.A..."):
            # Guardar y mostrar mensaje del usuario
            st.session_state.messages.append({"role": "user", "content": prompt})
            with st.chat_message("user"):
                st.markdown(prompt)

            # Generar respuesta del asistente
            with st.chat_message("assistant"):
                with st.spinner("E.V.A. está pensando..."):
                    # Llamada directa al modelo actual y estable
                    response = client.models.generate_content(
                        model="gemini-2.5-flash",
                        contents=prompt,
                    )
                    bot_response = response.text
                    st.markdown(bot_response)
                    # Guardar respuesta en el historial
                    st.session_state.messages.append({"role": "assistant", "content": bot_response})

    except Exception as e:
        st.error(f"Error en el módulo de inteligencia: {e}")
