'''
MIT License

Copyright (c) 2019 Daniel Torres, Artturi Rämänen

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

import csv
import argparse
from datetime import datetime 


__author__ = 'Daniel Torres'

date_index = 2
payee_index = 4
amount_index = 3
info_index = 10

def get_cli_args():
    parser = argparse.ArgumentParser( description='Parse Nordea Bank transactions files into into YNAB-ready files. Designed and tested for the Danish version of Nordea\'s website.')
    parser.add_argument('-s', '--source', type=str, help='Source filename (the CSV file exported using Nordea Web Banking)', required=True)
    parser.add_argument('-d', '--destination', type=str, help='Destination filename', default='ynab.csv')
    args = parser.parse_args()
    return args.source, args.destination
	
def convertToValidDate(row):
    newRow = []
    for cell in row:
        try: 
            parsed = datetime.strptime(cell,"%d-%m-%Y")
            newRow.append(parsed.strftime("%d/%m/%Y"))
        except:
            newRow.append(cell)
    return newRow

def main():
    source, destination = get_cli_args()
	# The .csv file from Nordea uses some sort of encoding other than unicode
    with open(source) as inputFile, open(destination, 'w+') as outputFile:
        convertFiles(inputFile, outputFile)


    print('YNAB file written to \'' + destination + '\'')

def convertFiles(inputFile, outputFile):
    # remove first lines
    inputFile.readline()
    inputFile.readline()
    inputFile.readline()
    inputFile.readline()

    csvObj =  csv.reader(inputFile,delimiter='\t')
    
    # the destination file will be encoded using unicode
    outputFile.write('Date;Payee;Memo;Inflow\n')
    for row in csvObj:
        if row == []:
            continue
        outputRow = []
        outputRow.append(row[date_index])
        outputRow.append(row[payee_index])
        outputRow.append(row[info_index])
        outputRow.append(row[amount_index])
        outputRow=convertToValidDate(outputRow)
        outputFile.write(';'.join(outputRow) + '\n')

if __name__=="__main__":
   main() 
