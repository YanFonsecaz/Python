#!/usr/bin/env python3
"""
Teste de Integração dos Agentes de IA SEO
Testa o sistema completo com os novos agentes especializados integrados.
"""

import requests
import json
import time
import sys
from typing import Dict, Any

class IntegratedAgentsTest:
    """Classe para testar os agentes de IA integrados no sistema."""
    
    def __init__(self, base_url: str = "http://127.0.0.1:5000"):
        """
        Inicializa o teste.
        
        Args:
            base_url: URL base da API Flask
        """
        self.base_url = base_url
        self.session = requests.Session()
        
    def test_health_check(self) -> bool:
        """Testa se a API está funcionando."""
        try:
            response = self.session.get(f"{self.base_url}/health")
            if response.status_code == 200:
                print("✅ Health check passou - API está funcionando")
                return True
            else:
                print(f"❌ Health check falhou - Status: {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ Erro no health check: {str(e)}")
            return False
    
    def start_audit_with_agents(self, url: str) -> Dict[str, Any]:
        """
        Inicia uma auditoria completa com os agentes integrados.
        
        Args:
            url: URL para auditar
            
        Returns:
            Resultado da auditoria
        """
        try:
            print(f"\n🚀 Iniciando auditoria completa para: {url}")
            
            payload = {
                "url": url,
                "options": {
                    "enable_crawler": True,
                    "enable_apis": True,
                    "enable_chrome_validations": True,
                    "crawler_depth": 2,
                    "max_pages": 10
                }
            }
            
            response = self.session.post(
                f"{self.base_url}/audit/start",
                json=payload,
                headers={'Content-Type': 'application/json'}
            )
            
            if response.status_code in [200, 202]:  # 202 é aceito para auditoria assíncrona
                result = response.json()
                audit_id = result.get('audit_id')
                print(f"✅ Auditoria iniciada - ID: {audit_id}")
                return result
            else:
                print(f"❌ Erro ao iniciar auditoria - Status: {response.status_code}")
                print(f"Resposta: {response.text}")
                return {}
                
        except Exception as e:
            print(f"❌ Erro ao iniciar auditoria: {str(e)}")
            return {}
    
    def monitor_audit_progress(self, audit_id: str, max_wait: int = 300) -> Dict[str, Any]:
        """
        Monitora o progresso da auditoria.
        
        Args:
            audit_id: ID da auditoria
            max_wait: Tempo máximo de espera em segundos
            
        Returns:
            Status final da auditoria
        """
        print(f"\n📊 Monitorando progresso da auditoria {audit_id}...")
        
        start_time = time.time()
        last_progress = -1
        
        while time.time() - start_time < max_wait:
            try:
                response = self.session.get(f"{self.base_url}/audit/status/{audit_id}")
                
                if response.status_code == 200:
                    status = response.json()
                    current_progress = status.get('progress', 0)
                    current_step = status.get('current_step', 'unknown')
                    audit_status = status.get('status', 'unknown')
                    
                    # Mostrar progresso apenas se mudou
                    if current_progress != last_progress:
                        print(f"📈 Progresso: {current_progress}% - Etapa: {current_step}")
                        last_progress = current_progress
                    
                    # Verificar se completou
                    if audit_status == 'completed':
                        print("✅ Auditoria completada!")
                        return status
                    elif audit_status == 'failed':
                        print("❌ Auditoria falhou!")
                        return status
                    
                    time.sleep(5)  # Aguardar 5 segundos antes da próxima verificação
                else:
                    print(f"❌ Erro ao verificar status - Status: {response.status_code}")
                    break
                    
            except Exception as e:
                print(f"❌ Erro ao monitorar progresso: {str(e)}")
                break
        
        print("⏰ Timeout - Auditoria não completou no tempo esperado")
        return {}
    
    def get_audit_results(self, audit_id: str) -> Dict[str, Any]:
        """
        Obtém os resultados detalhados da auditoria.
        
        Args:
            audit_id: ID da auditoria
            
        Returns:
            Resultados da auditoria
        """
        try:
            response = self.session.get(f"{self.base_url}/audit/result/{audit_id}")
            
            if response.status_code == 200:
                return response.json()
            else:
                print(f"❌ Erro ao obter resultados - Status: {response.status_code}")
                return {}
                
        except Exception as e:
            print(f"❌ Erro ao obter resultados: {str(e)}")
            return {}
    
    def analyze_agent_results(self, results: Dict[str, Any]) -> None:
        """
        Analisa os resultados dos agentes de IA.
        
        Args:
            results: Resultados da auditoria
        """
        print("\n🔍 ANÁLISE DOS RESULTADOS DOS AGENTES DE IA")
        print("=" * 50)
        
        # Analisar etapas da auditoria
        steps = results.get('steps', [])
        validation_step = None
        documentation_step = None
        
        for step in steps:
            if step.get('step') == 'validations_execution':
                validation_step = step
            elif step.get('step') == 'documentation_generation':
                documentation_step = step
        
        # Resultados do Agente de Auditoria SEO
        if validation_step:
            print("\n🤖 AGENTE DE AUDITORIA SEO:")
            print(f"   • Problemas SEO encontrados: {validation_step.get('seo_problems_found', 0)}")
            print(f"   • Validações originais: {validation_step.get('original_validations_count', 0)}")
            print(f"   • Auditoria SEO bem-sucedida: {validation_step.get('seo_audit_success', False)}")
            print(f"   • Score geral: {validation_step.get('overall_score', 0)}")
        
        # Resultados do Agente de Documentação SEO
        if documentation_step:
            print("\n📝 AGENTE DE DOCUMENTAÇÃO SEO:")
            print(f"   • Seções SEO geradas: {documentation_step.get('seo_sections_generated', 0)}")
            print(f"   • Tem documentação SEO: {documentation_step.get('has_seo_documentation', False)}")
            print(f"   • URL documento original: {documentation_step.get('original_document_url', 'N/A')}")
        
        # Dados detalhados da auditoria SEO
        seo_audit_data = results.get('seo_audit_data', {})
        if seo_audit_data.get('success'):
            print(f"\n📊 ESTATÍSTICAS DA AUDITORIA SEO:")
            stats = seo_audit_data.get('statistics', {})
            print(f"   • Total de URLs auditadas: {stats.get('total_urls', 0)}")
            print(f"   • Total de problemas: {stats.get('total_problems', 0)}")
            print(f"   • Problemas críticos: {stats.get('critical_problems', 0)}")
            print(f"   • Problemas de rastreio: {stats.get('crawling_problems', 0)}")
            print(f"   • Problemas de Core Web Vitals: {stats.get('cwv_problems', 0)}")
        
        # Documentação gerada
        documentation = results.get('documentation', {})
        if 'seo_specialized' in documentation:
            seo_doc = documentation['seo_specialized']
            if seo_doc.get('status') == 'no_problems':
                print(f"\n✅ {seo_doc.get('message', 'Sem problemas encontrados')}")
            else:
                sections = seo_doc.get('sections', [])
                print(f"\n📋 SEÇÕES DE DOCUMENTAÇÃO GERADAS: {len(sections)}")
                for i, section in enumerate(sections[:3], 1):  # Mostrar apenas as 3 primeiras
                    print(f"   {i}. {section.get('title', 'Sem título')}")
                    print(f"      Severidade: {section.get('severity', 'N/A')}")
                    print(f"      Categoria: {section.get('category', 'N/A')}")
    
    def run_complete_test(self, test_url: str = "https://example.com") -> bool:
        """
        Executa o teste completo do sistema integrado.
        
        Args:
            test_url: URL para testar
            
        Returns:
            True se todos os testes passaram
        """
        print("🧪 TESTE COMPLETO DOS AGENTES DE IA INTEGRADOS")
        print("=" * 60)
        
        # 1. Verificar saúde da API
        if not self.test_health_check():
            return False
        
        # 2. Iniciar auditoria
        audit_result = self.start_audit_with_agents(test_url)
        if not audit_result:
            return False
        
        audit_id = audit_result.get('audit_id')
        if not audit_id:
            print("❌ ID da auditoria não encontrado")
            return False
        
        # 3. Monitorar progresso
        final_status = self.monitor_audit_progress(audit_id)
        if not final_status or final_status.get('status') != 'completed':
            print("❌ Auditoria não completou com sucesso")
            return False
        
        # 4. Obter e analisar resultados
        results = self.get_audit_results(audit_id)
        if not results:
            print("❌ Não foi possível obter resultados")
            return False
        
        # 5. Analisar resultados dos agentes
        self.analyze_agent_results(results)
        
        print("\n✅ TESTE COMPLETO CONCLUÍDO COM SUCESSO!")
        print("🎉 Os agentes de IA estão funcionando corretamente!")
        
        return True

def main():
    """Função principal do teste."""
    if len(sys.argv) > 1:
        test_url = sys.argv[1]
    else:
        test_url = "https://httpbin.org"  # URL de teste confiável
    
    print(f"🎯 URL de teste: {test_url}")
    
    tester = IntegratedAgentsTest()
    success = tester.run_complete_test(test_url)
    
    if success:
        print("\n🎊 TODOS OS TESTES PASSARAM!")
        sys.exit(0)
    else:
        print("\n💥 ALGUNS TESTES FALHARAM!")
        sys.exit(1)

if __name__ == "__main__":
    main()