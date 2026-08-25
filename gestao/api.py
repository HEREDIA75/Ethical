from ninja import NinjaAPI
from .schemas import (
    PrecificacaoInput,
    PrecificacaoOutput,
    ViabilidadeInput,
    ViabilidadeOutput,
)
from .models import ProjetoEstudantil, ProdutoServico, SimulacaoViabilidade

api = NinjaAPI(title="API de Gestão & Precificação Técnico")


@api.post("/precificar/", response=PrecificacaoOutput)
def calcular_precificacao(request, payload: PrecificacaoInput):
    soma_percentuais = (payload.impostos_pct + payload.margem_lucro_pct) / 100.0

    if soma_percentuais >= 1:
        raise ValueError(
            "A soma dos impostos e da margem de lucro deve ser menor que 100%."
        )

    custo_total_direto = payload.custo_variavel + payload.custo_fixo_rateado
    preco_venda = custo_total_direto / (1 - soma_percentuais)

    margem_contribucao = (
        preco_venda
        - payload.custo_variavel
        - (preco_venda * (payload.impostos_pct / 100.0))
    )
    ponto_equilibrio = (
        int(payload.custo_fixo_rateado / margem_contribucao)
        if margem_contribucao > 0
        else 0
    )

    # Persiste o cálculo no banco de dados
    try:
        projeto = ProjetoEstudantil.objects.get(id=payload.projeto_id)
        ProdutoServico.objects.create(
            projeto=projeto,
            nome=payload.nome_produto,
            custo_variavel_unitario=payload.custo_variavel,
            margem_lucro_desejada=payload.margem_lucro_pct,
            aliquota_imposto=payload.impostos_pct,
        )
    except ProjetoEstudantil.DoesNotExist:
        pass

    return {
        "nome_produto": payload.nome_produto,
        "preco_venda_sugerido": round(preco_venda, 2),
        "margem_contribuição_reais": round(margem_contribucao, 2),
        "ponto_equilibrio_unidades": ponto_equilibrio,
    }


@api.post("/viabilidade/", response=ViabilidadeOutput)
def calcular_viabilidade(request, payload: ViabilidadeInput):
    lucro_mensal = (
        payload.lucro_liquido_unitario * payload.vendas_estimadas_mes
    ) - payload.custos_fixos_mensais

    if lucro_mensal <= 0:
        return {
            "lucro_mensal_estimado": round(lucro_mensal, 2),
            "ponto_equilibrio_unidades": 0,
            "payback_meses": 0.0,
            "viavel": False,
        }

    payback = payload.investimento_inicial / lucro_mensal
    ponto_equilibrio = int(
        payload.custos_fixos_mensais / payload.lucro_liquido_unitario
    )

    return {
        "lucro_mensal_estimado": round(lucro_mensal, 2),
        "ponto_equilibrio_unidades": ponto_equilibrio,
        "payback_meses": round(payback, 1),
        "viavel": payback <= 24,
    }
