import requests
from bs4 import BeautifulSoup
import pandas as pd
from textblob import TextBlob
import re
from datetime import datetime, timedelta
import json
from typing import List, Dict
import asyncio
import aiohttp
from urllib.parse import urljoin, urlparse
import time

class ColetorWebAvancado:
    """
    Módulo avançado para web scraping e análise de notícias financeiras
    """
    
    def __init__(self):
        self.sessao = requests.Session()
        self.sessao.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'pt-BR,pt;q=0.9,en;q=0.8',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1'
        })
        
        # Sites financeiros brasileiros para monitoramento
        self.fontes_financeiras = {
            'infomoney': 'https://www.infomoney.com.br',
            'valor': 'https://valor.globo.com',
            'investing': 'https://br.investing.com',
            'suno': 'https://www.suno.com.br',
            'btg_research': 'https://www.btgpactual.com/research'
        }
        
        # Palavras-chave para análise de sentimento
        self.palavras_chave_investimento = [
            'alta', 'subida', 'valorização', 'crescimento', 'otimista',
            'queda', 'baixa', 'desvalorização', 'pessimista', 'crise',
            'oportunidade', 'recomendação', 'compra', 'venda', 'neutro'
        ]
    
    def coletar_noticias_infomoney(self, max_artigos: int = 10) -> List[Dict]:
        """
        Coleta notícias do InfoMoney
        """
        print("📰 Coletando notícias do InfoMoney...")
        
        try:
            url = "https://www.infomoney.com.br/mercados/"
            resposta = self.sessao.get(url, timeout=10)
            soup = BeautifulSoup(resposta.content, 'html.parser')
            
            artigos = []
            elementos_artigo = soup.find_all(['article', 'div'], class_=re.compile(r'.*article.*|.*news.*|.*post.*'))
            
            for i, elemento in enumerate(elementos_artigo[:max_artigos]):
                try:
                    elemento_titulo = elemento.find(['h1', 'h2', 'h3'], class_=re.compile(r'.*title.*|.*headline.*'))
                    elemento_link = elemento.find('a', href=True)
                    
                    if elemento_titulo and elemento_link:
                        titulo = elemento_titulo.get_text().strip()
                        link = urljoin(url, elemento_link['href'])
                        
                        # Análise de sentimento básica
                        sentimento = self.analisar_sentimento(titulo)
                        
                        artigos.append({
                            'titulo': titulo,
                            'link': link,
                            'fonte': 'InfoMoney',
                            'data_hora': datetime.now(),
                            'sentimento': sentimento,
                            'pontuacao_relevancia': self.calcular_relevancia(titulo)
                        })
                        
                except Exception as e:
                    continue
            
            print(f"✅ Coletadas {len(artigos)} notícias do InfoMoney")
            return artigos
            
        except Exception as e:
            print(f"❌ Erro ao coletar InfoMoney: {str(e)}")
            return []
    
    def coletar_dados_investing(self) -> Dict:
        """
        Coleta dados do Investing.com Brasil
        """
        print("📊 Coletando dados do Investing.com...")
        
        try:
            url = "https://br.investing.com/indices/bovespa"
            resposta = self.sessao.get(url, timeout=10)
            soup = BeautifulSoup(resposta.content, 'html.parser')
            
            dados = {}
            
            # Coleta preço atual do Ibovespa
            elemento_preco = soup.find(['span', 'div'], {'data-test': 'instrument-price-last'})
            if not elemento_preco:
                elemento_preco = soup.find(['span', 'div'], class_=re.compile(r'.*price.*|.*last.*'))
            
            if elemento_preco:
                texto_preco = elemento_preco.get_text().strip()
                dados['preco_ibovespa'] = self.limpar_preco(texto_preco)
            
            # Coleta variação percentual
            elemento_variacao = soup.find(['span', 'div'], class_=re.compile(r'.*change.*|.*percent.*'))
            if elemento_variacao:
                texto_variacao = elemento_variacao.get_text().strip()
                dados['variacao_ibovespa'] = self.limpar_porcentagem(texto_variacao)
            
            # Coleta dados de outros índices
            indices = ['selic', 'cdi', 'dolar', 'euro']
            for indice in indices:
                try:
                    url_indice = f"https://br.investing.com/rates-bonds/{indice}"
                    resp = self.sessao.get(url_indice, timeout=5)
                    soup_indice = BeautifulSoup(resp.content, 'html.parser')
                    
                    elemento_preco = soup_indice.find(['span', 'div'], {'data-test': 'instrument-price-last'})
                    if elemento_preco:
                        dados[f'taxa_{indice}'] = self.limpar_preco(elemento_preco.get_text().strip())
                except:
                    continue
            
            print(f"✅ Dados coletados do Investing: {list(dados.keys())}")
            return dados
            
        except Exception as e:
            print(f"❌ Erro ao coletar Investing: {str(e)}")
            return {}
    
    def coletar_recomendacoes_suno(self) -> List[Dict]:
        """
        Coleta recomendações da Suno Research
        """
        print("💡 Coletando recomendações da Suno...")
        
        try:
            url = "https://www.suno.com.br/artigos/"
            resposta = self.sessao.get(url, timeout=10)
            soup = BeautifulSoup(resposta.content, 'html.parser')
            
            recomendacoes = []
            elementos_artigo = soup.find_all(['div', 'article'], class_=re.compile(r'.*card.*|.*article.*|.*post.*'))
            
            for elemento in elementos_artigo[:5]:
                try:
                    elemento_titulo = elemento.find(['h1', 'h2', 'h3', 'a'])
                    if elemento_titulo:
                        titulo = elemento_titulo.get_text().strip()
                        
                        # Identifica se é recomendação de compra/venda
                        tipo_recomendacao = self.identificar_tipo_recomendacao(titulo)
                        
                        if tipo_recomendacao != 'neutro':
                            recomendacoes.append({
                                'titulo': titulo,
                                'tipo': tipo_recomendacao,
                                'fonte': 'Suno Research',
                                'confianca': self.calcular_confianca(titulo),
                                'data_hora': datetime.now()
                            })
                            
                except Exception as e:
                    continue
            
            print(f"✅ Coletadas {len(recomendacoes)} recomendações da Suno")
            return recomendacoes
            
        except Exception as e:
            print(f"❌ Erro ao coletar Suno: {str(e)}")
            return []
    
    def analisar_sentimento(self, texto: str) -> Dict:
        """
        Análise de sentimento usando TextBlob e palavras-chave
        """
        try:
            # Análise com TextBlob
            blob = TextBlob(texto)
            polaridade = blob.sentiment.polarity
            
            # Análise com palavras-chave
            texto_minusculo = texto.lower()
            palavras_positivas = ['alta', 'subida', 'valorização', 'crescimento', 'otimista', 'oportunidade', 'compra', 'lucro']
            palavras_negativas = ['queda', 'baixa', 'desvalorização', 'pessimista', 'crise', 'venda', 'prejuízo', 'risco']
            
            contagem_positiva = sum(1 for palavra in palavras_positivas if palavra in texto_minusculo)
            contagem_negativa = sum(1 for palavra in palavras_negativas if palavra in texto_minusculo)
            
            # Combina análises
            if polaridade > 0.1 or contagem_positiva > contagem_negativa:
                sentimento = 'positivo'
                pontuacao = max(polaridade, (contagem_positiva - contagem_negativa) / 10)
            elif polaridade < -0.1 or contagem_negativa > contagem_positiva:
                sentimento = 'negativo' 
                pontuacao = min(polaridade, (contagem_negativa - contagem_positiva) / -10)
            else:
                sentimento = 'neutro'
                pontuacao = polaridade
            
            return {
                'sentimento': sentimento,
                'pontuacao': pontuacao,
                'confianca': abs(pontuacao)
            }
            
        except Exception as e:
            return {'sentimento': 'neutro', 'pontuacao': 0, 'confianca': 0}
    
    def calcular_relevancia(self, texto: str) -> float:
        """
        Calcula relevância do texto para investimentos
        """
        termos_investimento = [
            'ação', 'ações', 'fii', 'fundos', 'investimento', 'carteira',
            'portfólio', 'renda fixa', 'renda variável', 'bovespa', 'ibovespa',
            'selic', 'cdi', 'tesouro', 'debêntures', 'dividendos'
        ]
        
        texto_minusculo = texto.lower()
        pontuacao_relevancia = sum(2 if termo in texto_minusculo else 0 for termo in termos_investimento)
        
        # Normaliza entre 0 e 1
        return min(pontuacao_relevancia / 10, 1.0)
    
    def identificar_tipo_recomendacao(self, texto: str) -> str:
        """
        Identifica tipo de recomendação (compra, venda, neutra)
        """
        texto_minusculo = texto.lower()
        
        sinais_compra = ['compra', 'comprar', 'recomenda', 'oportunidade', 'subir', 'alta']
        sinais_venda = ['venda', 'vender', 'evitar', 'cuidado', 'descer', 'baixa']
        
        contagem_compra = sum(1 for sinal in sinais_compra if sinal in texto_minusculo)
        contagem_venda = sum(1 for sinal in sinais_venda if sinal in texto_minusculo)
        
        if contagem_compra > contagem_venda:
            return 'compra'
        elif contagem_venda > contagem_compra:
            return 'venda'
        else:
            return 'neutro'
    
    def calcular_confianca(self, texto: str) -> float:
        """
        Calcula confiança da recomendação
        """
        indicadores_confianca = [
            'certeza', 'confirmado', 'definitivo', 'forte', 'clara',
            'provável', 'possível', 'talvez', 'pode', 'esperado'
        ]
        
        texto_minusculo = texto.lower()
        confianca = 0.5  # Base
        
        for indicador in indicadores_confianca[:5]:  # Alta confiança
            if indicador in texto_minusculo:
                confianca += 0.1
        
        for indicador in indicadores_confianca[5:]:  # Menor confiança
            if indicador in texto_minusculo:
                confianca -= 0.1
        
        return max(0.1, min(confianca, 1.0))
    
    def limpar_preco(self, texto_preco: str) -> float:
        """
        Limpa e converte texto de preço para float
        """
        try:
            # Remove caracteres não numéricos exceto ponto e vírgula
            limpo = re.sub(r'[^\d.,\-]', '', texto_preco)
            
            # Converte vírgula decimal brasileira para ponto
            if ',' in limpo and '.' in limpo:
                # Formato brasileiro: 123.456,78
                limpo = limpo.replace('.', '').replace(',', '.')
            elif ',' in limpo:
                # Apenas vírgula decimal: 123,78
                limpo = limpo.replace(',', '.')
            
            return float(limpo)
        except:
            return 0.0
    
    def limpar_porcentagem(self, texto_porcentagem: str) -> float:
        """
        Limpa e converte texto de porcentagem para float
        """
        try:
            limpo = re.sub(r'[^\d.,\-+%]', '', texto_porcentagem)
            limpo = limpo.replace('%', '').replace(',', '.')
            return float(limpo)
        except:
            return 0.0
    
    async def coletar_multiplas_fontes_async(self, fontes: List[str]) -> Dict:
        """
        Coleta dados de múltiplas fontes de forma assíncrona
        """
        print("🚀 Iniciando coleta assíncrona de múltiplas fontes...")
        
        async def buscar_fonte(sessao, url, nome_fonte):
            try:
                async with sessao.get(url, timeout=10) as resposta:
                    conteudo = await resposta.text()
                    soup = BeautifulSoup(conteudo, 'html.parser')
                    
                    # Extrai títulos e links principais
                    artigos = []
                    for elemento in soup.find_all(['h1', 'h2', 'h3'])[:5]:
                        titulo = elemento.get_text().strip()
                        if len(titulo) > 20:  # Filtra títulos muito curtos
                            artigos.append({
                                'titulo': titulo,
                                'fonte': nome_fonte,
                                'sentimento': self.analisar_sentimento(titulo),
                                'relevancia': self.calcular_relevancia(titulo)
                            })
                    
                    return {nome_fonte: artigos}
                    
            except Exception as e:
                print(f"❌ Erro ao coletar {nome_fonte}: {str(e)}")
                return {nome_fonte: []}
        
        # Executa coleta assíncrona
        async with aiohttp.ClientSession() as sessao:
            tarefas = []
            for nome_fonte, url in self.fontes_financeiras.items():
                tarefas.append(buscar_fonte(sessao, url, nome_fonte))
            
            resultados = await asyncio.gather(*tarefas)
        
        # Consolida resultados
        dados_consolidados = {}
        for resultado in resultados:
            dados_consolidados.update(resultado)
        
        return dados_consolidados
    
    def gerar_relatorio_sentimento_mercado(self, dados_noticias: List[Dict]) -> Dict:
        """
        Gera relatório de sentimento do mercado
        """
        print("📊 Gerando relatório de sentimento do mercado...")
        
        if not dados_noticias:
            return {'sentimento_geral': 'neutro', 'confianca': 0}
        
        sentimentos = []
        pesos_relevancia = []
        
        for artigo in dados_noticias:
            dados_sentimento = artigo.get('sentimento', {})
            if dados_sentimento:
                sentimentos.append(dados_sentimento.get('pontuacao', 0))
                pesos_relevancia.append(artigo.get('relevancia', 0.5))
        
        if not sentimentos:
            return {'sentimento_geral': 'neutro', 'confianca': 0}
        
        # Calcula sentimento ponderado pela relevância
        sentimento_ponderado = sum(s * w for s, w in zip(sentimentos, pesos_relevancia)) / sum(pesos_relevancia)
        
        # Determina sentimento geral
        if sentimento_ponderado > 0.1:
            sentimento_geral = 'positivo'
        elif sentimento_ponderado < -0.1:
            sentimento_geral = 'negativo'
        else:
            sentimento_geral = 'neutro'
        
        # Análise por categoria
        artigos_positivos = [a for a in dados_noticias if a.get('sentimento', {}).get('sentimento') == 'positivo']
        artigos_negativos = [a for a in dados_noticias if a.get('sentimento', {}).get('sentimento') == 'negativo']
        
        return {
            'sentimento_geral': sentimento_geral,
            'pontuacao_sentimento': sentimento_ponderado,
            'confianca': abs(sentimento_ponderado),
            'total_artigos': len(dados_noticias),
            'artigos_positivos': len(artigos_positivos),
            'artigos_negativos': len(artigos_negativos),
            'artigos_neutros': len(dados_noticias) - len(artigos_positivos) - len(artigos_negativos),
            'top_positivos': artigos_positivos[:3],
            'top_negativos': artigos_negativos[:3]
        }
    
    def executar_analise_abrangente(self) -> Dict:
        """
        Executa análise abrangente coletando dados de múltiplas fontes
        """
        print("🔍 Iniciando análise abrangente do mercado...")
        print("=" * 60)
        
        resultados = {
            'data_hora': datetime.now(),
            'dados_noticias': [],
            'dados_mercado': {},
            'recomendacoes': [],
            'relatorio_sentimento': {}
        }
        
        # 1. Coleta notícias do InfoMoney
        noticias_infomoney = self.coletar_noticias_infomoney()
        resultados['dados_noticias'].extend(noticias_infomoney)
        
        # 2. Coleta dados do Investing
        dados_investing = self.coletar_dados_investing()
        resultados['dados_mercado'].update(dados_investing)
        
        # 3. Coleta recomendações da Suno
        recomendacoes_suno = self.coletar_recomendacoes_suno()
        resultados['recomendacoes'].extend(recomendacoes_suno)
        
        # 4. Gera relatório de sentimento
        todos_artigos = resultados['dados_noticias'] + resultados['recomendacoes']
        relatorio_sentimento = self.gerar_relatorio_sentimento_mercado(todos_artigos)
        resultados['relatorio_sentimento'] = relatorio_sentimento
        
        # 5. Salva resultados
        self.salvar_resultados(resultados)
        
        print("\n" + "=" * 60)
        print("✅ Análise abrangente finalizada!")
        print(f"📰 {len(resultados['dados_noticias'])} notícias coletadas")
        print(f"💡 {len(resultados['recomendacoes'])} recomendações encontradas")
        print(f"📊 Sentimento geral: {relatorio_sentimento.get('sentimento_geral', 'N/A')}")
        
        return resultados
    
    def salvar_resultados(self, resultados: Dict):
        """
        Salva resultados em arquivos JSON e CSV
        """
        marca_tempo = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        # Salva em JSON
        nome_arquivo_json = f'analise_mercado_{marca_tempo}.json'
        with open(nome_arquivo_json, 'w', encoding='utf-8') as f:
            # Converte datetime para string para serialização JSON
            copia_resultados = resultados.copy()
            copia_resultados['data_hora'] = copia_resultados['data_hora'].isoformat()
            
            for artigo in copia_resultados['dados_noticias']:
                if 'data_hora' in artigo:
                    artigo['data_hora'] = artigo['data_hora'].isoformat()
            
            for rec in copia_resultados['recomendacoes']:
                if 'data_hora' in rec:
                    rec['data_hora'] = rec['data_hora'].isoformat()
            
            json.dump(copia_resultados, f, ensure_ascii=False, indent=2)
        
        # Salva notícias em CSV
        if resultados['dados_noticias']:
            df_noticias = pd.DataFrame(resultados['dados_noticias'])
            nome_arquivo_csv = f'dados_noticias_{marca_tempo}.csv'
            df_noticias.to_csv(nome_arquivo_csv, index=False, encoding='utf-8')
            print(f"📁 Dados salvos: {nome_arquivo_json}, {nome_arquivo_csv}")
        
        print(f"📁 Resultados salvos em: {nome_arquivo_json}")

