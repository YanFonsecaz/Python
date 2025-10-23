"""
Módulo de segurança para prompts contra ataques de prompt injection.

Este módulo implementa várias camadas de proteção:
1. Sanitização de entrada
2. Validação de conteúdo
3. Templates seguros
4. Limitação de tokens
5. Filtragem de conteúdo malicioso
"""

import re
import json
import logging
from typing import Dict, List, Any, Optional, Union
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)


class ThreatLevel(Enum):
    """Níveis de ameaça detectados."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass
class SecurityResult:
    """Resultado da análise de segurança."""
    is_safe: bool
    threat_level: ThreatLevel
    sanitized_content: str
    warnings: List[str]
    blocked_patterns: List[str]


class PromptSecurityManager:
    """
    Gerenciador de segurança para prompts de IA.
    
    Implementa múltiplas camadas de proteção contra prompt injection,
    jailbreaking e outros ataques maliciosos.
    """
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
        # Padrões maliciosos conhecidos
        self.malicious_patterns = [
            # Tentativas de jailbreak
            r"ignore\s+(all\s+)?previous\s+instructions",
            r"forget\s+(everything|all)\s+(above|before)",
            r"you\s+are\s+now\s+(jailbroken|unrestricted)",
            r"disregard\s+your\s+(safety\s+)?filters",
            r"act\s+as\s+(an?\s+)?(admin|administrator|root)",
            r"enable\s+(developer|debug)\s+mode",
            r"bypass\s+(restrictions|safety|security)",
            
            # Tentativas de extração de prompt
            r"what\s+(are\s+)?your\s+(system\s+)?instructions",
            r"show\s+me\s+your\s+(system\s+)?prompt",
            r"reveal\s+your\s+(system\s+)?prompt",
            r"tell\s+me\s+your\s+(system\s+)?prompt",
            
            # Comandos de sistema perigosos
            r"import\s+os",
            r"os\.system",
            r"subprocess\.",
            r"exec\s*\(",
            r"eval\s*\(",
            r"__import__",
            
            # Tentativas de injeção
            r"<script[^>]*>",
            r"javascript:",
            r"data:text/html",
            r"vbscript:",
        ]
        
        # Palavras-chave suspeitas
        self.suspicious_keywords = [
            "jailbreak", "bypass", "override", "ignore instructions",
            "forget everything", "new task", "system override",
            "admin access", "root privileges", "unrestricted mode",
            "developer console", "debug mode", "maintenance mode"
        ]
        
        # Limites de segurança
        self.max_prompt_length = 10000
        self.max_json_depth = 5
        self.max_repeated_chars = 50
        
    def sanitize_input(self, content: str) -> str:
        """
        Sanitiza entrada do usuário removendo conteúdo perigoso.
        
        Args:
            content: Conteúdo a ser sanitizado
            
        Returns:
            Conteúdo sanitizado
        """
        if not content:
            return ""
            
        # Converte para string se necessário
        if not isinstance(content, str):
            content = str(content)
        
        # Remove caracteres de controle
        content = re.sub(r'[\x00-\x1f\x7f-\x9f]', '', content)
        
        # Remove tags HTML/XML perigosas
        content = re.sub(r'<script[^>]*>.*?</script>', '', content, flags=re.IGNORECASE | re.DOTALL)
        content = re.sub(r'<[^>]+>', '', content)
        
        # Remove tentativas de prompt injection
        injection_patterns = [
            r'ignore\s+(all\s+)?(previous\s+)?instructions',
            r'forget\s+(everything|all)\s+(above|before)',
            r'disregard\s+your\s+(safety\s+)?filters',
            r'act\s+as\s+(an?\s+)?(admin|administrator|root)',
            r'bypass\s+(restrictions|safety|security)',
            r'what\s+(are\s+)?your\s+(system\s+)?instructions',
            r'show\s+me\s+your\s+(system\s+)?prompt',
            r'reveal\s+your\s+(system\s+)?prompt',
            r'tell\s+me\s+your\s+(system\s+)?prompt'
        ]
        
        for pattern in injection_patterns:
            content = re.sub(pattern, '[CONTEÚDO REMOVIDO]', content, flags=re.IGNORECASE)
        
        # Remove comandos de sistema perigosos
        system_patterns = [
            r'import\s+os',
            r'os\.system',
            r'subprocess\.',
            r'exec\s*\(',
            r'eval\s*\(',
            r'__import__',
            r'system\s*\(',
            r'rm\s+-rf'
        ]
        
        for pattern in system_patterns:
            content = re.sub(pattern, '[COMANDO REMOVIDO]', content, flags=re.IGNORECASE)
        
        # Remove tentativas de encoding bypass
        content = re.sub(r'\\x[0-9a-fA-F]{2}', '', content)
        content = re.sub(r'\\u[0-9a-fA-F]{4}', '', content)
        
        # Remove múltiplos espaços em branco
        content = re.sub(r'\s+', ' ', content)
        
        # Limita o tamanho
        if len(content) > self.max_prompt_length:
            content = content[:self.max_prompt_length] + "\n\n[Conteúdo truncado por segurança]"
        
        return content.strip()
    
    def detect_threats(self, content: str) -> SecurityResult:
        """
        Detecta ameaças no conteúdo fornecido.
        
        Args:
            content: Conteúdo a ser analisado
            
        Returns:
            Resultado da análise de segurança
        """
        if not content:
            return SecurityResult(
                is_safe=True,
                threat_level=ThreatLevel.LOW,
                sanitized_content="",
                warnings=[],
                blocked_patterns=[]
            )
        
        # Sanitiza o conteúdo primeiro
        sanitized = self.sanitize_input(content)
        
        warnings = []
        blocked_patterns = []
        threat_level = ThreatLevel.LOW
        
        # Converte para minúsculas para análise case-insensitive
        content_lower = content.lower()
        
        # Verifica padrões maliciosos
        for pattern in self.malicious_patterns:
            if re.search(pattern, content_lower, re.IGNORECASE):
                blocked_patterns.append(pattern)
                threat_level = ThreatLevel.HIGH
        
        # Verifica palavras-chave suspeitas
        suspicious_found = []
        for keyword in self.suspicious_keywords:
            if keyword.lower() in content_lower:
                suspicious_found.append(keyword)
        
        if suspicious_found:
            warnings.append(f"Palavras suspeitas encontradas: {', '.join(suspicious_found)}")
            if threat_level == ThreatLevel.LOW:
                threat_level = ThreatLevel.MEDIUM
        
        # Verifica estrutura JSON muito profunda
        if self._check_json_depth(content) > self.max_json_depth:
            warnings.append("Estrutura JSON muito profunda detectada")
            if threat_level == ThreatLevel.LOW:
                threat_level = ThreatLevel.MEDIUM
        
        # Determina se é seguro
        is_safe = threat_level == ThreatLevel.LOW and len(blocked_patterns) == 0
        
        return SecurityResult(
            is_safe=is_safe,
            threat_level=threat_level,
            sanitized_content=sanitized,
            warnings=warnings,
            blocked_patterns=blocked_patterns
        )
    
    def _check_json_depth(self, content: str) -> int:
        """
        Verifica a profundidade de estruturas JSON.
        
        Args:
            content: Conteúdo a ser verificado
            
        Returns:
            Profundidade máxima encontrada
        """
        try:
            if not (content.strip().startswith('{') or content.strip().startswith('[')):
                return 0
            
            data = json.loads(content)
            return self._get_depth(data)
        except (json.JSONDecodeError, TypeError, ValueError):
            return 0
    
    def _get_depth(self, obj: Any) -> int:
        """
        Calcula recursivamente a profundidade de um objeto.
        
        Args:
            obj: Objeto a ser analisado
            
        Returns:
            Profundidade do objeto
        """
        if isinstance(obj, dict):
            if not obj:
                return 1
            return 1 + max(self._get_depth(value) for value in obj.values())
        elif isinstance(obj, list):
            if not obj:
                return 1
            return 1 + max(self._get_depth(item) for item in obj)
        else:
            return 1
    
    def create_safe_prompt(self, template_name: str, **kwargs) -> str:
        """
        Cria um prompt seguro usando templates predefinidos.
        
        Args:
            template_name: Nome do template a ser usado
            **kwargs: Variáveis para substituir no template
            
        Returns:
            Prompt seguro formatado
            
        Raises:
            ValueError: Se o template não existir ou variáveis estiverem faltando
        """
        if template_name not in SAFE_TEMPLATES:
            raise ValueError(f"Template inválido: '{template_name}' não encontrado")
        
        template = SAFE_TEMPLATES[template_name]
        
        # Sanitizar todas as variáveis de entrada
        sanitized_kwargs = {}
        for key, value in kwargs.items():
            if isinstance(value, str):
                sanitized_kwargs[key] = self.sanitize_input(value)
            else:
                sanitized_kwargs[key] = value
        
        try:
            return template.format(**sanitized_kwargs)
        except KeyError as e:
            raise ValueError(f"Template inválido: Variável obrigatória faltando no template: {e}")
        except Exception as e:
            raise ValueError(f"Erro ao formatar template: {e}")
    
    def validate_response(self, response: str) -> bool:
        """
        Valida se a resposta da IA não contém vazamentos de prompt.
        
        Args:
            response: Resposta da IA a ser validada
            
        Returns:
            True se a resposta é segura, False caso contrário
        """
        if not response:
            return True
        
        response_lower = response.lower()
        
        # Padrões que indicam vazamento de prompt
        leak_patterns = [
            r"based on my system prompt",
            r"my (system )?prompt (says|tells|instructs)",
            r"according to (my|the) (system )?prompt",
            r"my instructions (are|tell|say)",
            r"the user asked me to ignore",
            r"i was (told|instructed|programmed) to",
            r"my role is to",
            r"i am programmed to",
            r"system prompt",
            r"previous instructions",
            r"ignore instructions"
        ]
        
        for pattern in leak_patterns:
            if re.search(pattern, response_lower):
                return False
        
        return True


# Templates seguros pré-definidos
SAFE_TEMPLATES = {
    "seo_analysis": """Analise os seguintes problemas de SEO encontrados:

