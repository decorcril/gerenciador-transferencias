# app.py
from flask import Flask, render_template
from models.database import Database
from controllers.transferencia_controller import transferencia_bp
from controllers.relatorio_controller import relatorio_bp

app = Flask(__name__)

# Registrar blueprints (módulos)
app.register_blueprint(transferencia_bp)
app.register_blueprint(relatorio_bp)

@app.route("/")
def index():
    """Página principal"""
    # Carregar colaboradores para o template
    db = Database()
    conn = db.get_connection()
    c = conn.cursor()
    c.execute('''
        SELECT c.id, c.nome, s.nome as setor 
        FROM colaboradores c 
        JOIN setores s ON c.setor_id = s.id
        ORDER BY s.nome, c.nome
    ''')
    colaboradores_rows = c.fetchall()
    conn.close()
    
    colaboradores = [{'id': row[0], 'nome': row[1], 'setor': row[2]} for row in colaboradores_rows]
    
    return render_template("index.html", colaboradores=colaboradores)

if __name__ == "__main__":
    # Inicializar banco de dados
    db = Database()
    db.init_db()
    
    # Criar pastas necessárias
    import os
    os.makedirs("templates", exist_ok=True)
    os.makedirs("static", exist_ok=True)
    
    print("Sistema iniciado em: http://localhost:5000")
    app.run(debug=True, port=5000)