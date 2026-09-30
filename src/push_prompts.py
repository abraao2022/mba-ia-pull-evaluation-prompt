"""
Script para fazer push de prompts otimizados ao LangSmith Prompt Hub.

Este script:
1. Lê os prompts otimizados de prompts/bug_to_user_story_v2.yml
2. Valida os prompts
3. Faz push PÚBLICO para o LangSmith Hub
4. Adiciona metadados (tags, descrição, técnicas utilizadas)
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv
from langsmith import Client
from langchain_core.prompts import ChatPromptTemplate
from utils import load_yaml, check_env_vars, print_section_header

load_dotenv()

PROMPT_FILE = Path(__file__).parent.parent / "prompts" / "bug_to_user_story_v2.yml"
PROMPT_KEY = "bug_to_user_story_v2"


def push_prompt_to_langsmith(prompt_name: str, prompt_data: dict) -> bool:
    """
    Faz push do prompt otimizado para o LangSmith Hub (PÚBLICO).

    Args:
        prompt_name: Nome do prompt (ex.: "handle/bug_to_user_story_v2")
        prompt_data: Dados do prompt

    Returns:
        True se sucesso, False caso contrário
    """
    try:
        prompt = ChatPromptTemplate.from_messages([
            ("system", prompt_data["system_prompt"]),
            ("user", prompt_data.get("user_prompt") or "{bug_report}"),
        ])

        techniques = prompt_data.get("techniques_applied", [])
        description = prompt_data.get("description", "")
        if techniques:
            description = f"{description} Técnicas: {', '.join(techniques)}."

        url = Client().push_prompt(
            prompt_name,
            object=prompt,
            is_public=True,
            description=description[:500],
            tags=prompt_data.get("tags", []),
        )
        print(f"✓ Push realizado: {url}")
        return True
    except Exception as e:
        print(f"❌ Erro ao fazer push do prompt: {e}")
        return False


def validate_prompt(prompt_data: dict) -> tuple[bool, list]:
    """
    Valida estrutura básica de um prompt (versão simplificada).

    Args:
        prompt_data: Dados do prompt

    Returns:
        (is_valid, errors) - Tupla com status e lista de erros
    """
    errors = []

    for field in ("description", "system_prompt", "version"):
        if not prompt_data.get(field):
            errors.append(f"Campo obrigatório faltando ou vazio: {field}")

    system_prompt = prompt_data.get("system_prompt", "")
    if "[TODO]" in system_prompt or "TODO" in system_prompt:
        errors.append("system_prompt contém TODO")

    user_prompt = prompt_data.get("user_prompt", "")
    if "{bug_report}" not in user_prompt and "{bug_report}" not in system_prompt:
        errors.append("O template precisa conter a variável {bug_report}")

    if len(prompt_data.get("techniques_applied", [])) < 2:
        errors.append("Liste ao menos 2 técnicas em techniques_applied")

    return (len(errors) == 0, errors)


def main():
    """Função principal"""
    print_section_header("PUSH DE PROMPTS PARA O LANGSMITH")

    if not check_env_vars(["LANGSMITH_API_KEY", "USERNAME_LANGSMITH_HUB"]):
        return 1

    data = load_yaml(str(PROMPT_FILE))
    if not data or PROMPT_KEY not in data:
        print(f"❌ Chave '{PROMPT_KEY}' não encontrada em {PROMPT_FILE}")
        return 1

    prompt_data = data[PROMPT_KEY]

    is_valid, errors = validate_prompt(prompt_data)
    if not is_valid:
        print("❌ Prompt inválido:")
        for error in errors:
            print(f"   - {error}")
        return 1

    username = os.getenv("USERNAME_LANGSMITH_HUB")
    prompt_name = f"{username}/{PROMPT_KEY}"
    print(f"Publicando {prompt_name}...")

    return 0 if push_prompt_to_langsmith(prompt_name, prompt_data) else 1


if __name__ == "__main__":
    sys.exit(main())
