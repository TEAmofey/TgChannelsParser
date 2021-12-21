import pandas as pd
import openpyxl  # <--- necessary for pd.read_excel()


def dump_excel(filepath):
    file = pd.read_excel(filepath, sheet_name="Sheet1")
    data = pd.DataFrame(file)
    return data["Ссылка"].values.tolist()


if __name__ == "__main__":
    filepath = "test.xlsx"
    print(dump_excel(filepath))
    print("Done")
