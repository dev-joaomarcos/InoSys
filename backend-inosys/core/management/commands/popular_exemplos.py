from datetime import timedelta

from django.core.management.base import BaseCommand
from django.utils import timezone

from estoque.models import Movimentacao, Produto
from fretes.models import Entregador, Frete

PRODUTOS = [  # nome, sku, unidade, mínimo, movimentações (tipo, quantidade)
    ("Caixa de papelão 40x30", "CX-4030", "un", 50, [("E", 200), ("S", 120)]),
    ("Fita adesiva 48mm", "FT-48", "un", 40, [("E", 120), ("S", 90)]),
    ("Filme stretch 500mm", "FS-500", "kg", 25, [("E", 60), ("S", 60)]),
    ("Palete PBR", "PL-PBR", "un", 10, [("E", 45), ("S", 12)]),
    ("Etiqueta térmica 100x150", "ET-100", "cx", 15, [("E", 40), ("S", 22)]),
]
ENTREGADORES = {
    "TransLog": ("(11) 3000-1000", "Frota rodoviária"), "AeroCargo": ("(11) 3555-2000", "Aéreo"),
    "RodoSul": ("(51) 3111-4000", "Caminhão"), "Mar Norte": ("(13) 3222-0000", "Navio"),
    "FerroBR": ("(34) 3888-4000", "Trem"),
}
FRETES = [  # origem, destino, entregador, modal, dias até a previsão, status, valor, cliente
    ("São Paulo", "Rio de Janeiro", "TransLog", "Rodoviário", 1, "Em trânsito", 4200, "Mercantil Aurora"),
    ("Santos", "Manaus", "Mar Norte", "Marítimo", 11, "Em trânsito", 18500, "Indústrias Pampa"),
    ("Curitiba", "Porto Alegre", "TransLog", "Rodoviário", -6, "Entregue", 3100, "Farmácias Vitta"),
    ("São Paulo", "Recife", "AeroCargo", "Aéreo", -5, "Entregue", 12400, "Tech Nordeste"),
    ("Belo Horizonte", "Salvador", "RodoSul", "Rodoviário", -4, "Atrasado", 5600, "Mercantil Aurora"),
    ("Santos", "Buenos Aires", "Mar Norte", "Marítimo", 5, "Pendente", 14900, "Distribuidora Platina"),
    ("Campinas", "Curitiba", "TransLog", "Rodoviário", 2, "Em trânsito", 2700, "Farmácias Vitta"),
    ("São Paulo", "Brasília", "AeroCargo", "Aéreo", -4, "Atrasado", 9800, "Tech Nordeste"),
    ("Uberlândia", "Santos", "FerroBR", "Ferroviário", 3, "Em trânsito", 6300, "Agro Cerrado"),
    ("Porto Alegre", "São Paulo", "RodoSul", "Rodoviário", 0, "Pendente", 5200, "Distribuidora Platina"),
]


class Command(BaseCommand):
    help = "Cria dados de exemplo (só se estoque e fretes estiverem vazios)."

    def handle(self, *args, **options):
        if Produto.objects.exists() or Frete.objects.exists():
            self.stdout.write("Já existem dados; nada foi criado.")
            return
        hoje = timezone.localdate()
        for nome, sku, un, minimo, movs in PRODUTOS:
            p = Produto.objects.create(nome=nome, sku=sku, unidade=un, estoque_minimo=minimo, quantidade=0)
            for i, (tipo, qtd) in enumerate(movs):
                Movimentacao.objects.create(produto=p, tipo=tipo, quantidade=qtd, observacao="Exemplo",
                                            data=hoje - timedelta(days=len(movs) - i))
                p.quantidade += qtd if tipo == "E" else -qtd
            p.save()
        ent = {n: Entregador.objects.create(nome=n, telefone=t, veiculo=v) for n, (t, v) in ENTREGADORES.items()}
        for o, d, e, m, dias, st, valor, cli in FRETES:
            Frete.objects.create(origem=o, destino=d, entregador=ent[e], modal=m, status=st, valor=valor,
                                 cliente=cli, previsao=hoje + timedelta(days=dias))
        self.stdout.write(self.style.SUCCESS("Dados de exemplo criados."))
