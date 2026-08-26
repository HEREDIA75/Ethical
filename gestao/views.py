from decimal import Decimal
from django.db import connection
from django.shortcuts import render
from rest_framework import serializers, status
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import (
    ProdutoServico,
    ProjetoEstudantil,
    ResumoProjetoView,
    SimulacaoViabilidade,
)

# ==========================================
# SERIALIZERS (Validação dos dados)
# ==========================================


class PrecificacaoSerializer(serializers.Serializer):
    projeto_id = serializers.IntegerField(required=False, allow_null=True)
    nome_produto = serializers.CharField(
        max_length=100, required=False, allow_blank=True, default="Produto Exemplo"
    )
    custo_variavel = serializers.DecimalField(
        max_digits=10, decimal_places=2, min_value=Decimal("0.00")
    )
    custo_fixo_rateado = serializers.DecimalField(
        max_digits=10,
        decimal_places=2,
        min_value=Decimal("0.00"),
        default=Decimal("0.00"),
    )
    impostos_pct = serializers.DecimalField(
        max_digits=5, decimal_places=2, min_value=Decimal("0.00")
    )
    margem_lucro_pct = serializers.DecimalField(
        max_digits=5, decimal_places=2, min_value=Decimal("0.00")
    )

    def validate(self, data):
        if data["impostos_pct"] + data["margem_lucro_pct"] >= Decimal("100"):
            raise serializers.ValidationError(
                {
                    "non_field_errors": [
                        "A soma de impostos e margem de lucro deve ser menor que 100%."
                    ]
                }
            )
        return data


class ViabilidadeSerializer(serializers.Serializer):
    projeto_id = serializers.IntegerField(required=False, allow_null=True)
    investimento_inicial = serializers.DecimalField(
        max_digits=12, decimal_places=2, min_value=Decimal("0.00")
    )
    custos_fixos_mensais = serializers.DecimalField(
        max_digits=12, decimal_places=2, min_value=Decimal("0.00")
    )
    lucro_liquido_unitario = serializers.DecimalField(
        max_digits=10, decimal_places=2, min_value=Decimal("0.00")
    )
    vendas_estimadas_mes = serializers.IntegerField(min_value=0)


# ==========================================
# VIEWS (API & Persistência)
# ==========================================


class PrecificarAPIView(APIView):
    def post(self, request):
        serializer = PrecificacaoSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        d = serializer.validated_data
        custo_var = d["custo_variavel"]
        custo_fixo = d["custo_fixo_rateado"]
        impostos_pct = d["impostos_pct"]
        margem_pct = d["margem_lucro_pct"]

        # 1. Uso da Function SQL (ou fallback via Python caso o BD esteja limpo)
        preco_venda = None
        try:
            with connection.cursor() as cursor:
                cursor.execute(
                    "SELECT fn_calcular_preco_venda(%s, %s, %s);",
                    [custo_var + custo_fixo, margem_pct, impostos_pct],
                )
                preco_venda = Decimal(str(cursor.fetchone()[0]))
        except Exception:
            denominador = Decimal("1") - ((impostos_pct + margem_pct) / Decimal("100"))
            preco_venda = (custo_var + custo_fixo) / denominador

        margem_contrib = (
            preco_venda - custo_var - (preco_venda * (impostos_pct / Decimal("100")))
        )
        ponto_equilibrio = int(custo_fixo / margem_contrib) if margem_contrib > 0 else 0

        # 2. Persistência no banco (se projeto_id for informado)
        if d.get("projeto_id"):
            projeto = ProjetoEstudantil.objects.filter(id=d["projeto_id"]).first()
            if projeto:
                ProdutoServico.objects.create(
                    projeto=projeto,
                    nome=d.get("nome_produto", "Sem Nome"),
                    custo_variavel_unitario=custo_var,
                    margem_lucro_desejada=margem_pct,
                    aliquota_imposto=impostos_pct,
                )

        return Response(
            {
                "nome_produto": d.get("nome_produto", ""),
                "preco_venda_sugerido": round(float(preco_venda), 2),
                "margem_contribuição_reais": round(float(margem_contrib), 2),
                "ponto_equilibrio_unidades": ponto_equilibrio,
            },
            status=status.HTTP_200_OK,
        )


class ViabilidadeAPIView(APIView):
    def post(self, request):
        serializer = ViabilidadeSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        d = serializer.validated_data
        investimento = d["investimento_inicial"]
        custos_fixos = d["custos_fixos_mensais"]
        lucro_unitario = d["lucro_liquido_unitario"]
        vendas_mes = d["vendas_estimadas_mes"]

        lucro_bruto_vendas = lucro_unitario * vendas_mes
        lucro_mensal_estimado = lucro_bruto_vendas - custos_fixos

        ponto_equilibrio = (
            int(custos_fixos / lucro_unitario) if lucro_unitario > 0 else 0
        )
        payback = (
            float(investimento / lucro_mensal_estimado)
            if lucro_mensal_estimado > 0
            else None
        )
        viavel = lucro_mensal_estimado > 0

        # Persistência no banco (se projeto_id for informado)
        if d.get("projeto_id"):
            projeto = ProjetoEstudantil.objects.filter(id=d["projeto_id"]).first()
            if projeto:
                SimulacaoViabilidade.objects.create(
                    projeto=projeto,
                    projecao_vendas_mensal=vendas_mes,
                    preco_venda_calculado=lucro_unitario,
                    ponto_equilibrio_unidades=ponto_equilibrio,
                    payback_meses=Decimal(str(round(payback, 2))) if payback else None,
                )

        return Response(
            {
                "lucro_mensal_estimado": round(float(lucro_mensal_estimado), 2),
                "ponto_equilibrio_unidades": ponto_equilibrio,
                "payback_meses": round(payback, 2) if payback is not None else None,
                "viavel": viavel,
            },
            status=status.HTTP_200_OK,
        )


# ==========================================
# PAINEL & CONSULTAS AVANÇADAS (JOIN, BETWEEN, VIEW)
# ==========================================


def painel_view(request):
    # Consulta 1: JOIN (Navegação ORM entre tabelas Produto e Projeto)
    produtos_com_projeto = ProdutoServico.objects.select_related("projeto").all()[:10]

    # Consulta 2: BETWEEN (Filtrando investimento entre R$ 1.000 e R$ 50.000)
    projetos_faixa_investimento = ProjetoEstudantil.objects.filter(
        investimento_inicial__range=(1000.00, 50000.00)
    )

    # Consulta 3: VIEW SQL Mapeada (vw_resumo_projetos)
    resumo_projetos_view = ResumoProjetoView.objects.all()

    return render(
        request,
        "gestao/painel.html",
        {
            "produtos": produtos_com_projeto,
            "projetos_faixa": projetos_faixa_investimento,
            "resumo_views": resumo_projetos_view,
        },
    )
