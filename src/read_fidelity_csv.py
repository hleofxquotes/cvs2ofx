import csv


class FidelityCsv:
    def __init__(self, filename, header_lineno=6):
        self.filename = filename
        self.header_lineno = header_lineno
        [headers, rows_dict] = self.parse_fidelity_history_for_account()
        self.headers = headers
        self.rows = rows_dict

    def action(self, row):
        value = row["Action"]
        if "BOUGHT" in value:
            return "BUY"

        if "REINVESTMENT" in value:
            return "REINVESTMENT"

        if "DIVIDEND" in value:
            return "DIVIDEND"

        return "NONE"

    def parse_fidelity_history_for_account(self):
        rows_dict = []
        with open(filename, mode="r") as file:
            csvreader = csv.reader(file)
            lines = 0
            # header_lineno = 6
            headers = []
            ended = False
            for row in csvreader:
                lines += 1
                if lines < self.header_lineno:
                    continue
                if lines == self.header_lineno:
                    headers = row
                else:
                    if len(row) == 0:
                        ended = True

                    if not ended:
                        cols = min(len(headers), len(row))
                        # print(cols)
                        row_dict = {}
                        for i in range(0, cols):
                            key = headers[i]
                            value = row[i]
                            # print(key, value)
                            row_dict[key] = value
                        rows_dict.append(row_dict)
        return [headers, rows_dict]


filename = "../data/History_for_Account_Z20488312.csv"
fidelity_csv = FidelityCsv(filename)
print(fidelity_csv.headers)
for row in fidelity_csv.rows:
    print(row["Action"], fidelity_csv.action(row), row["Symbol"], row["Amount ($)"])
