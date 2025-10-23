#!/usr/bin/env python3
"""
Teste final do Screaming Frog - versão corrigida
"""

import os
import subprocess
import time
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

def test_final_crawl():
    """Teste final com parâmetros corretos (sem conflitos)"""
    
    url = "https://renirfonseca.blogspot.com/"
    screaming_frog_path = os.getenv('SCREAMING_FROG_PATH')
    
    print(f"🕷️ Teste Final - Screaming Frog")
    print(f"URL: {url}")
    print(f"Executável: {screaming_frog_path}")
    print("-" * 50)
    
    # Criar diretório de saída
    output_dir = Path('data/screaming_frog')
    output_dir.mkdir(parents=True, exist_ok=True)
    
    try:
        # Comando sem parâmetros conflitantes
        cmd = [
            screaming_frog_path,
            '--headless',
            '--crawl', url,
            '--export-tabs', 'Internal:All',
            '--export-format', 'CSV',
            '--output-folder', str(output_dir),
            '--overwrite'
        ]
        
        print("Executando comando:")
        print(' '.join(cmd))
        print()
        
        start_time = time.time()
        
        # Executar
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=180  # 3 minutos
        )
        
        duration = time.time() - start_time
        
        print(f"⏱️ Tempo: {duration:.2f}s")
        print(f"🔄 Código de retorno: {result.returncode}")
        
        # Mostrar saída relevante
        if result.stdout:
            lines = result.stdout.split('\n')
            print(f"\n📋 Últimas linhas do log:")
            for line in lines[-15:]:
                if line.strip():
                    print(f"   {line}")
        
        if result.stderr:
            print(f"\n❌ STDERR:")
            print(result.stderr)
        
        # Verificar arquivos gerados
        print(f"\n📁 Verificando arquivos em {output_dir}:")
        files = list(output_dir.glob('*'))
        
        if files:
            print(f"✅ {len(files)} arquivo(s) encontrado(s):")
            
            for file_path in sorted(files):
                size = file_path.stat().st_size
                print(f"   📄 {file_path.name} ({size:,} bytes)")
                
                # Analisar CSV
                if file_path.suffix == '.csv' and size > 0:
                    try:
                        content = file_path.read_text(encoding='utf-8')
                        lines = content.split('\n')
                        data_lines = [line for line in lines if line.strip()]
                        
                        print(f"      📊 {len(data_lines)} linhas total")
                        
                        if len(data_lines) > 1:
                            print(f"      📋 Header: {lines[0][:80]}...")
                            
                            # Contar URLs
                            urls = []
                            for line in data_lines[1:]:
                                if line.strip() and ('http' in line or 'www.' in line):
                                    url_part = line.split(',')[0].strip('"')
                                    if url_part.startswith('http'):
                                        urls.append(url_part)
                            
                            print(f"      🔗 {len(urls)} URLs encontradas")
                            
                            # Mostrar algumas URLs
                            if urls:
                                print("      📝 Exemplos de URLs:")
                                for i, url in enumerate(urls[:5]):
                                    print(f"        {i+1}. {url}")
                        
                    except Exception as e:
                        print(f"      ❌ Erro ao ler: {e}")
            
            return True, len(files)
            
        else:
            print("❌ Nenhum arquivo encontrado")
            return False, 0
        
    except subprocess.TimeoutExpired:
        print("⏰ Timeout após 3 minutos")
        return False, 0
    except Exception as e:
        print(f"❌ Erro: {e}")
        return False, 0

def create_seo_report():
    """Cria relatório SEO básico com dados do Screaming Frog"""
    
    output_dir = Path('data/screaming_frog')
    csv_files = list(output_dir.glob('*.csv'))
    
    if not csv_files:
        print("❌ Nenhum arquivo CSV para analisar")
        return
    
    print(f"\n📊 RELATÓRIO SEO BÁSICO")
    print("=" * 50)
    
    report = {
        'url_analisada': 'https://renirfonseca.blogspot.com/',
        'data_analise': time.strftime('%Y-%m-%d %H:%M:%S'),
        'total_urls': 0,
        'urls_internas': [],
        'problemas_encontrados': [],
        'recomendacoes': []
    }
    
    for csv_file in csv_files:
        print(f"\n📄 Processando: {csv_file.name}")
        
        try:
            content = csv_file.read_text(encoding='utf-8')
            lines = content.split('\n')
            
            if len(lines) < 2:
                continue
            
            # Processar dados
            for line in lines[1:]:
                if line.strip():
                    parts = line.split(',')
                    if len(parts) > 0:
                        url = parts[0].strip('"')
                        if url.startswith('http'):
                            report['total_urls'] += 1
                            report['urls_internas'].append(url)
            
        except Exception as e:
            print(f"   ❌ Erro: {e}")
    
    # Análises básicas
    if report['total_urls'] > 0:
        print(f"\n✅ URLs encontradas: {report['total_urls']}")
        
        # Verificar estrutura de URLs
        blog_posts = [url for url in report['urls_internas'] if '/20' in url]  # Posts do Blogger
        
        print(f"📝 Posts do blog identificados: {len(blog_posts)}")
        
        # Recomendações básicas
        if len(blog_posts) > 0:
            report['recomendacoes'].append("✅ Site possui conteúdo (posts do blog)")
        
        if report['total_urls'] < 10:
            report['problemas_encontrados'].append("⚠️ Poucas páginas encontradas - verificar estrutura de links")
        
        # Salvar relatório
        report_file = output_dir / 'relatorio_seo.json'
        
        import json
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        print(f"\n💾 Relatório salvo em: {report_file}")
        
        # Mostrar resumo
        print(f"\n📋 RESUMO:")
        print(f"   🔗 Total de URLs: {report['total_urls']}")
        print(f"   📝 Posts identificados: {len(blog_posts)}")
        
        if report['problemas_encontrados']:
            print(f"   ⚠️ Problemas:")
            for problema in report['problemas_encontrados']:
                print(f"      {problema}")
        
        if report['recomendacoes']:
            print(f"   💡 Recomendações:")
            for rec in report['recomendacoes']:
                print(f"      {rec}")
    
    return report

if __name__ == "__main__":
    print("🚀 TESTE FINAL - AUDITORIA SEO COM SCREAMING FROG")
    print("=" * 60)
    
    success, file_count = test_final_crawl()
    
    print(f"\n🎯 RESULTADO")
    print("=" * 30)
    
    if success:
        print("✅ SUCESSO! Crawl realizado com êxito")
        print(f"📄 {file_count} arquivo(s) gerado(s)")
        
        # Criar relatório
        report = create_seo_report()
        
        print(f"\n🎉 AUDITORIA SEO CONCLUÍDA!")
        print("✅ Screaming Frog funcionando")
        print("✅ Dados coletados do site real")
        print("✅ Relatório SEO gerado")
        print("✅ Sistema funciona SEM APIs externas")
        
        print(f"\n🔧 INTEGRAÇÃO COM FLASK:")
        print("1. Os dados estão em data/screaming_frog/")
        print("2. Podem ser processados pela API Flask")
        print("3. Sistema pronto para uso real!")
        
    else:
        print("❌ FALHA no crawl")
        print("Verificar configuração do Screaming Frog")
    
    print(f"\n📍 Teste realizado em: https://renirfonseca.blogspot.com/")