import os
import re
from collections import defaultdict


os.system('cls' if os.name == 'nt' else 'clear')

# ======= CONFIGURE AQUI =======
PASTA = r"\\C:"  # pasta onde estão os .LST
BITOLAS_VALIDAS = {5, 6.3, 8, 10, 12.5, 16, 20, 25, 32, 40, 50}  # bitolas que você quer considerar
# ==============================

# Regex para linhas do RESUMO DE AÇO: ACO  BIT  COMPR  PESO
LINHA_RESUMO = re.compile(
    r'^\s*(50A|60A)\s+(\d+(?:[.,]\d+)?)\s+(\d+(?:[.,]\d+)?)\s+(\d+(?:[.,]\d+)?)\s*$'
)

def parse_num(s: str) -> float | None:
    """Converte texto numérico: aceita ponto ou vírgula; remove separador de milhar."""
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

def processar_lst(caminho_arquivo: str):
    """Lê um .LST e retorna somas por bitola e por AÇO (50A/60A)."""
    # Tenta encodings comuns do Windows
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

# ====== Varre a pasta e acumula ======
total_geral_bitola = defaultdict(float)
total_geral_aco = defaultdict(float)

arquivos = [f for f in os.listdir(PASTA) if f.lower().endswith(".lst")]
if not arquivos:
    print("Nenhum arquivo .LST encontrado na pasta. Verifique PASTA.")
else:
    for nome in arquivos:
        caminho = os.path.join(PASTA, nome)
        soma_folha_bitola, soma_folha_aco = processar_lst(caminho)

        print(f"\n {nome}")
        if not soma_folha_bitola:
            print("  (nenhuma linha válida no RESUMO DE AÇO)")
        else:
            for bit in sorted(soma_folha_bitola):
                print(f"  Bitola {bit:g} mm: {soma_folha_bitola[bit]:.2f} kgf")

        # acumula nos totais gerais
        for bit, v in soma_folha_bitola.items():
            total_geral_bitola[bit] += v
        for aco, v in soma_folha_aco.items():
            total_geral_aco[aco] += v

    # Totais finais
    print("\n TOTAL GERAL (todas as folhas) — por bitola:")
    for bit in sorted(total_geral_bitola):
        print(f"  Bitola {bit:g} mm: {total_geral_bitola[bit]:.2f} kgf")

    print("\n Totais por AÇO (opcional):")
    for aco in ("50A", "60A"):
        if aco in total_geral_aco:
            print(f"  {aco}: {total_geral_aco[aco]:.2f} kgf")
