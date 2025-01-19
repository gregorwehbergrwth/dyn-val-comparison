import re
from collections import Counter


def get_text(name):
    with open(name, 'r', encoding='utf-8') as file:
        return file.read()


def filter_numbers(text):
    numbers = re.findall(r'\d+,\d+\n|\d+\n|-\d+,\d+\n|-\d+\n', text)
    return [float(number.replace(',', '.')) for number in numbers]


def clear_dynexite_text(text):
    lines = text.split('\n')
    start_index = [i for i, line in enumerate(lines) if "Punkte" in line and i > 10][0]
    end_index = [i for i, line in enumerate(lines) if "wurden gespeichert." in line][0]
    lines = lines[start_index:end_index+1]
    text = '\n'.join(lines)
    patterns = [r'\d+ Punkte', r'\d+ Punkt', r'\d+ NKS', r'HEB \d+', r'HEA \d+']  # Subject-specific sequences need to be added manually
    return re.sub('|'.join(patterns), '', text)

def filter_moodle_text(text):
    lines = text.split('\n')
    try:
        start_index = [i for i, line in enumerate(lines) if "Aufgabe" in line and i > 5][0]
    except IndexError:
        start_index = [i for i, line in enumerate(lines) if "Antwort:" in line and i > 5][0]
    end_index = [i for i, line in enumerate(lines) if "Direkt zu:" in line][0]

    lines = lines[start_index:end_index+1]
    # print(*lines, sep='\n')
    pattern = r'Antwort:Frage \d+'

    moodle_numbers = []
    for i, line in enumerate(lines):
        if re.match(pattern, line):
            try:
                moodle_numbers.append(float(lines[i+1].replace(',', '.')))
            except ValueError:
                input(f"Error in line {i+1}: {lines[i+1]}")
    return moodle_numbers


def get_leftovers(dynexite_numbers, excel_numbers):
    return list((Counter(excel_numbers) - Counter(dynexite_numbers)).elements())



def get_wrong_numbers(dynexite_numbers, excel_numbers):
    dynexite_counter = Counter(dynexite_numbers)
    excel_counter = Counter(excel_numbers)
    wrong_numbers_counter = dynexite_counter - excel_counter
    return list(wrong_numbers_counter.elements())

def get_very_close_numbers(wrong_numbers, leftovers, tolerance=0.2):
    very_close_numbers = []
    if leftovers:
        for number in wrong_numbers:
            closest = min(leftovers, key=lambda x: abs(x-number))
            if abs(closest - number) <= tolerance:
                very_close_numbers.append(number)
    return very_close_numbers

def filter_yes_no(text):
    yes = list(map(lambda x: x.replace("\n", ""), re.findall(r'Ja\n', text)))
    no = list(map(lambda x: x.replace("\n", ""), re.findall(r'Nein\n', text)))
    return yes, no

def yes_no_check(dynexite, excel):
    if len(dynexite[0]) > 0 or len(excel[0]) > 0 or len(dynexite[1]) > 0 or len(excel[1]) > 0:
        if dynexite == excel:
            print(f"Ja/Nein stimmen genau überein")
        else:
            print(f"Ja/Nein stimmen nicht überein. Dynexite: {len(dynexite[0])} Ja, {len(dynexite[1])} Nein. Excel: {len(excel[0])} Ja, {len(excel[1])} Nein")
            print(dynexite, "\t"*5, excel)

if __name__ == '__main__':
    tolerance = 0.2

    # if input("Do you want to check Dynexite? (y/n) ") == 'y':
    # if True:
    if True:
        dynexite_text = get_text("Dynexite_Text.txt")
        excel_text = get_text("Excel_Text.txt")

        dynexite_numbers = filter_numbers(clear_dynexite_text(dynexite_text))
        excel_numbers = filter_numbers(excel_text)
        # yes, no = filter_yes_no(dynexite_text)
        # yes, no = filter_yes_no(excel_text)

        leftovers = get_leftovers(dynexite_numbers, excel_numbers)
        wrong_numbers = get_wrong_numbers(dynexite_numbers, excel_numbers)
        very_close_numbers = get_very_close_numbers(wrong_numbers, leftovers, tolerance)
        yes_no_check(filter_yes_no(dynexite_text), filter_yes_no(excel_text))
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
