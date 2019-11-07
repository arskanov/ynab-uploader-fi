# ynab-uploader-fi
Upload Nordea Bank transactions files to YNAB via their API
Made for the Finnish version of Nordea's website.

### Usage example:
Add file "config.py" with contents:
```
personal_access_token = '0f...77'
budget_id = '3a...99'
accounts = {
    "FI5...8": "87...65",
    "FI5...9": "87...66"
}
```

All but the `accounts` key values are available from YNAB. The `accounts` dict maps your IBAN to YNAB accounts.


Open the terminal and run
```sh
$ pipenv install
$ pipenv run python site.py
```
Open browser at http://localhost:8080
Select your bank and file to upload

### How to export CSV file from Nordea
Export your bank transactions using Nordea Home banking
![Imgur](https://i.imgur.com/aLoTe8w.png)

Save file (ex: nordea.csv)

### Requirements
 Python v3.7
 pipenv
