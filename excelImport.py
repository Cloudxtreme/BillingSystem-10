import pyexcel
from pyexcel.ext import xlsx, xls
from infoGatherer.models import Diagnosis_Codes

icd_data_sheet = pyexcel.get_sheet(file_name="C:\Users\Ami\Desktop\BillingSystem\ICD-Codes-Sheet.xlsx")
icd_data_sheet.name_columns_by_row(0)
icd_records = icd_data_sheet.to_records()

 
for record in icd_records:
    name = record['name']
    code = record['code']
    d = Diagnosis_Codes(diagnosis_code=code,diagnosis_name=name)
    d.save()

cpt_data_sheet = pyexcel.get_sheet(file_name="C:\Users\Ami\Desktop\BillingSystem\ICD-Codes-Sheet.xlsx")
cpt_data_sheet.name_columns_by_row(0)
cpt_records = cpt_data_sheet.to_records()

for rec in cpt_records:
    pass