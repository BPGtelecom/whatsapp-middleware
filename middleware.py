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

        if "plano de internet" in msg_in or "valores do plano" in msg_in:
            reply = "Para te informar os valores do plano de internet, preciso do seu CEP ou endereço. Por favor, informe para que eu possa verificar os planos disponíveis na sua região."
        
        elif any(city in msg_in for city in ["poá", "itaquaquecetuba"]):
            reply = "O seu endereço corresponde a nossa área de cobertura. Estou transferindo você para um de nossos atendentes. Aguarde um momento, por favor."
        
        elif "problema técnico" in msg_in or "sem sinal" in msg_in:
            reply = "Vamos tentar resolver o seu problema. Verifique se há uma luz vermelha acesa nos seus equipamentos."
        
        elif "luz vermelha" in msg_in:
            reply = "Se há uma luz vermelha, verifique se todos os cabos estão corretamente conectados."
        
        elif "cabos conectados" in msg_in:
            reply = "Já que todos os cabos estão conectados corretamente e ainda há luz vermelha, estou transferindo você para o suporte técnico. Aguarde um momento."
        
        elif "sem luz vermelha" in msg_in:
            reply = "Por favor, desligue os equipamentos da tomada por 3 minutos e ligue novamente. Isso pode resolver o problema."
        
        else:
            # Usar ChatGPT para outras respostas
            response = openai_client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "Você é um assistente virtual da BPG Telecom. Responda sempre de forma clara e objetiva sobre planos, suporte técnico e atendimento ao cliente."},
                    {"role": "user", "content": msg_in}
                ]
            )
            
            reply = response.choices[0].message.content

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
