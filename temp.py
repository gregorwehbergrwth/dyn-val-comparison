import re
from collections import Counter


def read_file(file_name):
    with open(file_name, 'r', encoding='utf-8') as file:
        return file.read()


def extract_numbers(text):
    number_patterns = re.findall(r'\d+,\d+\n|\d+\n|-\d+,\d+\n|-\d+\n', text)
    return [float(num.replace(',', '.')) for num in number_patterns]


def clean_dynexite_text(text):
    lines = text.split('\n')
    start_index = next(i for i, line in enumerate(lines) if "Punkte" in line and i > 10)
    end_index = next(i for i, line in enumerate(lines) if "wurden gespeichert." in line)
    text_section = lines[start_index:end_index + 1]
    patterns_to_remove = [r'\d+ Punkte', r'\d+ Punkt', r'\d+ NKS', r'HEB \d+', r'HEA \d+'] # Subject-specific sequences need to be added manually
    return re.sub('|'.join(patterns_to_remove), '', '\n'.join(text_section))


def find_missing_numbers(dynexite_list, excel_list):
    return list((Counter(excel_list) - Counter(dynexite_list)).elements())


def find_extra_numbers(dynexite_list, excel_list):
    return list((Counter(dynexite_list) - Counter(excel_list)).elements())


def find_near_matches(extra_numbers, missing_numbers, tolerance=0.2):
    close_matches = []
    for num in extra_numbers:
        closest_match = min(missing_numbers, key=lambda x: abs(x - num), default=None)
        if closest_match and abs(closest_match - num) <= tolerance:
            close_matches.append(num)
    return close_matches


def extract_yes_no_responses(text):
    yes_responses = re.findall(r'Ja\n', text)
    no_responses = re.findall(r'Nein\n', text)
    return yes_responses, no_responses


def compare_yes_no_responses(dynexite, excel):
    if dynexite == excel:
        print("Ja/Nein responses match exactly.")
    else:
        print(f"Ja/Nein responses do not match. Dynexite: {len(dynexite[0])} Ja, {len(dynexite[1])} Nein. Excel: {len(excel[0])} Ja, {len(excel[1])} Nein")


def main():
    tolerance = 0.2

    dynexite_text = read_file("Dynexite_Text.txt")
    excel_text = read_file("Excel_Text.txt")

    dynexite_numbers = extract_numbers(clean_dynexite_text(dynexite_text))
    excel_numbers = extract_numbers(excel_text)

    missing_numbers = find_missing_numbers(dynexite_numbers, excel_numbers)
    extra_numbers = find_extra_numbers(dynexite_numbers, excel_numbers)
    near_matches = find_near_matches(extra_numbers, missing_numbers, tolerance)

    compare_yes_no_responses(extract_yes_no_responses(dynexite_text), extract_yes_no_responses(excel_text))

    if dynexite_numbers == excel_numbers:
        print("All numbers match exactly and are in order.")
    elif len(dynexite_numbers) != len(excel_numbers):
        print(f"Mismatch in count: Dynexite ({len(dynexite_numbers)}) vs Excel ({len(excel_numbers)})")
    elif extra_numbers:
        for num in extra_numbers:
            closest_match = min(missing_numbers, key=lambda x: abs(x - num), default=None)
            print(f"Extra number {num} found. Closest match in Excel: {closest_match}.")
        if len(near_matches) == len(extra_numbers):
            print("All extra numbers are very close to missing ones.")
    else:
        print("Numbers match but are out of order:")
        print(f"Dynexite: {dynexite_numbers}")
        print(f"Excel: {excel_numbers}")


if __name__ == '__main__':
    main()
