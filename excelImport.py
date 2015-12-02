import pyexcel
from pyexcel.ext import xlsx

book = pyexcel.get_book(filename="C:\Users\Ami\Desktop\BillingSystem\ICD-Codes.xlsx")
sheets = book.to_dict() 
for name in sheets.keys():
    name