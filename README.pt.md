# Microsoft Fabric & OneLake — Recuperação de Capacidade e Reestruturação do Lakehouse

> **Estudo de caso** · Central de compras pública da saúde (Portugal) · Microsoft Fabric, OneLake, Lakehouse, Dataflows Gen2, Pipelines, Notebooks PySpark, T-SQL, Power BI, Gateways on-premises e VNet
>
> 🇬🇧 [English version](README.md)

Uma capacidade Fabric de produção chegava a **365% de utilização**, com throttling nas atualizações e lentidão em todos os dashboards usados para acompanhar as compras públicas de vários hospitais. Diagnostiquei as causas raiz, reestruturei a camada OneLake/Lakehouse, redesenhei a estratégia de ingestão e refresh, e avaliei a arquitetura de gateway/rede necessária para migrar a ingestão de Dataflows para Notebooks Spark.

*Nomes do cliente, servidores, IPs, contas e connection strings foram anonimizados. O código deste repositório é uma versão genérica e higienizada do que correu em produção.*

---

## Resumo

| | |
|---|---|
| **Problema** | Throttling da capacidade (picos de 365%), refreshes a falhar, relatórios lentos, gateway físico frágil |
| **Papel** | Engenheira Fabric/BI — diagnóstico, arquitetura, implementação, ligação com o TI |
| **Stack** | Lakehouse Fabric (Delta), OneLake, Dataflows Gen2, Data Pipelines, PySpark, T-SQL (SQL analytics endpoint), modelos semânticos Power BI, On-prem Data Gateway, VNet Data Gateway (avaliação) |
| **Fontes** | API REST interna (backoffice/catálogo), SharePoint (Excel + Listas), tabelas de referência nativas do OneLake |
| **Consumo** | Dashboards Power BI com segurança ao nível da linha (RLS) por hospital/entidade |

## O que fiz

1. **Diagnóstico da capacidade** com a app *Fabric Capacity Metrics* — identifiquei os itens que mais consumiam CUs e cinco causas raiz:
   - modelo semântico em **DirectQuery**, a consultar o Lakehouse a cada interação
   - **views SQL não materializadas**, recalculadas a cada leitura
   - um único dataflow a misturar extração e transformação de todas as fontes e anos
   - **tabelas Delta sem manutenção** (sem `OPTIMIZE` / `VACUUM`) → fragmentação
   - modelo sem star schema (relações N:N)
2. **Ingestão separada por frequência** — um dataflow dividido em *ano corrente* (diário), *previsões* e *histórico*, para que anos antigos deixem de ser reingeridos todos os dias.
3. **Materialização das views** — notebook PySpark que lê cada view de negócio e grava como tabela Delta física (`vw_X → tb_X`); modelos semânticos reapontados para as tabelas `tb_`.
4. **Manutenção Delta** — notebook agendado com `OPTIMIZE` + `VACUUM`.
5. **DirectQuery → Import** nos modelos semânticos, com refresh agendado de acordo com a necessidade real.
6. **Orquestração num único Pipeline** (dataflows → manutenção → materialização → refresh dos modelos).
7. **Gateway e rede** — operação do gateway on-premises, gestão de um incidente de queda de energia de ponta a ponta, e desenho do VNet Data Gateway (VNet + subnet delegada + RBAC + NSG) para uma futura ingestão por notebooks — com a recomendação de **adiar** essa etapa depois de confirmar que o desenho alvo não a exigia nesta fase.
8. **Roadmap em 3 fases** documentado para a equipa do cliente (vitórias rápidas → estrutural → star schema).

Detalhes técnicos em [`docs/`](docs/), código em [`notebooks/`](notebooks/) e [`sql/`](sql/), gateway em [`gateway/`](gateway/).

## Serviços

- **Health check de capacidade** Fabric e redução de CUs/throttling
- **Desenho de OneLake / Lakehouse** — camadas medallion, manutenção Delta, convenções e estrutura de workspaces
- Migração de **Dataflows Gen2 para Pipelines + Notebooks**
- Configuração e troubleshooting de **gateways** (on-premises e VNet)
- Otimização de **modelos semânticos** Power BI (Import / Direct Lake, RLS, star schema)

📫 **Contacto:** _adicione o seu email / LinkedIn aqui_