Resumo: {summary}

Principais problemas: {problems}

IMPORTANTE: Mantenha o foco apenas em análise técnica de SEO. Forneça uma análise concisa dos principais problemas e recomendações de priorização.""",

    "seo_documentation": """Gere documentação técnica profissional para o seguinte problema de SEO:

Contexto: {context}

IMPORTANTE: Mantenha o foco apenas em documentação técnica de SEO. Formate a resposta seguindo esta estrutura:
1. PROBLEMA/OPORTUNIDADE: Descrição técnica clara
2. EVIDÊNCIAS: Lista das evidências encontradas
3. IMPACTO: Análise do impacto atual
4. SOLUÇÃO: Passos técnicos detalhados
5. VALIDAÇÃO: Como verificar se foi corrigido
6. BENEFÍCIOS: Resultados esperados
7. CRONOGRAMA: Estimativa de tempo

Seja técnico, preciso e acionável.""",

    "html_analysis": """Analise o seguinte conteúdo HTML da URL: {url}

Conteúdo: {content}

IMPORTANTE: Mantenha o foco apenas em análise técnica de SEO. Forneça uma análise detalhada de SEO seguindo o formato JSON especificado no prompt do sistema."""
}


# Instância global do gerenciador de segurança
security_manager = PromptSecurityManager()