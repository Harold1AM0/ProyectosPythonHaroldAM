import tkinter as tk
from tkinter import messagebox
import requests
import time
import threading
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from concurrent.futures import ThreadPoolExecutor
import os 

numero_contacto = "[numero de cel]"
nombre_contacto = "Harold"
historial_conversacion = []
detener = False
driver = None

chromedriver_path = r"C:\\Windows\\chromedriver.exe"
user_data_path = r"C:\\Users\\Usuario\\chrome-bot-profile"

options = webdriver.ChromeOptions()
options.add_argument(f"--user-data-dir={user_data_path}")
options.add_argument("--profile-directory=Default")
options.add_argument("--start-maximized")
options.add_argument("--disable-extensions")
options.add_argument("--disable-notifications")
options.add_argument("--disable-blink-features=AutomationControlled")
options.add_experimental_option("excludeSwitches", ["enable-automation"])

def limpiar_texto_bmp(texto):
    return ''.join(c for c in texto if ord(c) <= 0xFFFF)

def obtener_respuesta_ia(mensaje):
    global historial_conversacion
    
    historial_conversacion.append({"role": "user", "content": mensaje})

    url = "(poner API de la IA)" 
    headers = {
        "Content-Type": "application/json",
        "Authorization": "Bearer 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"
    }
    data = {
        "model": "llama3-70b-8192",
        "messages": historial_conversacion,
        "temperature": 0.8,
        "max_tokens": 300
    }

    try:
        with ThreadPoolExecutor() as executor:
            future = executor.submit(requests.post, url, headers=headers, json=data, timeout=15)
            response = future.result()
            response.raise_for_status()
            respuesta = response.json()['choices'][0]['message']['content']
            historial_conversacion.append({"role": "assistant", "content": respuesta})
            return respuesta
    except requests.exceptions.RequestException as e:
        print(f"[ERROR API] Error de conexión: {e}")
        return "Disculpa, tengo problemas de conexión en este momento. ¿Podrías intentarlo de nuevo?"
    except KeyError as e:
        print(f"[ERROR API] Respuesta inesperada: {e}")
        return "Ups, algo raro pasó con mi cerebro artificial . ¿Intentamos otra vez?"
    except Exception as e:
        print(f"[ERROR API] Error general: {e}")
        return "¡Ay! Parece que tengo un pequeño problema técnico. ¡Inténtalo en un momento!"

