/* InoSys · avisos vindos do servidor.
   O Django responde 204 com o cabeçalho HX-Trigger: {"fretesAtualizados": {"mensagem": "..."}};
   o htmx dispara o evento e aqui ele vira o aviso flutuante (toast) do design system. */
(function () {
  'use strict';
  ['estoqueAtualizado', 'fretesAtualizados', 'entregadoresAtualizados', 'usuariosAtualizados'].forEach(function (nome) {
    document.body.addEventListener(nome, function (e) {
      var mensagem = e.detail && e.detail.mensagem;
      if (mensagem && window.inosys) window.inosys.toast(mensagem);
    });
  });
})();
