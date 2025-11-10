# services/relatorio_service.py
import pandas as pd
from models.database import Database
from utils.date_utils import get_brasilia_time
from utils.export_utils import criar_pasta_exportacao
from openpyxl.styles import Font, Alignment, PatternFill, Border, Side
import os

class RelatorioService:
    def __init__(self):
        self.db = Database()
    
    def exportar_para_dataframe(self, data=None):
        """Exporta transferências para DataFrame"""
        conn = self.db.get_connection()
        
        if data:
            query = '''
                SELECT t.data, c.nome as colaborador, s.nome as setor, t.canal
                FROM transferencias t
                JOIN colaboradores c ON t.colaborador_id = c.id
                JOIN setores s ON c.setor_id = s.id
                WHERE DATE(t.data) = ?
                ORDER BY t.data
            '''
            df = pd.read_sql_query(query, conn, params=(data,))
        else:
            query = '''
                SELECT t.data, c.nome as colaborador, s.nome as setor, t.canal
                FROM transferencias t
                JOIN colaboradores c ON t.colaborador_id = c.id
                JOIN setores s ON c.setor_id = s.id
                ORDER BY t.data
            '''
            df = pd.read_sql_query(query, conn)
        
        conn.close()
        
        # Converter datas para horário de Brasília
        df['data'] = pd.to_datetime(df['data']).dt.tz_localize('UTC').dt.tz_convert('America/Sao_Paulo')
        df['data_only'] = df['data'].dt.strftime('%d/%m/%Y')
        df['hora_only'] = df['data'].dt.strftime('%H:%M')
        
        return df
    
    def gerar_relatorio_diario(self):
        """Gera relatório diário completo"""
        data_hoje = get_brasilia_time().strftime('%Y-%m-%d')
        data_formatada = get_brasilia_time().strftime('%d/%m/%Y')
        hora_formatada = get_brasilia_time().strftime('%H:%M')
        
        # Buscar dados
        df_detalhes = self.exportar_para_dataframe(data_hoje)
        
        if df_detalhes.empty:
            return None
        
        # Buscar totais
        conn = self.db.get_connection()
        
        # Totais por colaborador
        query_totais = '''
            SELECT 
                c.nome as colaborador,
                s.nome as setor,
                SUM(CASE WHEN t.canal = 'WhatsApp' THEN 1 ELSE 0 END) as whatsapp,
                SUM(CASE WHEN t.canal = 'Instagram' THEN 1 ELSE 0 END) as instagram,
                COUNT(*) as total
            FROM transferencias t
            JOIN colaboradores c ON t.colaborador_id = c.id
            JOIN setores s ON c.setor_id = s.id
            WHERE DATE(t.data) = ?
            GROUP BY c.nome, s.nome
            ORDER BY total DESC
        '''
        df_totais = pd.read_sql_query(query_totais, conn, params=(data_hoje,))
        
        # Totais gerais
        query_geral = '''
            SELECT 
                COUNT(*) as total_geral,
                SUM(CASE WHEN t.canal = 'WhatsApp' THEN 1 ELSE 0 END) as total_whatsapp,
                SUM(CASE WHEN t.canal = 'Instagram' THEN 1 ELSE 0 END) as total_instagram
            FROM transferencias t
            WHERE DATE(t.data) = ?
        '''
        df_geral = pd.read_sql_query(query_geral, conn, params=(data_hoje,))
        
        conn.close()
        
        return {
            'df_detalhes': df_detalhes,
            'df_totais': df_totais,
            'df_geral': df_geral,
            'data_formatada': data_formatada,
            'hora_formatada': hora_formatada,
            'quantidade': len(df_detalhes)
        }
    
    def exportar_relatorio_excel(self, relatorio):
        """Exporta o relatório para Excel"""
        pasta = criar_pasta_exportacao()
        data_exportacao = get_brasilia_time().strftime('%d-%m-%Y_%H-%M')
        nome_arquivo = f'relatorio_diario_{data_exportacao}.xlsx'
        caminho_arquivo = os.path.join(pasta, nome_arquivo)
                
        return nome_arquivo, caminho_arquivo