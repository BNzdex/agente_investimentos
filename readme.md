# 🤖 Agente IA de Investimentos

Um sistema inteligente de análise de investimentos que coleta dados de mercado em tempo real, analisa oportunidades e gera recomendações personalizadas de carteira com base no perfil de risco do investidor.

## ✨ Principais Funcionalidades

- 📊 **Análise de Dados de Mercado**: Coleta automática de dados do Yahoo Finance
- 🎯 **Recomendações Personalizadas**: Carteiras otimizadas por perfil de risco
- 📈 **Visualizações Inteligentes**: Gráficos e relatórios profissionais
- 📰 **Análise de Notícias**: Coleta e processamento de notícias financeiras
- 💡 **Múltiplas Classes de Ativos**: Renda fixa, variável, FIIs e internacional
- 📄 **Relatórios Detalhados**: Documentação completa das análises

## 🔧 Correções Implementadas

### Problemas Identificados e Solucionados:

1. **Importações Circulares**: Reorganizada estrutura de imports
2. **Matplotlib Backend**: Configurado backend não-interativo para evitar erros
3. **Tratamento de Erros**: Implementado sistema robusto de exception handling  
4. **Dependências**: Simplificadas e organizadas as bibliotecas necessárias
5. **Paths e Diretórios**: Sistema automático de criação de estrutura de pastas
6. **Compatibilidade**: Testado com Python 3.8+
7. **Logging**: Sistema de logs melhorado e organizado
8. **Coleta de Dados**: Tratamento de falhas na API do Yahoo Finance
9. **Validação de Dados**: Verificações de integridade implementadas
10. **Interface de Usuário**: Menu interativo simplificado

## 🚀 Instalação Rápida

### Pré-requisitos
- Python 3.8 ou superior
- Conexão com internet
- pip atualizado

### Passo 1: Clone ou baixe os arquivos
```bash
# Salve os dois arquivos principais:
# - agente_ia_investimentos.py (código principal)
# - instalar_dependencias.py (instalador)
```

### Passo 2: Execute o instalador
```bash
python instalar_dependencias.py
```

### Passo 3: Execute o sistema
```bash
python agente_ia_investimentos.py
```

## 📋 Comandos Disponíveis

### Executar Análise Completa
```bash
python agente_ia_investimentos.py
```

### Teste Rápido do Sistema
```bash
python agente_ia_investimentos.py teste
```

### Verificar Instalação
```bash
python instalar_dependencias.py verificar
```

### Limpar Instalação
```bash
python instalar_dependencias.py limpar
```

## 🎯 Perfis de Investidor

### 🛡️ Conservador
- **Foco**: Segurança e preservação de capital
- **Alocação**: 80% Renda Fixa, 10% Renda Variável, 10% FIIs
- **Retorno Esperado**: ~12% ao ano
- **Risco**: Baixo

### ⚖️ Moderado (Padrão)
- **Foco**: Equilíbrio entre risco e retorno
- **Alocação**: 50% Renda Fixa, 25% Renda Variável, 20% FIIs, 5% Internacional
- **Retorno Esperado**: ~18% ao ano  
- **Risco**: Médio

### 🚀 Arrojado
- **Foco**: Maximização de retornos
- **Alocação**: 20% Renda Fixa, 40% Renda Variável, 25% FIIs, 15% Internacional
- **Retorno Esperado**: ~25% ao ano
- **Risco**: Alto

## 📊 Classes de Ativos Analisadas

### 🏦 Renda Fixa
- CDB 100% CDI e 120% CDI
- LCI/LCA (isentos de IR)
- Tesouro IPCA+
- Debêntures

### 📈 Renda Variável
- Ibovespa (índice principal)
- Ações Growth
- ETFs setoriais

### 🏢 Fundos Imobiliários (FIIs)
- KNRI11, HGLG11, MXRF11, VISC11
- Análise de dividend yield
- Segmentos: Logística, Shopping, Corporativo

### 🌍 Internacional
- S&P 500 (mercado americano)
- Bitcoin (cripto - apenas perfil arrojado)
- Ouro (reserva de valor)

## 📁 Estrutura de Arquivos Gerados

```
projeto/
├── logs/                          # Logs do sistema
│   └── agente_ia_AAAAMMDD.log
├── relatorios/                    # Relatórios e gráficos
│   ├── analise_investimentos_*.png
│   └── relatorio_investimentos_*.txt
├── dados/                         # Cache de dados (futuro)
└── backups/                       # Backups automáticos
```

## 🔍 Funcionalidades Detalhadas

### Coleta de Dados
- **Yahoo Finance API**: Preços, volatilidade, retornos
- **Web Scraping**: Notícias de InfoMoney e Valor Econômico
- **Tratamento de Falhas**: Sistema continua mesmo com dados limitados

### Análise Quantitativa
- **Sharpe Ratio**: Relação risco/retorno
- **Volatilidade**: Risco anualizado
- **Correlações**: Entre classes de ativos
- **Cenários**: Pessimista, realista, otimista

### Visualizações
- **Pizza**: Alocação da carteira recomendada
- **Barras**: Retornos esperados por categoria
- **Cenários**: Análise de diferentes situações de mercado
- **Resumo**: Informações-chave em formato visual

### Relatórios
- **Executivo**: Resumo das principais recomendações
- **Detalhado**: Análise completa por classe de ativo
- **Técnico**: Métricas quantitativas e estatísticas
- **Educacional**: Explicações e disclaimers

## ⚠️ Avisos Importantes

### Disclaimer Legal
- Este sistema é **apenas educacional e inform