import requests
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')  # Backend não-interativo para evitar problemas
import matplotlib.pyplot as plt
import seaborn as sns
from bs4 import BeautifulSoup
import yfinance as yf
from datetime import datetime, timedelta
import warnings
import json
import time
import logging
import os
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass

# Configuração inicial
warnings.filterwarnings('ignore')
plt.style.use('default')  # Usa estilo padrão seguro

@dataclass
class ConfiguracaoAgente:
    """Configurações do agente de IA"""
    PERFIL_RISCO_PADRAO: str = 'moderado'
    MAX_ARTIGOS_POR_FONTE: int = 10
    TIMEOUT_REQUISICAO: int = 15
    TAXA_SELIC_ATUAL: float = 13.75  # Taxa Selic atual para cálculos
    
    PERFIS_CARTEIRA: Dict = None
    
    def __post_init__(self):
        if self.PERFIS_CARTEIRA is None:
            self.PERFIS_CARTEIRA = {
                'conservador': {
                    'renda_fixa': 80,
                    'renda_variavel': 10,
                    'fiis': 10,
                    'internacional': 0,
                    'retorno_esperado': 12
                },
                'moderado': {
                    'renda_fixa': 50,
                    'renda_variavel': 25,
                    'fiis': 20,
                    'internacional': 5,
                    'retorno_esperado': 18
                },
                'arrojado': {
                    'renda_fixa': 20,
                    'renda_variavel': 40,
                    'fiis': 25,
                    'internacional': 15,
                    'retorno_esperado': 25
                }
            }

class UtilitariosFinanceiros:
    """Classe com funções utilitárias para cálculos financeiros"""
    
    @staticmethod
    def configurar_logging() -> logging.Logger:
        """Configura sistema de logging"""
        os.makedirs('logs', exist_ok=True)
        nome_arquivo_log = f"logs/agente_ia_{datetime.now().strftime('%Y%m%d')}.log"
        
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(nome_arquivo_log, encoding='utf-8'),
                logging.StreamHandler()
            ]
        )
        return logging.getLogger('AgenteIA')
    
    @staticmethod
    def limpar_valor_numerico(valor) -> float:
        """Limpa e converte valores numéricos"""
        if pd.isna(valor) or valor is None:
            return 0.0
        
        if isinstance(valor, (int, float)):
            return float(valor)
        
        if isinstance(valor, str):
            # Remove caracteres não numéricos exceto vírgula e ponto
            import re
            valor_limpo = re.sub(r'[^\d.,\-]', '', valor.strip())
            
            # Converte formato brasileiro para internacional
            if ',' in valor_limpo and '.' in valor_limpo:
                valor_limpo = valor_limpo.replace('.', '').replace(',', '.')
            elif ',' in valor_limpo:
                valor_limpo = valor_limpo.replace(',', '.')
            
            try:
                return float(valor_limpo)
            except (ValueError, TypeError):
                return 0.0
        
        return 0.0
    
    @staticmethod
    def calcular_sharpe_ratio(retornos: List[float], taxa_livre_risco: float = 0.1375) -> float:
        """Calcula o Sharpe Ratio"""
        if not retornos or len(retornos) == 0:
            return 0.0
        
        retorno_medio = np.mean(retornos)
        desvio_padrao = np.std(retornos)
        
        if desvio_padrao == 0:
            return 0.0
        
        return (retorno_medio - taxa_livre_risco) / desvio_padrao
    
    @staticmethod
    def formatar_valor_brasileiro(valor: float, casas_decimais: int = 2) -> str:
        """Formata valores no padrão brasileiro"""
        if pd.isna(valor) or valor is None:
            return "N/A"
        
        return f"{valor:,.{casas_decimais}f}".replace(',', 'X').replace('.', ',').replace('X', '.')

