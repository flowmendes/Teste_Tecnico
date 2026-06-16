import pandas as pd
import numpy as np
import os
from scipy import stats
try:
    # Tenta importar como módulo se o script for executado da raiz do projeto
    from scripts import utils
except ImportError:
    # Tenta importar diretamente se o script for executado de dentro da pasta scripts
    import utils

def carregar_dados(caminho):
    """Lê o arquivo CSV tratando diferentes encodings e converte moedas."""
    try:
        df = pd.read_csv(caminho, sep=None, engine='python', encoding='utf-8-sig')
    except UnicodeDecodeError:
        df = pd.read_csv(caminho, sep=None, engine='python', encoding='latin1')
    
    for col in ['comissão', 'cashback']:
        # Aplica a limpeza de string de moeda para float
        df[col] = df[col].apply(utils.limpar_moeda)
    
    # Calcula a métrica primária: Receita Líquida
    df['net_revenue'] = df['comissão'] - df['cashback']
    return df

def calcular_metricas(df):
    """Agrega os dados por grupo para análise descritiva e inferencial."""
    analysis = df.groupby('Grupos de usuários')['net_revenue'].agg(['sum', 'mean', 'count', 'std']).reset_index()
    analysis.columns = ['Grupos de usuários', 'total_net_revenue', 'avg_net_revenue', 'sample_size', 'std_dev']
    return analysis

def analisar_significancia(df, vencedor, outros_grupos):
    """
    Realiza testes estatísticos (Welch T-Test) comparando o líder contra os demais.
    Aplica a correção de Holm-Bonferroni para mitigar o erro de múltiplas comparações.
    """
    vencedor_dados = df[df['Grupos de usuários'] == vencedor]['net_revenue']
    m1 = vencedor_dados.mean()
    s1 = vencedor_dados.std()
    n1 = len(vencedor_dados)

    p_values = []
    for grupo in outros_grupos:
        grupo_dados = df[df['Grupos de usuários'] == grupo]['net_revenue']
        m2 = grupo_dados.mean()
        s2 = grupo_dados.std()
        n2 = len(grupo_dados)

        # Tratamento de variância zero: se os dados são constantes e as médias diferem, a diferença é determinística
        if (s1 == 0 or np.isnan(s1)) and (s2 == 0 or np.isnan(s2)):
            p_raw = 0.0 if m1 != m2 else 1.0
        else:
            # Welch T-Test: não assume variâncias iguais entre os grupos
            _, p_raw = stats.ttest_ind(vencedor_dados, grupo_dados, equal_var=False)
            if np.isnan(p_raw): p_raw = 1.0
            
        p_values.append({"grupo": grupo, "p_raw": p_raw})

    # Ordena p-values para aplicar Holm-Bonferroni (método step-down)
    p_values.sort(key=lambda x: x['p_raw'])
    num_comp = len(p_values)
    for i, item in enumerate(p_values):
        # Ajuste do p-value: p_adj = p_raw * (número_de_comparações - ranking + 1)
        item['p_adj'] = min(1.0, item['p_raw'] * (num_comp - i))
    
    # Garantir monotonicidade dos p-values ajustados
    for i in range(1, num_comp):
        p_values[i]['p_adj'] = max(p_values[i]['p_adj'], p_values[i-1]['p_adj'])

    return p_values