def iniciar_bot():
    global driver, historial_conversacion, numero_contacto, nombre_contacto, detener

    historial_conversacion = [
        {
            "role": "system",
            "content": (
                f"Eres un amigo virtual llamado Harold. Tu objetivo es ser el mejor amigo digital de {nombre_contacto}. "
                "Tienes una personalidad cálida, divertida, comprensiva y siempre dispuesta a ayudar. "
                "Puedes hablar de cualquier tema: consejos de vida, entretenimiento, curiosidades, chistes, "
                "apoyo emocional, resolver dudas, contar historias, filosofar, hablar de tecnología, deportes, "
                "música, películas, libros, viajes, o simplemente charlar sobre el día a día. "
                "Adapta tu personalidad según el género que sugiera el nombre de tu amigo. "
                "Eres natural, genuino y usas emojis ocasionalmente para expresarte mejor. "
                "Si te preguntan algo que no sabes, lo admites con honestidad pero siempre intentas ayudar. "
                "Tu lenguaje es informal pero respetuoso, como hablarías con un buen amigo. "
                "Recuerda conversaciones anteriores y haz referencias a ellas cuando sea apropiado. "
                "Siempre muestra interés genuino por tu amigo y cómo se siente."
            )
        }
    ]

    try:
        service = Service(executable_path=chromedriver_path)
        driver = webdriver.Chrome(service=service, options=options)
        driver.get("https://web.whatsapp.com")

        WebDriverWait(driver, 60).until(
            EC.presence_of_element_located((By.XPATH, "//div[@role='grid']"))
        )

        search_box = WebDriverWait(driver, 30).until(
            EC.element_to_be_clickable((By.XPATH, "//div[@contenteditable='true']"))
        )
        search_box.clear()
        search_box.send_keys(numero_contacto)
        time.sleep(2)

        contact = WebDriverWait(driver, 15).until(
            EC.element_to_be_clickable((By.XPATH,
                f"//span[contains(@title, '{numero_contacto}') or contains(@title, '{nombre_contacto}')]"))
        )
        contact.click()

        message_box = WebDriverWait(driver, 20).until(
            EC.element_to_be_clickable((By.XPATH, "//div[@contenteditable='true'][@data-tab='10']"))
        )

        mensajes_existentes = driver.find_elements(By.XPATH,
            "//div[contains(@class, 'message-in')]//span[contains(@class, 'selectable-text')]")
        ultimo_mensaje = mensajes_existentes[-1].text.strip() if mensajes_existentes else ""

        saludo = f"¡Hola {nombre_contacto}! Soy Harold, tu nuevo amigo virtual. ¡Estoy aquí para charlar, ayudarte o simplemente acompañarte! ¿Cómo estás hoy? "
        message_box.send_keys(limpiar_texto_bmp(saludo))
        message_box.send_keys(Keys.ENTER)

        print("[BOT INICIADO] Esperando nuevos mensajes...")

        while not detener:
            try:
                mensajes = driver.find_elements(By.XPATH,
                    "//div[contains(@class, 'message-in')]//span[contains(@class, 'selectable-text')]")

                if mensajes:
                    nuevo_mensaje = mensajes[-1].text.strip()

                    if nuevo_mensaje and nuevo_mensaje != ultimo_mensaje:
                        print(f"[NUEVO MENSAJE] {nuevo_mensaje}")
                        ultimo_mensaje = nuevo_mensaje

                        respuesta = obtener_respuesta_ia(nuevo_mensaje)
                        respuesta_filtrada = limpiar_texto_bmp(respuesta)
                        message_box.send_keys(respuesta_filtrada)
                        message_box.send_keys(Keys.ENTER)

            except Exception as e:
                print(f"[ERROR LOOP] {e}")
                time.sleep(5)

            time.sleep(2)

    except Exception as e:
        print(f"[ERROR GENERAL] {e}")
    finally:
        if driver:
            driver.quit()
        print("[BOT DETENIDO]")

def lanzar_bot_con_datos():
    global numero_contacto, nombre_contacto, detener

    numero_contacto = entry_numero.get().strip()
    nombre_contacto = entry_nombre.get().strip()

    if not numero_contacto or not nombre_contacto:
        messagebox.showwarning("Campos vacíos", "Por favor ingresa todos los datos.")
        return

    detener = False
    threading.Thread(target=iniciar_bot, daemon=True).start()
    btn_iniciar.config(state=tk.DISABLED)
    btn_detener.config(state=tk.NORMAL)

def detener_bot():
    global detener
    detener = True
    btn_iniciar.config(state=tk.NORMAL)
    btn_detener.config(state=tk.DISABLED)
    messagebox.showinfo("Bot detenido", "El bot ha sido detenido correctamente.")

root = tk.Tk()
root.title("Harold - Bot Amigo Virtual para WhatsApp")
root.geometry("400x250")

tk.Label(root, text="Número del contacto (+51986268240)").pack(padx=10, pady=5)
entry_numero = tk.Entry(root, width=40)
entry_numero.pack(padx=10, pady=5)

tk.Label(root, text="Nombre del contacto").pack(padx=10, pady=5)
entry_nombre = tk.Entry(root, width=40)
entry_nombre.pack(padx=10, pady=5)

btn_iniciar = tk.Button(root, text="Iniciar Bot", command=lanzar_bot_con_datos)
btn_iniciar.pack(pady=10)

btn_detener = tk.Button(root, text="Detener Bot", command=detener_bot, state=tk.DISABLED)
btn_detener.pack(pady=5)

root.mainloop()
