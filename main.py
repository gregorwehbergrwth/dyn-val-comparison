import re
from collections import Counter
from excel_integration import save_numbers_to_file, numbers_from_excel
from clipboard import clipboard_loop


def read_file(name):
    with open(name, 'r', encoding='utf-8') as file:
        return file.read()


def extract_numbers(text):
    patterns = re.findall(r'\d+,\d+\n|\d+\n|-\d+,\d+\n|-\d+\n', text)
    return [float(num.replace(',', '.')) for num in patterns]


def clean_dynexite_text(text):
    lines = text.split('\n')
    start_index = next(i for i, line in enumerate(lines) if "Punkte" in line and i > 10)
    end_index = next(i for i, line in enumerate(lines) if "wurden gespeichert." in line)
    text_section = '\n'.join(lines[start_index:end_index])
    text_section +="\n"
    patterns = [r'\d+ Punkte', r'\d+ Punkt', r'\d+ NKS', r'HEB \d+', r'HEA \d+', r'D\d+-D\d+', r'Platte D\d+', r'XC\d+', r'D\d+']  # Subject-specific sequences need to be added manually
    return re.sub('|'.join(patterns), '', text_section)


def get_leftovers(dyn, xl):
    return list((Counter(xl) - Counter(dyn)).elements())


def get_wrong(dyn, xl):
    return list((Counter(dyn) - Counter(xl)).elements())


def near_matches(wrong, leftovers, tolerance=0.4):
    close_matches = []
    if leftovers:
        for num in wrong:
            closest_match = min(leftovers, key=lambda x: abs(x - num), default=None)
            if closest_match and abs(closest_match - num) <= tolerance:
                close_matches.append(num)
        return close_matches


def filter_yes_no(text):
    yes = list(map(lambda x: x.replace("\n", ""), re.findall(r'Ja\n', text)))
    no = list(map(lambda x: x.replace("\n", ""), re.findall(r'Nein\n', text)))
    return yes, no


def compare_yes_no(dyn, xl):
    if dyn == xl and dyn != 0:
        print(f"Ja/Nein stimmen genau überein")
    elif dyn == xl and dyn == 0:
        print("Keine Ja/Nein")
    else:
        print(f"Ja/Nein stimmen nicht überein. Dynexite: {len(dyn[0])} Ja, {len(dyn[1])} Nein. Excel: {len(xl[0])} Ja, {len(xl[1])} Nein")
        print(dyn, "\t" * 5, xl)


if __name__ == '__main__':
    # excel_filepath = r"C:\Users\grego\Downloads\Massivbau 2 HÜ 2, aktualisiertSS21.xlsx"  # Todo
    # position = 'D18:D129'  # Todo
    # excel_filepath = r"C:\Users\grego\Downloads\MB_II_Hausübung_2.xlsx"
    # position = 'D8:D117'
    excel_filepath = r"C:\Users\grego\Downloads\HÜ_01_Excel.xlsx"
    position = 'B13:B40'

    numbers = numbers_from_excel(excel_filepath, position)
    save_numbers_to_file('excel.txt', numbers)
    tolerance = 0.2

    dynexite_text = read_file("Dynexite.txt")
    excel_text = read_file("Excel.txt")

    dynexite_numbers = extract_numbers(clean_dynexite_text(dynexite_text))
    excel_numbers = extract_numbers(excel_text)

    leftover_numbers = get_leftovers(dynexite_numbers, excel_numbers)
    wrong_numbers = get_wrong(dynexite_numbers, excel_numbers)
    near_matches = near_matches(wrong_numbers, leftover_numbers, tolerance=tolerance)

    compare_yes_no(filter_yes_no(dynexite_text), filter_yes_no(excel_text))

    close_matches = []

    if dynexite_numbers == excel_numbers:
        print("All numbers match exactly and are in order.")
    elif len(dynexite_numbers) != len(excel_numbers):
        print(f"Mismatch in count: Dynexite ({len(dynexite_numbers)}) vs Excel ({len(excel_numbers)})")
        print(f"Dynexite: {dynexite_numbers}")
        print(f"Excel:    {excel_numbers}")


    elif wrong_numbers:
        for num in wrong_numbers:
            closest_match = min(leftover_numbers, key=lambda x: abs(x - num), default=None)
            close_matches.append([num, closest_match, abs(closest_match - num)])
        for num in close_matches:
            print(f'Number: {num[0]}, Closest Match: {num[1]}, Difference: {round(num[2], 2)}')
        if all(diff <= tolerance for _, _, diff in close_matches):
            print(f"All extra numbers are very close to missing ones within the tolerance of {tolerance}.")
        else:
            med_diff = sum([diff for _, _, diff in close_matches])/len(close_matches)
            print(f"Not all extra numbers are close to missing ones (Medium difference: {med_diff}.")  # todo hier weitermachen
    else:
        print("Numbers match but are out of order:")
        print(f"Dynexite: {dynexite_numbers}")
        print(f"Excel:    {excel_numbers}")

    print(f"Dynexite: {dynexite_numbers}")
    print(f"Excel:    {excel_numbers}")

# if input("Do you want to start the clipboard loop? (y/n)") == "y":
#     clipboard_loop("excel.txt")
