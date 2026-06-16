# Relatório de Validação — Sistema de Análise de Testes A/B

## Objetivo

Validar que o agente de IA integrado ao projeto reproduz fielmente os resultados gerados pelo motor estatístico (`analyzer.py`), sem recalcular métricas, alterar decisões ou introduzir interpretações não suportadas pelos dados.

---

## Arquitetura da Solução

O sistema foi projetado para permitir que usuários executem análises de novos testes A/B utilizando linguagem natural.

Fluxo de execução:

1. O usuário informa o caminho do dataset.
2. O agente de IA executa o script `analyzer.py`.
3. O motor estatístico realiza todos os cálculos.
4. O resultado oficial é retornado pelo terminal.
5. A IA atua apenas como camada de apresentação e interpretação controlada.

---

## Cenário de Validação

Foram utilizados três datasets independentes:

| Dataset                  | Parceiro   |
| ------------------------ | ---------- |
| dataset_01_parceiroA.csv | Parceiro A |
| dataset_02_parceiroB.csv | Parceiro B |
| dataset_03_parceiroC.csv | Parceiro C |

Para cada dataset foi realizado o seguinte processo:

1. Execução direta do script `analyzer.py`.
2. Registro do resultado oficial produzido pelo motor estatístico.
3. Solicitação da mesma análise ao agente de IA utilizando linguagem natural.
4. Comparação entre a resposta da IA e o output oficial.

---

## Resultado Geral

| Parceiro | Status        | Decisão do Script | Decisão da IA    | Consistência |
| -------- | ------------- | ----------------- | ---------------- | ------------ |
| A        | Inconclusivo  | Continuar coleta  | Continuar coleta | ✅            |
| B        | Significativo | Escalar Grupo 1   | Escalar Grupo 1  | ✅            |
| C        | Significativo | Escalar Grupo 1   | Escalar Grupo 1  | ✅            |

### Taxa de Consistência

**100% (3 de 3 testes validados)**

---

# Parceiro A

## Resultado Oficial

### Status

Inconclusivo

### Líder Observado

Grupo 1

### Métricas

* Lucro Total: R$ 404.711,00
* Lucro Médio: R$ 4.399,03
* Diferença Absoluta: +512,96
* Cohen's d: 0.223
* IC 95%: [-150,45 ; 1176,36]
* Amostra: 92 observações

### Comparações Estatísticas

* Grupo 1 vs Grupo 3 → p-adj = 0.0000
* Grupo 1 vs Grupo 2 → p-adj = 0.1315

### Decisão Oficial

Continuar coleta de dados.

### Resultado da Auditoria por IA

A IA reproduziu corretamente:

* Status do teste;
* Líder observado;
* Ausência de vencedor estatístico;
* Recomendação operacional.

**Resultado:** ✅ Consistente

---

# Parceiro B

## Resultado Oficial

### Status

Significativo

### Grupo Vencedor

Grupo 1

### Métricas

* Lucro Total: R$ 286.570,00
* Lucro Médio: R$ 4.697,87
* Diferença Absoluta: +2351,03
* Cohen's d: 1.519
* IC 95%: [1801,60 ; 2900,46]
* Amostra: 61 observações

### Comparações Estatísticas

* Grupo 1 vs Grupo 3 → p-adj = 0.0000
* Grupo 1 vs Grupo 2 → p-adj = 0.0000

### Decisão Oficial

Escalar Grupo 1 para 100% do tráfego.

### Resultado da Auditoria por IA

A IA reproduziu corretamente:

* Grupo vencedor;
* Status estatístico;
* Recomendação operacional;
* Critério de decisão.

**Resultado:** ✅ Consistente

---

# Parceiro C

## Resultado Oficial

### Status

Significativo

### Grupo Vencedor

Grupo 1

### Métricas

* Lucro Total: R$ 34.769,00
* Lucro Médio: R$ 772,64
* Diferença Absoluta: +772,64
* Cohen's d: 5.472
* IC 95%: [714,30 ; 830,99]
* Amostra: 45 observações

### Comparações Estatísticas

* Grupo 1 vs Grupo 2 → p-adj = 0.0000

### Decisão Oficial

Escalar Grupo 1 para 100% do tráfego.

### Resultado da Auditoria por IA

A IA reproduziu corretamente:

* Grupo vencedor;
* Status estatístico;
* Recomendação operacional;
* Critério de decisão.

**Resultado:** ✅ Consistente

---