# Integração com o agente principal
class AgenteInvestimentosAprimorado:
    """
    Agente de investimentos aprimorado com web scraping avançado
    """
    
    def __init__(self):
        from investment_ai_agent import AgenteIAInvestimentos  # Import do arquivo principal
        self.agente_base = AgenteIAInvestimentos()
        self.coletor_web = ColetorWebAvancado()
    
    def executar_analise_aprimorada(self, perfil_risco: str = 'moderado'):
        """
        Executa análise completa com dados web atualizados
        """
        print("🚀 Iniciando análise aprimorada com dados web...")
        
        # 1. Coleta dados web atualizados
        resultados_web = self.coletor_web.executar_analise_abrangente()
        
        # 2. Executa análise base
        resultados_base = self.agente_base.executar_analise_completa(perfil_risco)
        
        # 3. Combina resultados
        resultados_aprimorados = {
            **resultados_base,
            'dados_web': resultados_web,
            'sentimento_mercado': resultados_web['relatorio_sentimento'],
            'insights_noticias': self.extrair_insights_investimento(resultados_web['dados_noticias']),
            'resumo_recomendacoes': self.resumir_recomendacoes(resultados_web['recomendacoes'])
        }
        
        # 4. Gera relatório aprimorado
        self.gerar_relatorio_aprimorado(resultados_aprimorados)
        
        return resultados_aprimorados
    
    def extrair_insights_investimento(self, dados_noticias: List[Dict]) -> Dict:
        """
        Extrai insights de investimento das notícias
        """
        insights = {
            'ativos_tendencia': [],
            'temas_mercado': [],
            'alertas_risco': []
        }
        
        # Analisa títulos para identificar ativos em tendência
        mencoes_ativos = {}
        palavras_risco = ['risco', 'crise', 'queda', 'volatilidade', 'incerteza']
        
        for artigo in dados_noticias:
            titulo = artigo.get('titulo', '').lower()
            
            # Conta menções de ativos específicos
            ativos = ['petrobras', 'vale', 'itau', 'bradesco', 'bitcoin', 'dolar']
            for ativo in ativos:
                if ativo in titulo:
                    mencoes_ativos[ativo] = mencoes_ativos.get(ativo, 0) + 1
            
            # Identifica alertas de risco
            if any(palavra in titulo for palavra in palavras_risco):
                insights['alertas_risco'].append(artigo['titulo'])
        
        # Ativos mais mencionados
        insights['ativos_tendencia'] = sorted(mencoes_ativos.items(), 
                                           key=lambda x: x[1], reverse=True)[:5]
        
        return insights
    
    def resumir_recomendacoes(self, recomendacoes: List[Dict]) -> Dict:
        """
        Sumariza recomendações coletadas
        """
        if not recomendacoes:
            return {'sinais_compra': 0, 'sinais_venda': 0, 'sinais_neutros': 0}
        
        contagem_compra = sum(1 for rec in recomendacoes if rec.get('tipo') == 'compra')
        contagem_venda = sum(1 for rec in recomendacoes if rec.get('tipo') == 'venda')
        contagem_neutro = len(recomendacoes) - contagem_compra - contagem_venda
        
        return {
            'total_recomendacoes': len(recomendacoes),
            'sinais_compra': contagem_compra,
            'sinais_venda': contagem_venda,
            'sinais_neutros': contagem_neutro,
            'proporcao_compra': contagem_compra / len(recomendacoes) if recomendacoes else 0,
            'media_confianca': sum(rec.get('confianca', 0) for rec in recomendacoes) / len(recomendacoes)
        }
    
    def gerar_relatorio_aprimorado(self, resultados: Dict):
        """
        Gera relatório aprimorado com dados web
        """
        marca_tempo = datetime.now().strftime('%d/%m/%Y %H:%M')
        
        relatorio = f"""
================================================================================
                🤖 RELATÓRIO APRIMORADO - AGENTE IA COM WEB SCRAPING
                              Data: {marca_tempo}
================================================================================

📊 ANÁLISE DE SENTIMENTO DO MERCADO:
Sentimento Geral: {resultados['sentimento_mercado'].get('sentimento_geral', 'N/A').upper()}
Pontuação de Sentimento: {resultados['sentimento_mercado'].get('pontuacao_sentimento', 0):.3f}
Confiança: {resultados['sentimento_mercado'].get('confianca', 0):.2f}

📰 RESUMO DE NOTÍCIAS:
• Total de artigos analisados: {resultados['sentimento_mercado'].get('total_artigos', 0)}
• Notícias positivas: {resultados['sentimento_mercado'].get('artigos_positivos', 0)}
• Notícias negativas: {resultados['sentimento_mercado'].get('artigos_negativos', 0)}
• Notícias neutras: {resultados['sentimento_mercado'].get('artigos_neutros', 0)}

💡 RESUMO DE RECOMENDAÇÕES:
• Sinais de compra: {resultados['resumo_recomendacoes'].get('sinais_compra', 0)}
• Sinais de venda: {resultados['resumo_recomendacoes'].get('sinais_venda', 0)}
• Sinais neutros: {resultados['resumo_recomendacoes'].get('sinais_neutros', 0)}
• Proporção compra/total: {resultados['resumo_recomendacoes'].get('proporcao_compra', 0):.1%}

🔥 ATIVOS EM TENDÊNCIA:
"""
        
        for ativo, mencoes in resultados['insights_noticias'].get('ativos_tendencia', [])[:5]:
            relatorio += f"• {ativo.upper()}: {mencoes} menções\n"
        
        relatorio += f"""

⚠️ ALERTAS DE RISCO IDENTIFICADOS:
"""
        
        for alerta in resultados['insights_noticias'].get('alertas_risco', [])[:3]:
            relatorio += f"• {alerta}\n"
        
        relatorio += f"""

{resultados['relatorio']}

================================================================================
          Relatório Aprimorado gerado pelo Agente IA com Web Scraping
                              {marca_tempo}
================================================================================
"""
        
        # Salva relatório aprimorado
        with open('relatorio_aprimorado.txt', 'w', encoding='utf-8') as f:
            f.write(relatorio)
        
        print("✅ Relatório aprimorado salvo em: relatorio_aprimorado.txt")

# Exemplo de uso
if __name__ == "__main__":
    # Teste do coletor
    coletor = ColetorWebAvancado()
    resultados = coletor.executar_analise_abrangente()
    
    # Ou use o agente aprimorado
    # agente_aprimorado = AgenteInvestimentosAprimorado()
    # resultados_aprimorados = agente_aprimorado.executar_analise_aprimorada('moderado')