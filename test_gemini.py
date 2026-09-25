import os
from dotenv import load_dotenv
from google import genai

load_dotenv()

client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

# 1. Busca os modelos disponíveis na sua chave
print("Buscando modelos disponíveis na sua conta...")
models_list = []
try:
    for m in client.models.list():
        # Filtra apenas modelos que geram conteúdo
        if "generateContent" in getattr(m, "supported_actions", []) or "generateContent" in getattr(m, "supported_generation_methods", []):
            models_list.append(m.name)
except Exception as e:
    print(f"Erro ao listar modelos: {e}")

# 2. Tenta fazer a chamada com o primeiro modelo disponível
if not models_list:
    # Caso a listagem não venha formatada, tenta os nomes padrão
    models_list = ["models/gemini-1.5-flash", "models/gemini-1.5-pro", "gemini-1.5-flash"]

print(f"Modelos encontrados: {models_list[:3]}")

for model_name in models_list:
    try:
        print(f"Testando com o modelo: {model_name}...")
        response = client.models.generate_content(
            model=model_name,
            contents="Olá! Confirma que está funcionando?",
        )
        print("\n--- RESPOSTA DA IA ---")
        print(response.text)
        print("----------------------\n")
        print(f"SUCESSO! Use o modelo '{model_name}' no seu projeto.")
        break
    except Exception as err:
        print(f"Falha no modelo {model_name}: {err}\n")