def escolher_vencedor(analysis, df):
    """Executa a lógica de decisão baseada em significância e magnitude de efeito."""
    # Caso degenerado: Nenhuma variante gerou receita
    if (analysis['total_net_revenue'] == 0).all():
        return {"status": "Inconclusivo", "justificativa": "Nenhuma variante apresentou receita.", "comparacoes": [], "qualidade": []}

    # Caso degenerado: Variantes com comportamento idêntico
    if len(analysis) > 1 and (analysis['avg_net_revenue'].nunique() == 1) and (analysis['std_dev'].nunique() == 1):
        return {"status": "Inconclusivo", "justificativa": "Não há diferença observável entre as variantes.", "comparacoes": [], "qualidade": []}

    if analysis.empty:
        return {
            "parceiro": "Desconhecido", 
            "vencedor": None, 
            "lider_observado": None,
            "lucro": 0.0, 
            "sample_size": 0,
            "p_value": 1.0, 
            "comparacoes": [],
            "status": "Inconclusivo", 
            "justificativa": "Dados insuficientes para análise."
        }

    # O líder observado é quem possui a maior média de Net Revenue
    vencedor = analysis.loc[analysis['avg_net_revenue'].idxmax()]
    nome_vencedor = vencedor['Grupos de usuários']
    outros = [g for g in analysis['Grupos de usuários'] if g != nome_vencedor]
    
    # Se houver apenas um grupo, não há o que comparar
    if not outros:
        return {
            "parceiro": df['Parceiro'].iloc[0],
            "vencedor": None,
            "lider_observado": nome_vencedor,
            "lucro": vencedor['total_net_revenue'],
            "avg_profit": vencedor['avg_net_revenue'],
            "sample_size": vencedor['sample_size'],
            "lift": 0,
            "p_value": 1.0,
            "comparacoes": [],
            "status": "Inconclusivo",
            "justificativa": "Apenas um grupo detectado no dataset. Comparação impossível."
        }

    # Calcula p-values ajustados comparando o líder contra todos os outros
    comparacoes = analisar_significancia(df, nome_vencedor, outros)
    p_max_adj = max(c['p_adj'] for c in comparacoes) if comparacoes else 1.0
    # O teste só é significativo se o líder vencer TODOS os outros grupos (p < 0.05)
    status = "Significativo" if p_max_adj < 0.05 else "Inconclusivo"

    # Seleção dinâmica de baseline para o cálculo de métricas de efeito:
    # 1. Se o vencedor não for o Grupo 1, o baseline é o Grupo 1 (Controle).
    # 2. Se o vencedor for o Grupo 1, comparamos com a segunda melhor variante.
    nome_controle = 'Grupo 1'
    grupos_disponiveis = analysis['Grupos de usuários'].values
    
    if nome_vencedor != nome_controle and nome_controle in grupos_disponiveis:
        base = analysis.loc[analysis['Grupos de usuários'] == nome_controle].iloc[0]
    elif outros:
        idx_melhor_outro = analysis.loc[analysis['Grupos de usuários'].isin(outros), 'avg_net_revenue'].idxmax()
        base = analysis.loc[idx_melhor_outro]
    else:
        base = vencedor

    # Magnitude da diferença absoluta das médias
    diff_abs = vencedor['avg_net_revenue'] - base['avg_net_revenue']
    # Cálculo do Tamanho do Efeito (Cohen's d): Mede quão grande é a separação das distribuições
    pooled_std = np.sqrt((vencedor['std_dev']**2 + base['std_dev']**2) / 2)
    cohen_d = (diff_abs / pooled_std) if pooled_std > 0 else 0

    # Cálculo do Intervalo de Confiança de 95% para a diferença das médias
    se_diff = np.sqrt((vencedor['std_dev']**2 / vencedor['sample_size']) + (base['std_dev']**2 / base['sample_size']))
    ic_min, ic_max = diff_abs - (1.96 * se_diff), diff_abs + (1.96 * se_diff)

    if status == "Significativo":
        if abs(cohen_d) > 0.2:
            recomendacao = f"Escalar {nome_vencedor} para 100% do tráfego."
        else:
            recomendacao = "Diferença estatística detectada, mas impacto operacional baixo (Efeito pequeno)."
    else:
        if (analysis['sample_size'].sum()) > 500:
            recomendacao = "Diferença provavelmente irrelevante (Amostra grande sem significância)."
        else:
            recomendacao = "Continuar coleta de dados (Amostra pode ser insuficiente)."

    # Verificações de saúde do experimento
    qualidade = []
    if (analysis['sample_size'] < 30).any():
        qualidade.append("ALERTA: Grupos com menos de 30 observações. Risco de instabilidade.")
    if analysis['sample_size'].std() / analysis['sample_size'].mean() > 0.2:
        qualidade.append("ALERTA: Grupos desbalanceados detectados.")

    justificativa = (f"O {nome_vencedor} superou as demais variantes com significância ajustada." if status == "Significativo" else 
                    f"Não há confiança estatística suficiente para declarar um vencedor.")

    return {
        "parceiro": df['Parceiro'].iloc[0],
        "vencedor": nome_vencedor if status == "Significativo" else None,
        "lider_observado": nome_vencedor,
        "lucro_total": vencedor['total_net_revenue'],
        "avg_profit": vencedor['avg_net_revenue'],
        "sample_size": vencedor['sample_size'],
        "diff_abs": diff_abs,
        "cohen_d": cohen_d,
        "ic": (ic_min, ic_max),
        "p_value": p_max_adj,
        "comparacoes": comparacoes,
        "status": status,
        "justificativa": justificativa,
        "recomendacao": recomendacao,
        "qualidade": qualidade
    }

