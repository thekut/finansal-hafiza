import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os
from datetime import datetime

# E-posta Ayarları (GitHub Secrets üzerinden alınır)
SMTP_SERVER = "smtp.gmail.com" 
SMTP_PORT = 587
EMAIL_SENDER = os.environ.get("EMAIL_USER")
EMAIL_PASSWORD = os.environ.get("EMAIL_PASS")
EMAIL_RECIPIENT = "gururlu_kimya7o@icloud.com" # Buraya kendi mail adresinizi yazın

def send_weekly_report(report_body):
    if not EMAIL_SENDER or not EMAIL_PASSWORD:
        print("E-posta gönderimi atlandı: Kimlik bilgileri (Secrets) bulunamadı.")
        return

    msg = MIMEMultipart()
    msg['From'] = EMAIL_SENDER
    msg['To'] = EMAIL_RECIPIENT
    msg['Subject'] = f"Finansal Hafıza Haftalık Rapor - {datetime.now().strftime('%d.%m.%Y')}"

    body = f"""
    Merhaba,
    
    Finansal Hafıza sistemi haftalık taramasını başarıyla tamamladı.
    
    Özet:
    {report_body}
    
    Web sitesi güncellendi ve GitHub'a pushlandı.
    
    İyi çalışmalar,
    FinansBot
    """
    msg.attach(MIMEText(body, 'plain'))

    try:
        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        server.starttls()
        server.login(EMAIL_SENDER, EMAIL_PASSWORD)
        text = msg.as_string()
        server.sendmail(EMAIL_SENDER, EMAIL_RECIPIENT, text)
        server.quit()
        print("Haftalık rapor e-postası başarıyla gönderildi.")
    except Exception as e:
        print(f"E-posta gönderilemedi: {e}")

if __name__ == "__main__":
    # Test çalışması
    send_weekly_report("Piyasa verileri (Altın, Dolar, Euro) güncellendi. Asgari ücret verisi doğrulandı.")