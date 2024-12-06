from fastapi import FastAPI, HTTPException
import zipfile
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
import os
from pydantic import BaseModel
from main import get_final_json  # Import from main.py

app = FastAPI()

# Email credentials (use environment variables or a secure vault in production)
SENDER_EMAIL = "kappsmapalo@gmail.com"
SENDER_PASSWORD = "mkwt pyym fryt muoy"

class EmailRequest(BaseModel):
    recipient_email: str
    unique_id: str

    
    
def json_to_xml(json_obj, line_padding=""):
    """
    Recursively converts a JSON object into an XML string.
    """
    result_list = []

    if isinstance(json_obj, dict):
        for tag_name, value in json_obj.items():
            result_list.append(f"{line_padding}<{tag_name}>")
            result_list.append(json_to_xml(value, line_padding + "  "))
            result_list.append(f"{line_padding}</{tag_name}>")

    elif isinstance(json_obj, list):
        for value in json_obj:
            result_list.append(json_to_xml(value, line_padding))

    else:
        result_list.append(f"{line_padding}{json_obj}")

    return "\n".join(result_list)

def write_xml_to_file(json_data, file_path):
    """
    Converts JSON data to XML and writes it to a specified file.
    """
    xml_data = f"<epcraTier2Dataset xmlns='https://cameo.noaa.gov/epcra_tier2/data_standard/v1' version='1.0.0'>\n{json_to_xml(json_data)}\n</epcraTier2Dataset>"
    with open(file_path, "w", encoding="utf-8") as xml_file:
        xml_file.write(xml_data)
    return file_path

def send_email_with_attachment(recipient_email, subject, body, attachment_path):
    """
    Sends an email with an attachment.
    """
    try:
        # Set up the MIME
        message = MIMEMultipart()
        message['From'] = SENDER_EMAIL
        message['To'] = recipient_email
        message['Subject'] = subject
        message.attach(MIMEText(body, 'plain'))

        # Attach the file
        with open(attachment_path, "rb") as attachment:
            part = MIMEBase('application', 'octet-stream')
            part.set_payload(attachment.read())
        encoders.encode_base64(part)
        part.add_header(
            "Content-Disposition",
            f"attachment; filename={os.path.basename(attachment_path)}",
        )
        message.attach(part)

        # Send email
        with smtplib.SMTP('smtp.gmail.com', 587) as server:
            server.starttls()
            server.login(SENDER_EMAIL, SENDER_PASSWORD)
            server.sendmail(SENDER_EMAIL, recipient_email, message.as_string())
        print("Email sent successfully.")
    except Exception as e:
        print(f"Error sending email: {e}")
        raise

@app.post("/generate_xml")
def create_xml_and_send_email(request: EmailRequest):
    try:
        # Retrieve recipient email from the request body
        recipient_email = request.recipient_email

        uid = request.unique_id

        # Retrieve JSON data from main.py
        dataset_json = get_final_json(filter_id=uid)

        # Generate XML and save to file
        xml_file_path = "Tier2.xml"
        write_xml_to_file(dataset_json, xml_file_path)

        # Zip the XML file
        zip_file_path = "Tier2Report.zip"
        with zipfile.ZipFile(zip_file_path, 'w') as zip_file:
            zip_file.write(xml_file_path)

        # Email the ZIP file
        subject = "Your Tier2 Report"
        body = "Please find the attached Tier2 Report."
        send_email_with_attachment(recipient_email, subject, body, zip_file_path)

        return {"message": "XML generated, zipped, and sent via email successfully.", "code":"200"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to process request: {str(e)}")
    finally:
        # Clean up files
        if os.path.exists(xml_file_path):
            os.remove(xml_file_path)
        if os.path.exists(zip_file_path):
            os.remove(zip_file_path)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
