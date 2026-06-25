import os
import re
from collections import defaultdict


os.system('cls' if os.name == 'nt' else 'clear')

# ======= CONFIGURE AQUI =======
PASTA = r"c:\caminho\da\pasta"  # pasta onde estão os .LST
BITOLAS_VALIDAS = {5, 6.3, 8, 10, 12.5, 16, 20, 25, 32, 40, 50}  # bitolas que você quer considerar
# ==============================

# Regex para linhas do RESUMO DE AÇO: ACO  BIT  COMPR  PESO
LINHA_RESUMO = re.compile(
    r'^\s*(50A|60A)\s+(\d+(?:[.,]\d+)?)\s+(\d+(?:[.,]\d+)?)\s+(\d+(?:[.,]\d+)?)\s*$'
)

#Converte texto numérico: aceita ponto ou vírgula; remove separador de milhar
def parse_num(s: str) -> float | None:

    t = s.strip()
    if "," in t and "." in t:
        # Formato tipo 1.685,00 -> 1685.00
        t = t.replace(".", "").replace(",", ".")
    else:
        t = t.replace(",", ".")
    try:
        return float(t)
    except ValueError:
        return None

 #Lê um .LST e retorna somas por bitola e por AÇO (50A/60A)
 # Tenta encodings comuns do Windows
def numero_folha(nome):
    m = re.match(r'^(\d+)', nome)  # pega o número do início do arquivo

    if m:
        return int(m.group(1))

    return 999999

def processar_lst(caminho_arquivo: str):
 
    for enc in ("cp1252", "latin-1", "utf-8"):
        try:
            linhas = open(caminho_arquivo, "r", encoding=enc, errors="ignore").read().splitlines()
            break
        except Exception:
            linhas = None
    soma_por_bitola = defaultdict(float)
    soma_por_aco = defaultdict(float)

    for linha in linhas:
        # Pula linhas de resumo geral para não contar duas vezes
        if "peso total" in linha.lower():
            continue

        m = LINHA_RESUMO.match(linha)
        if not m:
            continue

        aco, bit_s, compr_s, peso_s = m.groups()
        bit = parse_num(bit_s)
        peso = parse_num(peso_s) 

        # Filtra só as bitolas que você listou
        if bit is None or peso is None or bit not in BITOLAS_VALIDAS:
            continue

        # Soma por bitola (independente do aço)
        soma_por_bitola[bit] += peso
        # Soma por AÇO (se quiser conferir)
        soma_por_aco[aco] += peso

    return soma_por_bitola, soma_por_aco

# AGRUPA POR PAVIMENTO

PADRAO_PAVIMENTO = re.compile(
    r'(?i)\d{3}[-_](FUN|PIL|TER|TÉR|HAL|G1_|ELE|COB|TEL|MAQ|CAI|CIN|PAT|ESP|SUB1|GAR|GAR2|LAZ|RAM|SUB2|G2_|TIP1|SAL|TIP5|TIP69|TIP1015|TIP1619|TIP2025|TIP2627|DUP|DUPS|MOT|CAL|PAT2|TIP)'
)

MAPA_PAVIMENTO = {
    "FUN": "Fundação",
    "PIL": "Pilares",
    "SUB2": "Subsolo-2",
    "SUB1": "Subsolo-1",
    "RAM": "Rampa",
    "CAL": "Calçada",
    "TER": "Térreo",
    "TÉR": "Térreo",
    "HAL": "Hall",
    "GAR": "Garagem-1",
    "GAR1": "G1",
    "G1_": "GAR1",
    "GAR2": "Garagem-2",
    "G2_": "GAR2",
    "ELE": "Elevado-G1",
    "LAZ": "Lazer",
    "TIP1": "Tipo-1",
    "TIP5": "PAV 5",
    "TIP69": "Tipo-6-9",
    "TIP1015": "Tipo-10-15",
    "TIP1619": "Tipo-16-19",
    "TIP2025": "Tipo-20-25",
    "TIP2627": "Tipo-26-27",
    "TIP": "TIPO",
    "DUP": "Duplex-inferior",
    "PAT": "Patamar",
    "PAT2": "PATAMAR-SUPERIOR",
    "DUPS": "Duplex-superior",
    "SAL": "Salão-festas",
    "ESP": "Espaço Técnico",
    "COB": "Cobertura",
    "TEL": "Telhado",
    "MAQ": "Casa de Máquinas",
    "MOT": "MOTOR",
    "CAI": "Caixa",
    "CIN": "Cinta",
}

arquivos = [f for f in os.listdir(PASTA) if f.lower().endswith(".lst")]

arquivos_por_pavimento = defaultdict(list)

for nome in arquivos:

    m = PADRAO_PAVIMENTO.search(nome)

    if m:
        codigo = m.group(1).upper()
        pavimento = MAPA_PAVIMENTO.get(codigo, codigo)
    else:
        pavimento = "SEM_PAVIMENTO"

    arquivos_por_pavimento[pavimento].append(nome)

# PROCESSAMENTO 

total_geral_bitola = defaultdict(float)
total_geral_aco = defaultdict(float)
total_geral = 0

for pavimento in sorted(arquivos_por_pavimento):

    print("\n" + "=" * 80)
    print(f"PAVIMENTO: {pavimento}")
    print("=" * 80)

    total_pavimento = 0
    total_pavimento_bitola = defaultdict(float)

    for nome in sorted(
    arquivos_por_pavimento[pavimento],
    key=numero_folha):

        caminho = os.path.join(PASTA, nome)

        soma_folha_bitola, soma_folha_aco = processar_lst(caminho)

        total_folha = sum(soma_folha_bitola.values())
        total_pavimento += total_folha

        print(f"\n{nome}")

        if not soma_folha_bitola:
            print("  (nenhuma linha válida no RESUMO DE AÇO)")
        else:
            for bit in sorted(soma_folha_bitola):
                print(
                    f"  Bitola {bit:g} mm: "
                    f"{soma_folha_bitola[bit]:.2f} kgf"
                )

            print(f"  TOTAL DA FOLHA: {total_folha:.2f} kgf")

        for bit, valor in soma_folha_bitola.items():
            total_pavimento_bitola[bit] += valor
            total_geral_bitola[bit] += valor

        for aco, valor in soma_folha_aco.items():
            total_geral_aco[aco] += valor

    print("\nTOTAL POR BITOLA DO PAVIMENTO:")

    for bit in sorted(total_pavimento_bitola):
        print(
            f"  Bitola {bit:g} mm: "
            f"{total_pavimento_bitola[bit]:.2f} kgf"
        )

    print(
        f"\n>>> TOTAL DO PAVIMENTO "
        f"{pavimento}: {total_pavimento:.2f} kgf"
    )

    total_geral += total_pavimento

# TOTAIS GERAIS

print("\n" + "=" * 80)
print(f"TOTAL GERAL DE AÇO: {total_geral:.2f} kgf")
print("=" * 80)

print("\nTOTAL GERAL POR BITOLA:")

for bit in sorted(total_geral_bitola):
    print(
        f"  Bitola {bit:g} mm: "
        f"{total_geral_bitola[bit]:.2f} kgf"
    )

print("\nTOTAL POR AÇO:")

for aco in ("50A", "60A"):
    if aco in total_geral_aco:
        print(f"  {aco}: {total_geral_aco[aco]:.2f} kgf")