'''
ynab.py by wesselt, license is for this file
Modified by Artturi Rämänen

Tooling to read transactions from BUNQ (https://www.bunq.com/nl/)
and upload them to YNAB (https://www.youneedabudget.com)

Copyright (C) 2018 and later   wesselt@github

This program is free software; you can redistribute it and/or modify
it under the terms of the GNU General Public License iversion 2 as 
published by the Free Software Foundation.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program; if not, write to the Free Software
Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA
'''

from decimal import Decimal
import json
import os
import requests
import uuid

from config import personal_access_token

url = 'https://api.youneedabudget.com/'

# 1 to log http calls, 2 to include headers
log_level = 0


# -----------------------------------------------------------------------------

def read_file(fname):
    fn = os.path.join(os.path.dirname(__file__), fname)
    if os.path.isfile(fn):
        with open(fn, 'r') as f:
            return f.read()


def get_personal_access_token():
    return personal_access_token


# -----------------------------------------------------------------------------

def log_request(action, method, headers, data):
    if log_level < 1:
        return
    print("******************************")
    print("{0} {1}".format(action, method))
    if log_level > 1:
        for k, v in headers.items():
            print("  {0}: {1}".format(k, v))
    if data:
        print("-----")
        print(json.dumps(data, indent=2))
        print("-----")


def log_reply(reply):
    if log_level < 1:
        return
    print("Status: {0}".format(reply.status_code))
    if log_level > 1:
        for k, v in reply.headers.items():
            print("  {0}: {1}".format(k, v))
    print("----------")
    if reply.headers["Content-Type"].startswith("application/json"):
        print(json.dumps(reply.json(), indent=2))
    else:
        print(reply.text)
    print("******************************")


def call(action, method, data_obj=None):
    data = json.dumps(data_obj) if data_obj else ''
    headers = {
        'Authorization': 'Bearer ' + get_personal_access_token(),
        'Content-type': 'application/json'
    }
    log_request(action, method, headers, data_obj)
    if action == 'GET':
        reply = requests.get(url + method, headers=headers)
    elif action == 'POST':
        reply = requests.post(url + method, headers=headers, data=data)
    log_reply(reply)
    result = reply.json()
    if "error" in result:
        raise Exception("{0} (details: {1})".format(
                           result["error"]["name"], result["error"]["detail"]))
    return result["data"]


# -----------------------------------------------------------------------------

def is_uuid(id):
    try:
        uuid.UUID("{" + id + "}")
        return True
    except ValueError as e:
        return False


def get_budget_id(budget_name):
    if is_uuid(budget_name):
        return budget_name

    reply = get('v1/budgets')
    for b in reply["budgets"]:
        if b["name"].casefold() == budget_name.casefold():
            return b["id"]
    raise Exception("YNAB budget '{0}' not found".format(budget_name))


def get_account_id(budget_id, account_name):
    if is_uuid(account_name):
        return account_name

    reply = get('v1/budgets/' + budget_id + "/accounts")
    for a in reply["accounts"]:
        if a["name"].casefold() == account_name.casefold():
            return a["id"]
    raise Exception("YNAB account '{0}' not found".format(account_name))


def upload_transactions(budget_id, account_id, transactions):
    ynab_transactions = []
    for t in transactions:
        milliunits = str((1000 * Decimal(t["amount"])).quantize(1))
        # Calculate import_id for YNAB duplicate detection
        occurrence = 1 + len([y for y in ynab_transactions
                      if y["amount"] == milliunits and y["date"] == t["date"]])
        ynab_transactions.append({
            "account_id": account_id,
            "date": t["date"],
            "amount": milliunits,
            "payee_name": t["payee"][:50],  # YNAB payee is max 50 chars
            "memo": t["description"][:100],  # YNAB memo is max 100 chars
            "cleared": "cleared",
            "import_id": "YNAB:{}:{}:{}".format(
                                             milliunits, t["date"], occurrence)
        })

    method = "v1/budgets/" + budget_id + "/transactions/bulk"
    result = post(method, {"transactions": ynab_transactions})
    return result["bulk"]


# -----------------------------------------------------------------------------

def set_log_level(level):
    global log_level
    log_level = level


def get(method):
    return call('GET', method)


def post(method, data):
    return call('POST', method, data)
