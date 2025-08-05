import sys
import os
from datetime import datetime

def exibir_menu():
    """Exibe menu de opções"""
    print("\n" + "="*60)
    print("🤖 AGENTE IA DE INVESTIMENTOS")
    print("="*60)
    print("1. Análise Completa (Rápida)")
    print("2. Análise com Web Scraping (Completa)")
    print("3. Análise Personalizada")
    print("4. Relatório de Mercado")
    print("5. Configurações")
    print("6. Histórico de Análises")
    print("0. Sair")
    print("="*60)

def selecionar_perfil_risco():
    """Permite seleção do perfil de risco"""
    print("\n📊 SELECIONE SEU PERFIL DE RISCO:")
    print("1. Conservador (Foco em segurança)")
    print("2. Moderado (Equilibrio risco/retorno)")
    print("3. Arrojado (Foco em rentabilidade)")
    
    while True:
        escolha = input("\nDigite sua escolha (1-3): ").strip().lower()
        perfis = {'1': 'conservador', '2': 'moderado', '3': 'arrojado'}
        
        if escolha in perfis:
            return perfis[escolha]
        elif escolha == '':
            return 'moderado'  # Padrão
        else:
            print("❌ Opção inválida. Tente novamente.")

def executar_analise_completa():
    """Executa análise completa"""
    from agente_ia_investimentos import AgenteIAInvestimentos
    
    print("🚀 Iniciando análise completa...")
    perfil = selecionar_perfil_risco()
    
    agente = AgenteIAInvestimentos()
    resultados = agente.executar_analise_completa(perfil)
    
    print(f"\n✅ Análise concluída para perfil {perfil}!")
    return resultados

def executar_analise_web_scraping():
    """Executa análise com web scraping"""
    from coletor_web_avancado import AgenteInvestimentosAprimorado
    
    print("🌐 Iniciando análise com web scraping...")
    perfil = selecionar_perfil_risco()
    
    agente = AgenteInvestimentosAprimorado()
    resultados = agente.executar_analise_aprimorada(perfil)
    
    print(f"\n✅ Análise web concluída para perfil {perfil}!")
    return resultados

def exibir_historico():
    """Exibe histórico de análises"""
    print("📊 HISTÓRICO DE ANÁLISES:")
    
    # Lista arquivos de relatório
    arquivos_relatorio = []
    for arquivo in os.listdir('.'):
        if arquivo.startswith('relatorio_') and arquivo.endswith('.txt'):
            arquivos_relatorio.append(arquivo)
    
    if not arquivos_relatorio:
        print("Nenhum relatório encontrado.")
        return
    
    arquivos_relatorio.sort(reverse=True)  # Mais recentes primeiro
    
    for i, arquivo in enumerate(arquivos_relatorio[:10], 1):
        data_modificacao = datetime.fromtimestamp(os.path.getmtime(arquivo))
        print(f"{i}. {arquivo} ({data_modificacao.strftime('%d/%m/%Y %H:%M')})")

def principal():
    """Função principal"""
    try:
        from agente_ia_investimentos import AgenteIAInvestimentos
        from utilitarios import configurar_logging
        logger = configurar_logging()
        config = ConfiguracaoAgente()
        
        logger.info("Iniciando Agente IA de Investimentos")
        
        while True:
            exibir_menu()
            escolha = input("\nDigite sua escolha: ").strip()
            
            if escolha == '1':
                executar_analise_completa()
            elif escolha == '2':
                executar_analise_web_scraping()
            elif escolha == '3':
                print("🔧 Análise personalizada - Em desenvolvimento")
            elif escolha == '4':
                print("📊 Relatório de mercado - Em desenvolvimento")
            elif escolha == '5':
                print("⚙️ Configurações - Em desenvolvimento")
            elif escolha == '6':
                exibir_historico()
            elif escolha == '0':
                print("👋 Encerrando o Agente IA. Até logo!")
                break
            else:
                print("❌ Opção inválida. Tente novamente.")
            
            input("\nPressione Enter para continuar...")
    
    except KeyboardInterrupt:
        print("\n\n👋 Programa interrompido pelo usuário. Até logo!")
    except Exception as e:
        print(f"\n❌ Erro inesperado: {str(e)}")
        print("Por favor, verifique os logs para mais detalhes.")

if __name__ == "__main__":
    principal()