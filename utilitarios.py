import pandas as pd
import numpy as np
from datetime import datetime
import logging
import os
import json

# --- NOVO: Gerenciador de Caminhos ---
def obter_caminho(subpasta: str, nome_arquivo: str) -> str:
    """
    Cria um caminho absoluto para um arquivo dentro de uma subpasta do projeto,
    garantindo que a pasta exista.
    """
    # Obtém o diretório onde este script (utilitarios.py) está localizado
    diretorio_base = os.path.dirname(os.path.abspath(__file__))
    
    # Constrói o caminho para a subpasta
    caminho_pasta = os.path.join(diretorio_base, subpasta)
    
    # Cria a subpasta se ela não existir
    os.makedirs(caminho_pasta, exist_ok=True)
    
    # Retorna o caminho completo para o arquivo
    return os.path.join(caminho_pasta, nome_arquivo)

def configurar_logging():
    """Configura sistema de logging para o agente de investimentos
    
    Cria um logger que envia mensagens tanto para um arquivo de log diário
    quanto para o console. O arquivo de log é salvo na pasta 'logs' com o nome
    no formato 'agente_ia_AAAAMMDD.log'.
    
    Returns:
        logging.Logger: Objeto logger configurado
    """
    nome_arquivo_log = f"agente_ia_{datetime.now().strftime('%Y%m%d')}.log"
    caminho_log = obter_caminho('logs', nome_arquivo_log)
    
    # Remove handlers antigos para evitar duplicação de logs em execuções múltiplas
    for handler in logging.root.handlers[:]:
        logging.root.removeHandler(handler)
        
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(caminho_log, encoding='utf-8'),
            logging.StreamHandler()
        ]
    )
    return logging.getLogger('AgenteIA')

def limpar_dados_numericos(valor):
    """Limpa e converte dados numéricos de forma robusta."""
    if pd.isna(valor) or valor is None:
        return 0.0
    
    if isinstance(valor, (int, float)):
        return float(valor)

    if isinstance(valor, str):
        valor_limpo = valor.strip()
        # Remove prefixos e sufixos comuns
        valor_limpo = valor_limpo.replace('R$', '').replace('%', '').strip()
        # Padrão brasileiro (1.234,56) para padrão US (1234.56)
        if ',' in valor_limpo and '.' in valor_limpo:
            valor_limpo = valor_limpo.replace('.', '').replace(',', '.')
        else:
            valor_limpo = valor_limpo.replace(',', '.')
        
        try:
            return float(valor_limpo)
        except (ValueError, TypeError):
            return 0.0
            
    return 0.0


def calcular_sharpe_ratio(retornos, taxa_livre_risco=0.1375):
    """Calcula o Sharpe Ratio
    
    Args:
        retornos: Lista ou array de retornos percentuais
        taxa_livre_risco: Taxa livre de risco anual em formato decimal (ex: 0.1375 para 13.75%)
        
    Returns:
        float: Índice de Sharpe
    """
    if len(retornos) == 0:
        return 0.0
    
    # Converte taxa anual para a mesma periodicidade dos retornos (assumindo retornos mensais)
    taxa_livre_risco_ajustada = (1 + taxa_livre_risco) ** (1/12) - 1
    
    retorno_medio = np.mean(retornos)
    desvio_padrao = np.std(retornos)
    
    if desvio_padrao == 0:
        return 0.0
    
    return (retorno_medio - taxa_livre_risco_ajustada) / desvio_padrao

def calcular_drawdown_maximo(precos):
    """Calcula o drawdown máximo (queda máxima) de uma série de preços
    
    Args:
        precos: Lista ou array de preços em ordem cronológica
        
    Returns:
        float: Valor absoluto do drawdown máximo (entre 0 e 1)
    """
    if len(precos) == 0:
        return 0.0
    
    # Calcula os picos acumulados (máximos históricos)
    picos = np.maximum.accumulate(precos)
    
    # Calcula os drawdowns como percentuais negativos
    drawdowns = (precos - picos) / picos
    
    # Retorna o valor absoluto do drawdown máximo
    return abs(np.min(drawdowns))

def formatar_numero_brasileiro(numero, casas_decimais=2):
    """Formata números no padrão brasileiro (usando vírgula como separador decimal e ponto como separador de milhar)
    
    Args:
        numero: Valor numérico a ser formatado
        casas_decimais: Número de casas decimais a serem exibidas
        
    Returns:
        str: Número formatado no padrão brasileiro ou "N/A" se o valor for None ou NaN
    """
    if numero is None or pd.isna(numero):
        return "N/A"
    
    # Formata o número com separador de milhar e casas decimais
    # Depois substitui os separadores para o padrão brasileiro
    return f"{numero:,.{casas_decimais}f}".replace(',', 'X').replace('.', ',').replace('X', '.')

def obter_cor_performance(performance):
    """Retorna código de cor hexadecimal baseado no valor de performance
    
    Args:
        performance: Valor numérico de performance (geralmente em percentual)
        
    Returns:
        str: Código de cor hexadecimal (#RRGGBB)
            - Verde (#4CAF50) para performance > 10
            - Amarelo (#FFC107) para performance entre 5 e 10
            - Laranja (#FF9800) para performance entre 0 e 5
            - Vermelho (#F44336) para performance <= 0
    """
    if performance > 10:
        return '#4CAF50'  # Verde
    elif performance > 5:
        return '#FFC107'  # Amarelo
    elif performance > 0:
        return '#FF9800'  # Laranja
    else:
        return '#F44336'  # Vermelho

def salvar_backup_dados(dados, nome_arquivo=None):
    """Salva backup dos dados em formato JSON
    
    Args:
        dados: Dicionário ou objeto serializável para JSON
        nome_arquivo: Nome do arquivo de backup (opcional). Se não fornecido,
                      será gerado um nome com timestamp atual
        
    Returns:
        str: Caminho completo onde o arquivo de backup foi salvo
    """
    # Se nome do arquivo não foi fornecido, gera um com timestamp
    if nome_arquivo is None:
        marca_tempo = datetime.now().strftime('%Y%m%d_%H%M%S')
        nome_arquivo = f'backup_dados_{marca_tempo}.json'
    
    # Cria pasta de backup se não existir
    pasta_backup = 'backups'
    if not os.path.exists(pasta_backup):
        os.makedirs(pasta_backup)
    
    caminho_completo = os.path.join(pasta_backup, nome_arquivo)
    
    # Importa json aqui para evitar importação desnecessária se o módulo não for usado
    import json
    
    # Salva os dados em formato JSON
    with open(caminho_completo, 'w', encoding='utf-8') as f:
        json.dump(dados, f, ensure_ascii=False, indent=2, default=str)
    
    return caminho_completo