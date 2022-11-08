import re
import argparse

from PyPDF2 import PdfReader


class SalaryAndBenefitsReport:

  @staticmethod
  def check_if_page_contains_headers(rows_from_pdf, source_text):
    # strip out the headlines
    match = re.search(r"Other Benefits", source_text, re.I)
    rows_from_pdf = source_text[match.span()[-1]:].strip().split("\n")
    if re.search("Due to rounding in formula calculations", rows_from_pdf[-1]):
      rows_from_pdf = rows_from_pdf[:-1]
    return rows_from_pdf

  def print_salary_and_benefit_data_to_console(self, rows):
    for row in rows:
      splitted_text = row.split()

      fte_index = self.find_the_fte_index(splitted_text)
      fte = splitted_text[fte_index]
      # first name is the first column
      last_name = splitted_text[0]
      first_name = splitted_text[1]

      # the index of the Title is between the first name and the fte index
      title = " ".join(splitted_text[2: fte_index])
      base_salary = splitted_text[fte_index + 1].replace(",", "")
      retirement = splitted_text[fte_index + 2].replace(",", "")
      total_salary = splitted_text[fte_index + 3].replace(",", "")

      print(",".join([last_name, first_name, title, base_salary, retirement, total_salary, fte]))

  @staticmethod
  def find_the_fte_index(splitted_text):
    for text in splitted_text:
      try:
        float(text)
        fte_index = splitted_text.index(text)
        break
      except:
        pass
    return fte_index


class SalaryCompensationReport:
  @classmethod
  def print_salary_compensation_data_to_console(cls, source_text):
    # strip out the headlines
    match = re.search(r"\nPayout in \n\d+-\d+\n", source_text, re.I)
    rows = source_text[match.span()[-1]:].split("\n")

    for row in rows:
      # lets find the contract days, that'll orient how we find the remaining data
      row = row.split()
      for text in row:
        if re.match(r"\d{3}", text):
          break

      cls.extract_salary_compensation_data(row, text)

  @staticmethod
  def extract_salary_compensation_data(row, text):
      contract_days_index = row.index(text)
      contract_days = row[contract_days_index]

      first_name = row[contract_days_index - 1]
      last_name = row[contract_days_index - 2]
      last_name_index = row.index(last_name)
      position = " ".join(row[:last_name_index])

      full_year_base_salary_index = contract_days_index + 1
      full_year_base_salary = row[full_year_base_salary_index].replace(",", "")
      # next column
      next_col = full_year_base_salary_index + 1
      if len(row[next_col]) == 1:
        full_year_base_salary += row[next_col]

      trs = row[next_col + 1].replace(",", "")
      total_salary = row[next_col + 2].replace(",", "")
      print(",".join([position, last_name, first_name, contract_days, full_year_base_salary, trs, total_salary]))


def print_headers(salary_and_benefits_reports_header=None, salary_compensation_report_header=None):
  if salary_and_benefits_reports_header:
    text = "Last Name,First Name,Title,Base Salary,Retirement,Total Salary,FTE"
  elif salary_compensation_report_header:
    text = "Position,Last Name,First Name,Contract Days,Full Year Base Salary,TRS,Total Salary"
  print(f"\n{text}")


def main(pdf_file):
  reader = PdfReader(pdf_file)
  for number in range(reader.numPages):
    page = reader.pages[number]
    source_text = page.extract_text()
    rows_from_pdf = source_text.split("\n")

    if re.search("Salary and Benefits Report", source_text, re.I):
      print_headers(salary_and_benefits_reports_header=True)
      salary_benefits_report_object = SalaryAndBenefitsReport()
      rows = salary_benefits_report_object.check_if_page_contains_headers(rows_from_pdf, source_text)
      salary_benefits_report_object.print_salary_and_benefit_data_to_console(rows)
    
    elif re.search("Salary Compensation Report", source_text, re.I):
      print_headers(salary_compensation_report_header=True)
      SalaryCompensationReport.print_salary_compensation_data_to_console(source_text)


if __name__ == "__main__":
  parser = argparse.ArgumentParser()
  parser.add_argument("--file", type=str, required=True)
  args = parser.parse_args()
  main(args.file)