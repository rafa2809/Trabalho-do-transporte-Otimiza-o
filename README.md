Problema de Transporte — Implementação em Python (PuLP)

Este repositório contém a implementação computacional do Problema de Transporte, desenvolvido como trabalho final da disciplina Pesquisa Operacional.
O projeto utiliza Programação Linear contínua e o solver PuLP/CBC para encontrar o plano de transporte de menor custo possível, incluindo análise de sensibilidade e exportação de resultados para CSV.

 1. Introdução

O Problema de Transporte determina a quantidade ótima de produtos enviada de várias origens para múltiplos destinos, minimizando o custo total e respeitando:

Limites de oferta das fábricas

Demandas mínimas dos centros de distribuição

Não negatividade das variáveis

Este trabalho modela o envio de produtos de três fábricas (A, B e C) para quatro CDs (CD1–CD4), utilizando Programação Linear contínua.

 2. Descrição do Problema

Fábricas:

A

B

C

Centros de Distribuição (CDs):

CD1

CD2

CD3

CD4

Tabela de custos, oferta e demanda
Fábrica	CD1	CD2	CD3	CD4	Oferta
A	4	5	2	8	100
B	3	6	4	7	80
C	5	3	5	9	120

Demanda: 50 • 70 • 110 • 60

 3. Formulação Matemática
Variável de decisão

𝑋
𝑖
𝑗
X
ij
	​

 = quantidade transportada da fábrica i para o CD j

Função objetivo

Minimizar:

Z = 4X11 + 5X12 + 2X13 + 8X14
  + 3X21 + 6X22 + 4X23 + 7X24
  + 5X31 + 3X32 + 5X33 + 9X34

Restrições

Oferta:

X11 + X12 + X13 + X14 ≤ 100
X21 + X22 + X23 + X24 ≤ 80
X31 + X32 + X33 + X34 ≤ 120


Demanda:

X11 + X21 + X31 ≥ 50
X12 + X22 + X32 ≥ 70
X13 + X23 + X33 ≥ 110
X14 + X24 + X34 ≥ 60


Não negatividade:

Xij ≥ 0

 4. Implementação — Python + PuLP

O código deste repositório possui:

Entrada manual de dados (oferta, demanda e custos)

Montagem automática do modelo no PuLP

Geração do cenário base

Análise de sensibilidade alterando:

custos

oferta

demanda

Comparação entre cenários

Exportação para CSV (relatorio_transporte.csv)

 5. Resultados

A execução exibe:

Status: solução ótima

Custo total mínimo

Rotas utilizadas

Subtotais por rota

Exemplo (simplificado):

Status da Solução: Optimal
Custo Total Mínimo: R$ 1.090,00

Origem       -> Destino    Qtd   Custo   Subtotal
Fabrica_A    -> CD_3       100     2        200
...

 6. Análise de Sensibilidade

Exemplos:

✔ Cenário 1: Redução do custo A → CD1 de 4 para 1

→ Novo custo total: R$ 1.060,00

 Cenário 2: Aumento da oferta da Fábrica B de 80 para 100

→ Novo custo total: R$ 1.050,00

Esses cenários ajudam a entender como pequenas mudanças afetam o custo total.

 7. Interpretação Gerencial

O modelo permite apoiar decisões logísticas mostrando:

Quais rotas são realmente utilizadas

Qual fábrica é mais eficiente

Onde aumentar oferta reduz custos

Como mudanças de custo refletem na operação

É uma ferramenta importante para minimizar gastos logísticos.

 8. Como Executar
1. Instalar dependência
pip install pulp

2. Rodar o programa
python transporte.py

3. Arquivo gerado automaticamente

relatorio_transporte.csv
Com todas as rotas usadas e custos por cenário.

 9. Conclusão

Este projeto demonstra como a Programação Linear pode ser aplicada para: reduzir custos logísticos

atender demandas de forma ótima

apoiar decisões gerenciais

simular cenários alternativos

O código em Python e o modelo matemático garantem uma solução exata, rápida e confiável.
