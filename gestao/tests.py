from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient


class FinancialAPITestCase(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_calcular_precificacao(self):
        payload = {
            "projeto_id": 1,
            "nome_produto": "Salgado Gourmet",
            "custo_variavel": 2.50,
            "custo_fixo_rateado": 1.00,
            "impostos_pct": 10.0,
            "margem_lucro_pct": 20.0,
        }
        response = self.client.post("/api/precificar/", payload, format="json")
        self.assertEqual(response.status_code, 200)
        self.assertIn("preco_venda_sugerido", response.data)
        self.assertGreater(response.data["preco_venda_sugerido"], 3.50)

    def test_calcular_viabilidade(self):
        payload = {
            "investimento_inicial": 1000.00,
            "custos_fixos_mensais": 200.00,
            "lucro_liquido_unitario": 5.00,
            "vendas_estimadas_mes": 100,
        }
        response = self.client.post("/api/viabilidade/", payload, format="json")
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.data["viavel"])
        self.assertEqual(response.data["lucro_mensal_estimado"], 300.00)
