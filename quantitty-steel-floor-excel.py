import os
import re
from collections import defaultdict
from openpyxl import load_workbook

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
    r'(?i)\d{3}[-_](FUN|PIL|TER|TÉR|HAL|G1_|ELE|COB|TEL|MAQ|CAI|CIN|PAT|ESP|SUB1|GAR|GAR2|LAZ|RAM|SUB2|G2_|TIP1|SAL|TIP5|TIP69|TIP1015|TIP1619|TIP2025|TIP2627|DUP|DUPS|MOT|CAL|PAT2|TIP)[-_](LAJ|VIG|ESC|FOR|OUT|FUN|PIL)[-_]\d{3}'
)

# Dicionários de tradução
MAPA_PAVIMENTO = {
    "FUN": "Fundação",
    "PIL": "Pilares",
    "TER": "Térreo",
    "TÉR": "Térreo",
    "HAL": "Hall",
    "GAR1": "G1",
    "ELE": "Elevado-G1",
    "COB": "Cobertura",
    "TEL": "Telhado",
    "MAQ": "Casa de Máquinas",
    "CAI": "Caixa d’Água",
    "CIN": "Cinta",
    "PAT": "Patamar",
    "PAT2": "PATAMAR-SUPERIOR",
    "ESP": "Espaço Técnico",
    "SUB1": "Subsolo-1",
    "SUB2": "Subsolo-2",
    "GAR": "Garagem-1",
    "GAR2": "Garagem-2",
    "LAZ": "Lazer",
    "RAM": "Rampa",
    "GAR2": "G2",
    "TIP1": "Tipo-1",
    "SAL": "Salão-festas",
    "TIP5": "PAV 5",
    "TIP69": "Tipo-6-9",
    "TIP1015": "Tipo-10-15",
    "TIP7A14": "Tipo-7-14",
    "TIP15A23": "Tipo-15-23",
    "TIP1619": "Tipo-16-19",
    "TIP2025": "Tipo-20-25",
    "TIP2627": "Tipo-26-27",
    "DUP": "Duplex-inferior",
    "DUPS": "Duplex-superior",
    "G1_": "GAR1",
    "G2_": "GAR2",
    "TIP": "TIPO",
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
        print(f" Nome do arquivo fora do padrão: {nome}")
        continue

    pav_raw, elem_raw = m.groups()

    # Verifica se o código existe no mapa
    pavimento = MAPA_PAVIMENTO.get(pav_raw.upper())
    elemento = MAPA_ELEMENTO.get(elem_raw.upper())

    if not pavimento:
        print(f" Pavimento '{pav_raw}' não mapeado (arquivo: {nome})")
        pavimento = pav_raw
    if not elemento:
        print(f" Elemento '{elem_raw}' não mapeado (arquivo: {nome})")
        elemento = elem_raw

    for bit, peso in soma_folha_bitola.items():
        dados[pavimento][elemento][bit] += peso


# ====== EXIBE RESULTADOS ======
print("\n TOTAL DE AÇO POR PAVIMENTO, ELEMENTO E BITOLA:\n")

total_geral = 0

for pav, elementos in dados.items():
    print(f" {pav.upper()}:")
    total_pav = 0
    for elem, bitolas in elementos.items():
        total_elem = sum(bitolas.values())
        total_pav += total_elem
        print(f"  - {elem}: total {total_elem:.2f} kgf")
        for bit in sorted(bitolas):
            print(f"      Bitola {bit:g} mm: {bitolas[bit]:.2f} kgf")
        print()
    total_geral += total_pav
    print(f"  Total do pavimento {pav}: {total_pav:.2f} kgf\n")

print(f"\n TOTAL GERAL DE AÇO: {total_geral:.2f} kgf\n")

from openpyxl import Workbook

# ====== EXPORTA PARA EXCEL ======
from openpyxl import load_workbook

# =====================================================
# LINHAS DOS PAVIMENTOS
# =====================================================

LINHAS_PAVIMENTOS = {
    "Cinta": 7,
    "MOTOR": 8,
    "Cobertura": 9,
    "Duplex-superior": 10,
    "Patamar-Superior": 11,
    "Duplex-inferior": 12,
    "Tipo-26-27": 13,
    "Tipo-20-25": 14,
    "Tipo-16-19": 15,
    "Tipo-10-15": 16,
    "Tipo-6-9": 17,
    "PAV 5": 18,
    "Lazer": 19,
    "Patamar": 20,
    "Térreo": 21,
    "Calçada": 22,
    "Subsolo-1": 23,
    "Rampa": 24,
    "Subsolo-2": 25,
    "Pilares": 26,
    "Fundação": 27,
    "GAR1": 40,
    "GAR2": 41,
    "Tipo-1": 42,
    "TIPO": 43,
    "Salão-festas": 44,
    "Telhado": 45,
    "Caixa d’Água": 46
}

# =====================================================
# COLUNAS DA PLANILHA
# =====================================================

COLUNAS = {

    "Vigas": {
        5: "C",
        6.3: "D",
        8: "E",
        10: "F",
        12.5: "G",
        16: "H",
        20: "I",
    },

    "Lajes": {
        5: "J",
        6.3: "K",
        8: "L",
        10: "M",
        12.5: "N",
        16: "O",
        20: "P",
    },

    "Escadas": {
        5: "J",
        6.3: "K",
        8: "L",
        10: "M",
        12.5: "N",
        16: "O",
        20: "P",
    },

    "Pilares": {
        5: "R",
        6.3: "S",
        8: "T",
        10: "U",
        12.5: "V",
        16: "W",
        20: "X",
        25: "Y",
    },

    "Blocos": {
        5: "R",
        6.3: "S",
        8: "T",
        10: "U",
        12.5: "V",
        16: "W",
        20: "X",
        25: "Y",
    }
}

# =====================================================
# PLANILHA MODELO
# =====================================================
MODELO = r"\\C:"

wb = load_workbook(MODELO)
ws = wb.active

# =====================================================
# PREENCHE A PLANILHA
# =====================================================

for pav, elementos in dados.items():

    linha = LINHAS_PAVIMENTOS.get(pav)

    if linha is None:
        print(f" Pavimento sem linha definida: {pav}")
        continue

    for elem, bitolas in elementos.items():

        mapa_colunas = COLUNAS.get(elem)

        if mapa_colunas is None:
            print(f" Elemento sem coluna definida: {elem}")
            continue

        for bit, peso in bitolas.items():

            coluna = mapa_colunas.get(bit)

            if coluna is None:
                print(
                    f" Sem coluna para "
                    f"{pav} / {elem} / {bit} mm"
                )
                continue

            celula = f"{coluna}{linha}"

            valor_atual = ws[celula].value

            if valor_atual is None:
                valor_atual = 0

            ws[celula] = round(float(valor_atual) + peso, 2)

# =====================================================
# TOTAL GERAL
# =====================================================
ws["Z1"] = round(total_geral, 2)

# =====================================================
# SALVA
# =====================================================
saida = r"\\C:"

wb.save(saida)

print(f"\n Planilha gerada com sucesso:")
print(saida)