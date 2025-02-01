from flask import Flask, request, jsonify, render_template
import sqlite3
import openai
import os

app = Flask(__name__)

# Conectar ao banco de dados SQLite
conn = sqlite3.connect("conversas.db", check_same_thread=False)
c = conn.cursor()
c.execute('''CREATE TABLE IF NOT EXISTS chats (id INTEGER PRIMARY KEY AUTOINCREMENT, sender TEXT, message TEXT, response TEXT, timestamp DATETIME DEFAULT CURRENT_TIMESTAMP)''')
conn.commit()

def salvar_conversa(sender, message, response):
    c.execute("INSERT INTO chats (sender, message, response) VALUES (?, ?, ?)", (sender, message, response))
    conn.commit()

@app.route("/")
def index():
    c.execute("SELECT * FROM chats ORDER BY timestamp DESC")
    messages = c.fetchall()
    return render_template("index.html", messages=messages)

@app.route("/send", methods=["POST"])
def send_message():
    data = request.json
    sender = data.get("sender")
    message = data.get("message")

    # Gerar resposta do ChatGPT
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "system", "content": "Você é um assistente da BPG Telecom."},
                  {"role": "user", "content": message}]
    )
    
    reply = response["choices"][0]["message"]["content"]
    salvar_conversa(sender, message, reply)

    return jsonify({"reply": reply})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)

