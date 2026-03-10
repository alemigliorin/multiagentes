from agent import orquestrador

print("Acionando o orquestrador...")
try:
    response = orquestrador.run("Quero uma imagem de um macaco chutando uma bola de futebol no gol")
    print(response.content)
except Exception as e:
    print(f"Erro fatal: {e}")
