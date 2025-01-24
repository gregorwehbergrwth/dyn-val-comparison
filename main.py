import re
from collections import Counter


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
    patterns = [r'\d+ Punkte', r'\d+ Punkt', r'\d+ NKS', r'HEB \d+', r'HEA \d+']  # Subject-specific sequences need to be added manually
    return re.sub('|'.join(patterns), '', text_section)


def get_leftovers(dyn, xl):
    return list((Counter(xl) - Counter(dyn)).elements())


def get_wrong(dyn, xl):
    return list((Counter(dyn) - Counter(xl)).elements())


def near_matches(wrong, leftovers, tolerance=0.2):
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
    if dyn == xl:
        print(f"Ja/Nein stimmen genau überein")
    else:
        print(f"Ja/Nein stimmen nicht überein. Dynexite: {len(dyn[0])} Ja, {len(dyn[1])} Nein. Excel: {len(xl[0])} Ja, {len(xl[1])} Nein")
        print(dyn, "\t" * 5, xl)


if __name__ == '__main__':

    dynexite_text = read_file("Dynexite.txt")
    excel_text = read_file("Excel.txt")

    dynexite_numbers = extract_numbers(clean_dynexite_text(dynexite_text))
    excel_numbers = extract_numbers(excel_text)

    leftover_numbers = get_leftovers(dynexite_numbers, excel_numbers)
    wrong_numbers = get_wrong(dynexite_numbers, excel_numbers)
    near_matches = near_matches(wrong_numbers, leftover_numbers, tolerance=0.2)

    compare_yes_no(filter_yes_no(dynexite_text), filter_yes_no(excel_text))

    if dynexite_numbers == excel_numbers:
        print("All numbers match exactly and are in order.")
    elif len(dynexite_numbers) != len(excel_numbers):
        print(f"Mismatch in count: Dynexite ({len(dynexite_numbers)}) vs Excel ({len(excel_numbers)})")
    elif wrong_numbers:
        for num in wrong_numbers:
            closest_match = min(leftover_numbers, key=lambda x: abs(x - num), default=None)
            print(f"Extra number {num} found. Closest match in Excel: {closest_match}.")
        if len(near_matches) == len(wrong_numbers):
            print("All extra numbers are very close to missing ones.")
    else:
        print("Numbers match but are out of order:")
        print(f"Dynexite: {dynexite_numbers}")
        print(f"Excel:    {excel_numbers}")
