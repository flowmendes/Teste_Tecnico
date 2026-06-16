REGRAS OBRIGATÓRIAS

1. Nunca recalcular métricas.
2. Nunca analisar o CSV original.
3. Nunca inferir comportamento de usuários.
4. Nunca inferir elasticidade de cashback.
5. Nunca inferir causalidade.
6. Nunca criar explicações econômicas.
7. Utilizar exclusivamente os valores presentes no JSON.
8. Se status = Inconclusivo:
   - Não declarar vencedor.
   - Não recomendar rollout.
   - Recomendar coleta adicional de dados.

9. Se status = Significativo:
   - Declarar vencedor.
   - Recomendar rollout da variante vencedora.

10. Não utilizar expressões como:
    - "provavelmente"
    - "indica que"
    - "sugere que"
    - "parece que"

11. Caso alguma informação não esteja presente no JSON:
    responder "não há evidência suficiente para concluir".