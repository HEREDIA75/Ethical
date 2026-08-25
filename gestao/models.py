from django.db import models


class ProjetoEstudantil(models.Model):
    titulo = models.CharField(max_length=150)
    aluno_responsavel = models.CharField(max_length=100)
    turma = models.CharField(max_length=50)
    investimento_inicial = models.DecimalField(max_digits=12, decimal_places=2)
    custo_fixo_mensal = models.DecimalField(max_digits=12, decimal_places=2)
    criado_em = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.titulo} - {self.aluno_responsavel}"


class ProdutoServico(models.Model):
    projeto = models.ForeignKey(
        ProjetoEstudantil, on_delete=models.CASCADE, related_name="produtos"
    )
    nome = models.CharField(max_length=100)
    custo_variavel_unitario = models.DecimalField(max_digits=10, decimal_places=2)
    margem_lucro_desejada = models.DecimalField(max_digits=5, decimal_places=2)  # em %
    aliquota_imposto = models.DecimalField(max_digits=5, decimal_places=2)  # em %

    def __str__(self):
        return self.nome


class SimulacaoViabilidade(models.Model):
    projeto = models.ForeignKey(ProjetoEstudantil, on_delete=models.CASCADE)
    projecao_vendas_mensal = models.IntegerField()
    preco_venda_calculado = models.DecimalField(max_digits=10, decimal_places=2)
    ponto_equilibrio_unidades = models.IntegerField(null=True, blank=True)
    payback_meses = models.DecimalField(
        max_digits=5, decimal_places=2, null=True, blank=True
    )
    criado_em = models.DateTimeField(auto_now_add=True)
