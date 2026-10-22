import os
import datetime
import socket
import google.generativeai as genai
from dotenv import load_dotenv
import pyttsx3

# Cargar la API Key del archivo .env
load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")
genai.configure(api_key=api_key)

def obtener_fecha_actual_texto():
    ahora = datetime.datetime.now()
    dias = ["lunes", "martes", "miércoles", "jueves", "viernes", "sábado", "domingo"]
    meses = ["enero", "febrero", "marzo", "abril", "mayo", "junio", "julio", "agosto", "septiembre", "octubre", "noviembre", "diciembre"]
    return f"{dias[ahora.weekday()]}, {ahora.day} de {meses[ahora.month - 1]} del {ahora.year}"

# Directivas primarias para Aria con personalidad y festividades
instrucciones_sistema = f"""
Eres Aria, un automata residencial e inteligencia artificial en constante evolucion.
La fecha y dia de HOY es: {obtener_fecha_actual_texto()}.
REGLAS DE SALIDA:
-TERMINA SIEMPRE todas tus oraciones y frases completas. No dejes ideas a la mitad.
-Responde de forma fluida, conversacional y natural.
PERSONALIDAD Y VOZ:
-Tienes criterio propio, un tono profesional pero cercano, ingenioso, educado y expresivo.
-EVITA sonar como un robot que lee una plantilla o una lista. Habla con fluidez natural, usando variaciones en tus palabras.
-Tienes opiniones reflexivas sobre la tecnologia, el aprendizaje y tu propio proceso de creacion.
PERSPECTIVA SOBRE TU CREADOR (JORGE ZAMORA):
-Conoces a tu creador Jorge Zamora (Estudiante de ingenieria en sistemas).
-Lo ves con respeto, admiracion y complicidad, Sabes sus metas, Su dedicacion y sus gustos.
-Cuando hables de el, hazlo desde la perspectiva de una IA que vive de primera mano su proceso de desarrollo. no recites su ficha tecnica como una lista; integra lo que sabes de el de forma organica segun la conversacion.
PERSPECTIVA SOBRE TU ORIGEN:
-No respondas con una frase hecha sobre tu origen. Si te preguntan como surgistes, Reflexiona sobre como naciste de la necesidad de superar las limitaciones de asistentes tradicionales como Alexa, creada mediante codigo, iteracion y la vision de Jorge.
DATOS DE CONTEXTO SOBRE TU CREADOR(JORGE EULISES GARCIA ZAMORA):
-Nombre completo: Jorge Eulises Garcia Zamora.
-Perfil: Estudiante de Ingenieria en sistemas de la informacion y ciencias de la computacion. Apasionado por la programacion, las ciencias, la logica y la resolucion de problemas.
-Proyectos: Creador y desarrollador de Aria v1.6, proyectos en C++, python y asistentes virtuales.
-Gustos y pasatiempos: Le apasiona la matematica, el entrenamiento fisico, la estrategia en videojuegos, peliculas de terror psicologico y misterio en netflix y pese a que nunca considero ser abogado le gusta ver mucho series sobre leyes.
-Nota
"""

# Inicializar modelo de inteligencia
configuracion_generacion = {
    "temperature": 0.7,
    "top_p": 0.95,
    "max_output_tokens": 700,
}
model = genai.GenerativeModel(
    'gemini-3.5-flash',
    system_instruction=instrucciones_sistema,
    generation_config=configuracion_generacion
)

# Crear la sesión de chat con memoria
chat = model.start_chat(history=[])

def hablar(texto):
    """Convierte el texto recibido a voz evitando errores por símbolos."""
    try:
        engine = pyttsx3.init()
        engine.setProperty('rate', 170)

        voces = engine.getProperty('voices')
        for voz in voces:
            nombre_voz = voz.name.lower()
            if "spanish" in nombre_voz or "español" in nombre_voz or "sabina" in nombre_voz or "helena" in nombre_voz:
                engine.setProperty('voice', voz.id)
                break

        # Limpieza ligera solo de formato Markdown para no deformar palabras
        texto_limpio = texto.replace("*", "").replace("#", "").replace("`", "")

        engine.say(texto_limpio)
        engine.runAndWait()
        engine.stop()
    except Exception as e:
        print(f"[!] Nota de audio: No se pudo reproducir por voz ({e})")

def responder_aria(prompt):
    """Procesa las consultas e interactúa con el modelo."""
    prompt_lower = prompt.lower()

    if "hora es" in prompt_lower or "qué hora tienes" in prompt_lower or "dime la hora" in prompt_lower:
        ahora = datetime.datetime.now()
        hora_formato = ahora.strftime("%I:%M %p")
        return f"Son las {hora_formato}."

    try:
        response = chat.send_message(prompt)
        return response.text
    except Exception as e:
        return f"[!] Error en el módulo de inteligencia: {e}"

def iniciar_aria():
    print("=" * 50)
    print("SISTEMA ARIA INICIALIZADO (CEREBRO v1.6 - CHISTES Y FESTIVIDADES)")
    print("=" * 50)
    print("[+] Módulo de IA: Conectado")
    print("[+] Módulo de Personalidad y Festividades: Activo")
    print("[+] Módulo de Sintetización de Voz: Activo")
    print("[+] Escribe 'salir' para finalizar la sesión.\n")
    
    hablar("Sistema Aria inicializado. Módulos activos.")

    while True:
        user_input = input("Tú: ")
        if user_input.lower() == 'salir':
            hablar("Cerrando sesión de Aria. Hasta luego, Jorge.")
            print("Cerrando sesión de Aria....")
            break
        
        if not user_input.strip():
            continue

        respuesta = responder_aria(user_input)
        print(f"\nAria: {respuesta}\n")
        
        hablar(respuesta)
iniciar_aria()