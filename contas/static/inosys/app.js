/* ==========================================================================
   InoSys · comportamento comum a todas as telas
   - Menu lateral: marca o módulo ativo (o painel do celular é o offcanvas-lg do Bootstrap)
   - Modais: abertura por data-abrir-modal, foco no 1º campo e fechamento quando o servidor responde 204
   - Avisos flutuantes: a mensagem vem do servidor no cabeçalho HX-Trigger
   - window.inosys: formatadores e funções usadas pelos scripts de cada tela
   O servidor decide tudo; aqui só há apoio visual.
   ========================================================================== */
(function () {
  'use strict';

  /* ------------------------------------------------------- formatadores */
  var fmtInteiro = new Intl.NumberFormat('pt-BR', { maximumFractionDigits: 0 });
  var fmtMoeda = new Intl.NumberFormat('pt-BR', { style: 'currency', currency: 'BRL' });
  var formatar = {
    numero: function (v) { return fmtInteiro.format(Number(v) || 0); },
    moeda: function (v) { return fmtMoeda.format(Number(v) || 0); }
  };

  /* ---------------------------------------- aviso flutuante (some em 4 s) */
  function toast(mensagem) {  // o ícone vem do trilho do .alert (estilos.css)
    var area = document.querySelector('.is-toasts');
    if (!area) {
      area = document.createElement('div');
      area.className = 'is-toasts';
      area.setAttribute('aria-live', 'polite');
      document.body.appendChild(area);
    }
    var item = document.createElement('div');
    item.className = 'alert alert-success';
    item.setAttribute('role', 'status');
    item.textContent = mensagem;
    area.appendChild(item);
    window.setTimeout(function () { item.remove(); }, 4000);
  }

  // O Django responde 204 com HX-Trigger: {"fretesAtualizados": {"mensagem": "..."}};
  // o htmx dispara o evento no <body> e a mensagem vira o aviso flutuante.
  ['estoqueAtualizado', 'fretesAtualizados', 'entregadoresAtualizados', 'usuariosAtualizados'].forEach(function (nome) {
    document.addEventListener(nome, function (e) {
      var mensagem = e.detail && e.detail.mensagem;
      if (mensagem) toast(mensagem);
    });
  });

  /* -------------------------------------------------------------- modais */
  function abrirModal(seletor) {
    var el = document.querySelector(seletor);
    if (el && window.bootstrap) window.bootstrap.Modal.getOrCreateInstance(el).show();
  }
  function fecharModal(alvo) {
    var el = typeof alvo === 'string' ? document.querySelector(alvo) : alvo;
    if (el && window.bootstrap) window.bootstrap.Modal.getOrCreateInstance(el).hide();
  }

  // Botão com data-abrir-modal:
  //  - sem hx-get: abre o modal na hora;
  //  - com hx-get: abre depois que o HTMX troca o conteúdo do modal.
  document.addEventListener('click', function (e) {
    var el = e.target.closest('[data-abrir-modal]');
    if (el && !el.hasAttribute('hx-get')) abrirModal(el.getAttribute('data-abrir-modal'));
  });
  document.addEventListener('htmx:afterSwap', function (e) {
    var origem = e.detail && e.detail.requestConfig && e.detail.requestConfig.elt;
    if (origem && origem.hasAttribute && origem.hasAttribute('data-abrir-modal')) {
      abrirModal(origem.getAttribute('data-abrir-modal'));
    }
  });

  // Ao abrir um modal com formulário, o cursor já vai para o primeiro campo.
  document.addEventListener('shown.bs.modal', function (e) {
    var campo = e.target.querySelector('form input:not([type=hidden]):not([type=radio]):not([type=checkbox]):not([readonly]), form select, form textarea');
    if (campo) campo.focus();
  });

  // Formulário dentro de modal que o Django respondeu com 204 = salvo.
  // O HX-Trigger da resposta recarrega a lista; aqui só fechamos o modal.
  document.addEventListener('htmx:afterRequest', function (e) {
    var elt = e.detail && e.detail.elt;
    var xhr = e.detail && e.detail.xhr;
    if (!elt || !xhr || xhr.status !== 204) return;
    var modal = elt.closest('.modal');
    if (modal) fecharModal(modal);
  });

  /* --------------------------------------------------------- menu lateral */
  function marcarModuloAtivo() {
    var modulo = document.body.getAttribute('data-modulo');
    if (!modulo) return;
    document.querySelectorAll('.is-nav-link[data-modulo]').forEach(function (a) {
      var ativo = a.getAttribute('data-modulo') === modulo;
      a.classList.toggle('active', ativo);
      if (ativo) a.setAttribute('aria-current', 'page'); else a.removeAttribute('aria-current');
    });
  }

  window.inosys = { formatar: formatar, toast: toast, abrirModal: abrirModal, fecharModal: fecharModal };

  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', marcarModuloAtivo);
  else marcarModuloAtivo();
})();
