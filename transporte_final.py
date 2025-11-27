import pulp
import csv
import os

# ==============================================================================
# FUNÇÕES DE UTILIDADE E ENTRADA
# ==============================================================================

def ler_float(msg):
    """Lê um número decimal do usuário com tratamento de erro."""
    while True:
        v = input(msg).strip()
        try:
            return float(v)
        except ValueError:
            print(" Valor inválido. Digite um número (ex: 10 ou 10.5).")

def ler_int(msg, minimo, maximo):
    """Lê um número inteiro dentro de um intervalo."""
    while True:
        v = input(msg).strip()
        if v.isdigit():
            v = int(v)
            if minimo <= v <= maximo:
                return v
        print(f" Opção inválida. Escolha entre {minimo} e {maximo}.")

def configurar_modelo_manual():
    """Permite ao usuário digitar todos os dados manualmente."""
    ORIGENS = ["Fabrica_A", "Fabrica_B", "Fabrica_C"]
    DESTINOS = ["CD_1", "CD_2", "CD_3", "CD_4"]

    print("\n=== CONFIGURAÇÃO DO MODELO DE TRANSPORTE ===")

    oferta = {}
    print("\n--- Informe a OFERTA (Capacidade) ---")
    for i in ORIGENS:
        oferta[i] = ler_float(f"Oferta da {i}: ")

    demanda = {}
    print("\n--- Informe a DEMANDA (Necessidade) ---")
    for j in DESTINOS:
        demanda[j] = ler_float(f"Demanda do {j}: ")

    custos = {}
    print("\n--- Informe os CUSTOS DE TRANSPORTE unitários ---")
    for i in ORIGENS:
        custos[i] = {}
        print(f"Origem: {i}")
        for j in DESTINOS:
            custos[i][j] = ler_float(f"   Custo p/ {j}: ")

    return ORIGENS, DESTINOS, oferta, demanda, custos

# ==============================================================================
# MOTOR DE OTIMIZAÇÃO (PuLP)
# ==============================================================================

def resolver_modelo(ORIGENS, DESTINOS, oferta, demanda, custos):
    """Cria e resolve o modelo de transporte."""
    
    # Validar viabilidade básica (apenas aviso)
    total_oferta = sum(oferta.values())
    total_demanda = sum(demanda.values())
    
    if total_oferta < total_demanda:
        print(f"\n  AVISO CRÍTICO: Oferta Total ({total_oferta}) < Demanda Total ({total_demanda}).")
        print("   O modelo provavelmente será INVIÁVEL (Infeasible).")

    # 1. Criar o Problema
    modelo = pulp.LpProblem("Problema_de_Transporte", pulp.LpMinimize)

    # 2. Criar Variáveis de Decisão (x_ij >= 0)
    # Lista de tuplas (origem, destino) para índices
    rotas = [(i, j) for i in ORIGENS for j in DESTINOS]
    x = pulp.LpVariable.dicts("Rota", rotas, lowBound=0, cat=pulp.LpContinuous)

    # 3. Função Objetivo: Minimizar Custo Total
    modelo += pulp.lpSum(x[(i, j)] * custos[i][j] for i in ORIGENS for j in DESTINOS)

    # 4. Restrições de Oferta (O que sai da fábrica <= Capacidade)
    for i in ORIGENS:
        modelo += pulp.lpSum(x[(i, j)] for j in DESTINOS) <= oferta[i], f"Oferta_{i}"

    # 5. Restrições de Demanda (O que chega no destino >= Necessidade)
    for j in DESTINOS:
        modelo += pulp.lpSum(x[(i, j)] for i in ORIGENS) >= demanda[j], f"Demanda_{j}"

    # 6. Resolver (sem imprimir log do solver no terminal para ficar limpo)
    modelo.solve(pulp.PULP_CBC_CMD(msg=False))
    
    return modelo, x

# ==============================================================================
# EXIBIÇÃO E EXPORTAÇÃO
# ==============================================================================

def mostrar_resumo(nome_cenario, modelo, x, ORIGENS, DESTINOS, custos):
    """Exibe os resultados no terminal."""
    print(f"\n{'='*50}")
    print(f"RESULTADOS: {nome_cenario.upper()}")
    print(f"{'='*50}")
    
    status = pulp.LpStatus[modelo.status]
    print(f"Status da Solução: {status}")

    if status != "Optimal":
        print(" Não foi possível encontrar uma solução ótima.")
        return None

    custo_total = pulp.value(modelo.objective)
    print(f"💰 Custo Total Mínimo: R$ {custo_total:,.2f}")

    print("\n Detalhe das Rotas Utilizadas:")
    print(f"{'Origem':<12} -> {'Destino':<10} {'Qtd':<10} {'Custo Unit.':<12} {'Subtotal':<10}")
    print("-" * 60)
    
    dados_exportacao = [] # Lista para salvar no CSV depois

    for i in ORIGENS:
        for j in DESTINOS:
            qtd = x[(i, j)].varValue
            if qtd > 0.001: # Filtrar apenas rotas usadas (maior que zero)
                custo_unit = custos[i][j]
                subtotal = qtd * custo_unit
                print(f"{i:<12} -> {j:<10} {qtd:<10.0f} R$ {custo_unit:<10.2f} R$ {subtotal:,.2f}")
                
                # Salvar dados para o CSV
                dados_exportacao.append([nome_cenario, i, j, qtd, custo_unit, subtotal])
    
    return dados_exportacao

