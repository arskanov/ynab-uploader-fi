'''
MIT License

Copyright (c) 2019 Artturi Rämänen

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
'''

from bottle import route, request, run
import os, io, csv

from ynab_converter import convertFiles
from ynab import upload_transactions

from config import budget_id, accounts

@route('/')
def uploadForm():
    return '''
        <select name="banklist" form="upload_form">
        <option value="nordea">Nordea</option>
        <option value="osuuspankki">OP</option>
        </select>

        <form id="upload_form" action="/upload" method="post" enctype="multipart/form-data">
        Select bank data to import: <input type="file" name="upload" />
        <input type="submit" value="Upload" />
        </form>
        '''

@route('/upload', method='POST')
def do_upload():
    bank = request.forms.get('banklist')
    upload = request.files.get('upload')
    name, ext = os.path.splitext(upload.filename)

    if ext not in ('.csv','.txt'):
        return 'File extension not allowed! .csv and .txt ok :)'

    iban = get_iban(name, bank)
    if iban == None:
        return "Couldn't get iban for filename " + name + " with bank " + bank

    accountId = get_account_id(iban)
    if accountId == None:
        return "Couldn't get account ID for " + iban

    transactions = []
    with io.StringIO() as standard, \
         io.TextIOWrapper(upload.file, encoding="utf-8") as inputFile:
        convertFiles(inputFile, standard)
        # Get ready to read file
        standard.seek(0)

        # Read as CSV file
        reader = csv.DictReader(standard, delimiter=';')
        for row in reader:
            date = row['Date'].split('.')
            transactions.append({
                "date": "{}-{}-{}".format(date[2],date[1], date[0]),
                "payee": row['Payee'],
                "description": row['Memo'],
                "amount": row['Inflow'].replace(',', '.') # Ynab.py wants dot
            })

    print("Transactions count = " + str(len(transactions)))
    upload_to_ynab(accountId, transactions)

    return 'OK, uploaded transactions from ' + bank


def get_iban(fullFileName, bank):
    if bank == "nordea":
        return fullFileName.split("_")[1]
    return None

def upload_to_ynab(account_id, transactions):
    result = upload_transactions(
        budget_id, account_id, transactions)
    print("Upload result: " + str(result))

def get_account_id(ibanToFind):
    return accounts.get(ibanToFind)


run(host='0.0.0.0', port=8080, debug=True)