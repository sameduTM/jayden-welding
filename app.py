from flask import Flask, render_template, request, jsonify
import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from urllib.parse import quote

app = Flask(__name__, static_folder='static', static_url_path='/static')

# Configuration for email (using environment variables - set these in your system)
BUSINESS_PHONE = "+254705327497"  # WhatsApp business number
BUSINESS_EMAIL = os.getenv('BUSINESS_EMAIL', 'contact@jaydenmetalworks.com')
SMTP_SERVER = os.getenv('SMTP_SERVER', 'smtp.gmail.com')
SMTP_PORT = int(os.getenv('SMTP_PORT', 587))
SENDER_EMAIL = os.getenv('SENDER_EMAIL', 'your-email@gmail.com')
SENDER_PASSWORD = os.getenv('SENDER_PASSWORD', 'your-app-password')


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/send-quote', methods=['POST'])
def send_quote():
    try:
        data = request.json
        name = data.get('name', '').strip()
        email = data.get('email', '').strip()
        phone = data.get('phone', '').strip()
        product = data.get('product', '').strip()
        details = data.get('details', '').strip()

        if not all([name, email, phone, product]):
            return jsonify({'success': False, 'error': 'Missing required fields'}), 400

        # Format message for WhatsApp and Email
        message = f"""
Hello Jayden Metal Works,

I would like to request a quote for the following:

Name: {name}
Email: {email}
Phone: {phone}

Product/Service: {product}

Details: {details}

Please contact me with a quote.

Thank you!
        """.strip()

        # Send Email
        try:
            msg = MIMEMultipart()
            msg['From'] = SENDER_EMAIL
            msg['To'] = BUSINESS_EMAIL
            msg['Subject'] = f"New Quote Request from {name}"

            body = f"""
New Quote Request:

Name: {name}
Email: {email}
Phone: {phone}

Product/Service: {product}

Details: {details}
            """

            msg.attach(MIMEText(body, 'plain'))

            server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
            server.starttls()
            server.login(SENDER_EMAIL, SENDER_PASSWORD)
            server.send_message(msg)
            server.quit()
            email_sent = True
        except Exception as e:
            print(f"Email error: {e}")
            email_sent = False

        # Create WhatsApp link
        whatsapp_message = quote(message)
        whatsapp_link = f"https://wa.me/{BUSINESS_PHONE.replace('+', '')}?text={whatsapp_message}"

        return jsonify({
            'success': True,
            'whatsapp_link': whatsapp_link,
            'email_sent': email_sent,
            'message': 'Quote request processed successfully!'
        })

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


if __name__ == "__main__":
    app.run(port=5001, host='0.0.0.0')
