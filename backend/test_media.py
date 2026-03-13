# noqa: E501
from media_tools import gerar_imagem

print("Testando geração de imagem (Google GenAI Imagen 3)...")
resultado_imagem = gerar_imagem("Um cenário cyberpunk no Brasil, com um vira-lata caramelo robótico. Alta qualidade, 4k, hyper-realista, iluminação neon.")
print(f"Resultado Imagem:\n{resultado_imagem}\n")

# print("Testando geração de vídeo (Google Veo) - isso pode falhar se a chave não tiver acesso ao beta...")
# resultado_video = gerar_video("Um vira-lata caramelo andando lentamente por uma rua neon do Rio de Janeiro cyberpunk, chovendo, câmera lenta cinematográfica.")
# print(f"Resultado Vídeo:\n{resultado_video}\n")
