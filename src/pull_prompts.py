"""
Script para fazer pull de prompts do LangSmith Prompt Hub.

Este script:
1. Conecta ao LangSmith usando credenciais do .env
2. Faz pull do prompt semente do desafio
3. Salva localmente em prompts/bug_to_user_story_v1.yml
"""

import sys
from pathlib import Path
from dotenv import load_dotenv
from langsmith import Client
from utils import save_yaml, check_env_vars, print_section_header

load_dotenv()

SEED_PROMPT = "leonanluppi/bug_to_user_story_v1"
OUTPUT_PATH = Path(__file__).parent.parent / "prompts" / "bug_to_user_story_v1.yml"


def _message_template(message) -> str:
    """Extrai o texto do template de uma mensagem do ChatPromptTemplate."""
    return message.prompt.template


def pull_prompts_from_langsmith() -> bool:
    """Faz pull do prompt semente e salva em YAML. Retorna True se sucesso."""
    print(f"Fazendo pull do prompt: {SEED_PROMPT}")

    try:
        client = Client()
        prompt = client.pull_prompt(SEED_PROMPT, dangerously_pull_public_prompt=True)
    except Exception as e:
        print(f"❌ Erro ao fazer pull do prompt: {e}")
        return False

    system_prompt = ""
    user_prompt = ""
    for message in prompt.messages:
        kind = type(message).__name__
        if "System" in kind:
            system_prompt = _message_template(message)
        elif "Human" in kind:
            user_prompt = _message_template(message)

    data = {
        "bug_to_user_story_v1": {
            "description": "Prompt para converter relatos de bugs em User Stories",
            "system_prompt": system_prompt,
            "user_prompt": user_prompt,
            "version": "v1",
            "tags": ["bug-analysis", "user-story", "product-management"],
        }
    }

    if not save_yaml(data, str(OUTPUT_PATH)):
        return False

    print(f"✓ Prompt salvo em {OUTPUT_PATH}")
    return True


def main():
    """Função principal"""
    print_section_header("PULL DE PROMPTS DO LANGSMITH")

    if not check_env_vars(["LANGSMITH_API_KEY"]):
        return 1

    return 0 if pull_prompts_from_langsmith() else 1


if __name__ == "__main__":
    sys.exit(main())
