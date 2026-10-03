/* Estoque · comportamento dos modais e atalhos. O servidor decide tudo; aqui só há apoio visual. */
(function () {
  'use strict';

  /* ------ modal de movimentação: motivo só na saída, saldo e saldo depois ------ */
  function atualizarMovimentacao() {
    var f = document.getElementById('form-movimentacao');
    if (!f) return;
    var sel = f.elements.material;
    var opt = sel.options[sel.selectedIndex];
    var tem = !!(opt && opt.value);
    var saldo = tem ? Number(opt.dataset.saldo) : 0;
    var un = tem ? opt.dataset.unidade : '';
    var saida = f.elements.tipo.value === 'saida';
    var qtd = Number(f.elements.quantidade.value) || 0;
    var fmt = window.inosys ? window.inosys.formatar.numero : String;

    f.querySelector('#grupo-motivo').hidden = !saida;
    f.elements.motivo.required = saida;

    var campo = f.elements.quantidade;
    var texto = f.querySelector('#mov-quantidade-erro');
    if (tem && saida && qtd > saldo) {
      texto.textContent = 'Saldo insuficiente: há ' + fmt(saldo) + ' ' + un + ' em estoque.';
      campo.classList.add('is-invalid');
    } else if (campo.classList.contains('is-invalid') && qtd > 0) {
      campo.classList.remove('is-invalid');
    }
    f.querySelector('[data-campo="saldo"]').textContent = tem ? fmt(saldo) + ' ' + un : '—';
    f.querySelector('[data-campo="saldo_depois"]').textContent =
      tem && qtd ? fmt(saldo + (saida ? -qtd : qtd)) + ' ' + un : '—';
  }
  ['input', 'change'].forEach(function (nome) {
    document.addEventListener(nome, function (e) {
      if (e.target.closest && e.target.closest('#form-movimentacao')) atualizarMovimentacao();
    });
  });
  document.addEventListener('htmx:afterSwap', atualizarMovimentacao);
  document.addEventListener('shown.bs.modal', atualizarMovimentacao);

  /* ------ atalhos "Ver só esses" (estoque baixo) e "Ver desativados" ------ */
  function filtrar(valores) {
    var f = document.getElementById('form-filtro-materiais');
    if (!f || !window.htmx) return;
    var d = Object.assign({ busca: '', situacao: '', status: 'ativo' }, valores);
    Object.keys(d).forEach(function (k) { f.elements[k].value = d[k]; });
    window.htmx.trigger(f, 'submit');
    var card = document.getElementById('card-materiais');
    if (card) card.scrollIntoView({ behavior: 'smooth', block: 'start' });
  }
  document.addEventListener('click', function (e) {
    if (e.target.closest('[data-ver-baixo]')) { e.preventDefault(); filtrar({ situacao: 'baixo' }); }
    else if (e.target.closest('[data-ver-inativos]')) { e.preventDefault(); filtrar({ status: 'inativo' }); }
  });
})();
