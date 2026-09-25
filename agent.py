import os
from dotenv import load_dotenv
from google import genai

load_dotenv()

client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

# 1. Carrega as regras do OpenSpec
with open("AGENTS.md", "r", encoding="utf-8") as f:
    openspec_rules = f.read()

# 2. Informa explicitamente que a proposta foi APROVADA e exige a fase APPLY
prompt_usuario = """
A proposta CHG-001-LOGIN-BASE foi APROVADA na revisão! 
Proceda imediatamente para a fase APPLY e gere o código Python/Reflex completo e pronto para uso da tela de login e seu respectivo State.
"""

prompt_final = f"""
És o assistente de desenvolvimento do projeto Famarcia_Anonima.
Siga estritamente as regras do OpenSpec definidas abaixo:

--- REGRAS OPENSPEC ---
{openspec_rules}

INSTRUÇÃO ATUAL DO USUÁRIO:
{prompt_usuario}
"""

# 3. Executa a chamada
chat = client.chats.create(model="models/gemma-4-26b-a4b-it")
response = chat.send_message(prompt_final)

print("\n--- CÓDIGO DA FASE APPLY ---")
print(response.text)
print("----------------------------\n")