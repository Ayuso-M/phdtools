import os
import pandas as pd
import re
from unidecode import unidecode

excel_path = "doc/BD_FITBIT_FE_MentalFit.xlsx"
codes = pd.read_excel(excel_path)

CENTRO = "Centro"
CODIGO = "CODIGO"
GENERO = "Genero"
FITBIT = "FITBIT"
COLUMNS = [CENTRO, CODIGO, GENERO, FITBIT]

codes = codes[COLUMNS]

CONDICIONES = ["OA", "OC", "STROOP", "PASAT", "PVTB", "MSIT", "PVSAT", "PVT-B", "PVT"]

CENTROS = {
    "ALBALAT": 8,
    "QUERCUS" : 1,
    "PUEBLA" : 2, # "ENRIQUE DÍEZ CANDO"
    "EMÉRITA AUGUSTA" : 3,
    "SAGRADO CORAZÓN MIAJADAS" : 4,
    "SALESIANOS BADAJOZ" : 5,
    "SANTA EULALIA MÉRIDA" : 6,
    "NUESTRA SEÑORA DOLORES GUAREÑA" : 7,
    "ALBALAT" : 8,
}

CENTROS = {unidecode(key): value for key, value in CENTROS.items()}

NEW_CENTROS = {}
for key, value in CENTROS.items:
    NEW_CENTROS[unidecode(key)] = value


def find_in_dict(key, dictionary):
    # 
    matches = [key_ for key_ in dictionary if key in key_ ]


    key = "AUGUSTA"

    matches = []
    for key_ in dictionary:
        if key in key_:
            matches.append(key_)

    if not any(matches):
        return None
    if len(matches) > 1:
        raise Exception("More than one match found")
    
    return matches[0]


def _starts_with_condition(file_name):    
    conditions = []
    for each in CONDICIONES:
        if file_name.startswith(each):
            conditions.append(each)
    return conditions


def check_beginning_is_correct(file_name):
    conditions = _starts_with_condition(file_name)
    if len(conditions) != 1:
        raise f"File does not have a valid condition: {conditions}"

def get_condition(file_name):
    conditions = _starts_with_condition(file_name)
    return conditions[0]


def get_centre_id(root):
    centre = root.split("/")[-2]
    if centre.startswith("M1") or centre.startswith("M2"):
        centre = centre[2:]

    centre = unidecode(centre.strip())
    key = find_in_dict(centre, CENTROS)
    if key is None:
        raise Exception(f"No key found for: {centre}")

    return CENTROS[key]

def get_user_id(file_name, condition):
    file_short = file_[len(condition):]

    # Check separator
    if file_short[0] not in ["_", " "]:
        raise Exception("Separator format invalid")

    # Remove separator
    file_short = file_short[1:]

    # check if there is 3 or 4 letters in the user id
    if file_short[3] in "0,1,2,3,4,5,6,7,8,9".split(","):
        # the name has 3 letters
        name = file_short[:3]
    else:
        # the name has four letters
        name = file_short[:4]
    
    # Filter codes by name
    code_ = codes[codes["CODIGO"].str.startswith(name)]
    if code_.shape[0] > 1:
        print(f"There are more than one user with that begining {name}")

    # Obtaining the center name
    centre_id = get_centre_id(root)

    # Filter by centre
    codigo = code_[code_[CENTRO] == centre_id]

    if len(codigo) != 1:
        raise Exception(f"Error filtering user for code {codigo}.\n{code_.head()}")

    year = re.match(r".*(2\d+)", codigo)
    if not year:
        year = "2024"

    gender = codigo[GENERO]
    fitbit = codigo[FITBIT]

    return codigo, year, gender, fitbit

root_path = "/Volumes/MENTALFIT/MENTALFIT/ESTUDIO 2/3.BD_Análisis/CASCO EEG MENTALFIT TODO"
# root_path = "/Users/german.ayuso/Desktop/Desktop/Mentalfit"

for root, subFolder, files in os.walk(root_path):
    if not files:
        # We are reading a directory, hence continue
        continue

    for file in files:

        if ".DS_Store" in file:
            continue

        # Obtain MX directoy
        MX = root.replace(root_path+"/", "").split("/")[0]

        # Skip the file if not in "M1" directory
        if MX != "M1":
            continue

        file_path = os.path.join(root, file)

        # Analysing M1 only
        print(f"\nAnalysing file: {file_path}")

        # Work with the name in capital letters
        file_ = file.upper().strip()
        
        # Store the new file name parts
        new_name = {}

        check_beginning_is_correct(file_)
        condition = get_condition(file_)
        new_name['condition'] = condition

        codigo, year, gender, fitbit = get_user_id(file_, condition)
        print(codigo, year, gender, fitbit)

        formato = "{directory}_{condition}_{user}_{centro}_{gender}"
        # formato.format(**new_name)