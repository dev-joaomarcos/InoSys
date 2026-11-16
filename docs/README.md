# Documentação do InoSys

O InoSys é o sistema interno da INOVE Divisórias e Forros para controlar o estoque de materiais e acompanhar o custo dos fretes. Esta pasta explica como ele funciona, da arquitetura ao uso.

## Por onde começar

| Você é... | Leia |
| --- | --- |
| Alguém de fora da área técnica | [Como o InoSys funciona, em linguagem simples](visao-simples.md) |
| Dev chegando no projeto | [Desenvolvimento](desenvolvimento.md), depois [Arquitetura](arquitetura.md) |
| Quem vai publicar a demo | [Deploy no Railway](deploy-railway.md) |
| Quem vai apresentar a demo | [Roteiro da demo](roteiro-demo.md) |
| Um agente de IA (Claude, Codex etc.) | [AGENTS.md](../AGENTS.md) na raiz, que aponta para cá |

## Mapa

| Documento | O que responde |
| --- | --- |
| [visao-simples.md](visao-simples.md) | O que o sistema faz e como, sem termos técnicos |
| [arquitetura.md](arquitetura.md) | Stack, apps, caminho de uma requisição, modelo de dados, permissões |
| [apps/contas.md](apps/contas.md) | Login, perfis, usuários, senha temporária, log de ações, anonimização |
| [apps/estoque.md](apps/estoque.md) | Materiais, entradas e saídas, alerta de estoque baixo |
| [apps/fretes.md](apps/fretes.md) | Entregadores, entregas, valor sugerido, divergência |
| [apps/relatorios.md](apps/relatorios.md) | Visão geral e relatórios |
| [frontend.md](frontend.md) | Templates, HTMX, CSS, e a comparação com o design system v2 |
| [desenvolvimento.md](desenvolvimento.md) | Rodar local, testes, convenções |
| [deploy-railway.md](deploy-railway.md) | Preparação e passo a passo do deploy |
| [roteiro-demo.md](roteiro-demo.md) | Passo a passo da apresentação e perguntas prováveis |
| [pendencias.md](pendencias.md) | Decisões em aberto e problemas conhecidos |
| [INOSYS-DESIGN-SYSTEM.html](INOSYS-DESIGN-SYSTEM.html) | Design system v2 (abrir no navegador) |
| [arquivo/](arquivo/README.md) | Material arquivado: mockups estáticos e design system v1 |

## Regra de manutenção

Mudou o comportamento de um app, muda o documento dele no mesmo commit. Quando o texto e o código discordarem, o código vence e o texto precisa ser corrigido.
