"""Dados de demonstração: usuários, materiais, movimentações, entregadores e entregas.

Os dados são fixos (sem sorteio) e as datas são relativas a hoje, para o roteiro da demo
(docs/roteiro-demo.md) poder citar nomes e números. Só roda em banco sem materiais nem entregadores.

Fica em `relatorios` porque é o único app que pode importar `estoque` e `fretes`.
"""
import os
from datetime import timedelta
from decimal import Decimal

from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from django.utils import timezone

from contas.logs import registrar_log
from contas.models import LogAcao, PerfilUsuario, Usuario
from estoque.models import Material, Movimentacao
from estoque.services import registrar_movimentacao
from fretes.models import Entrega, Entregador
from fretes.services import calcular_sugerido

E, S = Movimentacao.ENTRADA, Movimentacao.SAIDA
USO, PERDA, AJUSTE = "uso_producao", "perda_dano", "ajuste_inventario"
CONCLUIDA, ANDAMENTO, PENDENTE = Entrega.CONCLUIDA, Entrega.EM_ANDAMENTO, Entrega.PENDENTE
IGUAL = "igual"  # valor cobrado = valor sugerido

# (username, nome, perfil)
USUARIOS = [
    ("paula", "Paula Ribeiro", PerfilUsuario.ESTOQUE),
    ("fabio", "Fábio Lima", PerfilUsuario.FRETES),
    ("gustavo", "Gustavo Mendes", PerfilUsuario.GESTOR),
]

# chave: (nome, descrição, unidade, quantidade mínima, ativo)
MATERIAIS = {
    "gesso": ("Placa de gesso acartonado 12,5 mm", "Placa standard 1,20 × 2,40 m", "un", 20, True),
    "montante": ("Perfil montante 70 mm", "Aço galvanizado, barra de 3 m", "pç", 50, True),
    "guia": ("Perfil guia 48 mm", "Aço galvanizado, barra de 3 m", "pç", 30, True),
    "parafuso": ("Parafuso ponta broca 3,5 × 25 mm", "Caixa com 1.000 unidades", "cx", 10, True),
    "pvc": ("Forro de PVC 20 cm", "Branco, régua de 6 m", "m²", 100, True),
    "massa": ("Massa para junta", "Balde de 5 kg", "kg", 15, True),
    "fita": ("Fita telada para junta", "Rolo de 90 m", "rl", 8, True),
    "la": ("Lã de vidro 50 mm", "Isolamento acústico", "m²", 40, True),
    "naval": ("Painel divisória naval 35 mm", "Linha descontinuada", "un", 5, False),
}

# (dias atrás, material, tipo, quantidade, motivo)
MOVIMENTACOES = [
    (29, "naval", E, 10, ""), (28, "gesso", E, 60, ""), (27, "montante", E, 200, ""), (26, "guia", E, 40, ""),
    (25, "parafuso", E, 25, ""), (24, "pvc", E, 300, ""), (23, "massa", E, 30, ""), (22, "fita", E, 20, ""),
    (21, "gesso", S, 30, USO), (20, "la", E, 80, ""), (19, "naval", S, 10, USO), (18, "pvc", S, 120, USO),
    (16, "massa", S, 12, USO), (15, "montante", S, 20, USO), (14, "parafuso", S, 8, USO), (12, "guia", S, 30, USO),
    (11, "la", S, 30, USO), (10, "fita", S, 5, USO), (9, "gesso", S, 16, USO), (8, "massa", S, 6, USO),
    (7, "pvc", S, 60, USO), (6, "parafuso", S, 5, USO), (5, "guia", S, 2, PERDA), (3, "massa", S, 3, AJUSTE),
    (2, "la", E, 50, ""),
]

# chave: (nome, contato, valor por km, ativo)
ENTREGADORES = {
    "joao": ("João Batista", "(11) 5550-0101", "2.50", True),
    "carlos": ("Carlos Menezes", "(11) 5550-0102", "3.20", True),
    "marta": ("Marta Oliveira", "(11) 5550-0103", "2.80", True),
    "rogerio": ("Rogério Dias", "(11) 5550-0104", "3.00", False),
}

