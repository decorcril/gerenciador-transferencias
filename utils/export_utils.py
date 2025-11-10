# utils/export_utils.py
import os

def criar_pasta_exportacao():
    """Cria a pasta de exportação no caminho específico do usuário com fallback"""
    
    caminho_principal = r"C:\Users\User\Documents\Relatorio Transferencia"
    
    # Locais de fallback em ordem de preferência
    locais_fallback = [
        caminho_principal,
        os.path.join(os.path.expanduser("~"), "Documents", "Relatorio Transferencia"),
        os.path.join(os.path.expanduser("~"), "Desktop", "Relatorios_Transferencias"),
        os.path.join(os.path.expanduser("~"), "Downloads", "Relatorios_Transferencias"),
        "exportacoes"  # Fallback final
    ]
    
    for pasta in locais_fallback:
        try:
            if not os.path.exists(pasta):
                os.makedirs(pasta)
                print(f"✅ Pasta criada: {pasta}")
            else:
                print(f"✅ Pasta já existe: {pasta}")
            return pasta
        except Exception as e:
            print(f"❌ Erro ao criar pasta {pasta}: {e}")
            continue
    
    # Último fallback absoluto
    pasta_temp = os.path.join(os.getcwd(), "exportacoes")
    os.makedirs(pasta_temp, exist_ok=True)
    print(f"⚠️  Usando fallback final: {pasta_temp}")
    return pasta_temp