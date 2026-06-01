import os
import re

os.system('cls' if os.name == 'nt' else 'clear')

# Caminho da pasta com os arquivos
pasta = r"\\C:"

# Percorre todos os arquivos na pasta
for nome_arquivo in os.listdir(pasta):
    caminho_antigo = os.path.join(pasta, nome_arquivo)

    # Ignora se não for arquivo
    if not os.path.isfile(caminho_antigo):
        continue

    # Pega os 3 primeiros caracteres numéricos
    primeiros_tres = nome_arquivo[:3]

    # Procura outro número de 3 dígitos mais adiante no nome
    match = re.search(r'(\d{3})', nome_arquivo[3:])
    if match:
        numero_novo = match.group(1)

        # Se for diferente, renomeia
        if primeiros_tres != numero_novo:
            novo_nome = numero_novo + nome_arquivo[3:]
            caminho_novo = os.path.join(pasta, novo_nome)

            os.rename(caminho_antigo, caminho_novo)
            print(f"Renomeado: {nome_arquivo} → {novo_nome}")
