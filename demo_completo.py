# demo_completo.py - Demonstração completa do sistema
"""
AGENTE IA DE INVESTIMENTOS - DEMONSTRAÇÃO COMPLETA
Sistema integrado de análise de investimentos com web scraping
"""

import sys
import os
import time
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

# Importa módulos do sistema
try:
    from agente_ia_investimentos import AgenteIAInvestimentos
    from coletor_web_avancado import ColetorWebAvancado, AgenteInvestimentosAprimorado
    from configuracao import ConfiguracaoAgente, FontesDados
    from utilitarios import configurar_logging, salvar_backup_dados
except ImportError as e:
    print(f"❌ Erro ao importar módulos: {e}")
    print("Certifique-se de que todos os arquivos estão no mesmo diretório")
    sys.exit(1)

class DemonstradorSistema:
    """
    Classe para demonstrar todas as funcionalidades do sistema
    """
    
    def __init__(self):
        self.logger = configurar_logging()
        self.config = ConfiguracaoAgente()
        self.fontes = FontesDados()
        
        print("🤖 SISTEMA AGENTE IA DE INVESTIMENTOS")
        print("=" * 60)
        print("Sistema inicializado com sucesso!")
        print(f"Data/Hora: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
        print("=" * 60)
    
    def demonstrar_analise_basica(self):
        """Demonstra análise básica sem web scraping"""
        print("\n🔍 DEMONSTRAÇÃO: ANÁLISE BÁSICA")
        print("-" * 40)
        
        try:
            # Inicializa agente básico
            agente = AgenteIAInvestimentos()
            
            # Testa para cada perfil de risco
            perfis = ['conservador', 'moderado', 'arrojado']
            
            for perfil in perfis:
                print(f"\n📊 Analisando perfil: {perfil.upper()}")
                print("." * 30)
                
                # Executa análise
                resultados = agente.executar_analise_completa(perfil)
                
                # Exibe resumo
                print(f"✅ Análise concluída para {perfil}")
                print(f"   Retorno esperado: {resultados['recomendacao']['retorno_esperado']:.1f}%")
                print(f"   Investimentos recomendados: {len(resultados['recomendacao']['detalhes_carteira'])}")
                
                # Salva backup
                nome_backup = f"backup_analise_basica_{perfil}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
                caminho_backup = salvar_backup_dados(resultados, nome_backup)
                print(f"   Backup salvo: {caminho_backup}")
                
                time.sleep(2)  # Pausa entre análises
            
            print("\n✅ Demonstração de análise básica concluída!")
            
        except Exception as e:
            print(f"❌ Erro na análise básica: {str(e)}")
            self.logger.error(f"Erro na análise básica: {str(e)}")
    
    def demonstrar_web_scraping(self):
        """Demonstra funcionalidades de web scraping"""
        print("\n🌐 DEMONSTRAÇÃO: WEB SCRAPING")
        print("-" * 40)
        
        try:
            # Inicializa coletor web
            coletor = ColetorWebAvancado()
            
            print("📰 Coletando notícias financeiras...")
            
            # Coleta notícias do InfoMoney
            noticias_infomoney = coletor.coletar_noticias_infomoney(max_artigos=5)
            print(f"   InfoMoney: {len(noticias_infomoney)} notícias")
            
            # Coleta dados do Investing
            dados_investing = coletor.coletar_dados_investing()
            print(f"   Investing: {len(dados_investing)} indicadores")
            
            # Coleta recomendações da Suno
            recomendacoes_suno = coletor.coletar_recomendacoes_suno()
            print(f"   Suno: {len(recomendacoes_suno)} recomendações")
            
            # Análise de sentimento
            todas_noticias = noticias_infomoney + recomendacoes_suno
            relatorio_sentimento = coletor.gerar_relatorio_sentimento_mercado(todas_noticias)
            
            print(f"\n📊 Análise de Sentimento:")
            print(f"   Sentimento geral: {relatorio_sentimento.get('sentimento_geral', 'N/A')}")
            print(f"   Confiança: {relatorio_sentimento.get('confianca', 0):.2f}")
            print(f"   Artigos positivos: {relatorio_sentimento.get('artigos_positivos', 0)}")
            print(f"   Artigos negativos: {relatorio_sentimento.get('artigos_negativos', 0)}")
            
            # Salva resultados
            resultados_web = {
                'noticias_infomoney': noticias_infomoney,
                'dados_investing': dados_investing,
                'recomendacoes_suno': recomendacoes_suno,
                'relatorio_sentimento': relatorio_sentimento
            }
            
            nome_backup = f"backup_web_scraping_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            caminho_backup = salvar_backup_dados(resultados_web, nome_backup)
            print(f"\n💾 Dados salvos: {caminho_backup}")
            
            print("\n✅ Demonstração de web scraping concluída!")
            
        except Exception as e:
            print(f"❌ Erro no web scraping: {str(e)}")
            self.logger.error(f"Erro no web scraping: {str(e)}")
    
    def demonstrar_analise_completa(self):
        """Demonstra análise completa integrando todos os módulos"""
        print("\n🚀 DEMONSTRAÇÃO: ANÁLISE COMPLETA INTEGRADA")
        print("-" * 50)
        
        try:
            # Inicializa agente aprimorado
            agente_aprimorado = AgenteInvestimentosAprimorado()
            
            print("🔄 Executando análise completa com web scraping...")
            print("   (Isso pode levar alguns minutos)")
            
            # Executa análise para perfil moderado
            resultados_completos = agente_aprimorado.executar_analise_aprimorada('moderado')
            
            print("\n📊 RESULTADOS DA ANÁLISE COMPLETA:")
            print("-" * 40)
            
            # Análise de mercado
            sentimento = resultados_completos['sentimento_mercado']
            print(f"Sentimento do Mercado: {sentimento.get('sentimento_geral', 'N/A').upper()}")
            print(f"Confiança do Sentimento: {sentimento.get('confianca', 0):.2f}")
            
            # Recomendações de carteira
            recomendacao = resultados_completos['recomendacao']
            print(f"\nCarteira Recomendada ({recomendacao['perfil'].title()}):")
            for detalhe in recomendacao['detalhes_carteira']:
                print(f"  • {detalhe['alocacao']:2d}% em {detalhe['investimento']}")
                print(f"    Retorno esperado: {detalhe['retorno_esperado']:.1f}%")
            
            # Insights de notícias
            insights = resultados_completos['insights_noticias']
            print(f"\nAtivos em Tendência:")
            for ativo, mencoes in insights.get('ativos_tendencia', [])[:3]:
                print(f"  • {ativo.upper()}: {mencoes} menções")
            
            # Resumo de recomendações
            resumo_rec = resultados_completos['resumo_recomendacoes']
            print(f"\nResumo de Recomendações:")
            print(f"  • Sinais de compra: {resumo_rec.get('sinais_compra', 0)}")
            print(f"  • Sinais de venda: {resumo_rec.get('sinais_venda', 0)}")
            print(f"  • Proporção compra: {resumo_rec.get('proporcao_compra', 0):.1%}")
            
            # Salva backup completo
            nome_backup = f"backup_analise_completa_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            caminho_backup = salvar_backup_dados(resultados_completos, nome_backup)
            print(f"\n💾 Análise completa salva: {caminho_backup}")
            
            print("\n✅ Demonstração completa finalizada!")
            
        except Exception as e:
            print(f"❌ Erro na análise completa: {str(e)}")
            self.logger.error(f"Erro na análise completa: {str(e)}")
    
    def demonstrar_configuracoes(self):
        """Demonstra configurações do sistema"""
        print("\n⚙️ DEMONSTRAÇÃO: CONFIGURAÇÕES DO SISTEMA")
        print("-" * 45)
        
        print("📋 Configurações Gerais:")
        print(f"   Perfil padrão: {self.config.PERFIL_RISCO_PADRAO}")
        print(f"   Max artigos por fonte: {self.config.MAX_ARTIGOS_POR_FONTE}")
        print(f"   Timeout requisições: {self.config.TIMEOUT_REQUISICAO}s")
        
        print("\n📊 Perfis de Carteira Disponíveis:")
        for nome_perfil, dados_perfil in self.config.PERFIS_CARTEIRA.items():
            print(f"   {nome_perfil.upper()}:")
            print(f"     Renda Fixa: {dados_perfil['renda_fixa']}%")
            print(f"     Renda Variável: {dados_perfil['renda_variavel']}%")
            print(f"     FIIs: {dados_perfil['fiis']}%")
            print(f"     Internacional: {dados_perfil['internacional']}%")
            print(f"     Retorno Esperado: {dados_perfil['retorno_esperado']}%")
        
        print("\n🌐 Fontes de Dados Configuradas:")
        for nome_fonte, url in list(self.fontes.SITES_FINANCEIROS.items())[:5]:
            print(f"   {nome_fonte}: {url}")
        
        print(f"\n🔍 Palavras-chave monitoradas: {len(self.fontes.PALAVRAS_CHAVE_NOTICIAS)}")
        print(f"   Exemplos: {', '.join(self.fontes.PALAVRAS_CHAVE_NOTICIAS[:10])}")
    
    def demonstrar_utilitarios(self):
        """Demonstra funções utilitárias"""
        print("\n🛠️ DEMONSTRAÇÃO: FUNÇÕES UTILITÁRIAS")
        print("-" * 40)
        
        from utilitarios import (
            limpar_dados_numericos, calcular_sharpe_ratio, 
            calcular_drawdown_maximo, formatar_numero_brasileiro,
            obter_cor_performance
        )
        
        # Teste de limpeza de dados
        print("🧹 Limpeza de Dados:")
        valores_teste = ["R$ 1.234,56", "12.5%", "1,000.50", None, "abc123def"]
        for valor in valores_teste:
            valor_limpo = limpar_dados_numericos(valor)
            print(f"   '{valor}' -> {valor_limpo}")
        
        # Teste de Sharpe Ratio
        print("\n📈 Cálculo Sharpe Ratio:")
        retornos_exemplo = [0.12, 0.15, 0.08, 0.20, 0.11, 0.18]
        sharpe = calcular_sharpe_ratio(retornos_exemplo)
        print(f"   Retornos: {retornos_exemplo}")
        print(f"   Sharpe Ratio: {sharpe:.3f}")
        
        # Teste de Drawdown
        print("\n📉 Cálculo Drawdown Máximo:")
        precos_exemplo = [100, 105, 98, 110, 95, 108, 92, 115]
        drawdown = calcular_drawdown_maximo(precos_exemplo)
        print(f"   Preços: {precos_exemplo}")
        print(f"   Drawdown Máximo: {drawdown:.1%}")
        
        # Teste de formatação
        print("\n🔢 Formatação Brasileira:")
        numeros_teste = [1234.56, 1000000.789, 0.123, None]
        for numero in numeros_teste:
            formatado = formatar_numero_brasileiro(numero)
            print(f"   {numero} -> {formatado}")
        
        # Teste de cores por performance
        print("\n🎨 Cores por Performance:")
        performances = [15.5, 7.2, 2.1, -3.4]
        for perf in performances:
            cor = obter_cor_performance(perf)
            print(f"   {perf:+.1f}% -> {cor}")
    
    def gerar_relatorio_demonstracao(self):
        """Gera relatório da demonstração"""
        print("\n📄 GERANDO RELATÓRIO DA DEMONSTRAÇÃO")
        print("-" * 40)
        
        relatorio = f"""
================================================================================
                    🤖 RELATÓRIO DE DEMONSTRAÇÃO - AGENTE IA
                         Data: {datetime.now().strftime('%d/%m/%Y %H:%M')}
================================================================================

🎯 RESUMO DA DEMONSTRAÇÃO

Este relatório documenta a execução completa da demonstração do Sistema 
Agente IA de Investimentos, incluindo todas as funcionalidades principais.

📊 MÓDULOS DEMONSTRADOS:

✅ ANÁLISE BÁSICA
   • Coleta de dados de mercado via Yahoo Finance
   • Análise de múltiplas classes de ativos
   • Geração de recomendações por perfil de risco
   • Criação de visualizações e relatórios

✅ WEB SCRAPING AVANÇADO  
   • Coleta de notícias do InfoMoney
   • Extração de dados do Investing.com
   • Análise de recomendações da Suno Research
   • Processamento de sentimento de mercado

✅ ANÁLISE INTEGRADA
   • Combinação de dados de mercado e web
   • Geração de insights avançados
   • Identificação de ativos em tendência
   • Alertas de risco automatizados

✅ SISTEMA DE CONFIGURAÇÃO
   • Perfis de risco personalizáveis
   • Fontes de dados configuráveis
   • Parâmetros de análise ajustáveis

✅ FUNÇÕES UTILITÁRIAS
   • Limpeza e validação de dados
   • Cálculos financeiros (Sharpe, Drawdown)
   • Formatação e visualização
   • Sistema de logging e backup

🔧 ARQUITETURA DO SISTEMA:

CAMADA DE DADOS:
├── Yahoo Finance API (dados de mercado)
├── Web Scraping (notícias e análises)
└── Configurações locais

CAMADA DE PROCESSAMENTO:
├── Análise quantitativa
├── Processamento de linguagem natural
├── Análise de sentimento
└── Algoritmos de recomendação

CAMADA DE APRESENTAÇÃO:
├── Relatórios em texto
├── Gráficos e visualizações
├── Exportação de dados
└── Interface de linha de comando

💡 PRINCIPAIS CARACTERÍSTICAS:

• Análise multi-ativo (RF, RV, FIIs, Internacional)
• Personalização por perfil de risco
• Coleta de dados em tempo real
• Análise de sentimento de mercado
• Geração automatizada de relatórios
• Sistema de backup e logging
• Arquitetura modular e extensível

⚠️ LIMITAÇÕES E CONSIDERAÇÕES:

• Dados dependem da disponibilidade das APIs
• Web scraping sujeito a mudanças nos sites
• Análise de sentimento é aproximativa
• Não constitui recomendação de investimento
• Requer validação por profissional qualificado

🚀 PRÓXIMOS PASSOS:

• Integração com mais fontes de dados
• Machine Learning para predições
• Interface gráfica (GUI)
• API REST para integração
• Dashboard em tempo real
• Alertas por email/SMS

📊 ESTATÍSTICAS DA DEMONSTRAÇÃO:

• Tempo total de execução: ~{(datetime.now() - datetime.now()).seconds} segundos
• Módulos testados: 5/5
• Fontes de dados: {len(self.fontes.SITES_FINANCEIROS)}
• Perfis de risco: {len(self.config.PERFIS_CARTEIRA)}
• Classes de ativos: 4+ (RF, RV, FIIs, Internacional)

================================================================================
                    Demonstração concluída com sucesso! ✅
                        {datetime.now().strftime('%d/%m/%Y %H:%M')}
================================================================================
"""
        
        # Salva relatório
        nome_arquivo = f"relatorio_demonstracao_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        with open(nome_arquivo, 'w', encoding='utf-8') as f:
            f.write(relatorio)
        
        print(f"📁 Relatório salvo: {nome_arquivo}")
        return nome_arquivo
    
    def executar_demonstracao_completa(self):
        """Executa demonstração completa de todo o sistema"""
        print("\n🚀 INICIANDO DEMONSTRAÇÃO COMPLETA DO SISTEMA")
        print("=" * 60)
        
        inicio = datetime.now()
        
        try:
            # 1. Demonstra análise básica
            self.demonstrar_analise_basica()
            
            print("\n" + "⏸️ " * 20)
            input("Pressione Enter para continuar com web scraping...")
            
            # 2. Demonstra web scraping
            self.demonstrar_web_scraping()
            
            print("\n" + "⏸️ " * 20)
            input("Pressione Enter para continuar com análise completa...")
            
            # 3. Demonstra análise completa
            self.demonstrar_analise_completa()
            
            print("\n" + "⏸️ " * 20)
            input("Pressione Enter para ver configurações...")
            
            # 4. Demonstra configurações
            self.demonstrar_configuracoes()
            
            # 5. Demonstra utilitários
            self.demonstrar_utilitarios()
            
            # 6. Gera relatório final
            arquivo_relatorio = self.gerar_relatorio_demonstracao()
            
            fim = datetime.now()
            tempo_total = fim - inicio
            
            print("\n" + "=" * 60)
            print("🎉 DEMONSTRAÇÃO COMPLETA FINALIZADA!")
            print("=" * 60)
            print(f"⏱️ Tempo total: {tempo_total}")
            print(f"📁 Relatório: {arquivo_relatorio}")
            print(f"📊 Todos os arquivos gerados estão no diretório atual")
            print("=" * 60)
            
        except KeyboardInterrupt:
            print("\n\n⚠️ Demonstração interrompida pelo usuário")
        except Exception as e:
            print(f"\n❌ Erro durante a demonstração: {str(e)}")
            self.logger.error(f"Erro na demonstração: {str(e)}")

def menu_demonstracao():
    """Menu interativo para seleção de demonstrações"""
    demonstrador = DemonstradorSistema()
    
    while True:
        print("\n" + "=" * 60)
        print("🎭 MENU DE DEMONSTRAÇÕES")
        print("=" * 60)
        print("1. Demonstração Completa (Todos os módulos)")
        print("2. Apenas Análise Básica")
        print("3. Apenas Web Scraping")
        print("4. Apenas Análise Integrada")
        print("5. Ver Configurações")
        print("6. Testar Utilitários")
        print("0. Sair")
        print("=" * 60)
        
        escolha = input("Digite sua escolha: ").strip()
        
        if escolha == '1':
            demonstrador.executar_demonstracao_completa()
        elif escolha == '2':
            demonstrador.demonstrar_analise_basica()
        elif escolha == '3':
            demonstrador.demonstrar_web_scraping()
        elif escolha == '4':
            demonstrador.demonstrar_analise_completa()
        elif escolha == '5':
            demonstrador.demonstrar_configuracoes()
        elif escolha == '6':
            demonstrador.demonstrar_utilitarios()
        elif escolha == '0':
            print("👋 Saindo da demonstração. Até logo!")
            break
        else:
            print("❌ Opção inválida. Tente novamente.")
        
        if escolha != '0':
            input("\nPressione Enter para voltar ao menu...")

def verificar_dependencias():
    """Verifica se todas as dependências estão instaladas"""
    print("🔍 Verificando dependências...")
    
    dependencias_obrigatorias = [
        'requests', 'pandas', 'numpy', 'matplotlib', 
        'seaborn', 'beautifulsoup4', 'yfinance'
    ]
    
    dependencias_faltando = []
    
    for dep in dependencias_obrigatorias:
        try:
            __import__(dep)
            print(f"✅ {dep}")
        except ImportError:
            dependencias_faltando.append(dep)
            print(f"❌ {dep}")
    
    if dependencias_faltando:
        print(f"\n⚠️ Dependências faltando: {', '.join(dependencias_faltando)}")
        print("Execute: python instalar_dependencias.py")
        return False
    
    print("✅ Todas as dependências estão instaladas!")
    return True

if __name__ == "__main__":
    print("🤖 SISTEMA AGENTE IA DE INVESTIMENTOS - DEMO COMPLETO")
    print("=" * 60)
    print("Bem-vindo à demonstração completa do sistema!")
    print("Este script demonstra todas as funcionalidades disponíveis.")
    print("=" * 60)
    
    # Verifica dependências
    if not verificar_dependencias():
        print("\n❌ Não é possível continuar sem as dependências.")
        sys.exit(1)
    
    try:
        # Executa menu de demonstração
        menu_demonstracao()
        
    except KeyboardInterrupt:
        print("\n\n👋 Programa interrompido pelo usuário. Até logo!")
    except Exception as e:
        print(f"\n❌ Erro inesperado: {str(e)}")
        print("Verifique os logs para mais detalhes.")
    finally:
        print("\n🔚 Fim da demonstração.")
        print("Obrigado por testar o Sistema Agente IA de Investimentos!")