# (dias atrás, entregador, destino, km, valor cobrado, status)
ENTREGAS = [
    (29, "rogerio", "Depósito em Cotia", "50.0", IGUAL, CONCLUIDA),
    (27, "joao", "Obra na Vila Mariana", "18.0", IGUAL, CONCLUIDA),
    (26, "carlos", "Galpão em Guarulhos", "45.0", IGUAL, CONCLUIDA),
    (24, "joao", "Escritório em Pinheiros", "12.5", IGUAL, CONCLUIDA),
    (23, "marta", "Obra em São Bernardo", "28.0", IGUAL, CONCLUIDA),
    (21, "carlos", "Obra em Osasco", "30.0", "90.00", CONCLUIDA),          # cobrou R$ 6,00 a menos
    (20, "joao", "Clínica em Santo André", "32.0", "95.00", CONCLUIDA),    # cobrou R$ 15,00 a mais
    (17, "carlos", "Escritório em Barueri", "38.5", IGUAL, CONCLUIDA),
    (15, "joao", "Loja em São Caetano", "26.0", IGUAL, CONCLUIDA),
    (13, "marta", "Escritório na Paulista", "9.5", "40.00", CONCLUIDA),    # cobrou R$ 13,40 a mais
    (11, "carlos", "Loja em Santana", "20.0", IGUAL, CONCLUIDA),
    (9, "joao", "Obra na Mooca", "14.0", IGUAL, CONCLUIDA),
    (7, "marta", "Loja no Ipiranga", "17.0", IGUAL, CONCLUIDA),
    (6, "carlos", "Academia na Lapa", "15.0", IGUAL, CONCLUIDA),
    (4, "joao", "Escola em Diadema", "40.0", "120.00", CONCLUIDA),         # cobrou R$ 20,00 a mais
    (2, "carlos", "Obra em Itaquera", "35.0", None, ANDAMENTO),
    (1, "joao", "Obra no Tatuapé", "22.0", None, ANDAMENTO),
    (0, "joao", "Consultório em Moema", "16.0", None, PENDENTE),
    (0, "carlos", "Clínica no Butantã", "24.0", None, PENDENTE),
    (0, "marta", "Obra em Mauá", "42.0", None, PENDENTE),
]


class Command(BaseCommand):
    help = "Popula um banco vazio com dados de demonstração."

    def add_arguments(self, parser):
        parser.add_argument("--senha", help="Senha dos usuários de demonstração (ou variável DEMO_SENHA).")
        parser.add_argument("--se-vazio", action="store_true",
                            help="Se o banco já tiver dados ou faltar a senha, sai sem erro (para rodar em todo deploy).")

    def handle(self, *args, **opcoes):
        senha = opcoes["senha"] or os.environ.get("DEMO_SENHA", "")
        tem_dados = Material.objects.exists() or Entregador.objects.exists()
        if opcoes["se_vazio"] and (tem_dados or not senha):
            self.stdout.write("popular_demo: banco já tem dados ou DEMO_SENHA não definida; nada a fazer.")
            return
        if tem_dados:
            raise CommandError("O banco já tem materiais ou entregadores. Rode em um banco limpo.")
        if not senha:
            raise CommandError("Informe a senha dos usuários de demonstração: --senha ou variável DEMO_SENHA.")
        with transaction.atomic():
            self._popular(senha)
        self.stdout.write(self.style.SUCCESS(
            f"popular_demo: {len(MATERIAIS)} materiais, {len(MOVIMENTACOES)} movimentações, "
            f"{len(ENTREGADORES)} entregadores e {len(ENTREGAS)} entregas criados. "
            f"Usuários: {', '.join(u[0] for u in USUARIOS)}."))

    def _popular(self, senha):
        hoje = timezone.localdate()
        usuarios = {}
        for username, nome, perfil in USUARIOS:
            usuario = Usuario.objects.filter(username=username).first()
            if not usuario:
                usuario = Usuario.objects.create_user(username, senha, nome=nome, perfil=perfil)
            usuarios[perfil] = usuario
        estoquista, operador_fretes = usuarios[PerfilUsuario.ESTOQUE], usuarios[PerfilUsuario.FRETES]

        materiais = {chave: Material.objects.create(nome=nome, descricao=descricao, unidade_medida=unidade,
                                                    quantidade_minima=minimo)
                     for chave, (nome, descricao, unidade, minimo, _ativo) in MATERIAIS.items()}
        for dias, chave, tipo, quantidade, motivo in MOVIMENTACOES:  # o serviço mantém o saldo coerente
            registrar_movimentacao(estoquista, materiais[chave], tipo, quantidade, hoje - timedelta(days=dias), motivo)
        inativos = [materiais[chave].pk for chave, dados in MATERIAIS.items() if not dados[4]]
        Material.objects.filter(pk__in=inativos).update(status=Material.INATIVO)

        entregadores = {chave: Entregador.objects.create(nome=nome, contato=contato, valor_por_km=Decimal(valor))
                        for chave, (nome, contato, valor, _ativo) in ENTREGADORES.items()}
        for dias, chave, destino, km, cobrado, status in ENTREGAS:
            entregador = entregadores[chave]
            sugerido = calcular_sugerido(Decimal(km), entregador.valor_por_km)
            Entrega.objects.create(
                entregador=entregador, usuario=operador_fretes, destino=destino, data=hoje - timedelta(days=dias),
                distancia=Decimal(km), valor_sugerido=sugerido, status=status,
                valor_cobrado=sugerido if cobrado == IGUAL else (Decimal(cobrado) if cobrado else None))
            registrar_log(operador_fretes, LogAcao.CRIACAO)
        inativos = [entregadores[chave].pk for chave, dados in ENTREGADORES.items() if not dados[3]]
        Entregador.objects.filter(pk__in=inativos).update(status=Entregador.INATIVO)
