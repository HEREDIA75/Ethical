from django.contrib import admin
from .models import ProjetoEstudantil, ProdutoServico, SimulacaoViabilidade


@admin.register(ProjetoEstudantil)
class ProjetoEstudantilAdmin(admin.ModelAdmin):
    list_display = (
        "titulo",
        "aluno_responsavel",
        "turma",
        "investimento_inicial",
        "criado_em",
    )
    search_fields = ("titulo", "aluno_responsavel", "turma")


@admin.register(ProdutoServico)
class ProdutoServicoAdmin(admin.ModelAdmin):
    list_display = (
        "nome",
        "projeto",
        "custo_variavel_unitario",
        "margem_lucro_desejada",
        "aliquota_imposto",
    )
    list_filter = ("projeto",)


@admin.register(SimulacaoViabilidade)
class SimulacaoViabilidadeAdmin(admin.ModelAdmin):
    list_display = (
        "projeto",
        "projecao_vendas_mensal",
        "preco_venda_calculado",
        "payback_meses",
    )