class ColetorDadosMercado:
    """Classe responsável pela coleta de dados de mercado"""
    
    def __init__(self, config: ConfiguracaoAgente):
        self.config = config
        self.logger = UtilitariosFinanceiros.configurar_logging()
        self.sessao = requests.Session()
        self.sessao.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
    
    def obter_dados_yahoo_finance(self) -> Dict:
        """Coleta dados do Yahoo Finance de forma segura"""
        self.logger.info("Coletando dados do Yahoo Finance...")
        
        simbolos = {
            'IBOV': '^BVSP',
            'DOLAR': 'USDBRL=X',
            'BITCOIN': 'BTC-USD',
            'SP500': '^GSPC',
            'OURO': 'GC=F'
        }
        
        # FIIs populares
        fiis = ['KNRI11.SA', 'HGLG11.SA', 'MXRF11.SA', 'VISC11.SA']
        
        dados_mercado = {}
        
        # Coleta dados principais
        for nome, simbolo in simbolos.items():
            try:
                ticker = yf.Ticker(simbolo)
                hist = ticker.history(period='1y')
                
                if not hist.empty:
                    preco_atual = float(hist['Close'].iloc[-1])
                    preco_inicial = float(hist['Close'].iloc[0])
                    retorno_ano = ((preco_atual / preco_inicial) - 1) * 100
                    
                    # Calcula volatilidade anualizada
                    retornos_diarios = hist['Close'].pct_change().dropna()
                    volatilidade = float(retornos_diarios.std() * np.sqrt(252) * 100)
                    
                    dados_mercado[nome] = {
                        'preco': round(preco_atual, 2),
                        'retorno_ano': round(retorno_ano, 2),
                        'volatilidade': round(volatilidade, 2),
                        'simbolo': simbolo
                    }
                    
                    self.logger.info(f"✅ {nome}: {retorno_ano:.2f}% no ano")
                    
            except Exception as e:
                self.logger.warning(f"Erro ao coletar {nome}: {str(e)}")
                continue
        
        # Coleta dados dos FIIs
        dados_fiis = {}
        for fii in fiis:
            try:
                ticker = yf.Ticker(fii)
                hist = ticker.history(period='6mo')  # Período menor para FIIs
                
                if not hist.empty and len(hist) > 1:
                    preco_atual = float(hist['Close'].iloc[-1])
                    preco_inicial = float(hist['Close'].iloc[0])
                    retorno_periodo = ((preco_atual / preco_inicial) - 1) * 100
                    
                    dados_fiis[fii.replace('.SA', '')] = {
                        'preco': round(preco_atual, 2),
                        'retorno_periodo': round(retorno_periodo, 2),
                        'simbolo': fii
                    }
                    
            except Exception as e:
                self.logger.warning(f"Erro ao coletar FII {fii}: {str(e)}")
                continue
        
        if dados_fiis:
            dados_mercado['FIIs'] = dados_fiis
            
        return dados_mercado
    
    def coletar_noticias_basicas(self) -> List[Dict]:
        """Coleta notícias básicas de fontes confiáveis"""
        self.logger.info("Coletando notícias financeiras...")
        
        noticias = []
        
        # URLs de feeds RSS ou páginas de notícias
        fontes = {
            'InfoMoney': 'https://www.infomoney.com.br/mercados/',
            'Valor': 'https://valor.globo.com/financas/'
        }
        
        for fonte, url in fontes.items():
            try:
                response = self.sessao.get(url, timeout=self.config.TIMEOUT_REQUISICAO)
                if response.status_code == 200:
                    soup = BeautifulSoup(response.content, 'html.parser')
                    
                    # Busca títulos de notícias
                    titulos = soup.find_all(['h1', 'h2', 'h3'], limit=5)
                    
                    for titulo in titulos:
                        texto = titulo.get_text().strip()
                        if len(texto) > 20:  # Filtra títulos muito curtos
                            noticias.append({
                                'titulo': texto,
                                'fonte': fonte,
                                'data_coleta': datetime.now(),
                                'relevancia': self._calcular_relevancia(texto)
                            })
                            
            except Exception as e:
                self.logger.warning(f"Erro ao coletar de {fonte}: {str(e)}")
                continue
        
        return noticias[:self.config.MAX_ARTIGOS_POR_FONTE]
    
    def _calcular_relevancia(self, texto: str) -> float:
        """Calcula relevância do texto para investimentos"""
        palavras_chave = [
            'investimento', 'ações', 'fii', 'tesouro', 'selic', 'cdi',
            'bovespa', 'dólar', 'alta', 'baixa', 'mercado', 'economia'
        ]
        
        texto_lower = texto.lower()
        pontuacao = sum(1 for palavra in palavras_chave if palavra in texto_lower)
        
        return min(pontuacao / len(palavras_chave), 1.0)

