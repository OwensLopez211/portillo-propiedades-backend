import smtplib
from email.mime.text import MIMEText
import sys

def test_smtp_connection():
    try:
        # Intentar conexión
        print("Intentando conectar a smtp.zoho.com:587...")
        server = smtplib.SMTP('smtp.zoho.com', 587, timeout=20)
        
        print("Iniciando TLS...")
        server.starttls()
        
        print("Intentando login...")
        server.login('Forms@newlandpropiedades.cl', 'Form2024newland.')
        
        # Intentar enviar un correo de prueba
        msg = MIMEText('Este es un correo de prueba')
        msg['Subject'] = 'Test SMTP'
        msg['From'] = 'Forms@newlandpropiedades.cl'
        msg['To'] = 'Contacto@newlandpropiedades.cl'
        
        print("Enviando correo de prueba...")
        server.send_message(msg)
        
        print("Cerrando conexión...")
        server.quit()
        
        print("¡Prueba completada con éxito!")
        return True
        
    except Exception as e:
        print(f"Error: {str(e)}", file=sys.stderr)
        return False

if __name__ == "__main__":
    test_smtp_connection()