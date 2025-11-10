# services/transferencia_service.py
from models.database import Database
from utils.date_utils import get_brasilia_time, utc_to_brasilia
from datetime import datetime

class TransferenciaService:
    def __init__(self):
        self.db = Database()
    
    def registrar_transferencia(self, colaborador_id, canal):
        """Registra uma nova transferência"""
        # Validações de negócio
        if not colaborador_id:
            raise ValueError("Colaborador é obrigatório")
        if canal not in ['WhatsApp', 'Instagram']:
            raise ValueError("Canal deve ser 'WhatsApp' ou 'Instagram'")
        
        self.db.salvar_transferencia(colaborador_id, canal)
    
    def carregar_dados_interface(self):
        """Carrega todos os dados para a interface (substitui a função carregar_dados)"""
        conn = self.db.get_connection()
        c = conn.cursor()
        
        # Carregar colaboradores e setores
        c.execute('''
            SELECT c.id, c.nome as colaborador, s.nome as setor 
            FROM colaboradores c 
            JOIN setores s ON c.setor_id = s.id
            ORDER BY s.nome, c.nome
        ''')
        colaboradores_data = c.fetchall()
        
        # Totais por colaborador
        c.execute('''
            SELECT c.nome as colaborador, s.nome as setor, t.canal, COUNT(*) as total
            FROM transferencias t
            JOIN colaboradores c ON t.colaborador_id = c.id
            JOIN setores s ON c.setor_id = s.id
            GROUP BY c.nome, s.nome, t.canal
        ''')
        
        totais = {}
        for row in c.fetchall():
            colaborador = row[0]
            setor = row[1]
            canal = row[2]
            total = row[3]
            
            if colaborador not in totais:
                totais[colaborador] = {
                    'setor': setor,
                    'WhatsApp': 0, 
                    'Instagram': 0, 
                    'Total': 0
                }
            
            totais[colaborador][canal] = total
            totais[colaborador]['Total'] += total
        
        # Histórico recente (últimas 10 transferências)
        c.execute('''
            SELECT t.data, c.nome as colaborador, s.nome as setor, t.canal
            FROM transferencias t
            JOIN colaboradores c ON t.colaborador_id = c.id
            JOIN setores s ON c.setor_id = s.id
            ORDER BY t.data DESC
            LIMIT 10
        ''')
        
        historico = []
        hoje_brasilia = get_brasilia_time().date()
        
        for row in c.fetchall():
            # Converter para horário de Brasília
            data_utc = datetime.fromisoformat(row[0].replace('Z', '+00:00'))
            data_brasilia = utc_to_brasilia(data_utc)
            
            historico.append({
                'colaborador': row[1],
                'setor': row[2],
                'canal': row[3],
                'hora': data_brasilia.strftime('%H:%M'),
                'data_completa': data_brasilia.strftime('%d/%m/%Y %H:%M'),
                'hoje': data_brasilia.date() == hoje_brasilia
            })
        
        # Transferências de hoje
        data_hoje_brasilia = get_brasilia_time().strftime('%Y-%m-%d')
        c.execute('''
            SELECT t.canal, COUNT(*) as total
            FROM transferencias t
            WHERE DATE(t.data) = DATE(?)
            GROUP BY t.canal
        ''', (data_hoje_brasilia,))
        
        transferencias_hoje = 0
        whats_hoje = 0
        insta_hoje = 0
        for row in c.fetchall():
            total = row[1]
            transferencias_hoje += total
            if row[0] == 'WhatsApp':
                whats_hoje = total
            else:
                insta_hoje = total
        
        # Última transferência
        c.execute('''
            SELECT t.data, c.nome as colaborador, s.nome as setor, t.canal
            FROM transferencias t
            JOIN colaboradores c ON t.colaborador_id = c.id
            JOIN setores s ON c.setor_id = s.id
            ORDER BY t.data DESC
            LIMIT 1
        ''')
        
        ultimo_registro = None
        row = c.fetchone()
        if row:
            data_utc = datetime.fromisoformat(row[0].replace('Z', '+00:00'))
            data_brasilia = utc_to_brasilia(data_utc)
            
            ultimo_registro = {
                'colaborador': row[1],
                'setor': row[2],
                'canal': row[3],
                'hora': data_brasilia.strftime('%H:%M'),
                'data_completa': data_brasilia.strftime('%d/%m/%Y às %H:%M')
            }
        
        conn.close()
        
        # Calcular totais gerais
        total_whatsapp = sum(dados['WhatsApp'] for dados in totais.values())
        total_instagram = sum(dados['Instagram'] for dados in totais.values())
        total_geral = sum(dados['Total'] for dados in totais.values())
        
        colaboradores = [{'id': row[0], 'nome': row[1], 'setor': row[2]} for row in colaboradores_data]
        
        return {
            "totais": totais,
            "historico": historico,
            "transferencias_hoje": transferencias_hoje,
            "whats_hoje": whats_hoje,
            "insta_hoje": insta_hoje,
            "ultimo_registro": ultimo_registro,
            "total_whatsapp": total_whatsapp,
            "total_instagram": total_instagram,
            "total_geral": total_geral,
            "colaboradores": colaboradores
        }
    
    def obter_todas_transferencias(self):
        """Obtém todas as transferências para edição"""
        conn = self.db.get_connection()
        c = conn.cursor()
        
        c.execute('''
            SELECT t.id, t.data, c.nome as colaborador, s.nome as setor, t.canal, c.id as colaborador_id
            FROM transferencias t
            JOIN colaboradores c ON t.colaborador_id = c.id
            JOIN setores s ON c.setor_id = s.id
            ORDER BY t.data DESC
        ''')
        
        transferencias = []
        for row in c.fetchall():
            data_utc = datetime.fromisoformat(row[1].replace('Z', '+00:00'))
            data_brasilia = utc_to_brasilia(data_utc)
            
            transferencias.append({
                'id': row[0],
                'data': data_brasilia.strftime('%d/%m/%Y %H:%M'),
                'colaborador': row[2],
                'setor': row[3],
                'canal': row[4],
                'colaborador_id': row[5]
            })
        
        conn.close()
        return transferencias
    
    def editar_transferencia(self, transferencia_id, novo_colaborador_id, novo_canal):
        """Edita uma transferência existente"""
        conn = self.db.get_connection()
        c = conn.cursor()
        c.execute(
            'UPDATE transferencias SET colaborador_id = ?, canal = ? WHERE id = ?',
            (novo_colaborador_id, novo_canal, transferencia_id)
        )
        conn.commit()
        conn.close()
    
    def excluir_transferencia(self, transferencia_id):
        """Exclui uma transferência"""
        conn = self.db.get_connection()
        c = conn.cursor()
        c.execute('DELETE FROM transferencias WHERE id = ?', (transferencia_id,))
        conn.commit()
        conn.close()