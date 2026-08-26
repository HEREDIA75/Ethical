from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("gestao", "0001_initial"),  # Substitua pelo nome da sua primeira migração
    ]

    operations = [
        # 1. VIEW SQL (Relatório resumido com JOIN de projetos e produtos)
        migrations.RunSQL(
            sql="""
            CREATE VIEW vw_resumo_projetos AS
            SELECT 
                p.id AS projeto_id,
                p.titulo,
                p.aluno_responsavel,
                p.investimento_inicial,
                COUNT(prod.id) AS total_produtos
            FROM gestao_projetoestudantil p
            LEFT JOIN gestao_produtoservico prod ON p.id = prod.projeto_id
            GROUP BY p.id, p.titulo, p.aluno_responsavel, p.investimento_inicial;
            """,
            reverse_sql="DROP VIEW IF EXISTS vw_resumo_projetos;",
        ),
        # 2. FUNCTION SQL (Cálculo de Preço Sugerido direto no Banco)
        migrations.RunSQL(
            sql="""
            CREATE FUNCTION fn_calcular_preco_venda(custo NUMERIC, margem NUMERIC, imposto NUMERIC)
            RETURNS NUMERIC AS $$
            DECLARE
                denominador NUMERIC;
            BEGIN
                denominador := 1.0 - ((margem + imposto) / 100.0);
                IF denominador <= 0 THEN
                    RETURN 0;
                END IF;
                RETURN ROUND(custo / denominador, 2);
            END;
            $$ LANGUAGE plpgsql;
            """,
            reverse_sql="DROP FUNCTION IF EXISTS fn_calcular_preco_venda(NUMERIC, NUMERIC, NUMERIC);",
        ),
        # 3. TRIGGER SQL (Atualiza data na alteração de um Produto)
        migrations.RunSQL(
            sql="""
            CREATE OR REPLACE FUNCTION trg_atualizar_produto_timestamp()
            RETURNS TRIGGER AS $$
            BEGIN
                NEW.ultima_atualizacao = NOW();
                RETURN NEW;
            END;
            $$ LANGUAGE plpgsql;

            CREATE TRIGGER check_update_produto_timestamp
            BEFORE UPDATE ON gestao_produtoservico
            FOR EACH ROW
            EXECUTE FUNCTION trg_atualizar_produto_timestamp();
            """,
            reverse_sql="""
            DROP TRIGGER IF EXISTS check_update_produto_timestamp ON gestao_produtoservico;
            DROP FUNCTION IF EXISTS trg_atualizar_produto_timestamp();
            """,
        ),
    ]
