import requests
from lxml import html
import os
import datetime as dt
import smtplib
from email.message import EmailMessage

CHULO_VERDE = '✅'

def enviar_correo_con_texto(mensaje):
    msg = EmailMessage()
    msg['Subject'] = '🎓 Cursos disponibles - Reporte automático'
    msg['From'] = os.environ.get("EMAIL_USER")
    msg['To'] = os.environ.get("EMAIL_TO")
    msg.set_content(mensaje)

    with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
        smtp.login(os.environ.get("EMAIL_USER"), os.environ.get("EMAIL_PASS"))
        smtp.send_message(msg)

def entry_point():
    cursos = []
    contador = 1
    mensaje_correo = f"🎓 *Cursos disponibles extraídos automáticamente* ({dt.datetime.now().strftime('%d-%m-%Y %H:%M')})\n\n"

    for pagina in range(1, 6):
        url = f"https://www.cursosdev.com/coupons/Spanish?page={pagina}"
        headers = {
            "user-agent": "Mozilla/5.0"
        }

        respuesta = requests.get(url, headers=headers, timeout=10)
        parser = html.fromstring(respuesta.text)
        tarjetas = parser.xpath("//div[contains(@class, 'transition-transform')]")
        mensaje_correo += f"📚 Página {pagina}:\n"

        for tarjeta in tarjetas:
            titulo = tarjeta.xpath(".//h2/text()")
            autor = tarjeta.xpath(".//p[contains(@class, 'truncate')]/i/text()")
            enlace = tarjeta.xpath(".//a/@href")
            publicado = tarjeta.xpath(".//div[contains(@class, 'border-t')]//span[@class='text-xs']/text()")
            estado = tarjeta.xpath(".//div[contains(@class, 'bg-red-500') and contains(text(), 'Expirado')]")

            if not titulo or not enlace:
                continue
            if "Categoría" in titulo[0] or "/category/" in enlace[0]:
                continue
            if "/coupons-udemy/" not in enlace[0]:
                continue
            if estado:
                continue

            mensaje_correo += (
                f"📌 {titulo[0].strip()}\n"
                f"   👨‍🏫 Autor: {autor[0].strip() if autor else 'Desconocido'}\n"
                f"   ⏳ Publicado: {publicado[0].strip() if publicado else 'Sin fecha'}\n"
                f"   🎯 Estado: {CHULO_VERDE} Disponible\n"
                f"   🔗 [{contador}] Enlace: {enlace[0].strip()}\n\n"
            )
            contador += 1

    enviar_correo_con_texto(mensaje_correo)

if __name__ == "__main__":
    entry_point()
