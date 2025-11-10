// =============================================
// VARIÁVEIS GLOBAIS
// =============================================
const modal = document.getElementById('modal-editar');

// =============================================
// FUNÇÕES PRINCIPAIS
// =============================================

function carregarDados() {
    fetch('/api/dados')
        .then(response => response.json())
        .then(data => {
            atualizarInterface(data);
        })
        .catch(error => {
            console.error('Erro:', error);
        });
}

function registrarTransferencia(colaboradorId, canal) {
    const btn = document.querySelector('#form-transferencia .btn');
    const originalText = btn.textContent;
    
    btn.textContent = '⏳ Registrando...';
    btn.disabled = true;

    fetch('/api/registrar', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ colaborador_id: colaboradorId, canal: canal }),
    })
    .then(response => response.json())
    .then(data => {
        mostrarMensagem(data.message, 'success');
        btn.textContent = originalText;
        btn.disabled = false;
        carregarDados();
        
        // ✅ LIMPAR FORMULÁRIO APÓS REGISTRO BEM-SUCEDIDO
        limparFormulario();
    })
    .catch(error => {
        mostrarMensagem('❌ Erro ao registrar transferência', 'error');
        btn.textContent = originalText;
        btn.disabled = false;
    });
}

function limparFormulario() {
    console.log('🧹 Limpando formulário...');
    
    // 1. Limpar seleção do colaborador (voltar para o primeiro)
    const selectColaborador = document.getElementById('select-colaborador');
    if (selectColaborador) {
        selectColaborador.selectedIndex = 0;
        console.log('✅ Select colaborador limpo');
    }
    
    // 2. Limpar seleção do canal (desmarcar todos os radios)
    const radiosCanal = document.querySelectorAll('input[name="canal"]');
    let radiosLimpos = 0;
    radiosCanal.forEach(radio => {
        radio.checked = false;
        radiosLimpos++;
    });
    console.log(`✅ ${radiosLimpos} radios de canal limpos`);
    
    // 3. Dar foco no select para facilitar o próximo registro
    if (selectColaborador) {
        selectColaborador.focus();
    }
}

// =============================================
// FUNÇÕES DE EDIÇÃO - CORRIGIDAS
// =============================================

function carregarTransferencias() {
    console.log('🔍 Carregando transferências...');
    
    fetch('/api/transferencias')
        .then(response => response.json())
        .then(transferencias => {
            console.log('📊 Transferências carregadas:', transferencias.length);
            mostrarListaTransferencias(transferencias);
        })
        .catch(error => {
            console.error('Erro:', error);
            mostrarMensagem('❌ Erro ao carregar transferências', 'error');
        });
}

function mostrarListaTransferencias(transferencias) {
    const modalContent = document.querySelector('.modal-content');
    
    if (transferencias.length === 0) {
        modalContent.innerHTML = `
            <span class="close">&times;</span>
            <h3>📋 Gerenciar Transferências</h3>
            <p>Nenhuma transferência encontrada.</p>
            <button onclick="fecharModal()" class="btn">Fechar</button>
        `;
        reattacharEventosModal();
        modal.style.display = 'block';
        return;
    }
    
    modalContent.innerHTML = `
        <span class="close">&times;</span>
        <h3>📋 Gerenciar Transferências</h3>
        <div class="lista-transferencias">
            ${transferencias.map(transf => `
                <div class="transferencia-item">
                    <div class="transferencia-info">
                        <strong>${transf.colaborador}</strong> (${transf.setor})<br>
                        <small>${transf.canal} - ${transf.data}</small>
                    </div>
                    <div class="transferencia-acoes">
                        <button class="btn-editar" onclick="abrirEdicaoIndividual(${transf.id}, ${transf.colaborador_id}, '${transf.canal}', '${transf.data}', '${transf.colaborador}')">
                            ✏️ Editar
                        </button>
                    </div>
                </div>
            `).join('')}
        </div>
        <button onclick="fecharModal()" class="btn" style="margin-top: 15px;">Fechar</button>
    `;
    
    reattacharEventosModal();
    modal.style.display = 'block';
}

function reattacharEventosModal() {
    const closeBtn = document.querySelector('.close');
    if (closeBtn) {
        closeBtn.addEventListener('click', fecharModal);
    }
}

