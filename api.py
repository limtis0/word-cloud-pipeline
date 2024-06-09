import os
import zipfile
from fastapi import FastAPI, BackgroundTasks
from fastapi.responses import JSONResponse
import smtplib
from email.message import EmailMessage
from make_wordcloud import make_wordclouds
from pathlib import Path
from dotenv import load_dotenv

# Load .env variables
load_dotenv()

DATABASE_URL = os.getenv('DATABASE_URL')
SMTP_HOST = os.getenv('SMTP_HOST')
SMTP_PORT = os.getenv('SMTP_PORT')
SMTP_USERNAME = os.getenv('SMTP_USERNAME')
SMTP_PASSWORD = os.getenv('SMTP_PASSWORD')

# Prepare API
app = FastAPI()


def create_zip_from_folder(folder_path: Path, zip_path: Path):
    with zipfile.ZipFile(zip_path, 'w') as zipf:
        for file_path in folder_path.rglob('*.svg'):
            zipf.write(file_path, file_path.relative_to(folder_path))


def send_email_with_attachment(to_email: str, subject: str, body: str, attachment_path: str):
    msg = EmailMessage()
    msg['From'] = SMTP_USERNAME
    msg['To'] = to_email
    msg['Subject'] = subject
    msg.set_content(body)

    with open(attachment_path, 'rb') as f:
        file_data = f.read()
        file_name = os.path.basename(attachment_path)
        msg.add_attachment(file_data, maintype='application', subtype='zip', filename=file_name)

    with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as server:
        server.login(SMTP_USERNAME, SMTP_PASSWORD)
        server.send_message(msg)


def process_wordclouds_and_send_email(to_email: str, from_result: bool):
    try:
        output_folder = make_wordclouds(os.getenv('DATABASE_URL'), from_result=from_result)
        zip_path = output_folder / 'archived.zip'
        create_zip_from_folder(output_folder, zip_path)

        subject = "Updated Word Clouds"
        body = "Please find attached the word clouds you requested."

        send_email_with_attachment(to_email, subject, body, zip_path)
    except Exception as e:
        print('An error occurred:', e)


@app.get("/wordclouds")
def get_wordclouds(background_tasks: BackgroundTasks, to_email: str, from_result: bool):
    background_tasks.add_task(process_wordclouds_and_send_email, to_email, from_result)
    return JSONResponse(content={"message": "Word clouds are being processed and will be sent via email."})


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app)
