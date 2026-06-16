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
            elif '.' in s:
                # Se houver ponto mas não vírgula, verificamos se é separador de milhar.
                # Heurística: se houver 3 dígitos após o ponto ou múltiplos pontos.
                if len(s.split('.')[-1]) == 3 or s.count('.') > 1:
                    s = s.replace('.', '')
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
        scopes = [
            'https://www.googleapis.com/auth/spreadsheets',
            'https://www.googleapis.com/auth/drive'
        ]
        # Resolve o caminho absoluto para as credenciais (evita erro dependendo de onde o script é chamado)
        base_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        creds_path = os.path.join(base_path, 'credentials.json')

        if not os.path.exists(creds_path):
            print(f"Erro: Arquivo {creds_path} não encontrado.")
            return

        creds = Credentials.from_service_account_file(creds_path, scopes=scopes)
        client = gspread.authorize(creds)
        
        # Verifique se este ID é exatamente o que aparece na URL da sua planilha
        planilhas_disponiveis = client.openall()

        if not planilhas_disponiveis:
            print("Erro: O robô não tem acesso a nenhuma planilha. Compartilhe a nova planilha com o e-mail dele!")
            return

        # 2. Ele seleciona automaticamente a PRIMEIRA planilha que encontrar (a mais recente ou a única compartilhada)
        planilha_automatica = planilhas_disponiveis[0]
        sheet = planilha_automatica.get_worksheet(0)
        
        # Adiciona cabeçalhos automaticamente se a planilha estiver vazia
        if not sheet.get_all_values():
            sheet.append_row(list(entry.keys()))
            
        sheet.append_row(list(entry.values()))
        print("Registro no Google Sheets realizado com sucesso.")
    except Exception as e:
        print(f"\n[DEBUG SHEETS] Erro ao registrar: {type(e).__name__}")
        print(f"[DEBUG SHEETS] Detalhes: {e}")