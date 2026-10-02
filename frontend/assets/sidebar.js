/* ==========================================================================
   InoSys · comportamento comum a todas as telas
   - Sidebar: marca o módulo ativo (o painel do celular é o offcanvas-lg do Bootstrap)
   - Modais: abertura por data-abrir-modal (com ou sem hx-get) e foco no 1º campo
   - Mockup (file://): seletor de perfil, bloqueio das requisições HTMX,
     avisos flutuantes e modo de desenvolvimento do HTMX com ?htmx=1
   No Django, o perfil vem de request.user e o template já chega filtrado;
   a parte de mockup não roda fora de file://.
   ========================================================================== */
(function () {
  'use strict';

  // Só existe simulação quando a tela é aberta com duplo clique.
  window.inosysMockup = window.location.protocol === 'file:';

  var parametros = new URLSearchParams(window.location.search);
  var verGanchos = window.inosysMockup && parametros.has('htmx');

  // Usuários fictícios, um por perfil do README.
  var PERFIS = {
    estoque: { rotulo: 'Operacional de Estoque', nome: 'Paula Ribeiro', iniciais: 'PR' },
    fretes:  { rotulo: 'Operacional de Fretes',  nome: 'Diego Santos',  iniciais: 'DS' },
    gestor:  { rotulo: 'Gestor',                 nome: 'Marcos Lima',   iniciais: 'ML' },
    admin:   { rotulo: 'Administrador',          nome: 'Ana Souza',     iniciais: 'AS' }
  };
  var CHAVE_PERFIL = 'inosys-perfil';

  /* ---------------------------------------------------------------- util */
  function lerPerfil() {
    var valor = null;
    try { valor = window.localStorage.getItem(CHAVE_PERFIL); } catch (e) { /* sem storage */ }
    return PERFIS[valor] ? valor : 'admin';
  }
  function gravarPerfil(valor) {
    try { window.localStorage.setItem(CHAVE_PERFIL, valor); } catch (e) { /* sem storage */ }
  }

  var fmtInteiro = new Intl.NumberFormat('pt-BR', { maximumFractionDigits: 0 });
  var fmtDecimal = new Intl.NumberFormat('pt-BR', { minimumFractionDigits: 1, maximumFractionDigits: 1 });
  var fmtMoeda = new Intl.NumberFormat('pt-BR', { style: 'currency', currency: 'BRL' });

  var formatar = {
    numero: function (v) { return fmtInteiro.format(Number(v) || 0); },
    decimal: function (v) { return fmtDecimal.format(Number(v) || 0); },
    moeda: function (v) { return fmtMoeda.format(Number(v) || 0); },
    data: function (v) {
      if (!v) return '';
      var p = String(v).slice(0, 10).split('-');
      return p.length === 3 ? p[2] + '/' + p[1] + '/' + p[0] : v;
    }
  };

  // Preenche [data-campo="chave"] dentro de "raiz" usando data-formato.
  function preencher(raiz, dados) {
    Object.keys(dados).forEach(function (chave) {
      raiz.querySelectorAll('[data-campo="' + chave + '"]').forEach(function (el) {
        var f = formatar[el.getAttribute('data-formato')];
        el.textContent = f ? f(dados[chave]) : (dados[chave] == null ? '' : dados[chave]);
      });
    });
  }

  // Mostra só os [data-se="nome"] cujo nome está verdadeiro no mapa.
  // No Django isso é uma condição no template.
  function mostrarSe(raiz, mapa) {
    raiz.querySelectorAll('[data-se]').forEach(function (el) {
      el.hidden = !mapa[el.getAttribute('data-se')];
    });
  }

  function lerForm(form) {
    var dados = {};
    new FormData(form).forEach(function (valor, chave) { dados[chave] = valor; });
    return dados;
  }
  function preencherForm(form, dados) {
    Object.keys(dados).forEach(function (chave) {
      var campo = form.elements[chave];
      if (!campo) return;
      if (campo instanceof RadioNodeList) {
        Array.prototype.forEach.call(campo, function (r) { r.checked = r.value === String(dados[chave]); });
      } else if (campo.type === 'checkbox') {
        campo.checked = !!dados[chave];
      } else {
        campo.value = dados[chave] == null ? '' : dados[chave];
      }
    });
  }

  /* Lista do mockup: faz o papel do Django + Paginator (20 por página).
     Convenção dentro do card:
       <form data-lista-filtros>          filtros
       <tbody data-lista-itens>           linhas
       <tbody data-lista-vazia hidden>    "nenhum resultado"
       <template data-lista-linha>        corpo do laço for
       [data-contador] [data-pagina-texto] [data-pagina-acao="anterior|proxima"] */
  function lista(cfg) {
    var card = cfg.card;
    var POR_PAGINA = 20;
    var pagina = 1;
    var form = card.querySelector('[data-lista-filtros]');
    var corpo = card.querySelector('[data-lista-itens]');
    var vazio = card.querySelector('[data-lista-vazia]');
    var modelo = card.querySelector('[data-lista-linha]');

    function filtrados() {
      var filtros = form ? lerForm(form) : {};
      var itens = cfg.dados.filter(function (item) { return cfg.filtro ? cfg.filtro(item, filtros) : true; });
      return cfg.ordenar ? itens.sort(cfg.ordenar) : itens;
    }

    function render() {
      var itens = filtrados();
      var total = itens.length;
      var paginas = Math.max(1, Math.ceil(total / POR_PAGINA));
      if (pagina > paginas) pagina = paginas;
      var inicio = (pagina - 1) * POR_PAGINA;
      var fatia = itens.slice(inicio, inicio + POR_PAGINA);

      corpo.replaceChildren();
      fatia.forEach(function (item) {
        var tr = modelo.content.firstElementChild.cloneNode(true);
        tr.setAttribute('data-id', item.id);
        cfg.preencher(tr, item);
        corpo.appendChild(tr);
      });
      if (vazio) vazio.hidden = total > 0;

      var contador = card.querySelector('[data-contador]');
      if (contador) {
        contador.textContent = total
          ? 'Mostrando ' + (inicio + 1) + '–' + (inicio + fatia.length) + ' de ' + total
          : 'Nenhum resultado';
      }
      var texto = card.querySelector('[data-pagina-texto]');
      if (texto) texto.textContent = 'Página ' + pagina + ' de ' + paginas;
      card.querySelectorAll('[data-pagina-acao]').forEach(function (el) {
        var anterior = el.getAttribute('data-pagina-acao') === 'anterior';
        var bloqueado = anterior ? pagina === 1 : pagina === paginas;
        el.closest('.page-item').classList.toggle('disabled', bloqueado);
        el.setAttribute('aria-disabled', bloqueado ? 'true' : 'false');
      });
      if (cfg.depois) cfg.depois(itens);
    }

    if (form) {
      form.addEventListener('input', function () { pagina = 1; render(); });
      form.addEventListener('submit', function (e) { e.preventDefault(); pagina = 1; render(); });
      form.addEventListener('reset', function () { window.setTimeout(function () { pagina = 1; render(); }, 0); });
    }
    card.addEventListener('click', function (e) {
      var el = e.target.closest('[data-pagina-acao]');
      if (!el || el.closest('.page-item').classList.contains('disabled')) return;
      e.preventDefault();
      pagina += el.getAttribute('data-pagina-acao') === 'anterior' ? -1 : 1;
      render();
      card.scrollIntoView({ behavior: 'smooth', block: 'start' });
    });

    render();
    return {
      render: render,
      item: function (id) { return cfg.dados.filter(function (i) { return String(i.id) === String(id); })[0]; },
      // Item da linha onde o botão foi clicado.
      daLinha: function (el) {
        var tr = el.closest('tr[data-id]');
        return tr ? this.item(tr.getAttribute('data-id')) : null;
      }
    };
  }

  function hoje() {
    var d = new Date();
    var mes = String(d.getMonth() + 1).padStart(2, '0');
    var dia = String(d.getDate()).padStart(2, '0');
    return d.getFullYear() + '-' + mes + '-' + dia;
  }

  /* ---------------------------------------- aviso flutuante (some em 4 s) */
  function toast(mensagem, icone) {
    var area = document.querySelector('.is-toasts');
    if (!area) {
      area = document.createElement('div');
      area.className = 'is-toasts';
      area.setAttribute('aria-live', 'polite');
      document.body.appendChild(area);
    }
    var item = document.createElement('div');
    item.className = 'alert alert-success d-flex align-items-center gap-2';
    item.setAttribute('role', 'status');
    var i = document.createElement('i');
    i.className = 'bi ' + (icone || 'bi-check-circle');
    i.setAttribute('aria-hidden', 'true');
    var texto = document.createElement('span');
    texto.textContent = mensagem;
    item.appendChild(i);
    item.appendChild(texto);
    area.appendChild(item);
    window.setTimeout(function () { item.remove(); }, 4000);
  }

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
  //  - sem hx-get (ou no mockup): abre o modal na hora;
  //  - com hx-get no Django: abre depois que o HTMX troca o conteúdo.
  document.addEventListener('click', function (e) {
    var el = e.target.closest('[data-abrir-modal]');
    if (!el) return;
    if (window.inosysMockup || !el.hasAttribute('hx-get')) abrirModal(el.getAttribute('data-abrir-modal'));
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

  // No mockup não existe servidor: toda requisição HTMX é cancelada
  // e a simulação de cada tela faz o papel do Django.
  document.addEventListener('htmx:confirm', function (e) {
    if (window.inosysMockup) e.preventDefault();
  });

  /* ------------------------------------------------------------- sidebar */
  function marcarModuloAtivo() {
    var modulo = document.body.getAttribute('data-modulo');
    if (!modulo) return;
    document.querySelectorAll('.is-nav-link[data-modulo]').forEach(function (a) {
      var ativo = a.getAttribute('data-modulo') === modulo;
      a.classList.toggle('active', ativo);
      if (ativo) a.setAttribute('aria-current', 'page'); else a.removeAttribute('aria-current');
    });
  }

  /* ------------------------------------------------------ perfil (mockup) */
  function aplicarPerfil(perfil) {
    var dados = PERFIS[perfil];
    document.querySelectorAll('[data-usuario-nome]').forEach(function (el) { el.textContent = dados.nome; });
    document.querySelectorAll('[data-usuario-perfil]').forEach(function (el) { el.textContent = dados.rotulo; });
    document.querySelectorAll('[data-usuario-iniciais]').forEach(function (el) { el.textContent = dados.iniciais; });

    // Itens marcados com data-perfis aparecem só para os perfis listados.
    document.querySelectorAll('[data-perfis]').forEach(function (el) {
      if (el === document.body) return;
      el.hidden = el.getAttribute('data-perfis').split(/\s+/).indexOf(perfil) === -1;
    });

    // Tela inteira fora do perfil: mostra aviso no lugar do conteúdo.
    var permitidos = document.body.getAttribute('data-perfis');
    var conteudo = document.querySelector('[data-conteudo-tela]');
    if (!permitidos || !conteudo) return;
    var liberado = permitidos.split(/\s+/).indexOf(perfil) !== -1;
    var aviso = document.getElementById('is-sem-acesso');
    if (!aviso) {
      aviso = document.createElement('div');
      aviso.id = 'is-sem-acesso';
      aviso.className = 'card mx-auto my-5';
      aviso.innerHTML =
        '<div class="card-body text-center py-5 px-4">' +
        '<i class="bi bi-shield-lock fs-2 text-muted" aria-hidden="true"></i>' +
        '<h1 class="h5 mt-3">Esta tela não faz parte do seu perfil</h1>' +
        '<p class="text-muted mb-4">No sistema real o acesso é bloqueado pelo servidor. ' +
        'No mockup, troque o perfil no rodapé da sidebar para visualizar.</p>' +
        '<a class="btn btn-primary" href="selecao.html">Voltar ao início</a></div>';
      conteudo.parentNode.insertBefore(aviso, conteudo);
    }
    aviso.hidden = liberado;
    conteudo.hidden = !liberado;
  }

  function configurarPerfil() {
    var perfil = lerPerfil();
    document.querySelectorAll('[data-somente-mockup]').forEach(function (el) { el.hidden = !window.inosysMockup; });
    if (!window.inosysMockup) return;
    document.querySelectorAll('select[data-mockup-perfil]').forEach(function (sel) {
      sel.value = perfil;
      sel.addEventListener('change', function () {
        gravarPerfil(sel.value);
        aplicarPerfil(sel.value);
        document.dispatchEvent(new CustomEvent('inosys:perfil', { detail: { perfil: sel.value } }));
        toast('Perfil simulado: ' + PERFIS[sel.value].rotulo, 'bi-person-badge');
      });
    });
    aplicarPerfil(perfil);
  }

  /* ---------------------- modo de desenvolvimento do HTMX (?htmx=1) */
  function mostrarGanchos() {
    // O CSS (.htmx-debug) contorna todo elemento com hx-get / hx-post.
    document.body.classList.add('htmx-debug');

    // Mantém o ?htmx=1 ao navegar entre as telas.
    document.querySelectorAll('a[href$=".html"]').forEach(function (a) {
      a.setAttribute('href', a.getAttribute('href') + '?htmx=1');
    });

    var VERBOS = ['hx-get', 'hx-post', 'hx-put', 'hx-delete'];
    var ganchos = document.querySelectorAll(VERBOS.map(function (v) { return '[' + v + ']'; }).join(','));

    var painel = document.createElement('aside');
    painel.className = 'is-htmx-panel';
    painel.setAttribute('aria-label', 'Ganchos HTMX desta tela');
    var topo = document.createElement('div');
    topo.className = 'd-flex align-items-center justify-content-between gap-2';
    var titulo = document.createElement('h2');
    var fechar = document.createElement('button');
    fechar.type = 'button';
    fechar.className = 'btn-close btn-close-white';
    fechar.setAttribute('aria-label', 'Fechar painel');
    fechar.addEventListener('click', function () { painel.remove(); });
    topo.appendChild(titulo);
    topo.appendChild(fechar);
    painel.appendChild(topo);

    // Linhas de tabela repetem o mesmo gancho: agrupa e mostra "× N".
    var vistos = {};
    Array.prototype.forEach.call(ganchos, function (el) {
      var verbo = VERBOS.filter(function (v) { return el.hasAttribute(v); })[0];
      var url = el.getAttribute(verbo);
      var meta = [
        'gatilho: ' + (el.getAttribute('hx-trigger') || 'padrão'),
        'alvo: ' + (el.getAttribute('hx-target') || 'o próprio elemento'),
        'troca: ' + (el.getAttribute('hx-swap') || 'innerHTML')
      ].join(' · ') + (el.closest('.modal') ? ' · dentro de modal' : '');
      var chave = verbo + url + meta;
      if (vistos[chave]) {
        vistos[chave].total += 1;
        vistos[chave].conta.textContent = ' × ' + vistos[chave].total;
        return;
      }
      var botao = document.createElement('button');
      botao.type = 'button';
      botao.className = 'hook';
      var v = document.createElement('span');
      v.className = 'verbo';
      v.textContent = verbo.slice(3).toUpperCase();
      var u = document.createElement('span');
      u.className = 'url';
      u.textContent = url;
      var conta = document.createElement('span');
      conta.className = 'url';
      var m = document.createElement('span');
      m.className = 'meta';
      m.textContent = meta;
      botao.appendChild(v); botao.appendChild(u); botao.appendChild(conta); botao.appendChild(m);
      botao.addEventListener('click', function () { el.scrollIntoView({ behavior: 'smooth', block: 'center' }); });
      painel.appendChild(botao);
      vistos[chave] = { total: 1, conta: conta };
    });
    titulo.textContent = 'Ganchos HTMX · ' + Object.keys(vistos).length + ' nesta tela';
    document.body.appendChild(painel);
  }

  /* --------------------------------------------------------------- início */
  window.inosys = {
    PERFIS: PERFIS,
    perfil: lerPerfil,
    formatar: formatar,
    preencher: preencher,
    mostrarSe: mostrarSe,
    lerForm: lerForm,
    preencherForm: preencherForm,
    lista: lista,
    hoje: hoje,
    toast: toast,
    abrirModal: abrirModal,
    fecharModal: fecharModal
  };

  function iniciar() {
    marcarModuloAtivo();
    configurarPerfil();
    if (verGanchos) mostrarGanchos();
  }
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', iniciar);
  else iniciar();
})();
