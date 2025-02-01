from flask import Flask, request, jsonify
from twilio.twiml.messaging_response import MessagingResponse
from twilio.rest import Client
import openai
import os

app = Flask(__name__)

# Configuração do Twilio
ACCOUNT_SID = os.getenv("ACCOUNT_SID")
AUTH_TOKEN = os.getenv("AUTH_TOKEN")
TWILIO_WHATSAPP_NUMBER = "whatsapp:+14155238886"

if not ACCOUNT_SID or not AUTH_TOKEN:
    raise ValueError("Erro: ACCOUNT_SID ou AUTH_TOKEN não configurado corretamente!")

twilio_client = Client(ACCOUNT_SID, AUTH_TOKEN)

# Configuração da API OpenAI (ChatGPT)
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    raise ValueError("Erro: OPENAI_API_KEY não configurado corretamente!")

openai_client = openai.OpenAI(api_key=OPENAI_API_KEY)
print(f"OPENAI_API_KEY carregada: {OPENAI_API_KEY[:5]}***")  # Exibe parte da chave para debug

# Rota principal para verificar se o servidor está rodando
@app.route("/")
def home():
    return "Servidor do WhatsApp com ChatGPT rodando!"

# Rota para responder mensagens do WhatsApp
@app.route("/whatsapp", methods=["POST"])
def whatsapp_reply():
    try:
        msg_in = request.values.get("Body", "").strip().lower()
        sender = request.values.get("From", "")

        print(f"Mensagem recebida de {sender}: {msg_in}")

        # Usar um modelo mais barato para evitar erro de cota
        response = openai_client.chat.completions.create(
            model="gpt-3.5-turbo",  # Alterado para novo formato da API
            messages=[
                {"role": "system", "content": "Você é um assistente virtual da BPG Telecom. Responda sempre de forma clara e objetiva sobre planos, suporte técnico e atendimento ao cliente."},
                {"role": "user", "content": msg_in}
            ]
        )
        
        reply = response.choices[0].message.content
        print(f"Resposta do ChatGPT: {reply}")

        # Enviar a resposta para o usuário via Twilio
        message = twilio_client.messages.create(
            from_=TWILIO_WHATSAPP_NUMBER,
            body=reply,
            to=sender
        )

        print(f"Mensagem enviada para {sender}: {message.sid}")

        return "OK", 200

    except Exception as e:
        print(f"Erro no endpoint /whatsapp: {str(e)}")
        return f"Erro interno: {str(e)}", 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
