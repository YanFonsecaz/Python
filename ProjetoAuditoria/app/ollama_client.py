"""
Cliente Ollama para integração com modelos de IA locais.
"""

import os
import logging
from typing import Dict, Any, Optional, List
import ollama
from ollama import Client
from .prompt_security import security_manager, SAFE_TEMPLATES

logger = logging.getLogger(__name__)


class OllamaClient:
    """Cliente para interação com Ollama e modelos locais."""
    
    def __init__(self, host: str = None, model: str = "gemma3:4b"):
        """
        Inicializa o cliente Ollama.
        
        Args:
            host: URL do servidor Ollama (padrão: http://localhost:11434)
            model: Nome do modelo a ser usado (padrão: gemma3:4b)
        """
        self.host = host or os.getenv('OLLAMA_HOST', 'http://localhost:11434')
        self.model = model or os.getenv('OLLAMA_MODEL', 'gemma3:4b')
        self.client = Client(host=self.host)
        self.is_available = False
        
        # Verificar se o Ollama está disponível
        self._check_availability()
    
    def _check_availability(self) -> None:
        """Verifica se o Ollama está disponível e o modelo está instalado."""
        try:
            # Verificar se o servidor está rodando
            models = self.client.list()
            logger.info(f"Ollama conectado com sucesso. Modelos disponíveis: {len(models.get('models', []))}")
            
            # Verificar se o modelo específico está disponível
            # Os objetos Model têm o atributo 'model', não 'name'
            model_names = [model.model for model in models.get('models', [])]
            if self.model in model_names or any(self.model in name for name in model_names):
                self.is_available = True
                logger.info(f"Modelo {self.model} está disponível")
            else:
                logger.warning(f"Modelo {self.model} não encontrado. Tentando baixar...")
                self._pull_model()
                
        except Exception as e:
            logger.error(f"Erro ao conectar com Ollama: {e}")
            self.is_available = False
    
    def _pull_model(self) -> None:
        """Baixa o modelo se não estiver disponível."""
        try:
            logger.info(f"Baixando modelo {self.model}...")
            self.client.pull(self.model)
            self.is_available = True
            logger.info(f"Modelo {self.model} baixado com sucesso")
        except Exception as e:
            logger.error(f"Erro ao baixar modelo {self.model}: {e}")
            self.is_available = False
    
    def generate_response(self, prompt: str, system_prompt: str = None, 
                         temperature: float = 0.7, max_tokens: int = 2000) -> Optional[str]:
        """
        Gera uma resposta usando o modelo Ollama.
        
        Args:
            prompt: Prompt do usuário
            system_prompt: Prompt do sistema (opcional)
            temperature: Temperatura para geração (0.0 a 1.0)
            max_tokens: Número máximo de tokens
            
        Returns:
            Resposta gerada pelo modelo ou None se houver erro
        """
        if not self.is_available:
            logger.error("Ollama não está disponível")
            return None
        
        try:
            messages = []
            
            if system_prompt:
                messages.append({
                    'role': 'system',
                    'content': system_prompt
                })
            
            messages.append({
                'role': 'user',
                'content': prompt
            })
            
            response = self.client.chat(
                model=self.model,
                messages=messages,
                options={
                    'temperature': temperature,
                    'num_predict': max_tokens
                }
            )
            
            return response['message']['content']
            
        except Exception as e:
            logger.error(f"Erro ao gerar resposta com Ollama: {e}")
            return None
    
    def analyze_seo_content(self, content: str, url: str) -> Optional[Dict[str, Any]]:
        """
        Analisa conteúdo para problemas de SEO.
        
        Args:
            content: Conteúdo HTML da página
            url: URL da página
            
        Returns:
            Análise de SEO estruturada
        """
        try:
            # Validação de segurança da entrada
            security_result = security_manager.detect_threats(content)
            if not security_result.is_safe:
                logger.warning(f"Conteúdo suspeito detectado para URL {url}: {security_result.warnings}")
                content = security_result.sanitized_content
            
            # Limita tamanho do conteúdo (8000 tokens ≈ 32000 caracteres)
            if len(content) > 32000:
                content = content[:32000] + "... [truncado por segurança]"
                logger.info(f"Conteúdo HTML truncado para URL {url}")
            
            # System prompt seguro
            system_prompt = """Você é um especialista técnico em SEO. Analise o conteúdo HTML fornecido e retorne APENAS um JSON válido com a seguinte estrutura:

{
  "title_issues": ["lista de problemas com title"],
  "meta_description_issues": ["lista de problemas com meta description"],
  "heading_issues": ["lista de problemas com headings H1-H6"],
  "image_issues": ["lista de problemas com imagens e alt text"],
  "link_issues": ["lista de problemas com links"],
  "content_issues": ["lista de problemas com conteúdo"],
  "technical_issues": ["lista de problemas técnicos"],
  "recommendations": ["lista de recomendações prioritárias"]
}

IMPORTANTE: Responda APENAS com JSON válido. Não inclua explicações adicionais."""
            
            # Cria prompt seguro usando template
            safe_prompt = security_manager.create_safe_prompt(
                SAFE_TEMPLATES["html_analysis"],
                url=url,
                content=content
            )
            
            # Gera resposta
            response = self.generate_response(safe_prompt, system_prompt)
            
            # Valida resposta
            if not security_manager.validate_response(response):
                logger.error(f"Resposta suspeita detectada para URL {url}")
                return {"error": "Resposta inválida por motivos de segurança"}
            
            return response
            
        except Exception as e:
            logger.error(f"Erro na análise SEO para {url}: {e}")
            return {"error": f"Erro na análise: {str(e)}"}
    
    def generate_seo_documentation(self, audit_data: Dict[str, Any]) -> Optional[str]:
        """
        Gera documentação técnica de SEO baseada nos dados da auditoria.
        
        Args:
            audit_data: Dados da auditoria de SEO
            
        Returns:
            Documentação em formato Markdown ou None se houver erro
        """
        try:
            # Converte dados para string segura
            import json
            audit_str = json.dumps(audit_data, ensure_ascii=False, indent=2)
            
            # Validação de segurança da entrada
            security_result = security_manager.detect_threats(audit_str)
            if not security_result.is_safe:
                logger.warning(f"Dados de auditoria suspeitos detectados: {security_result.warnings}")
                audit_str = security_result.sanitized_content
            
            # Limita tamanho dos dados (6000 tokens ≈ 24000 caracteres)
            if len(audit_str) > 24000:
                audit_str = audit_str[:24000] + "... [truncado por segurança]"
                logger.info("Dados de auditoria truncados por segurança")
            
            # System prompt seguro
            system_prompt = """Você é um especialista em SEO técnico. Gere documentação técnica profissional em Markdown baseada nos dados de auditoria fornecidos.

ESTRUTURA OBRIGATÓRIA:
# Relatório de Auditoria SEO

## 1. RESUMO EXECUTIVO
- Visão geral dos principais problemas
- Impacto estimado no tráfego orgânico
- Prioridades de correção

## 2. PROBLEMAS CRÍTICOS
### [Nome do Problema]
- **Descrição**: [descrição técnica]
- **Evidências**: [evidências encontradas]
- **Impacto**: [impacto no SEO]
- **Solução**: [passos para correção]
- **Prazo**: [estimativa de tempo]

## 3. PROBLEMAS IMPORTANTES
[Mesmo formato dos críticos]

## 4. MELHORIAS RECOMENDADAS
[Mesmo formato]

## 5. MÉTRICAS E KPIs
- Métricas atuais relevantes
- Metas sugeridas

## 6. CRONOGRAMA DE IMPLEMENTAÇÃO
- Fase 1 (Crítico): [prazo]
- Fase 2 (Importante): [prazo]
- Fase 3 (Melhorias): [prazo]

IMPORTANTE: Mantenha o foco técnico e seja específico nas recomendações."""
            
            # Cria prompt seguro usando template
            safe_prompt = security_manager.create_safe_prompt(
                SAFE_TEMPLATES["seo_documentation"],
                context=audit_str
            )
            
            # Gera resposta
            response = self.generate_response(safe_prompt, system_prompt)
            
            # Valida resposta
            if not security_manager.validate_response(response):
                logger.error("Resposta suspeita detectada na geração de documentação")
                return None
            
            logger.info("Documentação SEO gerada com sucesso")
            return response
            
        except Exception as e:
            logger.error(f"Erro na geração de documentação SEO: {e}")
            return None
    
    def get_model_info(self) -> Dict[str, Any]:
        """
        Retorna informações sobre o modelo atual.
        
        Returns:
            Informações do modelo
        """
        return {
            'model': self.model,
            'host': self.host,
            'available': self.is_available,
            'client_type': 'ollama'
        }


# Instância global do cliente Ollama
ollama_client = None

def get_ollama_client() -> OllamaClient:
    """
    Retorna a instância global do cliente Ollama.
    
    Returns:
        Instância do OllamaClient
    """
    global ollama_client
    if ollama_client is None:
        ollama_client = OllamaClient()
    return ollama_client