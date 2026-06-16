import pandas as pd
import os

def limpar_moeda(valor):
    """Trata strings de moeda brasileira, nulos e valores numéricos para float."""
    if pd.isna(valor):
        return 0.0
    if isinstance(valor, (int, float)):
        return float(valor)
    if isinstance(valor, str):
        try:
            s = valor.replace('R$', '').replace('\xa0', '').strip()
            if not s:
                return 0.0
            if ',' in s:
                if '.' in s:
                    s = s.replace('.', '').replace(',', '.')
                else:
                    s = s.replace(',', '.')
            return float(s)
        except (ValueError, TypeError):
            return 0.0
    return 0.0

def registrar_no_historico(res):
    """Salva o resumo da decisão em um arquivo CSV local para auditoria."""
    output_dir = "outputs"
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    log_file = os.path.join(output_dir, "historico_testes.csv")
    entry = {
        "nome_do_teste": f"AB_Test_{res['parceiro']}",
        "descricao": f"Análise de lucro entre variantes",
        "resultado": f"Winner: {res['vencedor']} | P-val: {res['p_value']:.4f}",
        "decisao_tomada": f"Escalar {res['vencedor']}" if res['status'] == "Significativo" else "Manter busca por novas variantes"
    }
    
    df_log = pd.DataFrame([entry])
    df_log.to_csv(log_file, mode='a', index=False, header=not os.path.exists(log_file), encoding='utf-8-sig')
    return entry

def registrar_no_sheets(entry):
    """Envia os resultados para uma planilha do Google Sheets (opcional)."""
    try:
        import gspread
        from google.oauth2.service_account import Credentials
        scopes = ['https://www.googleapis.com/auth/spreadsheets']
        # Assume que o credentials.json está na raiz do projeto
        creds = Credentials.from_service_account_file('credentials.json', scopes=scopes)
        client = gspread.authorize(creds)
        sheet = client.open_by_key("1W5L7iL-F8M9-6o_KjD_3B_m_Yf8-k-P-U_K").get_worksheet(0)
        sheet.append_row(list(entry.values()))
        print("Registro no Google Sheets realizado com sucesso.")
    except Exception as e:
        print(f"Nota: Falha ao registrar no Google Sheets (Opcional): {e}")