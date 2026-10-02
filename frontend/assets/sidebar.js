/* ==========================================================================
   InoSys · comportamento comum a todas as telas
   - Sidebar: link ativo e painel deslizante abaixo de 992px
   - Modais: abertura por data-abrir-modal (com ou sem hx-get)
   - Mockup (file://): seletor de perfil, bloqueio das requisições HTMX,
     avisos (toasts) e visualização dos ganchos com ?htmx=1
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
  // No Django isso é um {% if %} no template.
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
       <template data-lista-linha>        corpo do {% for %}
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

  /* -------------------------------------------------------------- toasts */
  function toast(mensagem, icone) {
    var area = document.querySelector('.is-toasts');
    if (!area) {
      area = document.createElement('div');
      area.className = 'is-toasts';
      area.setAttribute('aria-live', 'polite');
      document.body.appendChild(area);
    }
    var item = document.createElement('div');
    item.className = 'is-toast';
    var i = document.createElement('i');
    i.className = 'bi ' + (icone || 'bi-check2-circle');
    i.setAttribute('aria-hidden', 'true');
    var texto = document.createElement('span');
    texto.textContent = mensagem;
    item.appendChild(i);
    item.appendChild(texto);
    area.appendChild(item);
    window.setTimeout(function () { item.remove(); }, 3800);
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
  function marcarLinkAtivo() {
    var pagina = document.body.getAttribute('data-pagina');
    if (!pagina) return;
    document.querySelectorAll('.is-nav-link[data-pagina]').forEach(function (a) {
      var ativo = a.getAttribute('data-pagina') === pagina;
      a.classList.toggle('active', ativo);
      if (ativo) a.setAttribute('aria-current', 'page'); else a.removeAttribute('aria-current');
    });
  }

  function configurarSidebarMovel() {
    var botao = document.querySelector('[data-abrir-sidebar]');
    var fundo = document.querySelector('.is-fundo-sidebar');
    if (!botao) return;
    function definir(aberta) {
      document.body.classList.toggle('is-sidebar-aberta', aberta);
      botao.setAttribute('aria-expanded', aberta ? 'true' : 'false');
    }
    botao.addEventListener('click', function () {
      definir(!document.body.classList.contains('is-sidebar-aberta'));
    });
    if (fundo) fundo.addEventListener('click', function () { definir(false); });
    document.addEventListener('keydown', function (e) {
      if (e.key === 'Escape' && document.body.classList.contains('is-sidebar-aberta')) { definir(false); botao.focus(); }
    });
    document.querySelectorAll('.is-sidebar a').forEach(function (a) {
      a.addEventListener('click', function () { definir(false); });
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
    // Esconde títulos de seção da sidebar que ficaram sem nenhum link.
    document.querySelectorAll('.is-nav-grupo').forEach(function (grupo) {
      var visiveis = grupo.querySelectorAll('.is-nav-link:not([hidden])').length;
      grupo.hidden = visiveis === 0;
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
      aviso.className = 'card is-sem-acesso';
      aviso.innerHTML =
        '<i class="bi bi-lock" aria-hidden="true"></i>' +
        '<h1 class="h5 mt-3">Esta tela não faz parte do seu perfil</h1>' +
        '<p class="text-secondary mb-4">No sistema real o acesso é bloqueado pelo servidor. ' +
        'No mockup, troque o perfil no rodapé da sidebar para visualizar.</p>' +
        '<a class="btn btn-primary" href="selecao.html">Voltar ao início</a>';
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
        document.querySelectorAll('select[data-mockup-perfil]').forEach(function (s) { s.value = sel.value; });
        document.dispatchEvent(new CustomEvent('inosys:perfil', { detail: { perfil: sel.value } }));
        toast('Perfil simulado: ' + PERFIS[sel.value].rotulo, 'bi-person-badge');
      });
    });
    aplicarPerfil(perfil);
  }

  /* ------------------------------------------- ganchos HTMX (?htmx=1) */
  function mostrarGanchos() {
    document.body.classList.add('is-ver-htmx');

    // Mantém o ?htmx=1 ao navegar entre as telas.
    document.querySelectorAll('a[href$=".html"]').forEach(function (a) {
      a.setAttribute('href', a.getAttribute('href') + '?htmx=1');
    });

    var ganchos = Array.prototype.filter.call(document.querySelectorAll('body *'), function (el) {
      return Array.prototype.some.call(el.attributes, function (at) { return at.name.indexOf('hx-') === 0; });
    });

    var painel = document.createElement('aside');
    painel.className = 'is-painel-htmx';
    painel.setAttribute('aria-label', 'Ganchos HTMX desta tela');
    var topo = document.createElement('header');
    var titulo = document.createElement('div');
    titulo.innerHTML = 'Ganchos HTMX <span></span>';
    titulo.querySelector('span').textContent = '· ' + ganchos.length + ' nesta tela';
    var recolher = document.createElement('button');
    recolher.type = 'button';
    recolher.textContent = 'recolher';
    recolher.addEventListener('click', function () {
      var r = painel.classList.toggle('is-recolhido');
      recolher.textContent = r ? 'expandir' : 'recolher';
    });
    topo.appendChild(titulo);
    topo.appendChild(recolher);
    painel.appendChild(topo);

    // Linhas de tabela repetem o mesmo gancho: agrupa e mostra "× N".
    var lista = document.createElement('ol');
    var vistos = {};
    ganchos.forEach(function (el) {
      el.classList.add('is-gancho');
      var partes = [];
      Array.prototype.forEach.call(el.attributes, function (at) {
        if (at.name.indexOf('hx-') === 0) partes.push(at.name + '="' + at.value + '"');
      });
      el.setAttribute('title', partes.join('\n'));
      var noModal = el.closest('.modal') ? ' (dentro de modal)' : '';
      var chave = '<' + el.tagName.toLowerCase() + '> ' + partes.join(' ') + noModal;
      if (vistos[chave]) {
        vistos[chave].total += 1;
        vistos[chave].code.textContent = chave + '  × ' + vistos[chave].total;
        return;
      }
      var li = document.createElement('li');
      var code = document.createElement('code');
      code.textContent = chave;
      li.appendChild(code);
      li.addEventListener('click', function () {
        el.scrollIntoView({ behavior: 'smooth', block: 'center' });
      });
      lista.appendChild(li);
      vistos[chave] = { total: 1, code: code };
    });
    titulo.querySelector('span').textContent = '· ' + Object.keys(vistos).length + ' nesta tela';
    painel.appendChild(lista);
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
    marcarLinkAtivo();
    configurarSidebarMovel();
    configurarPerfil();
    if (verGanchos) mostrarGanchos();
  }
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', iniciar);
  else iniciar();
})();
