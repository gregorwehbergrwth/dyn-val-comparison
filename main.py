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
    text_section = '\n'.join(lines[start_index:end_index + 1])
    patterns = [r'\d+ Punkte', r'\d+ Punkt', r'\d+ NKS', r'HEB \d+', r'HEA \d+'] # Subject-specific sequences need to be added manually
    return re.sub('|'.join(patterns), '', text_section)

def leftovers(dynexite_numbers, excel_numbers):
    return list((Counter(excel_numbers) - Counter(dynexite_numbers)).elements())


def wrong(dynexite_list, excel_list):
    return list((Counter(dynexite_list) - Counter(excel_list)).elements())


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

def compare_yes_no(dynexite, excel):
    if dynexite == excel:
        print(f"Ja/Nein stimmen genau überein")
    else:
        print(f"Ja/Nein stimmen nicht überein. Dynexite: {len(dynexite[0])} Ja, {len(dynexite[1])} Nein. Excel: {len(excel[0])} Ja, {len(excel[1])} Nein")
        print(dynexite, "\t"*5, excel)

if __name__ == '__main__':
    tolerance = 0.2

    dynexite_text = read_file("Dynexite.txt")
    excel_text = read_file("Excel.txt")

    dynexite_numbers = extract_numbers(clean_dynexite_text(dynexite_text))
    excel_numbers = extract_numbers(excel_text)

    leftovers = leftovers(dynexite_numbers, excel_numbers)
    wrong_numbers = wrong(dynexite_numbers, excel_numbers)
    very_close_numbers = near_matches(wrong_numbers, leftovers, tolerance)

    compare_yes_no(filter_yes_no(dynexite_text), filter_yes_no(excel_text))

    if dynexite_numbers == excel_numbers:
        print("All numbers are correct and in the same order.")
    elif len(dynexite_numbers) != len(excel_numbers):
        print(f"Something went wrong. The number of Dynexite numbers {len(dynexite_numbers)} is not equal to the number of Excel numbers {len(excel_numbers)}")
        print(f"Dynexite numbers: {dynexite_numbers}")
        print(f"Excel Numbers   : {excel_numbers}")
    elif len(wrong_numbers) != len(leftovers):
        print(f"Something went wrong. The number of wrong numbers {len(wrong_numbers)} is not equal to the number of leftovers {len(leftovers)}")
    elif wrong_numbers:
        for number in wrong_numbers:
            print(f"\tNumber {number} is not in Excel. {min(leftovers, key=lambda x: abs(x-number))} is the closest match. Other options: {', '.join(map(str, leftovers))}")
        if len(very_close_numbers) == len(wrong_numbers):
            print("All numbers are very close.")
    else:
        print("All numbers are correct, but not in the same order:")
        print(f"Dynexite: {dynexite_numbers}")
        print(f"Excel:    {excel_numbers}")