function abrirEdicaoIndividual(id, colaboradorId, canal, data, colaboradorNome) {
    console.log('✏️ Editando transferência:', id);
    
    fetch('/api/dados')
        .then(response => response.json())
        .then(dataApi => {
            const modalContent = document.querySelector('.modal-content');
            
            modalContent.innerHTML = `
                <span class="close">&times;</span>
                <h3>✏️ Editar Transferência</h3>
                <form id="form-editar">
                    <input type="hidden" id="editar-id" value="${id}">
                    
                    <label><strong>Data:</strong></label>
                    <input type="text" id="editar-data" value="${data}" readonly style="width: 100%; padding: 8px; margin: 5px 0;">
                    
                    <label><strong>👤 Colaborador:</strong></label>
                    <select id="editar-colaborador" name="colaborador_id" required style="width: 100%; padding: 8px; margin: 5px 0;">
                        ${dataApi.colaboradores.map(c => 
                            `<option value="${c.id}" ${c.id == colaboradorId ? 'selected' : ''}>${c.nome} (${c.setor})</option>`
                        ).join('')}
                    </select>
                    
                    <label><strong>📞 Canal:</strong></label><br>
                    <input type="radio" name="editar-canal" value="WhatsApp" ${canal === 'WhatsApp' ? 'checked' : ''} required> 📱 WhatsApp
                    <input type="radio" name="editar-canal" value="Instagram" ${canal === 'Instagram' ? 'checked' : ''} style="margin-left: 20px;"> 📷 Instagram<br><br>
                    
                    <div style="display: flex; gap: 10px;">
                        <button type="submit" class="btn" style="background: #28a745;">💾 Salvar</button>
                        <button type="button" id="btn-excluir" class="btn" style="background: #dc3545;">🗑️ Excluir</button>
                        <button type="button" id="btn-cancelar" class="btn" style="background: #6c757d;">❌ Cancelar</button>
                    </div>
                </form>
            `;
            
            reattacharEventosModal();
            
            document.getElementById('form-editar').addEventListener('submit', function(e) {
                e.preventDefault();
                salvarEdicao(id);
            });
            
            document.getElementById('btn-excluir').addEventListener('click', function() {
                excluirTransferencia(id);
            });
            
            document.getElementById('btn-cancelar').addEventListener('click', function() {
                carregarTransferencias();
            });
            
            modal.style.display = 'block';
        })
        .catch(error => {
            console.error('Erro ao carregar dados para edição:', error);
            mostrarMensagem('❌ Erro ao carregar dados', 'error');
        });
}

function salvarEdicao(id) {
    const colaboradorId = document.getElementById('editar-colaborador').value;
    const canal = document.querySelector('input[name="editar-canal"]:checked').value;
    
    console.log('💾 Salvando edição:', { id, colaboradorId, canal });
    
    fetch(`/api/editar_transferencia/${id}`, {
        method: 'PUT',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ colaborador_id: colaboradorId, canal: canal }),
    })
    .then(response => response.json())
    .then(data => {
        console.log('✅ Edição salva:', data);
        mostrarMensagem(data.message, 'success');
        fecharModal();
        carregarDados();
    })
    .catch(error => {
        console.error('❌ Erro ao editar:', error);
        mostrarMensagem('❌ Erro ao editar transferência', 'error');
    });
}

function excluirTransferencia(id) {
    if (confirm('Tem certeza que deseja excluir esta transferência?\nEsta ação não pode ser desfeita.')) {
        console.log('🗑️ Excluindo transferência:', id);
        
        fetch(`/api/excluir_transferencia/${id}`, {
            method: 'DELETE',
        })
        .then(response => response.json())
        .then(data => {
            console.log('✅ Transferência excluída:', data);
            mostrarMensagem(data.message, 'success');
            fecharModal();
            carregarDados();
        })
        .catch(error => {
            console.error('❌ Erro ao excluir:', error);
            mostrarMensagem('❌ Erro ao excluir transferência', 'error');
        });
    }
}

function fecharModal() {
    modal.style.display = 'none';
}

// =============================================
// FUNÇÕES DE EXPORTAÇÃO
// =============================================

function exportarRelatorioDiario() {
    console.log('📊 Exportando relatório diário...');
    
    // ✅ PEDIR CONFIRMAÇÃO ANTES
    if (!confirm('Deseja gerar e baixar o relatório diário?')) {
        console.log('❌ Download cancelado pelo usuário');
        return; // Usuário cancelou
    }
    
    const btnExportar = document.getElementById('btn-exportar');
    const originalText = btnExportar.textContent;
    
    btnExportar.textContent = '⏳ Gerando relatório...';
    btnExportar.disabled = true;

    fetch('/api/exportar/relatorio-diario')
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                mostrarMensagem(data.message, 'success');
                console.log(`✅ ${data.quantidade} transferências no relatório`);
                
                // ✅ DOWNLOAD COM CONFIRMAÇÃO VISUAL
                if (data.url) {
                    mostrarMensagem('📥 Preparando download...', 'success');
                    
                    // Pequeno delay para usuário ver a mensagem
                    setTimeout(() => {
                        const link = document.createElement('a');
                        link.href = data.url;
                        link.download = data.arquivo;
                        document.body.appendChild(link);
                        link.click();
                        document.body.removeChild(link);
                        
                        mostrarMensagem('✅ Download iniciado! Verifique sua pasta de downloads.', 'success');
                    }, 1000);
                }
            } else {
                mostrarMensagem(data.message, 'error');
            }
        })
        .catch(error => {
            console.error('Erro no relatório:', error);
            mostrarMensagem('❌ Erro ao gerar relatório', 'error');
        })
        .finally(() => {
            btnExportar.textContent = originalText;
            btnExportar.disabled = false;
        });
}
// =============================================
// FUNÇÕES DE INTERFACE
// =============================================

