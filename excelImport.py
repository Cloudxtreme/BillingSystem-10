import pyexcel
from pyexcel.ext import xlsx, xls
from infoGatherer.models import Diagnosis_Codes

data_sheet = pyexcel.get_sheet(file_name="C:\Users\Ami\Desktop\BillingSystem\ICD-Codes-Sheet.xlsx")
data_sheet.name_columns_by_row(0)
records = data_sheet.to_records()
 
for record in records:
    name = record['name']
    code = record['code']
    
    d = Diagnosis_Codes(diagnosis_code=code,diagnosis_name=name)
    
    d.save()
    
#print(json.dumps(data_sheet.to_array()))
#sheets = book.to_dict() 
#for name in sheets.keys():
#    name
