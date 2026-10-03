/* Fretes · apoio visual do modal de entrega e dos atalhos. O servidor calcula e valida tudo ao salvar. */
(function () {
  'use strict';

  function arred(v) { return Math.round(v * 100) / 100; }

  function sugeridoAtual() {
    var el = document.querySelector('#calculo-sugerido [data-valor]');
    var v = el ? el.getAttribute('data-valor') : '';
    return v === '' || v === null ? null : Number(v);
  }

  /* aviso "diferente do sugerido" enquanto a pessoa digita o valor cobrado */
  function avisarDivergencia() {
    var campo = document.getElementById('entrega-cobrado');
    var aviso = document.querySelector('[data-aviso-divergencia]');
    if (!campo || !aviso) return;
    var s = sugeridoAtual();
    var cobrado = campo.value === '' ? null : arred(Number(campo.value));
    var divergente = s !== null && cobrado !== null && cobrado !== s;
    aviso.hidden = !divergente;
    if (divergente) {
      var d = arred(cobrado - s);
      aviso.querySelector('[data-campo="diferenca"]').textContent =
        (d > 0 ? '+' : '\u2212') + window.inosys.formatar.moeda(Math.abs(d));
    }
  }

  document.addEventListener('input', function (e) {
    if (e.target.id === 'entrega-cobrado') avisarDivergencia();
  });
  document.addEventListener('htmx:afterSwap', avisarDivergencia);
  document.addEventListener('shown.bs.modal', avisarDivergencia);

  document.addEventListener('click', function (e) {
    /* "Usar sugerido" copia o valor calculado para o campo de valor cobrado */
    if (e.target.closest('[data-usar-sugerido]')) {
      var s = sugeridoAtual();
      var campo = document.getElementById('entrega-cobrado');
      if (s !== null && campo) { campo.value = s.toFixed(2); avisarDivergencia(); }
      return;
    }
    /* KPIs "Ver pendentes / em andamento / concluídas" filtram a lista logo abaixo */
    var kpi = e.target.closest('[data-ver-status]');
    if (kpi) {
      e.preventDefault();
      var f = document.getElementById('form-filtro-entregas');
      if (!f || !window.htmx) return;
      ['entregador', 'data_inicio', 'data_fim'].forEach(function (n) { f.elements[n].value = ''; });
      f.elements.status.value = kpi.getAttribute('data-ver-status');
      window.htmx.trigger(f, 'submit');
      var card = document.getElementById('card-entregas');
      if (card) card.scrollIntoView({ behavior: 'smooth', block: 'start' });
    }
  });
})();
