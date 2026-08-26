from django.core.management.base import BaseCommand
from gestao.models import ProjetoEstudantil, ProdutoServico, SimulacaoViabilidade
from decimal import Decimal


class Command(BaseCommand):
    help = "Povoa o banco de dados com projetos e simulações fictícias"

    def handle(self, *args, **kwargs):
        SimulacaoViabilidade.objects.all().delete()
        ProdutoServico.objects.all().delete()
        ProjetoEstudantil.objects.all().delete()

        # Criar Projetos
        p1 = ProjetoEstudantil.objects.create(
            titulo="Ecobag Biodegradável",
            aluno_responsavel="Maria Silva",
            turma="ADM3A",
            investimento_inicial=Decimal("5000.00"),
            custo_fixo_mensal=Decimal("800.00"),
        )

        p2 = ProjetoEstudantil.objects.create(
            titulo="Aplicativo Delivery Local",
            aluno_responsavel="João Santos",
            turma="INFO2B",
            investimento_inicial=Decimal("12000.00"),
            custo_fixo_mensal=Decimal("1500.00"),
        )

        # Criar Produtos
        ProdutoServico.objects.create(
            projeto=p1,
            nome="Ecobag Padrão",
            custo_variavel_unitario=Decimal("8.50"),
            margem_lucro_desejada=Decimal("30.00"),
            aliquota_imposto=Decimal("10.00"),
        )

        ProdutoServico.objects.create(
            projeto=p2,
            nome="Assinatura Mensal B2B",
            custo_variavel_unitario=Decimal("15.00"),
            margem_lucro_desejada=Decimal("40.00"),
            aliquota_imposto=Decimal("12.00"),
        )

        # Criar Simulações
        SimulacaoViabilidade.objects.create(
            projeto=p1,
            projecao_vendas_mensal=150,
            preco_venda_calculado=Decimal("14.17"),
            ponto_equilibrio_unidades=141,
            payback_meses=Decimal("11.50"),
        )

        self.stdout.write(self.style.SUCCESS("Banco de dados populado com sucesso!"))
