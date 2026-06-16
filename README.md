# Growth A/B Test Analyzer

Este projeto é uma ferramenta automatizada para análise de testes A/B de cashback. O objetivo é eliminar o processo manual de 2-4 horas, fornecendo uma decisão baseada em dados e significância estatística em segundos.

## Funcionalidades

- **Processamento Automatizado**: Limpeza de dados financeiros (formato BRL) e agregação de métricas.
- **Análise Estatística**: Cálculo de P-valor usando **Welch T-Test** com correção de **Holm-Bonferroni** para múltiplas comparações.
- **Decisão Inteligente**: Algoritmo que prioriza a média de lucro líquido (*Net Revenue*) e valida a magnitude do efeito (**Cohen's d**).
- **Logging Duplo**: Registro automático dos resultados em um arquivo CSV local e em uma planilha centralizada no Google Sheets.

## Pré-requisitos

Certifique-se de ter o Python 3.8+ instalado. As bibliotecas necessárias são:

```bash
pip install pandas numpy scipy gspread google-auth
```

## Estrutura de Pastas

```text
Teste_Tecnico_Growth/
├── scripts/
│   ├── analyzer.py      # Lógica de análise estatística
│   └── utils.py         # Funções auxiliares (Parsing, Logs, Sheets)
├── dados/               # Pasta contendo os CSVs dos testes (Input)
│   ├── dataset_01_parceiroA.csv
│   └── ...
├── outputs/             # Resultados e históricos
│   └── historico_testes.csv
└── credentials.json     # (Opcional) Credenciais para API do Google Sheets
```

## Como Executar

1. **Preparação dos Dados**: Coloque os arquivos `.csv` que deseja analisar dentro da pasta `dados/`. Certifique-se de que seguem o schema padrão (Data, Grupos de usuários, Parceiro, compradores, comissão, cashback, vendas totais).

2. **Execução**:
   Abra o terminal na pasta raiz do projeto e execute:
   ```bash
   python scripts/analyzer.py [CAMINHO_DO_ARQUIVO]
   ```

3. **Visualização**:
   - O script imprimirá um **Relatório Executivo** no terminal para cada parceiro.
   - Um log será atualizado em `outputs/historico_testes.csv`.
   - Se configurado, os dados aparecerão automaticamente na Planilha de Acompanhamento.

## Uso com Assistentes de IA (Claude Code, Cursor, Gemini)

Esta ferramenta foi desenhada para ser acionada via linguagem natural. Se você estiver usando um assistente com acesso ao terminal (como Claude Code, Cursor ou Gemini), você pode simplesmente dizer:

> "Analise o novo teste contido em `dados/novo_dataset.csv` usando o script analyzer e me dê a recomendação final."

**O que a IA fará:**
1. Executará o comando `python scripts/analyzer.py dados/novo_dataset.csv`.
2. Lerá o relatório gerado no terminal.
3. Resumirá para você o vencedor e a justificativa baseada na significância estatística.

## Entendendo a Análise

O analyzer utiliza as seguintes métricas chave:
- **Net Revenue**: Lucro bruto (Comissão - Cashback). É a métrica principal de decisão.
- **P-Value (Ajustado)**: Probabilidade de a diferença observada ser fruto do acaso. Utilizamos a correção de Holm-Bonferroni para mitigar falsos positivos em testes com muitos grupos.
- **Cohen's d**: Mede o "Tamanho do Efeito". Indica se a diferença, além de estatisticamente significante, é grande o suficiente para ter impacto real no negócio.
- **IC 95% (Diff)**: Intervalo de confiança para a diferença entre as médias.

**Lógica de Decisão:**
- O algoritmo identifica o líder pela **maior média de Net Revenue**.
- O líder é declarado vencedor apenas se superar **todos os outros grupos** individualmente com um p-valor ajustado inferior a 0.05.
- Se o efeito for estatisticamente significante mas o **Cohen's d** for muito baixo (< 0.2), o sistema alerta que o impacto operacional pode ser desprezível.
- Em caso de inconclusividade, o sistema recomenda a continuidade da coleta de dados.

## Configuração do Google Sheets

Para habilitar a escrita direta no Google Sheets:
1. Crie um projeto no Google Cloud Console.
2. Ative a **Google Sheets API** e **Google Drive API**.
3. Crie uma **Service Account**, gere uma chave JSON e salve-a como `credentials.json` na raiz deste projeto.
4. Compartilhe sua planilha de log com o e-mail da Service Account criada.

---