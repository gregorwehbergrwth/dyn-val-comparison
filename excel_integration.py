import openpyxl


excel_filepath = r"C:\Users\grego\Downloads\HÜ_01_Excel.xlsx"
position = 'B13:B36'


def numbers_from_excel(filepath, location):
    workbook = openpyxl.load_workbook(filepath, data_only=True)
    sheet = workbook.active

    numbers = []
    for cell_tuple in sheet[location]:
        cell = cell_tuple[0]
        if cell.value is not None:
            numbers.append(cell.value)
        else:
            numbers.append(0)
    return numbers


def save_numbers_to_file(filename, numbers):
    numbers = "\n".join(str(number).replace(".", ",") for number in numbers if number)
    with open(filename, 'w') as file:
        file.write(numbers + "\n")

    print("updated the excel numbers. check if the excel file was saved beforehand")




if __name__ =="__main__":
    numbers = numbers_from_excel(excel_filepath, position)
    save_numbers_to_file('excel.txt', numbers)





