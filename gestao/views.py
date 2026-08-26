from decimal import Decimal
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import ProjetoEstudantil, ProdutoServico, SimulacaoViabilidade

from django.shortcuts import render


class PrecificarAPIView(APIView):
    def post(self, request):
        d = request.data
        try:
            custo_var = Decimal(str(d["custo_variavel"]))
            custo_fixo = Decimal(
                str(
                    d[
                        (
                            "custo_fixo_rateadonumber"
                            if "custo_fixo_rateadonumber" in d
                            else "custo_fixo_rateado"
                        )
                    ]
                )
            )
            impostos_pct = Decimal(str(d["impostos_pct"]))
            margem_pct = Decimal(str(d["margem_lucro_pct"]))

            denominador = Decimal("1") - ((impostos_pct + margem_pct) / Decimal("100"))
            if denominador <= 0:
                return Response(
                    {"error": "Soma de impostos e margem deve ser menor que 100%"},
                    status=400,
                )

            preco_venda = (custo_var + custo_fixo) / denominador
            margem_contrib = (
                preco_venda
                - custo_var
                - (preco_venda * (impostos_pct / Decimal("100")))
            )
            ponto_equilibrio = (
                int(custo_fixo / margem_contrib) if margem_contrib > 0 else 0
            )

            return Response(
                {
                    "nome_produto": d.get("nome_produto", ""),
                    "preco_venda_sugerido": round(float(preco_venda), 2),
                    "margem_contribuição_reais": round(float(margem_contrib), 2),
                    "ponto_equilibrio_unidades": ponto_equilibrio,
                }
            )
        except (KeyError, ValueError, ZeroDivisionError) as e:
            return Response({"error": str(e)}, status=400)


class ViabilidadeAPIView(APIView):
    def post(self, request):
        d = request.data
        try:
            investimento = Decimal(str(d["investimento_inicial"]))
            custos_fixos = Decimal(str(d["custos_fixos_mensais"]))
            lucro_unitario = Decimal(str(d["lucro_liquido_unitario"]))
            vendas_mes = int(d["vendas_estimadas_mes"])

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

            return Response(
                {
                    "lucro_mensal_estimado": round(float(lucro_mensal_estimado), 2),
                    "ponto_equilibrio_unidades": ponto_equilibrio,
                    "payback_meses": round(payback, 2) if payback else None,
                    "viavel": viavel,
                }
            )
        except (KeyError, ValueError) as e:
            return Response({"error": str(e)}, status=400)


def painel_view(request):
    return render(request, "gestao/painel.html")
