#!/usr/bin/env python3
"""
Script de inicialização da aplicação Flask para Auditoria SEO Técnica Automatizada.

Este script executa a aplicação completa com todos os endpoints de auditoria.
"""

import os
import sys
from dotenv import load_dotenv

# Adicionar o diretório do projeto ao path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Carregar variáveis de ambiente
load_dotenv()

# Importar a aplicação completa do main.py
from app.main import app, initialize_app

if __name__ == '__main__':
    # Inicializar a aplicação
    initialize_app()
    
    # Configurações do servidor
    host = os.getenv('FLASK_HOST', '127.0.0.1')
    port = int(os.getenv('FLASK_PORT', 5000))
    debug = os.getenv('FLASK_DEBUG', 'true').lower() == 'true'

    print(f"""
    🚀 Iniciando Sistema de Auditoria SEO Técnica Automatizada
    
    📍 URL: http://{host}:{port}
    🔧 Modo Debug: {'Ativado' if debug else 'Desativado'}
    
    📋 Endpoints disponíveis:
    • GET  /health           - Verificação de saúde
    • POST /audit/start      - Iniciar auditoria
    • GET  /audit/status/<id> - Status da auditoria
    • GET  /audit/result/<id> - Resultado da auditoria
    
    💡 Para parar o servidor: Ctrl+C
    """)
    
    # Executar o servidor
    app.run(host=host, port=port, debug=debug, threaded=True)