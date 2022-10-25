import re
import argparse
from datetime import datetime

from PyPDF2 import PdfReader


def find_date_and_check_amount(data: str) -> tuple:
  # helper function
  date, check_amount = '', ''
  for datum in data:
    if re.match(r"\d+/\d+/\d+", datum):
      date = datum
    elif re.match(r"(\d+.\d+)", datum):
      check_amount = datum
  return date, check_amount


def print_to_console(rows_from_pdf: list) -> None:
  for row in rows_from_pdf:
    # row = rows_from_pdf[3]
    data = row.split()
    date, check_amount = find_date_and_check_amount(data)

    if date and check_amount:
      try:
        date_index = data.index(date)
        first_part = data[:date_index + 1] 
        if len(first_part) == 3:
          # set the bank number for the remaining rows
          global bank_no
          bank_no = first_part[0]
        elif len(first_part) == 2:
          first_part.insert(0, bank_no)

        # look for the check amount
        check_amount_index = data.index(check_amount) + 1
        last_part = data[check_amount_index-3:check_amount_index] 
        # strip void from check amount
        check_amount = last_part[-1]
        last_part[-1] = check_amount.lower().strip("void")

        # grab everything between our Check Date and Batch No, some of which is our payee name
        vendor_info = data[date_index+1:data.index(last_part[0])]
        # looks like the first data will always be our vendor number
        vendor_no = vendor_info[0]
        # and what's left is our vendor name
        vendor_name = " ".join(vendor_info[1:]).replace(",", "")

        # convert date to ISO format
        isodate = datetime.strptime(first_part[-1], "%m/%d/%Y").isoformat()
        # strip off T00:00:00
        first_part[-1] = isodate.split("T")[0]
        
        # add our vendor name to first_part
        first_part.append(vendor_name)
        
        joined_data = ','.join(first_part + last_part)
        print(joined_data)
      except Exception as err:
        pass


def check_if_page_contains_header(page: dict) -> list:
  source_text = page.extract_text()
  rows_from_pdf = source_text.split("\n")

  # check if the current page has our headers
  for row in rows_from_pdf:
    has_headers = all([ field in row for field in fields ])
    if has_headers:
      rows_from_pdf = rows_from_pdf[rows_from_pdf.index(row) + 1:]
      break

  return rows_from_pdf


def main(pdf_file: str) -> None:
  reader = PdfReader(pdf_file)
  number_of_pages = len(reader.pages)
  print(",".join(fields))  # print CSV headers

  for number in range(number_of_pages):
    page = reader.pages[number]
    rows = check_if_page_contains_header(page)
    print_to_console(rows)


if __name__ == "__main__":
  bank_no = ""
  fields = [
        "Bank No", 
        "Check No", 
        "Check Date",
        "Vendor Name",
        "Batch No",
        "Type",
        "Check Amount",
      ]

  parser = argparse.ArgumentParser()
  parser.add_argument("--file", type=str, required=True)
  args = parser.parse_args()
  main(args.file)