class AnalisadorInvestimentos:
    """Classe principal para análise de investimentos"""
    
    def __init__(self, config: ConfiguracaoAgente = None):
        self.config = config or ConfiguracaoAgente()
        self.logger = UtilitariosFinanceiros.configurar_logging()
        self.coletor = ColetorDadosMercado(self.config)
        self.dados_mercado = {}
        self.noticias = []
    
    def analisar_oportunidades(self, dados_mercado: Dict) -> Dict:
        """Analisa oportunidades de investimento"""
        self.logger.info("Analisando oportunidades de investimento...")
        
        analise = {
            'renda_fixa': self._analisar_renda_fixa(),
            'renda_variavel': self._analisar_renda_variavel(dados_mercado),
            'fiis': self._analisar_fiis(dados_mercado),
            'internacional': self._analisar_internacional(dados_mercado)
        }
        
        return analise
    
    def _analisar_renda_fixa(self) -> Dict:
        """Analisa opções de renda fixa"""
        selic = self.config.TAXA_SELIC_ATUAL
        
        return {
            'CDB_100_CDI': {
                'retorno': selic,
                'risco': 'Baixo',
                'liquidez': 'Alta',
                'tributacao': 'IR Regressivo'
            },
            'CDB_120_CDI': {
                'retorno': selic * 1.2,
                'risco': 'Baixo',
                'liquidez': 'Baixa',
                'tributacao': 'IR Regressivo'
            },
            'LCI_LCA': {
                'retorno': selic * 0.9,
                'risco': 'Baixo',
                'liquidez': 'Baixa',
                'tributacao': 'Isento IR'
            },
            'Tesouro_IPCA': {
                'retorno': 6.5,  # IPCA + juros reais
                'risco': 'Médio',
                'liquidez': 'Alta',
                'tributacao': 'IR Regressivo'
            }
        }
    
    def _analisar_renda_variavel(self, dados_mercado: Dict) -> Dict:
        """Analisa renda variável"""
        if 'IBOV' not in dados_mercado:
            return {}
        
        ibov_data = dados_mercado['IBOV']
        
        return {
            'IBOVESPA': {
                'retorno': ibov_data['retorno_ano'],
                'risco': 'Alto',
                'volatilidade': ibov_data['volatilidade'],
                'liquidez': 'Alta'
            },
            'Acoes_Growth': {
                'retorno': ibov_data['retorno_ano'] * 1.2,
                'risco': 'Muito Alto',
                'volatilidade': ibov_data['volatilidade'] * 1.3,
                'liquidez': 'Alta'
            }
        }
    
    def _analisar_fiis(self, dados_mercado: Dict) -> Dict:
        """Analisa Fundos Imobiliários"""
        if 'FIIs' not in dados_mercado:
            return {'Setor_FIIs': {'retorno': 8.5, 'risco': 'Médio-Alto'}}
        
        fiis_data = dados_mercado['FIIs']
        analise_fiis = {}
        
        for fii, dados in fiis_data.items():
            analise_fiis[fii] = {
                'retorno': dados['retorno_periodo'],
                'risco': 'Médio-Alto',
                'dividendos': 'Mensais',
                'liquidez': 'Boa'
            }
        
        return analise_fiis
    
    def _analisar_internacional(self, dados_mercado: Dict) -> Dict:
        """Analisa investimentos internacionais"""
        analise_intl = {}
        
        if 'SP500' in dados_mercado:
            sp500_data = dados_mercado['SP500']
            analise_intl['SP500'] = {
                'retorno': sp500_data['retorno_ano'],
                'risco': 'Alto',
                'moeda': 'USD',
                'liquidez': 'Alta'
            }
        
        if 'BITCOIN' in dados_mercado:
            btc_data = dados_mercado['BITCOIN']
            analise_intl['BITCOIN'] = {
                'retorno': btc_data['retorno_ano'],
                'risco': 'Muito Alto',
                'volatilidade': btc_data['volatilidade'],
                'liquidez': 'Boa'
            }
        
        return analise_intl
    
    def gerar_recomendacao_carteira(self, analise: Dict, perfil_risco: str = 'moderado') -> Dict:
        """Gera recomendação personalizada de carteira"""
        self.logger.info(f"Gerando recomendação para perfil {perfil_risco}...")
        
        if perfil_risco not in self.config.PERFIS_CARTEIRA:
            perfil_risco = self.config.PERFIL_RISCO_PADRAO
            
        perfil = self.config.PERFIS_CARTEIRA[perfil_risco]
        
        # Seleciona melhores investimentos de cada categoria
        recomendacoes = {}
        
        # Renda Fixa - seleciona melhor opção
        if analise['renda_fixa']:
            melhor_rf = max(analise['renda_fixa'].items(), 
                           key=lambda x: x[1].get('retorno', 0))
            recomendacoes['renda_fixa'] = melhor_rf
        
        # Renda Variável
        if analise['renda_variavel']:
            melhor_rv = max(analise['renda_variavel'].items(),
                           key=lambda x: x[1].get('retorno', 0))
            recomendacoes['renda_variavel'] = melhor_rv
        
        # FIIs
        if analise['fiis']:
            melhor_fii = max(analise['fiis'].items(),
                            key=lambda x: x[1].get('retorno', 0))
            recomendacoes['fiis'] = melhor_fii
        
        # Internacional
        if analise['internacional'] and perfil['internacional'] > 0:
            # Exclui Bitcoin para perfis conservadores
            opcoes_intl = analise['internacional'].copy()
            if perfil_risco == 'conservador' and 'BITCOIN' in opcoes_intl:
                opcoes_intl.pop('BITCOIN')
            
            if opcoes_intl:
                melhor_intl = max(opcoes_intl.items(),
                                 key=lambda x: x[1].get('retorno', 0))
                recomendacoes['internacional'] = melhor_intl
        
        # Monta carteira detalhada
        detalhes_carteira = []
        for categoria, percentual in perfil.items():
            if categoria != 'retorno_esperado' and percentual > 0:
                if categoria in recomendacoes:
                    investimento = recomendacoes[categoria]
                    detalhes_carteira.append({
                        'categoria': categoria.replace('_', ' ').title(),
                        'alocacao': percentual,
                        'investimento': investimento[0],
                        'retorno_esperado': investimento[1].get('retorno', 0),
                        'risco': investimento[1].get('risco', 'N/A')
                    })
        
        return {
            'perfil': perfil_risco,
            'alocacao': perfil,
            'recomendacoes': recomendacoes,
            'detalhes_carteira': detalhes_carteira,
            'retorno_esperado': perfil['retorno_esperado']
        }
    
    def criar_visualizacoes(self, analise: Dict, recomendacao: Dict):
        """Cria visualizações dos dados"""
        self.logger.info("Criando visualizações...")
        
        try:
            # Configura matplotlib
            plt.style.use('default')
            fig, axes = plt.subplots(2, 2, figsize=(15, 10))
            fig.suptitle('Análise de Investimentos - Agente IA', fontsize=16, fontweight='bold')
            
            # 1. Alocação da Carteira
            ax1 = axes[0, 0]
            if recomendacao['detalhes_carteira']:
                labels = [item['categoria'] for item in recomendacao['detalhes_carteira']]
                sizes = [item['alocacao'] for item in recomendacao['detalhes_carteira']]
                colors = ['#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4']
                
                ax1.pie(sizes, labels=labels, autopct='%1.1f%%', colors=colors[:len(sizes)])
                ax1.set_title(f'Carteira {recomendacao["perfil"].title()}')
            
            # 2. Retornos por Categoria
            ax2 = axes[0, 1]
            if recomendacao['detalhes_carteira']:
                categorias = [item['categoria'] for item in recomendacao['detalhes_carteira']]
                retornos = [item['retorno_esperado'] for item in recomendacao['detalhes_carteira']]
                
                bars = ax2.bar(range(len(categorias)), retornos, color=['#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4'])
                ax2.set_xticks(range(len(categorias)))
                ax2.set_xticklabels(categorias, rotation=45, ha='right')
                ax2.set_ylabel('Retorno (%)')
                ax2.set_title('Retornos Esperados por Categoria')
                
                # Adiciona valores nas barras
                for i, (bar, valor) in enumerate(zip(bars, retornos)):
                    ax2.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.5,
                            f'{valor:.1f}%', ha='center', va='bottom')
            
            # 3. Cenários de Retorno
            ax3 = axes[1, 0]
            cenarios = ['Pessimista', 'Realista', 'Otimista']
            retorno_base = recomendacao['retorno_esperado']
            retornos_cenario = [retorno_base * 0.6, retorno_base, retorno_base * 1.4]
            
            bars = ax3.bar(cenarios, retornos_cenario, color=['#FF6B6B', '#FFC107', '#4CAF50'])
            ax3.set_ylabel('Retorno (%)')
            ax3.set_title('Cenários de Retorno')
            
            for bar, valor in zip(bars, retornos_cenario):
                ax3.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.2,
                        f'{valor:.1f}%', ha='center', va='bottom')
            
            # 4. Resumo textual
            ax4 = axes[1, 1]
            ax4.axis('off')
            
            resumo_text = f"""
RESUMO EXECUTIVO

Perfil: {recomendacao['perfil'].title()}
Retorno Esperado: {recomendacao['retorno_esperado']:.1f}% a.a.

PRINCIPAIS RECOMENDAÇÕES:
"""
            
            for item in recomendacao['detalhes_carteira'][:3]:
                resumo_text += f"\n• {item['alocacao']}% em {item['investimento']}"
                resumo_text += f"\n  Retorno: {item['retorno_esperado']:.1f}%"
            
            resumo_text += "\n\nAVISOS:\n• Diversifique sempre\n• Reavalie periodicamente\n• Considere seu perfil"
            
            ax4.text(0.05, 0.95, resumo_text, transform=ax4.transAxes, fontsize=10,
                    verticalalignment='top', 
                    bbox=dict(boxstyle="round,pad=0.5", facecolor="lightblue", alpha=0.8))
            
            plt.tight_layout()
            
            # Salva o gráfico
            os.makedirs('relatorios', exist_ok=True)
            nome_arquivo = f"relatorios/analise_investimentos_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
            plt.savefig(nome_arquivo, dpi=300, bbox_inches='tight')
            plt.close()
            
            self.logger.info(f"Visualizações salvas em: {nome_arquivo}")
            return nome_arquivo
            
        except Exception as e:
            self.logger.error(f"Erro ao criar visualizações: {str(e)}")
            return None
    
    def gerar_relatorio_completo(self, analise: Dict, recomendacao: Dict, 
                                dados_mercado: Dict, noticias: List[Dict] = None) -> str:
        """Gera relatório completo"""
        self.logger.info("Gerando relatório completo...")
        
        relatorio = f"""
================================================================================
                    🤖 RELATÓRIO DE INVESTIMENTOS - AGENTE IA
                           Data: {datetime.now().strftime('%d/%m/%Y %H:%M')}
================================================================================

🎯 RESUMO EXECUTIVO

Perfil do Investidor: {recomendacao['perfil'].title()}
Retorno Esperado: {recomendacao['retorno_esperado']:.1f}% ao ano
Estratégia: Diversificação por classes de ativos

📊 ALOCAÇÃO RECOMENDADA:
"""
        
        for item in recomendacao['detalhes_carteira']:
            relatorio += f"""
• {item['alocacao']:2d}% - {item['investimento']}
  └─ Categoria: {item['categoria']}
  └─ Retorno Esperado: {item['retorno_esperado']:.1f}%
  └─ Nível de Risco: {item['risco']}
"""
        
        relatorio += "\n💰 ANÁLISE DETALHADA POR CATEGORIA:\n"
        
        # Renda Fixa
        if analise['renda_fixa']:
            relatorio += "\n🏦 RENDA FIXA:\n"
            for nome, dados in analise['renda_fixa'].items():
                relatorio += f"  • {nome.replace('_', ' ')}: {dados['retorno']:.1f}% - {dados['risco']}\n"
        
        # FIIs
        if analise['fiis']:
            relatorio += "\n🏢 FUNDOS IMOBILIÁRIOS:\n"
            for nome, dados in analise['fiis'].items():
                retorno = dados.get('retorno', dados.get('retorno_periodo', 0))
                relatorio += f"  • {nome}: {retorno:.1f}% - {dados['risco']}\n"
        
        # Renda Variável
        if analise['renda_variavel']:
            relatorio += "\n📈 RENDA VARIÁVEL:\n"
            for nome, dados in analise['renda_variavel'].items():
                relatorio += f"  • {nome}: {dados['retorno']:.1f}% - {dados['risco']}\n"
        
        # Internacional
        if analise['internacional']:
            relatorio += "\n🌍 INVESTIMENTOS INTERNACIONAIS:\n"
            for nome, dados in analise['internacional'].items():
                relatorio += f"  • {nome}: {dados['retorno']:.1f}% - {dados['risco']}\n"
        
        # Dados de mercado coletados
        if dados_mercado:
            relatorio += f"\n📊 DADOS DE MERCADO (últimos 12 meses):\n"
            for ativo, dados in dados_mercado.items():
                if ativo != 'FIIs' and isinstance(dados, dict):
                    relatorio += f"  • {ativo}: {dados.get('retorno_ano', 0):.1f}%\n"
        
        # Notícias relevantes
        if noticias:
            relatorio += f"\n📰 NOTÍCIAS RELEVANTES ({len(noticias)} coletadas):\n"
            for noticia in noticias[:5]:
                relatorio += f"  • {noticia['titulo'][:80]}... ({noticia['fonte']})\n"
        
        relatorio += f"""

💡 RECOMENDAÇÕES ESTRATÉGICAS:

1. DIVERSIFICAÇÃO é fundamental para redução de riscos
2. Mantenha reserva de emergência (6-12 meses de gastos)
3. Reavalie sua carteira trimestralmente  
4. Considere rebalanceamento semestral
5. Acompanhe indicadores econômicos (Selic, IPCA, PIB)
6. Estude antes de investir e considere custos

⚠️ CENÁRIOS E RISCOS:

OTIMISTA: Retorno até {recomendacao['retorno_esperado'] * 1.4:.1f}%
• Economia estável, queda da Selic, mercado em alta

REALISTA: Retorno {recomendacao['retorno_esperado']:.1f}%  
• Cenário base considerando condições atuais

PESSIMISTA: Retorno {recomendacao['retorno_esperado'] * 0.6:.1f}%
• Instabilidade política/econômica, alta volatilidade

🔍 PRÓXIMOS PASSOS:

1. Defina seus objetivos financeiros
2. Abra conta em corretora de confiança
3. Comece gradualmente seguindo a alocação sugerida
4. Configure aportes mensais automatizados
5. Acompanhe performance mensalmente

⚖️ DISCLAIMER:
Este relatório é gerado por IA para fins educacionais e informativos.
Rentabilidade passada não garante resultados futuros. Consulte sempre
um assessor de investimentos qualificado antes de tomar decisões financeiras.
O investidor deve estar ciente dos riscos envolvidos em cada modalidade.

================================================================================
                        Relatório gerado pelo Agente IA
                           {datetime.now().strftime('%d/%m/%Y %H:%M')}
================================================================================
"""
        
        # Salva o relatório
        os.makedirs('relatorios', exist_ok=True)
        nome_arquivo = f"relatorios/relatorio_investimentos_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        
        with open(nome_arquivo, 'w', encoding='utf-8') as f:
            f.write(relatorio)
        
        self.logger.info(f"Relatório salvo em: {nome_arquivo}")
        return nome_arquivo
    
    def executar_analise_completa(self, perfil_risco: str = 'moderado') -> Dict:
        """Executa análise completa de investimentos"""
        self.logger.info("🚀 Iniciando análise completa de investimentos...")
        print("=" * 60)
        print("🤖 AGENTE IA DE INVESTIMENTOS - ANÁLISE COMPLETA")
        print("=" * 60)
        
        try:
            # 1. Coleta dados de mercado
            print("📊 Coletando dados de mercado...")
            self.dados_mercado = self.coletor.obter_dados_yahoo_finance()
            
            if not self.dados_mercado:
                self.logger.warning("Nenhum dado de mercado coletado")
                print("⚠️ Aviso: Dados limitados. Usando valores de referência.")
            
            # 2. Coleta notícias (opcional - não bloqueia se falhar)
            print("📰 Coletando notícias financeiras...")
            try:
                self.noticias = self.coletor.coletar_noticias_basicas()
                print(f"✅ {len(self.noticias)} notícias coletadas")
            except Exception as e:
                self.logger.warning(f"Erro ao coletar notícias: {str(e)}")
                self.noticias = []
                print("⚠️ Notícias não disponíveis (continuando sem elas)")
            
            # 3. Analisa oportunidades
            print("🔍 Analisando oportunidades de investimento...")
            analise = self.analisar_oportunidades(self.dados_mercado)
            
            # 4. Gera recomendação
            print(f"💡 Gerando recomendação para perfil {perfil_risco}...")
            recomendacao = self.gerar_recomendacao_carteira(analise, perfil_risco)
            
            # 5. Cria visualizações
            print("📈 Criando visualizações...")
            arquivo_grafico = self.criar_visualizacoes(analise, recomendacao)
            
            # 6. Gera relatório
            print("📄 Gerando relatório detalhado...")
            arquivo_relatorio = self.gerar_relatorio_completo(
                analise, recomendacao, self.dados_mercado, self.noticias
            )
            
            # 7. Exibe resumo
            print("\n" + "=" * 60)
            print("✅ ANÁLISE COMPLETA FINALIZADA!")
            print("=" * 60)
            print(f"📊 Perfil analisado: {recomendacao['perfil'].title()}")
            print(f"📈 Retorno esperado: {recomendacao['retorno_esperado']:.1f}% a.a.")
            print(f"📁 Relatório: {arquivo_relatorio}")
            if arquivo_grafico:
                print(f"📊 Gráficos: {arquivo_grafico}")
            
            print("\n🎯 RESUMO DA CARTEIRA:")
            for item in recomendacao['detalhes_carteira']:
                print(f"  • {item['alocacao']:2d}% em {item['investimento']} "
                      f"({item['retorno_esperado']:.1f}% esperado)")
            
            return {
                'analise': analise,
                'recomendacao': recomendacao,
                'dados_mercado': self.dados_mercado,
                'noticias': self.noticias,
                'arquivo_relatorio': arquivo_relatorio,
                'arquivo_grafico': arquivo_grafico
            }
            
        except Exception as e:
            self.logger.error(f"Erro na análise completa: {str(e)}")
            print(f"❌ Erro durante a análise: {str(e)}")
            raise