function mostrarMensagem(texto, tipo) {
    const mensagemDiv = document.getElementById('mensagem');
    mensagemDiv.textContent = texto;
    mensagemDiv.className = `mensagem ${tipo}`;
    mensagemDiv.style.display = 'block';
    
    setTimeout(() => {
        mensagemDiv.style.display = 'none';
    }, 3000);
}

function atualizarInterface(data) {
    // Última transferência
    if (data.ultimo_registro) {
        document.getElementById('ultimo-registro').style.display = 'block';
        document.getElementById('ultimo-colaborador').textContent = data.ultimo_registro.colaborador;
        document.getElementById('ultimo-setor').textContent = data.ultimo_registro.setor;
        document.getElementById('ultimo-canal').textContent = data.ultimo_registro.canal;
        const horaDisplay = data.ultimo_registro.data_completa || data.ultimo_registro.hora;
        document.getElementById('ultimo-hora').textContent = horaDisplay;
    }

    // Totais por colaborador
    const totaisDiv = document.getElementById('totais-colaboradores');
    if (Object.keys(data.totais).length > 0) {
        totaisDiv.innerHTML = '';
        for (const [colaborador, dados] of Object.entries(data.totais)) {
            const div = document.createElement('div');
            div.className = 'colaborador-row';
            div.innerHTML = `
                <div>
                    <span class="colaborador-name">${colaborador}</span>
                    <small style="color: #666;">(${dados.setor})</small>
                </div>
                <span>📱 ${dados.WhatsApp} | 📷 ${dados.Instagram} | <strong>🔄 ${dados.Total}</strong></span>
            `;
            totaisDiv.appendChild(div);
        }
    }

    // Histórico recente
    const historicoDiv = document.getElementById('historico-recente');
    if (data.historico.length > 0) {
        historicoDiv.innerHTML = '';
        data.historico.forEach(registro => {
            const div = document.createElement('div');
            div.className = `registro-item ${registro.hoje ? 'hoje' : ''}`;
            div.innerHTML = `
                <div>
                    <strong>${registro.colaborador}</strong> 
                    <small>(${registro.setor})</small> - ${registro.canal}
                </div>
                <div style="font-size: 12px; color: #666;">
                    ${registro.data_completa || registro.hora}
                    ${registro.hoje ? '<span class="badge">HOJE</span>' : ''}
                </div>
            `;
            historicoDiv.appendChild(div);
        });
    }

    // Resumo do dia
    document.getElementById('resumo-hoje').innerHTML = `
        <div style="font-size: 24px; font-weight: bold; color: #28a745;">
            ${data.transferencias_hoje} transferências hoje
        </div>
        <div style="margin-top: 10px;">
            <span style="color: #25D366;">📱 ${data.whats_hoje} WhatsApp</span> | 
            <span style="color: #E4405F;">📷 ${data.insta_hoje} Instagram</span>
        </div>
    `;

    // Estatísticas gerais
    if (Object.keys(data.totais).length > 0) {
        document.getElementById('estatisticas-gerais').style.display = 'flex';
        document.getElementById('estatisticas-gerais').innerHTML = `
            <div class="stat-box">
                <h3>📱 WhatsApp</h3>
                <h2>${data.total_whatsapp}</h2>
            </div>
            <div class="stat-box">
                <h3>📷 Instagram</h3>
                <h2>${data.total_instagram}</h2>
            </div>
            <div class="stat-box">
                <h3>🔄 Total de Transferências</h3>
                <h2>${data.total_geral}</h2>
            </div>
        `;
    }
}

// =============================================
// INICIALIZAÇÃO
// =============================================

document.addEventListener('DOMContentLoaded', function() {
    console.log('🚀 Sistema carregado!');
    
    carregarDados();
    
    const formTransferencia = document.getElementById('form-transferencia');
    if (formTransferencia) {
        formTransferencia.addEventListener('submit', function(e) {
            e.preventDefault();
            const colaboradorId = document.getElementById('select-colaborador').value;
            const canal = document.querySelector('input[name="canal"]:checked').value;
            registrarTransferencia(colaboradorId, canal);
        });
    }
    
    const btnAbrirEdicao = document.getElementById('btn-abrir-edicao');
    if (btnAbrirEdicao) {
        btnAbrirEdicao.addEventListener('click', carregarTransferencias);
    }
    
    // BOTÃO DE RELATÓRIO DIÁRIO
    const btnExportar = document.getElementById('btn-exportar');
    if (btnExportar) {
        btnExportar.addEventListener('click', exportarRelatorioDiario);
    }
    
    console.log('✅ Todos os event listeners configurados');
    
    setInterval(carregarDados, 30000);
});