import os
from dataclasses import dataclass
from typing import Dict, List

@dataclass
class ConfiguracaoAgente:
    """Configurações do agente de IA"""
    
    # Configurações gerais
    PERFIL_RISCO_PADRAO: str = 'moderado'
    MAX_ARTIGOS_POR_FONTE: int = 10
    TIMEOUT_REQUISICAO: int = 10
    TENTATIVAS_REPETIR: int = 3
    
    # Configurações de análise
    PONTUACAO_MIN_RELEVANCIA: float = 0.3
    LIMITE_SENTIMENTO: float = 0.1
    LIMITE_CONFIANCA: float = 0.5
    
    # Configurações de carteira
    PERFIS_CARTEIRA: Dict = None
    
    def __post_init__(self):
        if self.PERFIS_CARTEIRA is None:
            self.PERFIS_CARTEIRA = {
                'conservador': {
                    'renda_fixa': 80,
                    'renda_variavel': 10,
                    'fiis': 10,
                    'internacional': 0,
                    'retorno_esperado': 12,
                    'volatilidade_maxima': 0.15
                },
                'moderado': {
                    'renda_fixa': 50,
                    'renda_variavel': 25,
                    'fiis': 20,
                    'internacional': 5,
                    'retorno_esperado': 18,
                    'volatilidade_maxima': 0.25
                },
                'arrojado': {
                    'renda_fixa': 20,
                    'renda_variavel': 40,
                    'fiis': 25,
                    'internacional': 15,
                    'retorno_esperado': 25,
                    'volatilidade_maxima': 0.40
                }
            }

# Configurações de fontes de dados
@dataclass
class FontesDados:
    """URLs e configurações das fontes de dados"""
    
    SITES_FINANCEIROS: Dict[str, str] = None
    APIS_DADOS_MERCADO: Dict[str, str] = None
    PALAVRAS_CHAVE_NOTICIAS: List[str] = None
    
    def __post_init__(self):
        if self.SITES_FINANCEIROS is None:
            self.SITES_FINANCEIROS = {
                'infomoney': 'https://www.infomoney.com.br/mercados/',
                'valor_economico': 'https://valor.globo.com/financas/',
                'investing_brasil': 'https://br.investing.com/',
                'suno_research': 'https://www.suno.com.br/artigos/',
                'btg_research': 'https://www.btgpactual.com/research',
                'xp_research': 'https://conteudos.xpi.com.br/',
                'rico_research': 'https://www.rico.com.br/blog/',
                'easynvest': 'https://www.easynvest.com.br/blog/',
                'toro_investimentos': 'https://blog.toroinvestimentos.com.br/'
            }
        
        if self.APIS_DADOS_MERCADO is None:
            self.APIS_DADOS_MERCADO = {
                'yahoo_finance': 'https://finance.yahoo.com/',
                'alpha_vantage': 'https://www.alphavantage.co/query',
                'bcb_api': 'https://api.bcb.gov.br/dados/serie/',
                'b3_api': 'http://www.b3.com.br/api-portal/'
            }
        
        if self.PALAVRAS_CHAVE_NOTICIAS is None:
            self.PALAVRAS_CHAVE_NOTICIAS = [
                # Indicadores econômicos
                'selic', 'cdi', 'ipca', 'igpm', 'pib', 'inflacao',
                
                # Investimentos
                'acoes', 'fiis', 'renda fixa', 'tesouro', 'cdb', 'lci', 'lca',
                'debentures', 'fundos', 'etf', 'bitcoin', 'criptomoeda',
                
                # Mercado financeiro
                'bovespa', 'ibovespa', 'b3', 'dolar', 'euro', 'ouro',
                'commodities', 'petroleo', 'vale', 'petrobras',
                
                # Análise técnica
                'suporte', 'resistencia', 'rompimento', 'alta', 'baixa',
                'tendencia', 'volatilidade', 'volume',
                
                # Sentimento
                'otimista', 'pessimista', 'neutro', 'oportunidade', 'risco'
            ]