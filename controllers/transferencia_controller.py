# controllers/transferencia_controller.py
from flask import Blueprint, request, jsonify
from services.transferencia_service import TransferenciaService

# Cria o Blueprint para transferências
transferencia_bp = Blueprint('transferencia', __name__)
service = TransferenciaService()

@transferencia_bp.route('/api/dados')
def api_dados():
    """API para carregar todos os dados da interface"""
    try:
        dados = service.carregar_dados_interface()
        return jsonify(dados)
    except Exception as e:
        return jsonify({
            "success": False, 
            "message": f"❌ Erro ao carregar dados: {str(e)}"
        }), 500

@transferencia_bp.route('/api/registrar', methods=['POST'])
def api_registrar():
    """API para registrar nova transferência"""
    try:
        data = request.get_json()
        colaborador_id = data.get("colaborador_id")
        canal = data.get("canal")
        
        service.registrar_transferencia(colaborador_id, canal)
        
        return jsonify({
            "success": True, 
            "message": "✅ Transferência registrada!"
        })
    except ValueError as e:
        return jsonify({
            "success": False, 
            "message": str(e)
        }), 400
    except Exception as e:
        return jsonify({
            "success": False, 
            "message": f"❌ Erro interno: {str(e)}"
        }), 500

@transferencia_bp.route('/api/transferencias')
def api_transferencias():
    """API para listar todas as transferências (para edição)"""
    try:
        transferencias = service.obter_todas_transferencias()
        return jsonify(transferencias)
    except Exception as e:
        return jsonify({
            "success": False, 
            "message": f"❌ Erro ao carregar transferências: {str(e)}"
        }), 500

@transferencia_bp.route('/api/editar_transferencia/<int:transferencia_id>', methods=['PUT'])
def api_editar_transferencia(transferencia_id):
    """API para editar uma transferência"""
    try:
        data = request.get_json()
        novo_colaborador_id = data.get("colaborador_id")
        novo_canal = data.get("canal")
        
        service.editar_transferencia(transferencia_id, novo_colaborador_id, novo_canal)
        
        return jsonify({
            "success": True, 
            "message": "✅ Transferência atualizada!"
        })
    except Exception as e:
        return jsonify({
            "success": False, 
            "message": f"❌ Erro ao editar transferência: {str(e)}"
        }), 500

@transferencia_bp.route('/api/excluir_transferencia/<int:transferencia_id>', methods=['DELETE'])
def api_excluir_transferencia(transferencia_id):
    """API para excluir uma transferência"""
    try:
        service.excluir_transferencia(transferencia_id)
        return jsonify({
            "success": True, 
            "message": "🗑️ Transferência excluída!"
        })
    except Exception as e:
        return jsonify({
            "success": False, 
            "message": f"❌ Erro ao excluir transferência: {str(e)}"
        }), 500