def responder(mensagem):
    if mensagem.lower() == "oi":
        return "Olá! Como posso te ajudar?"
    elif mensagem.lower() == "tchau":
        return "Até mais!"
    else:
        return "Não entendi. Pode repetir?"

while True:
    entrada = input("Você: ")
    if entrada.lower() == "sair":
        break
    resposta = responder(entrada)
    print("Bot:", resposta)
