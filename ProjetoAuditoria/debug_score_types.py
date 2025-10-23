#!/usr/bin/env python3
"""
Script de debug para identificar onde o score está sendo definido como dict.
"""

import json
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.validator_agent import ValidationResult, ValidatorAgent
from app.apis import APIManager
from app.crawler import CrawlerManager

def debug_validation_results():
    """Debug para identificar ValidationResults com score como dict."""
    
    # Simula dados de PSI que podem causar o problema
    test_psi_data = {
        'mobile': {
            'lighthouseResult': {
                'categories': {
                    'performance': {
                        'score': None  # Isso pode causar problemas
                    }
                }
            }
        },
        'desktop': {
            'lighthouseResult': {
                'categories': {
                    'performance': {
                        'score': {'value': 0.8}  # Isso definitivamente causará problemas
                    }
                }
            }
        }
    }
    
    print("=== DEBUG: Testando extração de scores ===")
    
    # Testa mobile score
    mobile_score = test_psi_data['mobile'].get('lighthouseResult', {}).get('categories', {}).get('performance', {}).get('score', 0)
    print(f"Mobile score raw: {mobile_score} (type: {type(mobile_score)})")
    
    if mobile_score is not None:
        try:
            mobile_score_final = mobile_score * 100
            print(f"Mobile score final: {mobile_score_final} (type: {type(mobile_score_final)})")
        except Exception as e:
            print(f"ERRO ao calcular mobile score: {e}")
    
    # Testa desktop score
    desktop_score = test_psi_data['desktop'].get('lighthouseResult', {}).get('categories', {}).get('performance', {}).get('score', 0)
    print(f"Desktop score raw: {desktop_score} (type: {type(desktop_score)})")
    
    if desktop_score is not None:
        try:
            # Aplica a mesma lógica de validação que foi implementada
            if isinstance(desktop_score, (int, float)) and desktop_score is not None:
                desktop_score_final = desktop_score * 100
            else:
                desktop_score_final = 0
            print(f"Desktop score final: {desktop_score_final} (type: {type(desktop_score_final)})")
        except Exception as e:
            print(f"ERRO ao calcular desktop score: {e}")
    
    print("\n=== DEBUG: Testando ValidationResult ===")
    
    # Testa criação de ValidationResult com score problemático
    try:
        # Aplica a mesma lógica de validação
        if isinstance(desktop_score, (int, float)) and desktop_score is not None:
            final_score = desktop_score * 100
        else:
            final_score = 0
            
        validation = ValidationResult(
            validation_type='performance_mobile',
            status='failed',
            score=final_score,
            message="Test",
            details={},
            recommendations=[]
        )
        print(f"ValidationResult criado com score: {validation.score} (type: {type(validation.score)})")
    except Exception as e:
        print(f"ERRO ao criar ValidationResult: {e}")

if __name__ == "__main__":
    debug_validation_results()