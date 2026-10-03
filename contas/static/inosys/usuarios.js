/* Administração · botão "Copiar" da senha temporária e texto de ajuda do perfil. */
(function () {
  'use strict';

  document.addEventListener('click', function (e) {
    var botao = e.target.closest('[data-copiar-senha]');
    if (!botao) return;
    var alvo = botao.parentNode.querySelector('[data-senha]');
    function avisar() { botao.innerHTML = '<i class="bi bi-check-lg" aria-hidden="true"></i> Copiada'; }
    function selecionar() {
      var faixa = document.createRange();
      faixa.selectNodeContents(alvo);
      var sel = window.getSelection();
      sel.removeAllRanges();
      sel.addRange(faixa);
    }
    try {
      navigator.clipboard.writeText(alvo.textContent.trim()).then(avisar, selecionar);
    } catch (erro) { selecionar(); }
  });

  var AJUDA = {
    '': 'Define quais módulos a pessoa enxerga.',
    estoque: 'Acessa só o módulo de estoque.',
    fretes: 'Acessa só o módulo de fretes.',
    gestor: 'Acessa estoque, fretes, visão geral e relatórios.',
    admin: 'Acesso completo, incluindo usuários, log de ações e anonimização.'
  };
  document.addEventListener('change', function (e) {
    if (e.target.id !== 'usuario-perfil') return;
    var ajuda = document.getElementById('ajuda-perfil');
    if (ajuda) ajuda.textContent = AJUDA[e.target.value] || AJUDA[''];
  });
})();