def main():
    """Função principal para execução do agente"""
    print("🤖 SISTEMA AGENTE IA DE INVESTIMENTOS")
    print("=" * 60)
    print("Bem-vindo ao seu assistente inteligente de investimentos!")
    print("=" * 60)
    
    try:
        # Inicializa configuração e agente
        config = ConfiguracaoAgente()
        agente = AnalisadorInvestimentos(config)
        
        # Menu de seleção de perfil
        print("\n📊 SELECIONE SEU PERFIL DE INVESTIDOR:")
        print("1. Conservador (Foco em segurança e baixo risco)")
        print("2. Moderado (Equilíbrio entre risco e retorno)")
        print("3. Arrojado (Foco em alta rentabilidade)")
        print("4. Comparar todos os perfis")
        
        while True:
            escolha = input("\nDigite sua escolha (1-4) ou Enter para Moderado: ").strip()
            
            if escolha == '1':
                perfil = 'conservador'
                break
            elif escolha == '2' or escolha == '':
                perfil = 'moderado'
                break
            elif escolha == '3':
                perfil = 'arrojado'
                break
            elif escolha == '4':
                # Executa análise para todos os perfis
                print("\n🔄 Executando análise comparativa para todos os perfis...")
                
                resultados_comparacao = {}
                for perfil_comparacao in ['conservador', 'moderado', 'arrojado']:
                    print(f"\n--- Analisando perfil {perfil_comparacao.upper()} ---")
                    resultado = agente.executar_analise_completa(perfil_comparacao)
                    resultados_comparacao[perfil_comparacao] = resultado
                    time.sleep(2)  # Pausa entre análises
                
                # Exibe comparação
                print("\n" + "=" * 80)
                print("📊 COMPARAÇÃO DE PERFIS")
                print("=" * 80)
                
                for perfil_comp, resultado in resultados_comparacao.items():
                    rec = resultado['recomendacao']
                    print(f"\n{perfil_comp.upper()}:")
                    print(f"  Retorno esperado: {rec['retorno_esperado']:.1f}% a.a.")
                    print("  Alocação:")
                    for item in rec['detalhes_carteira']:
                        print(f"    • {item['alocacao']:2d}% {item['categoria']}")
                
                print("\n✅ Análise comparativa concluída!")
                return
            else:
                print("❌ Opção inválida. Tente novamente.")
                continue
        
        # Confirma a escolha
        print(f"\n✅ Perfil selecionado: {perfil.upper()}")
        print("🔄 Iniciando análise...")
        
        # Executa análise completa
        resultado = agente.executar_analise_completa(perfil)
        
        # Pergunta se deseja visualizar o relatório
        ver_relatorio = input("\nDeseja visualizar o relatório completo? (s/N): ").strip().lower()
        if ver_relatorio in ['s', 'sim', 'y', 'yes']:
            if resultado['arquivo_relatorio'] and os.path.exists(resultado['arquivo_relatorio']):
                with open(resultado['arquivo_relatorio'], 'r', encoding='utf-8') as f:
                    print("\n" + "=" * 80)
                    print(f.read())
                    print("=" * 80)
            else:
                print("❌ Relatório não encontrado.")
        
        print(f"\n📁 Todos os arquivos foram salvos na pasta 'relatorios'")
        print("🎉 Obrigado por usar o Agente IA de Investimentos!")
        
    except KeyboardInterrupt:
        print("\n\n👋 Programa interrompido pelo usuário. Até logo!")
    except Exception as e:
        print(f"\n❌ Erro inesperado: {str(e)}")
        print("Por favor, verifique sua conexão com a internet e tente novamente.")


