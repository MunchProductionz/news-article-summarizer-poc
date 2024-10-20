import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.audio import MIMEAudio
from email.mime.base import MIMEBase
from email.mime.text import MIMEText
import io
import aiosmtplib
import logging
from datetime import datetime

smtp_server = 'smtp.gmail.com'
smtp_port = 587
smtp_username = 'carnegieaino@gmail.com'
smtp_password = 'royc bltj omda cbwq'
from_email = 'carnegieaino@gmail.com'


async def send_email_with_attachement(subject, body, to_email, audio_data_responses):
    
    msg = MIMEMultipart()
    msg['From'] = from_email
    msg['To'] = to_email
    msg['Subject'] = subject
    
    # Attach the body of the email as plain text
    msg.attach(MIMEText(body, 'plain'))

    buffer = io.BytesIO()

    for audio_data in audio_data_responses:
        for chunk in audio_data.iter_bytes(chunk_size=4096):
            buffer.write(chunk)
    buffer.seek(0)

    byte_data = buffer.getvalue()

    today_date = datetime.today().strftime("%Y-%m-%d")
    filename = f"Summaries {today_date}.mp3"
    
    # Create MIMEAudio object with the MP3 data directly from response
    audio = MIMEAudio(byte_data, _subtype='mp3')
    audio.add_header('Content-Disposition', f'attachment; filename={filename}')
    
    # Attach the audio to the email
    msg.attach(audio)
    try:
        res = await aiosmtplib.send(
            msg,
            hostname=smtp_server,
            port=smtp_port,
            start_tls=True,
            username=from_email,
            password=smtp_password
        )
        logging.info(res)
        print("Email sent successfully!")
        return "Email sent successfully!"
    except Exception as e:
        print(f"Failed to send email: {e}")
        return f"Failed to send email: {e}"


def send_email(subject, to_email, content):
    
    message = f'Subject: {subject}\n\n{content}'

    with smtplib.SMTP(smtp_server, smtp_port) as smtp:
        smtp.starttls()
        smtp.login(smtp_username, smtp_password)
        smtp.sendmail(from_email, to_email, message)