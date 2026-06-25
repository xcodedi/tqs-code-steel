import os
import re

os.system('cls' if os.name == 'nt' else 'clear')

def verificar_ordem_numerica(pasta):
    arquivos = os.listdir(pasta)
    
    # Filtrar apenas arquivos com extensões desejadas
    extensoes = ('.lst', '.pdf', '.dxf')
    arquivos_filtrados = [arq for arq in arquivos if arq.lower().endswith(extensoes)]

    numeros = []
    for nome in arquivos_filtrados:
        # Captura o primeiro número encontrado no nome do arquivo
        match = re.search(r'\b(\d+)\b', nome)
        if match:
            numeros.append(int(match.group()))

    if not numeros:
        print("Nenhum número foi encontrado nos nomes dos arquivos.")
        return

    numeros.sort()
    print("Números encontrados:", numeros)

    # Sequência obrigatoriamente começa em 1
    inicio = 1
    fim = numeros[-1]
    esperado = list(range(inicio, fim + 1))

    faltando = [num for num in esperado if num not in numeros]

    if faltando:
        print(f"Números faltando na sequência: {faltando}")
    else:
        print("Todos os números estão presentes, começando em 1 e sem falhas.")

# Caminho da pasta para renomear 
verificar_ordem_numerica(r"\\Mebranco\arquivo morto\arquivo morto\projetos\2024\1124 - Padre Canova 2621\plantas\ferros-lst")