def executar_teste_rapido():
    """Função para teste rápido do sistema"""
    print("🧪 EXECUTANDO TESTE RÁPIDO DO SISTEMA")
    print("=" * 50)
    
    try:
        config = ConfiguracaoAgente()
        agente = AnalisadorInvestimentos(config)
        
        print("✅ Configuração inicializada")
        print("✅ Agente criado")
        
        # Testa coleta de dados (sem falhar se não conseguir)
        print("🔄 Testando coleta de dados...")
        try:
            dados = agente.coletor.obter_dados_yahoo_finance()
            print(f"✅ Dados coletados: {len(dados)} ativos")
        except Exception as e:
            print(f"⚠️ Coleta limitada: {str(e)}")
            dados = {}
        
        # Testa análise básica
        print("🔄 Testando análise...")
        analise = agente.analisar_oportunidades(dados)
        print("✅ Análise concluída")
        
        # Testa geração de recomendação
        print("🔄 Testando recomendação...")
        recomendacao = agente.gerar_recomendacao_carteira(analise, 'moderado')
        print("✅ Recomendação gerada")
        
        print("\n🎉 TESTE CONCLUÍDO COM SUCESSO!")
        print(f"Retorno esperado (perfil moderado): {recomendacao['retorno_esperado']:.1f}%")
        print("O sistema está funcionando corretamente.")
        
        return True
        
    except Exception as e:
        print(f"❌ ERRO NO TESTE: {str(e)}")
        return False


if __name__ == "__main__":
    import sys
    
    # Verifica se é um teste rápido
    if len(sys.argv) > 1 and sys.argv[1] == 'teste':
        if executar_teste_rapido():
            sys.exit(0)
        else:
            sys.exit(1)
    else:
        main()