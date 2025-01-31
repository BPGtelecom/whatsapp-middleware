from flask import Flask, request
from twilio.twiml.messaging_response import MessagingResponse
from twilio.rest import Client
import openai
import os

# Inicializando o Flask
app = Flask(__name__)

# Configuração do Twilio
ACCOUNT_SID = os.getenv("ACCOUNT_SID")
AUTH_TOKEN = os.getenv("AUTH_TOKEN")
TWILIO_WHATSAPP_NUMBER = "whatsapp:+14155238886"

twilio_client = Client(ACCOUNT_SID, AUTH_TOKEN)

# Configuração da API OpenAI (ChatGPT)
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
openai.api_key = OPENAI_API_KEY

# Rota principal para verificar se o servidor está rodando
@app.route("/")
def home():
    return "Servidor está rodando corretamente!"

# Rota para responder mensagens do WhatsApp
@app.route("/whatsapp", methods=["POST"])
def whatsapp_reply():
    msg_in = request.values.get("Body", "").strip()
    sender = request.values.get("From", "")
    
    if not msg_in:
        return "Nenhuma mensagem recebida.", 400

    # Enviar a mensagem para o ChatGPT
    try:
        chat_response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "Você é um assistente da BPG Telecom ajudando clientes no WhatsApp."},
                {"role": "user", "content": msg_in}
            ]
        )
        
        reply = chat_response["choices"][0]["message"]["content"]

        # Enviar a resposta para o usuário via Twilio
        twilio_client.messages.create(
            from_=TWILIO_WHATSAPP_NUMBER,
            body=reply,
            to=sender
        )

        return "OK", 200

    except Exception as e:
        return f"Erro: {str(e)}", 500

# Rodando o aplicativo no Render
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
