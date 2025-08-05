#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
INSTALADOR DE DEPENDÊNCIAS - AGENTE IA INVESTIMENTOS
Script para instalar e verificar todas as dependências necessárias
"""

import subprocess
import sys
import os
import pkg_resources
from packaging import version

def verificar_python():
    """Verifica se a versão do Python é compatível"""
    print("🐍 Verificando versão do Python...")
    
    versao_atual = sys.version_info
    versao_minima = (3, 8)
    
    if versao_atual >= versao_minima:
        print(f"✅ Python {versao_atual.major}.{versao_atual.minor}.{versao_atual.micro} (compatível)")
        return True
    else:
        print(f"❌ Python {versao_atual.major}.{versao_atual.minor} (mínimo: {versao_minima[0]}.{versao_minima[1]})")
        return False

def instalar_pacote(pacote, versao_minima=None):
    """Instala um pacote usando pip com verificação de versão"""
    nome_pacote = pacote.split('>=')[0] if '>=' in pacote else pacote
    
    try:
        # Verifica se já está instalado
        try:
            distribuicao = pkg_resources.get_distribution(nome_pacote)
            versao_instalada = distribuicao.version
            
            if versao_minima:
                if version.parse(versao_instalada) >= version.parse(versao_minima):
                    print(f"✅ {nome_pacote} {versao_instalada} (já instalado)")
                    return True
                else:
                    print(f"⚠️ {nome_pacote} {versao_instalada} (atualizando...)")
            else:
                print(f"✅ {nome_pacote} {versao_instalada} (já instalado)")
                return True
                
        except pkg_resources.DistributionNotFound:
            print(f"📦 Instalando {pacote}...")
        
        # Instala ou atualiza o pacote
        subprocess.check_call([
            sys.executable, "-m", "pip", "install", "--upgrade", pacote
        ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        
        print(f"✅ {nome_pacote} instalado com sucesso")
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Erro ao instalar {nome_pacote}: {e}")
        return False
    except Exception as e:
        print(f"❌ Erro inesperado com {nome_pacote}: {e}")
        return False

def criar_estrutura_diretorios():
    """Cria estrutura de diretórios necessária"""
    print("📁 Criando estrutura de diretórios...")
    
    diretorios = ['logs', 'relatorios', 'dados', 'backups']
    
    for diretorio in diretorios:
        try:
            os.makedirs(diretorio, exist_ok=True)
            print(f"✅ Diretório '{diretorio}' criado/verificado")
        except Exception as e:
            print(f"❌ Erro ao criar '{diretorio}': {e}")

def verificar_conexao_internet():
    """Verifica conexão com a internet"""
    print("🌐 Verificando conexão com a internet...")
    
    try:
        import requests
        response = requests.get('https://httpbin.org/status/200', timeout=10)
        if response.status_code == 200:
            print("✅ Conexão com internet OK")
            return True
    except Exception:
        pass
    
    try:
        import urllib.request
        urllib.request.urlopen('https://www.google.com', timeout=10)
        print("✅ Conexão com internet OK")
        return True
    except Exception:
        print("❌ Sem conexão com a internet")
        return False

def testar_importacoes():
    """Testa se todas as bibliotecas podem ser importadas"""
    print("🧪 Testando importações...")
    
    bibliotecas_teste = [
        ('requests', 'requests'),
        ('pandas', 'pd'),
        ('numpy', 'np'),
        ('matplotlib.pyplot', 'plt'),
        ('seaborn', 'sns'),
        ('bs4', 'BeautifulSoup'),
        ('yfinance', 'yf'),
        ('datetime', 'datetime'),
        ('json', 'json'),
        ('logging', 'logging')
    ]
    
    sucessos = 0
    falhas = []
    
    for lib, alias in bibliotecas_teste:
        try:
            exec(f"import {lib} as {alias}")
            print(f"✅ {lib}")
            sucessos += 1
        except ImportError as e:
            print(f"❌ {lib}: {e}")
            falhas.append(lib)
        except Exception as e:
            print(f"⚠️ {lib}: {e}")
    
    print(f"\n📊 Resultado: {sucessos}/{len(bibliotecas_teste)} bibliotecas OK")
    
    if falhas:
        print(f"❌ Falhas: {', '.join(falhas)}")
        return False
    
    return True

def instalar_tudo():
    """Instala todas as dependências necessárias"""
    print("🚀 INSTALADOR AGENTE IA DE INVESTIMENTOS")
    print("=" * 60)
    
    # 1. Verifica Python
    if not verificar_python():
        print("\n❌ Versão do Python incompatível. Atualize para Python 3.8+")
        return False
    
    # 2. Atualiza pip
    print("\n📦 Atualizando pip...")
    try:
        subprocess.check_call([
            sys.executable, "-m", "pip", "install", "--upgrade", "pip"
        ], stdout=subprocess.DEVNULL)
        print("✅ pip atualizado")
    except Exception as e:
        print(f"⚠️ Aviso: Não foi possível atualizar pip: {e}")
    
    # 3. Lista de pacotes essenciais
    pacotes_essenciais = [
        "requests>=2.28.0",
        "pandas>=1.5.0",
        "numpy>=1.21.0",
        "matplotlib>=3.5.0",
        "seaborn>=0.11.0",
        "beautifulsoup4>=4.11.0",
        "yfinance>=0.2.0",
        "lxml>=4.9.0",
        "openpyxl>=3.0.0"
    ]
    
    # 4. Pacotes opcionais (não bloqueiam se falharem)
    pacotes_opcionais = [
        "plotly>=5.10.0",
        "textblob>=0.17.0",
        "aiohttp>=3.8.0",
        "scikit-learn>=1.1.0"
    ]
    
    # 5. Instala pacotes essenciais
    print(f"\n📦 Instalando {len(pacotes_essenciais)} pacotes essenciais...")
    falhas_essenciais = []
    
    for pacote in pacotes_essenciais:
        if not instalar_pacote(pacote):
            falhas_essenciais.append(pacote)
    
    # 6. Instala pacotes opcionais
    print(f"\n📦 Instalando {len(pacotes_opcionais)} pacotes opcionais...")
    falhas_opcionais = []
    
    for pacote in pacotes_opcionais:
        if not instalar_pacote(pacote):
            falhas_opcionais.append(pacote)
    
    # 7. Cria estrutura de diretórios
    print("\n📁 Configurando ambiente...")
    criar_estrutura_diretorios()
    
    # 8. Verifica conexão
    verificar_conexao_internet()
    
    # 9. Testa importações
    print("\n🧪 Testando sistema...")
    if not testar_importacoes():
        print("⚠️ Algumas bibliotecas falharam no teste")
    
    # 10. Relatório final
    print("\n" + "=" * 60)
    print("📊 RELATÓRIO DE INSTALAÇÃO")
    print("=" * 60)
    
    if not falhas_essenciais:
        print("✅ Todos os pacotes essenciais instalados com sucesso!")
    else:
        print(f"❌ Falhas em pacotes essenciais: {len(falhas_essenciais)}")
        for falha in falhas_essenciais:
            print(f"  • {falha}")
    
    if falhas_opcionais:
        print(f"⚠️ Falhas em pacotes opcionais: {len(falhas_opcionais)}")
        print("  (Não afetam o funcionamento básico)")
    
    if not falhas_essenciais:
        print("\n🎉 INSTALAÇÃO CONCLUÍDA COM SUCESSO!")
        print("Agora você pode executar:")
        print("  python agente_ia_investimentos.py")
        return True
    else:
        print("\n❌ INSTALAÇÃO INCOMPLETA")
        print("Tente instalar manualmente os pacotes que falharam:")
        print("  pip install " + " ".join(falhas_essenciais))
        return False

def verificar_sistema():
    """Verifica se o sistema está pronto para uso"""
    print("🔍 VERIFICAÇÃO DO SISTEMA")
    print("=" * 40)
    
    # Verifica Python
    if not verificar_python():
        return False
    
    # Verifica conexão
    if not verificar_conexao_internet():
        print("⚠️ Aviso: Sem internet. Algumas funcionalidades podem não funcionar.")
    
    # Testa importações
    if not testar_importacoes():
        print("❌ Sistema não está pronto. Execute a instalação primeiro.")
        return False
    
    # Verifica estrutura de diretórios
    diretorios = ['logs', 'relatorios']
    for diretorio in diretorios:
        if not os.path.exists(diretorio):
            print(f"⚠️ Diretório '{diretorio}' não existe. Criando...")
            os.makedirs(diretorio, exist_ok=True)
    
    print("✅ Sistema verificado e pronto para uso!")
    return True

def limpar_instalacao():
    """Remove pacotes instalados (usado para limpeza)"""
    print("🧹 LIMPEZA DE INSTALAÇÃO")
    print("=" * 30)
    
    confirmacao = input("Tem certeza que deseja remover os pacotes? (s/N): ").strip().lower()
    if confirmacao not in ['s', 'sim', 'y', 'yes']:
        print("Operação cancelada.")
        return
    
    pacotes_remover = [
        'yfinance', 'beautifulsoup4', 'seaborn', 'plotly', 
        'textblob', 'aiohttp', 'lxml'
    ]
    
    for pacote in pacotes_remover:
        try:
            subprocess.check_call([
                sys.executable, "-m", "pip", "uninstall", "-y", pacote
            ])
            print(f"✅ {pacote} removido")
        except Exception as e:
            print(f"⚠️ Não foi possível remover {pacote}: {e}")
    
    print("🧹 Limpeza concluída!")

def main():
    """Função principal do instalador"""
    if len(sys.argv) > 1:
        comando = sys.argv[1].lower()
        
        if comando == 'verificar':
            if verificar_sistema():
                sys.exit(0)
            else:
                sys.exit(1)
        elif comando == 'limpar':
            limpar_instalacao()
            sys.exit(0)
        elif comando == 'teste':
            if testar_importacoes():
                sys.exit(0)
            else:
                sys.exit(1)
        else:
            print(f"Comando desconhecido: {comando}")
            print("Comandos disponíveis: verificar, limpar, teste")
            sys.exit(1)
    else:
        # Instalação completa
        if instalar_tudo():
            sys.exit(0)
        else:
            sys.exit(1)

if __name__ == "__main__":
    main()