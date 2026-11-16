# Pendências

Atualizado em 16/11/2026. Ao resolver um item, remova-o daqui e atualize o documento do assunto. Decisões já tomadas ficam em [arquitetura.md](arquitetura.md#decisões-de-projeto).

## Antes da demo

| Tema | Situação |
| --- | --- |
| Deploy real | Repositório preparado e verificado localmente. Falta executar no Railway ([deploy-railway.md](deploy-railway.md)) |
| Ensaio da demo | O [roteiro](roteiro-demo.md) existe, mas ainda não foi ensaiado no ambiente publicado |
| Dependência de CDN | Bootstrap, HTMX, ícones e fontes vêm da internet. Se a rede do local da demo bloquear CDN, as telas ficam sem estilo e sem os ícones de alerta e badge. Testar no local ou ter o celular como roteador |
| Avisar o autor do design system | O HTML foi renomeado para `INOSYS-DESIGN-SYSTEM.html` e passou para a versão 2.1. Ele precisa partir desta versão nas próximas edições |

## Depois da demo

### Funcionalidade

| Tema | O que fazer |
| --- | --- |
| Log de ações | Registrar qual registro foi alterado, além de quem, ação e quando |
| Anonimização de entregadores | Avaliar estender o RF15 a entregadores (nome e contato são dados pessoais) |
| Gráficos | Decidir entre manter HTML/CSS ou adotar biblioteca |
| Backup diário do banco (RNF10) | Nada configurado. Depende do plano do Railway |

### Design system

| Tema | O que fazer |
| --- | --- |
| Tema escuro | Previsto no design system, não implementado. Exige tokens escuros, revisão das cores soltas restantes no CSS e teste das 11 telas |
| Badge escuro | No documento é navy sólido com texto branco; no sistema, navy translúcido com texto navy. Escolher um |

### Código e repositório

| Tema | Situação | O que fazer |
| --- | --- | --- |
| `docs/arquivo/mockups-front/` | Arquivamento temporário dos mockups | Remover |
| Integração contínua | Os 101 testes só rodam se alguém lembrar | Workflow simples do GitHub Actions |
| Healthcheck no Railway | Não configurado; exige ajuste no `settings.py` | Ver [deploy-railway.md](deploy-railway.md) |
