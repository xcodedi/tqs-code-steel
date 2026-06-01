import os
import re
from collections import defaultdict

os.system('cls' if os.name == 'nt' else 'clear')

# ======= CONFIGURAÇÕES =======
PASTA = r"\\C:"
BITOLAS_VALIDAS = {5, 6.3, 8, 10, 12.5, 16, 20,22,25,32,40,50}
# =============================

# Regex para ler linhas válidas de aço
LINHA_RESUMO = re.compile(
    r'^\s*(50A|60A)\s+(\d+(?:[.,]\d+)?)\s+(\d+(?:[.,]\d+)?)\s+(\d+(?:[.,]\d+)?)\s*$'
)

# Regex para extrair pavimento e elemento do nome do arquivo
PADRAO_NOME = re.compile(
    r'(?i)\d{3}[-_](FUN|PIL|TER|TÉR|HAL|G1_|ELE|COB|TEL|MAQ|CAI|CIN|PAT|ESP|SUB1|GAR|GAR2|LAZ|RAM|SUB2|G2_|TIP1|SAL|TIP5|TIP69|TIP1015|TIP1619|TIP2025|TIP2627|DUP|DUPS|MOT|CAL|PAT2)[-_](LAJ|VIG|ESC|FOR|OUT|FUN|PIL)[-_]\d{3}'
)

# Dicionários de tradução
MAPA_PAVIMENTO = {
    "FUN": "Fundação",
    "PIL": "Pilares",
    "TER": "Térreo",
    "TÉR": "Térreo",
    "HAL": "Hall",
    "G1_": "G1",
    "ELE": "Elevado-G1",
    "COB": "Cobertura",
    "TEL": "Telhado",
    "MAQ": "Casa de Máquinas",
    "CAI": "Caixa d’Água",
    "CIN": "Cinta",
    "PAT": "Patamar",
    "PAT2": "Patamar-Superior",
    "ESP": "Espaço Técnico",
    "SUB1": "Subsolo-1",
    "SUB2": "Subsolo-2",
    "GAR": "Garagem-1",
    "GAR2": "GAragem-2",
    "LAZ": "Lazer",
    "RAM": "Rampa",
    "G2_": "G2",
    "TIP1": "Tipo-1",
    "SAL": "Salão-festas",
    "TIP5": "Tipo-diferenciado",
    "TIP69": "Tipo-6-9",
    "TIP1015": "Tipo-10-15",
    "TIP1619": "Tipo-16-19",
    "TIP2025": "Tipo-20-25",
    "TIP2627": "Tipo-26-27",
    "DUP": "Duplex-inferior",
    "DUPS": "Duplex-superior",
    "MOT": "MOTOR",
    "CAL": "Calçada"
}

MAPA_ELEMENTO = {
    "LAJ": "Lajes",
    "VIG": "Vigas",
    "ESC": "Escadas",
    "FOR": "Formas",
    "OUT": "Outros Elementos",
    "PIL": "Pilares",
    "FUN": "Blocos"
}

def parse_num(s: str) -> float | None:
    """Converte texto numérico para float, aceita vírgula e ponto."""
    t = s.strip()
    if "," in t and "." in t:
        t = t.replace(".", "").replace(",", ".")
    else:
        t = t.replace(",", ".")
    try:
        return float(t)
    except ValueError:
        return None


def processar_lst(caminho_arquivo: str):
    """Processa um arquivo .LST e retorna a soma dos pesos por bitola."""
    for enc in ("cp1252", "latin-1", "utf-8"):
        try:
            linhas = open(caminho_arquivo, "r", encoding=enc, errors="ignore").read().splitlines()
            break
        except Exception:
            linhas = None

    soma_bitola = defaultdict(float)

    for linha in linhas:
        if "peso total" in linha.lower():
            continue

        m = LINHA_RESUMO.match(linha)
        if not m:
            continue

        _, bit_s, _, peso_s = m.groups()
        bit = parse_num(bit_s)
        peso = parse_num(peso_s)

        if bit is None or peso is None or bit not in BITOLAS_VALIDAS:
            continue

        soma_bitola[bit] += peso

    return soma_bitola


# ====== VARREDURA ======
arquivos = [f for f in os.listdir(PASTA) if f.lower().endswith(".lst")]
if not arquivos:
    print("Nenhum arquivo .LST encontrado na pasta. Verifique PASTA.")
    exit()

# Estrutura: {pavimento: {elemento: {bitola: peso}}}
dados = defaultdict(lambda: defaultdict(lambda: defaultdict(float)))

for nome in arquivos:
    caminho = os.path.join(PASTA, nome)
    soma_folha_bitola = processar_lst(caminho)

    m = PADRAO_NOME.search(nome)
    if not m:
        print(f"Nome do arquivo fora do padrão: {nome}")
        continue

    pav_raw, elem_raw = m.groups()

    # Verifica se o código existe no mapa
    pavimento = MAPA_PAVIMENTO.get(pav_raw.upper())
    elemento = MAPA_ELEMENTO.get(elem_raw.upper())

    if not pavimento:
        print(f"Pavimento '{pav_raw}' não mapeado (arquivo: {nome})")
        pavimento = pav_raw
    if not elemento:
        print(f"Elemento '{elem_raw}' não mapeado (arquivo: {nome})")
        elemento = elem_raw

    for bit, peso in soma_folha_bitola.items():
        dados[pavimento][elemento][bit] += peso


# ====== EXIBE RESULTADOS ======
print("\nTOTAL DE AÇO POR PAVIMENTO, ELEMENTO E BITOLA:\n")

total_geral = 0

for pav, elementos in dados.items():
    print(f"{pav.upper()}:")
    total_pav = 0
    for elem, bitolas in elementos.items():
        total_elem = sum(bitolas.values())
        total_pav += total_elem
        print(f"  - {elem}: total {total_elem:.2f} kgf")
        for bit in sorted(bitolas):
            print(f"      Bitola {bit:g} mm: {bitolas[bit]:.2f} kgf")
        print()
    total_geral += total_pav
    print(f"Total do pavimento {pav}: {total_pav:.2f} kgf\n")

print(f"\n TOTAL GERAL DE AÇO: {total_geral:.2f} kgf\n")