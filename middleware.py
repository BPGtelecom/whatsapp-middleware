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

twilio_client = Client(ACCOUNT_SID, AUTH_TOKEN)

# Configuração da API OpenAI (ChatGPT)
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
openai.api_key = OPENAI_API_KEY

# Lista de palavras-chave para direcionamento ao suporte humano
PALAVRAS_CRITICAS = ["ruim", "péssimo", "merda", "insatisfeito", "não funciona", "horrível", "lento", "reclamar"]

@app.route("/", methods=["GET"])
def home():
    return "Servidor do WhatsApp com ChatGPT rodando!"

@app.route("/whatsapp", methods=["POST"])
def whatsapp_reply():
    try:
        msg_in = request.values.get("Body", "").strip().lower()
        sender = request.values.get("From", "")

        print(f"Mensagem recebida de {sender}: {msg_in}")

        # **Identificação automática do atendimento**
        if "plano" in msg_in or "valor" in msg_in:
            reply = "Temos os seguintes planos disponíveis:\n\n💻 300MB - R$ 99,90/mês\n🚀 500MB - R$ 129,90/mês\n🔵 1GB - R$ 199,90/mês\n\nSe precisar de mais informações, me avise!"
        
        elif "sem sinal" in msg_in or "problema técnico" in msg_in or "internet caiu" in msg_in:
            reply = "Sinto muito pelo problema! Vamos tentar resolver:\n1️⃣ Verifique se o cabo de fibra está conectado corretamente ao modem.\n2️⃣ Desligue o modem por 10 segundos e ligue novamente.\n3️⃣ Verifique se a luz do equipamento está vermelha.\n\nSe o problema continuar, posso encaminhar para nosso suporte técnico. Você pode me informar o seu CPF ou número do contrato?"
        
        elif "luz vermelha" in msg_in:
            reply = "A luz vermelha no modem indica falha na conexão com a rede. Tente:\n🔹 Verificar se todos os cabos estão bem conectados.\n🔹 Reiniciar o modem e aguardar 2 minutos.\nSe a luz permanecer vermelha, me passe o seu CPF para que eu possa abrir um chamado no suporte técnico."

        elif "quem é você" in msg_in or "quem está falando" in msg_in:
            reply = "Olá! Sou o assistente virtual da BPG Telecom. Estou aqui para te ajudar com informações sobre planos, suporte técnico e atendimento ao cliente. Como posso te ajudar hoje?"

        elif any(palavra in msg_in for palavra in PALAVRAS_CRITICAS):
            reply = "Sinto muito que você esteja insatisfeito. Vou encaminhar você para um de nossos atendentes humanos. Aguarde um momento, por favor."
            # Aqui poderia enviar uma notificação para o time de suporte humano.

        else:
            # **Envia a mensagem para o ChatGPT**
            chat_response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "Você é um assistente virtual da BPG Telecom. Responda sempre de forma clara e objetiva sobre planos, suporte técnico e atendimento ao cliente."},
                    {"role": "user", "content": msg_in}
                ]
            )
            
            reply = chat_response["choices"][0]["message"]["content"]

        # **Envia a resposta para o WhatsApp**
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