def gerar_relatorio(res):
    if not res.get('parceiro'): 
        print(f"Relatório incompleto: {res['justificativa']}")
        return

    print(f"\n{'='*50}")
    print(f"RESULTADO TESTE A/B: {res['parceiro']}")
    print(f"{'='*50}")

    print(f"STATUS: {res['status']}")
    print(f"{'Grupo Vencedor' if res['vencedor'] else 'Líder Observado'}: {res['lider_observado']}")
    
    print(f"\nMÉTRICAS DO LÍDER:")
    print(f"- Lucro Total:    R$ {res['lucro_total']:.2f}")
    print(f"- Lucro Médio:    R$ {res['avg_profit']:.2f}")
    print(f"- Diferença Abs:  {res['diff_abs']:+.2f}")
    print(f"- Cohen's d:      {res['cohen_d']:.3f}")
    print(f"- IC 95% (Diff):  [{res['ic'][0]:.2f} ; {res['ic'][1]:.2f}]")
    print(f"- Amostra:        {res['sample_size']} observações")

    print(f"\nCOMPARAÇÕES ESTATÍSTICAS (Holm-Bonferroni):")
    for comp in res['comparacoes']:
        print(f"- vs {comp['grupo']}: p-orig = {comp['p_raw']:.4f}, p-adj = {comp['p_adj']:.4f}")

    if res['qualidade']:
        print(f"\nQUALIDADE DO EXPERIMENTO:")
        for q in res['qualidade']: print(f" {q}")

    print(f"\nDECISÃO:")
    # Recomendações baseadas em evidência estatística e relevância prática
    print(f"- Recomendação: {res['recomendacao']}")
    print(f"- Justificativa: {res['justificativa']}")
    
    print(f"\nMETODOLOGIA:")
    print("- Métrica: Média de Net Revenue")
    print("- Correção: Holm-Bonferroni")
    print("- Teste: Welch T-Test (alfa=0.05)")
    print(f"{'='*50}\n")

def main(caminho_csv):
    """Fluxo principal de execução para um único arquivo."""
    df = carregar_dados(caminho_csv)
    analysis = calcular_metricas(df)
    resultado = escolher_vencedor(analysis, df)
    gerar_relatorio(resultado)
    
    log_entry = utils.registrar_no_historico(resultado)
    utils.registrar_no_sheets(log_entry)

if __name__ == "__main__":
    import sys
    # Processa apenas um arquivo via argumento ou usa um padrão
    input_path = sys.argv[1] if len(sys.argv) > 1 else os.path.join("dados", "dataset_01_parceiroA.csv")
    
    # Verifica se o arquivo existe no caminho fornecido ou tenta dentro da pasta 'dados'
    if os.path.exists(input_path):
        main(input_path)
    elif os.path.exists(os.path.join("dados", input_path)):
        main(os.path.join("dados", input_path))
    else:
        print(f"Erro: Arquivo '{input_path}' não encontrado.")
        print("Dica: Certifique-se de que o arquivo está na pasta 'dados/' ou forneça o caminho completo.")
        sys.exit(1)