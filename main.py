import os
import streamlit as st
import google.generativeai as genai

# Configuración de la página de Streamlit
st.set_page_config(page_title="Proyecto E.V.A.", page_icon="🤖")

st.title("🤖 Proyecto E.V.A.")
st.write("Asistente inteligente conectado con Google Gemini.")

# Configurar la API Key desde los secretos de Streamlit Cloud o archivo .env
api_key = st.secrets.get("GEMINI_API_KEY") or os.getenv("GEMINI_API_KEY")

if not api_key:
    st.error("Falta configurar la GEMINI_API_KEY en los secretos de Streamlit.")
else:
    genai.configure(api_key=api_key)
    
    # Inicializar el modelo de Gemini
    model = genai.GenerativeModel("gemini-1.5-flash")
    
    if "chat" not in st.session_state:
        st.session_state.chat = model.start_chat(history=[])

    # Mostrar historial de mensajes en pantalla
    for message in st.session_state.chat.history:
        role = "user" if message.role == "user" else "assistant"
        with st.chat_message(role):
            st.markdown(message.parts[0].text)

    # Entrada de texto interactiva para el usuario en la web
    if prompt := st.chat_input("Escribe tu mensaje para E.V.A..."):
        with st.chat_message("user"):
            st.markdown(prompt)
        
        with st.chat_message("assistant"):
            with st.spinner("E.V.A. está pensando..."):
                try:
                    response = st.session_state.chat.send_message(prompt)
                    st.markdown(response.text)
                except Exception as e:
                    st.error(f"Error en el módulo de inteligencia: {e}")
