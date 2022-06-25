from __future__ import print_function
#Libraries for work with Google Sheets
import os.path
import time
import json
from google.auth import transport
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
#Libraries for get_currency function to get fresh currency data.
from lxml import etree
import requests
from datetime import datetime
#Library for work with Database.
import psycopg2
from copy import deepcopy
import telebot

def get_currency():
    today = datetime.now().strftime("%d/%m/%Y")
    xml_data = requests.get('https://www.cbr.ru/scripts/XML_daily.asp?date_req='+today).content
    xml_parse = etree.fromstring(xml_data)
    dollar_to_ruble = xml_parse.xpath('//ValCurs//Valute[@ID="R01235"]//Value')[0].text
    dollar_to_ruble = float(dollar_to_ruble.replace(',','.'))
    return dollar_to_ruble

def insert_update_database(data):
    conn = psycopg2.connect(database = "numberstest", user = "postgres", password = "postgres", host = "postgres_db", port = "5432")
    cur = conn.cursor()
    for one_data in data:
        cur.execute("SELECT * FROM numbersdata WHERE num = %s", (one_data[0],))
        if cur.fetchall()==[]:
            cur.execute("INSERT INTO numbersdata(num, ordernum, pricedollar, supplydate, priceruble) VALUES (%s, %s, %s, to_date(%s, 'DD.MM.YYYY'), %s)", 
                (one_data[0], one_data[1], one_data[2], one_data[3], one_data[4]))
            splitted_date = one_data[3].split('.')
            normalized_date = f'{splitted_date[2]}-{splitted_date[1]}-{splitted_date[0]}'
            json_data = {
                'num':one_data[0],
                'order_number':one_data[1],
                'price_dollar':one_data[2],
                'supply_date':normalized_date,
                'price_ruble':one_data[4]
            }
            requests.post('http://nginx:80/numberstest/numbers/', json=json_data)
        else:
            cur.execute("UPDATE numbersdata SET ordernum = %s, pricedollar = %s, supplydate = to_date(%s, 'DD.MM.YYYY'), priceruble=%s WHERE num = %s", 
                (one_data[1], one_data[2], one_data[3], one_data[4], one_data[0]))
            splitted_date = one_data[3].split('.')
            normalized_date = f'{splitted_date[2]}-{splitted_date[1]}-{splitted_date[0]}'
            json_data = {
                'num':one_data[0],
                'order_number':one_data[1],
                'price_dollar':one_data[2],
                'supply_date':normalized_date,
                'price_ruble':one_data[4]
            }
            requests.put(f'http://nginx:80/numberstest/numbers/{one_data[0]}', json=json_data)
    conn.commit()

def check_date(bot, archive, data, user_id):
    for one_data in data:
        if one_data[1] not in archive:
            archive.append(one_data[1])
            one_date = one_data[3].split('.')
            if datetime(int(one_date[2]), int(one_date[1]), int(one_date[0]), 0, 0, 0).timestamp() < datetime.now().timestamp():
                bot.send_message(user_id, f'Срок поставки заказа №{one_data[1]} прошел')
    return archive

def get_sheets_data(SAMPLE_SPREADSHEET_ID, SAMPLE_RANGE_NAME):
    """Shows basic usage of the Sheets API.
    Prints values from a sample spreadsheet.
    """
    SCOPES = ['https://www.googleapis.com/auth/spreadsheets.readonly']
    creds = None
    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(transport.requests.Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.json', 'w') as token:
            token.write(creds.to_json())

    try:
        service = build('sheets', 'v4', credentials=creds)

        # Call the Sheets API
        sheet = service.spreadsheets()
        result = sheet.values().get(spreadsheetId=SAMPLE_SPREADSHEET_ID,
                                    range=SAMPLE_RANGE_NAME).execute()
        values = result.get('values', [])

        if not values:
            print('No data found.')
            return

        return values
    except HttpError as err:
        print(err)


def main():
    SAMPLE_SPREADSHEET_ID = '14VXHzb1HlLiq7cmiNw-hyCcRkTQWW75a6M96BGOU6xI'
    SAMPLE_RANGE_NAME = 'Test!A2:D'
    TOKEN = '5593989075:AAHfDU4Hi4d-M0B_QPwkpaKb69Kz4A_f9O0'
    telegram_user_id = 789929585
    bot = telebot.TeleBot(TOKEN)
    archive = []
    first_data = get_sheets_data(SAMPLE_SPREADSHEET_ID, SAMPLE_RANGE_NAME)
    first_data_updated = deepcopy(first_data)
    dollar_to_ruble = get_currency()
    for one_data in first_data_updated:
        one_data.append(round(int(one_data[2])*dollar_to_ruble, 2))
    insert_update_database(first_data_updated)
    archive = check_date(bot, archive, first_data_updated, telegram_user_id)
    while True:
        data_new = get_sheets_data(SAMPLE_SPREADSHEET_ID, SAMPLE_RANGE_NAME)
        if first_data != data_new and len(data_new) > 0:
            print('New data')
            first_data = deepcopy(data_new)
            first_data_updated = deepcopy(first_data)
            dollar_to_ruble = get_currency()
            for one_data in first_data_updated:
                one_data.append(round(int(one_data[2])*dollar_to_ruble, 2))
            insert_update_database(first_data_updated)
            archive = check_date(bot, archive, first_data_updated, telegram_user_id)
        else:
            time.sleep(10)


if __name__ == '__main__':
    main()