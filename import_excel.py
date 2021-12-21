import pandas as pd


def dump_excel(filepath):
    file = pd.read_excel(filepath)
    data = pd.DataFrame(file)
    return data["Ссылка"].values.tolist()


if __name__ == "__main__":
    filepath = "test.xlsx"
    print(dump_excel(filepath))
    print("Done")
