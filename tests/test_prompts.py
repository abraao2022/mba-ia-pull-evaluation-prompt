"""
Testes automatizados para validação de prompts.
"""
import re
import pytest
import yaml
import sys
from pathlib import Path

# Adicionar src ao path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from utils import validate_prompt_structure

PROMPT_FILE = Path(__file__).parent.parent / "prompts" / "bug_to_user_story_v2.yml"


def load_prompts(file_path: str):
    """Carrega prompts do arquivo YAML."""
    with open(file_path, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f)


@pytest.fixture(scope="module")
def prompt():
    return load_prompts(str(PROMPT_FILE))["bug_to_user_story_v2"]


class TestPrompts:
    def test_prompt_has_system_prompt(self, prompt):
        """Verifica se o campo 'system_prompt' existe e não está vazio."""
        assert "system_prompt" in prompt
        assert prompt["system_prompt"].strip()

    def test_prompt_has_role_definition(self, prompt):
        """Verifica se o prompt define uma persona (ex: "Você é um Product Manager")."""
        text = prompt["system_prompt"]
        assert re.search(r"Você é (uma?|um)\s+\w+", text), "Persona não definida"
        assert re.search(r"Product Manager", text, re.IGNORECASE)

    def test_prompt_mentions_format(self, prompt):
        """Verifica se o prompt exige formato Markdown ou User Story padrão."""
        text = prompt["system_prompt"]
        assert "Markdown" in text or "Como [persona]" in text
        assert "Critérios de Aceitação" in text
        assert "Dado" in text and "Quando" in text and "Então" in text

    def test_prompt_has_few_shot_examples(self, prompt):
        """Verifica se o prompt contém exemplos de entrada/saída (técnica Few-shot)."""
        text = prompt["system_prompt"]
        assert len(re.findall(r"### Exemplo \d+", text)) >= 2
        assert text.count("Relato de Bug:") >= 2
        assert text.count("User Story:") >= 2

    def test_prompt_no_todos(self, prompt):
        """Garante que você não esqueceu nenhum `[TODO]` no texto."""
        full = prompt["system_prompt"] + prompt.get("user_prompt", "")
        assert "[TODO]" not in full
        assert "TODO" not in full

    def test_minimum_techniques(self, prompt):
        """Verifica (através dos metadados do yaml) se pelo menos 2 técnicas foram listadas."""
        techniques = prompt.get("techniques_applied", [])
        assert len(techniques) >= 2
        is_valid, errors = validate_prompt_structure(prompt)
        assert is_valid, errors


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