def exportar_csv(todos_resultados):
    """Gera o arquivo CSV exigido no trabalho."""
    if not todos_resultados:
        return

    arquivo = "relatorio_transporte.csv"
    print(f"\n Salvando arquivo '{arquivo}' (Requisito do Trabalho)...")
    
    # Cabeçalho do CSV
    header = ["Cenario", "Origem", "Destino", "Quantidade", "Custo_Unitario", "Custo_Total"]
    
    try:
        with open(arquivo, mode='w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f, delimiter=';') # Ponto e vírgula é melhor para Excel no Brasil
            writer.writerow(header)
            for linha in todos_resultados:
                writer.writerow(linha)
        print(" Arquivo salvo com sucesso!")
    except Exception as e:
        print(f" Erro ao salvar CSV: {e}")

# ==============================================================================
# ANÁLISE DE SENSIBILIDADE
# ==============================================================================

def menu_sensibilidade(ORIGENS, DESTINOS):
    print("\n--- Análise de Sensibilidade ---")
    print("Qual parâmetro você deseja alterar para criar um novo cenário?")
    print("1 - Custo de Transporte")
    print("2 - Oferta de uma Fábrica")
    print("3 - Demanda de um CD")
    print("0 - Finalizar e Sair")
    return ler_int("Opção: ", 0, 3)

def aplicar_alteracao(opcao, oferta, demanda, custos, ORIGENS, DESTINOS):
    # Copiar dados para não alterar o original
    nova_oferta = oferta.copy()
    nova_demanda = demanda.copy()
    novos_custos = {i: custos[i].copy() for i in ORIGENS}
    desc_alteracao = ""

    if opcao == 1: # Custo
        print("\nAlterar Custo:")
        for idx, o in enumerate(ORIGENS): print(f"{idx+1}. {o}")
        oi = ler_int("Escolha a Origem (Nº): ", 1, len(ORIGENS)) - 1
        
        for idx, d in enumerate(DESTINOS): print(f"{idx+1}. {d}")
        di = ler_int("Escolha o Destino (Nº): ", 1, len(DESTINOS)) - 1
        
        origem, destino = ORIGENS[oi], DESTINOS[di]
        valor_atual = custos[origem][destino]
        novo_valor = ler_float(f"Custo atual {origem}->{destino} é {valor_atual}. Novo valor: ")
        
        novos_custos[origem][destino] = novo_valor
        desc_alteracao = f"Custo {origem}->{destino} de {valor_atual} para {novo_valor}"

    elif opcao == 2: # Oferta
        print("\nAlterar Oferta:")
        for idx, o in enumerate(ORIGENS): print(f"{idx+1}. {o}")
        oi = ler_int("Escolha a Origem (Nº): ", 1, len(ORIGENS)) - 1
        
        origem = ORIGENS[oi]
        valor_atual = oferta[origem]
        novo_valor = ler_float(f"Oferta atual de {origem} é {valor_atual}. Nova oferta: ")
        
        nova_oferta[origem] = novo_valor
        desc_alteracao = f"Oferta {origem} de {valor_atual} para {novo_valor}"

    elif opcao == 3: # Demanda
        print("\nAlterar Demanda:")
        for idx, d in enumerate(DESTINOS): print(f"{idx+1}. {d}")
        di = ler_int("Escolha o Destino (Nº): ", 1, len(DESTINOS)) - 1
        
        destino = DESTINOS[di]
        valor_atual = demanda[destino]
        novo_valor = ler_float(f"Demanda atual de {destino} é {valor_atual}. Nova demanda: ")
        
        nova_demanda[destino] = novo_valor
        desc_alteracao = f"Demanda {destino} de {valor_atual} para {novo_valor}"

    return nova_oferta, nova_demanda, novos_custos, desc_alteracao

# ==============================================================================
# MAIN
# ==============================================================================

def main():
    print("=== TRABALHO FINAL PO: PROBLEMA DE TRANSPORTE ===")
    
    # Chama direto a configuração manual
    ORIGENS, DESTINOS, oferta, demanda, custos = configurar_modelo_manual()

    # Lista para acumular resultados para o CSV
    resultados_csv = []

    # 1. Resolver Cenário Base
    modelo_base, x_base = resolver_modelo(ORIGENS, DESTINOS, oferta, demanda, custos)
    res_base = mostrar_resumo("Cenario_Base", modelo_base, x_base, ORIGENS, DESTINOS, custos)
    
    if res_base:
        resultados_csv.extend(res_base)

    # 2. Loop de Análise de Sensibilidade
    while True:
        opcao = menu_sensibilidade(ORIGENS, DESTINOS)
        if opcao == 0:
            break
        
        oferta_nova, demanda_nova, custos_novos, desc = aplicar_alteracao(opcao, oferta, demanda, custos, ORIGENS, DESTINOS)
        
        print(f"\n Recalculando para: {desc}...")
        modelo_alt, x_alt = resolver_modelo(ORIGENS, DESTINOS, oferta_nova, demanda_nova, custos_novos)
        
        nome_cenario = f"Alterado_{opcao}"
        res_alt = mostrar_resumo(nome_cenario, modelo_alt, x_alt, ORIGENS, DESTINOS, custos_novos)
        
        if res_alt:
            resultados_csv.extend(res_alt)
            
            # Comparação Rápida de Custo
            custo_base = pulp.value(modelo_base.objective)
            custo_novo = pulp.value(modelo_alt.objective)
            diferenca = custo_novo - custo_base
            print(f"\n Comparação de Custos: Base ({custo_base:,.2f}) vs Novo ({custo_novo:,.2f})")
            print(f"   Diferença: R$ {diferenca:,.2f}")

    # 3. Finalizar e Salvar
    exportar_csv(resultados_csv)
    print("\nPrograma finalizado com sucesso.")

if __name__ == "__main__":
    main()