import os
import streamlit as st
import google.generativeai as genai

# Configuración de la página de Streamlit
st.set_page_config(page_title="Proyecto E.V.A.", page_icon="🤖")

st.title("🤖 Proyecto E.V.A.")
st.write("Asistente inteligente conectado con Google Gemini.")

# Obtener la API Key desde los secretos de Streamlit Cloud o variables de entorno
api_key = st.secrets.get("GEMINI_API_KEY") or os.getenv("GEMINI_API_KEY")

if not api_key:
    st.error("⚠️ Falta configurar la GEMINI_API_KEY en los secretos de Streamlit Cloud.")
else:
    # Configurar el cliente de Google Gemini
    genai.configure(api_key=api_key)

    # Guardar la instancia del chat en el estado de la sesión (session_state)
    if "chat" not in st.session_state:
        # Usamos el nombre del modelo estable
        model = genai.GenerativeModel("gemini-1.5-flash")
        st.session_state.chat = model.start_chat(history=[])

    # Mostrar historial de mensajes guardados previamente
    for message in st.session_state.chat.history:
        role = "user" if message.role == "user" else "assistant"
        with st.chat_message(role):
            # Extraer el texto de manera segura
            text_content = "".join([part.text for part in message.parts if hasattr(part, 'text')])
            st.markdown(text_content)

    # Entrada de texto del usuario
    if prompt := st.chat_input("Escribe tu mensaje para E.V.A..."):
        # Mostrar mensaje del usuario en la pantalla
        with st.chat_message("user"):
            st.markdown(prompt)
        
        # Enviar mensaje a Gemini y mostrar respuesta
        with st.chat_message("assistant"):
            with st.spinner("E.V.A. está pensando..."):
                try:
                    response = st.session_state.chat.send_message(prompt)
                    st.markdown(response.text)
                except Exception as e:
                    st.error(f"Error en el módulo de inteligencia: {e}")
