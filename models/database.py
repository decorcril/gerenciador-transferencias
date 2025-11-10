# models/database.py
import sqlite3
import os
from datetime import datetime, timezone, timedelta

class Database:
    def __init__(self, db_path='transferencias.db'):
        self.db_path = db_path
        self.timezone_brasilia = timezone(timedelta(hours=-3))
    
    def get_connection(self):
        """Cria conexão com o banco de dados"""
        return sqlite3.connect(self.db_path)
    
    def init_db(self):
        """Inicializa o banco de dados com as tabelas"""
        conn = self.get_connection()
        c = conn.cursor()
        
        # Tabela de setores
        c.execute('''
            CREATE TABLE IF NOT EXISTS setores (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nome TEXT NOT NULL UNIQUE
            )
        ''')
        
        # Tabela de colaboradores
        c.execute('''
            CREATE TABLE IF NOT EXISTS colaboradores (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nome TEXT NOT NULL,
                setor_id INTEGER,
                FOREIGN KEY (setor_id) REFERENCES setores(id)
            )
        ''')
        
        # Tabela de transferências
        c.execute('''
            CREATE TABLE IF NOT EXISTS transferencias (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                data TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                colaborador_id INTEGER,
                canal TEXT NOT NULL,
                FOREIGN KEY (colaborador_id) REFERENCES colaboradores(id)
            )
        ''')
        
        # Inserir dados iniciais se as tabelas estiverem vazias
        c.execute("SELECT COUNT(*) FROM setores")
        if c.fetchone()[0] == 0:
            # Inserir setores
            setores = [
                ('Vendas SP',),
                ('Vendas JP',),
                ('Pós-venda',),
                ('Financeiro',)
            ]
            c.executemany('INSERT INTO setores (nome) VALUES (?)', setores)
            
            # Inserir colaboradores
            colaboradores = [
                ('Olivia', 1),    # Vendas SP
                ('Fabiana', 1),   # Vendas SP
                ('Tatiane', 1),   # Vendas SP
                ('Gustavo', 1),   # Vendas SP
                ('Debora', 1),    # Vendas SP
                ('Evelin', 1),    # Vendas SP
                ('Maysa', 2),     # Vendas JP
                ('Otavia', 3),    # Pós-venda
                ('Adriana', 4)    # Financeiro
            ]
            c.executemany('INSERT INTO colaboradores (nome, setor_id) VALUES (?, ?)', colaboradores)
        
        conn.commit()
        conn.close()
    
    def salvar_transferencia(self, colaborador_id, canal):
        """Salva uma nova transferência no banco"""
        conn = self.get_connection()
        c = conn.cursor()
        c.execute(
            'INSERT INTO transferencias (colaborador_id, canal) VALUES (?, ?)',
            (colaborador_id, canal)
        )
        conn.commit()
        conn.close()