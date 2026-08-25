from pydantic import BaseModel


class PrecificacaoInput(BaseModel):
    projeto_id: int
    nome_produto: str
    custo_variavel: float
    custo_fixo_rateado: float
    impostos_pct: float
    margem_lucro_pct: float


class PrecificacaoOutput(BaseModel):
    nome_produto: str
    preco_venda_sugerido: float
    margem_contribuição_reais: float
    ponto_equilibrio_unidades: int


class ViabilidadeInput(BaseModel):
    investimento_inicial: float
    custos_fixos_mensais: float
    lucro_liquido_unitario: float
    vendas_estimadas_mes: int


class ViabilidadeOutput(BaseModel):
    lucro_mensal_estimado: float
    ponto_equilibrio_unidades: int
    payback_meses: float
    viavel: bool
