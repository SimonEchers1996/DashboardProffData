"""
Nedenstående information fundet ud fra kundeomsætningen og v.h.a.
Proff. Dette er baseret på alle købende kunder fra data givet.
"""

NACE_2025_kunder = [
    '10 Fremstilling af fødevarer',
    '16 Fremstilling af træ og varer af træ og kork, undtagen møbler; fremstilling af varer af strå og flettematerialer',
    '17 Fremstilling af papir og papirvarer',
    '18 Trykning og reproduktion af indspillede medier',
    '20 Fremstilling af kemiske produkter',
    '21 Fremstilling af farmaceutiske råvarer og farmaceutiske præparater',
    '22 Fremstilling af gummi- og plastprodukter',
    '23 Fremstilling af andre ikke-metalholdige mineralske produkter',
    '24 Fremstilling af basismetaller',
    '25 Fremstilling af færdige metalprodukter, undtagen maskiner og udstyr',
    '26 Fremstilling af computere, elektroniske og optiske produkter',
    '27 Fremstilling af elektrisk udstyr',
    '28 Fremstilling af maskiner og udstyr i.a.n.',
    '29 Fremstilling af motorkøretøjer, påhængsvogne og sættevogne',
    '30 Fremstilling af andre transportmidler',
    '32 Andre fremstillingsaktiviteter',
    '33 Reparation, vedligeholdelse og installation af maskiner og udstyr'
]

def handle_string(strings):
    return " ".join(strings).lstrip()

def convert_to_NACE(string):
    to_return, times = "", len(string)//2
    for _ in range(times-1):
        to_return += string[0:2]+"."
        string = string[2:]
    to_return += string[0:2]
    return to_return

NACE_dictionary = {convert_to_NACE(string.split()[0]):handle_string(string.split()[1:]) for string in NACE_2025_kunder}