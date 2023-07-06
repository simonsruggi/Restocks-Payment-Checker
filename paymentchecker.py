import requests
from datetime import datetime as dt2
import sys
from dotenv import load_dotenv
import os
import numpy as np

script_directory = os.path.dirname(os.path.abspath(__file__))

# Construct the full path to the "paid_ids.txt" file
sales_txt_path = os.path.join(script_directory, "paid_ids.txt")

# Load environment variables from .env file
load_dotenv()

# Access the email and password from environment variables
email = os.getenv('EMAIL')
password = os.getenv('PASSWORD')

# Check if the environment variables are set
if email is None or password is None:
    raise ValueError('Email or password environment variables are not set.')


api_restocks_headers = {
    'Host': 'api.restocks.net',
    'sec-ch-ua': '"Not.A/Brand";v="8", "Chromium";v="114", "Google Chrome";v="114"',
    'restocks-valuta': 'EUR',
    'restocks-platform': 'web',
    'accept-language': 'it',
    'sec-ch-ua-mobile': '?0',
    'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36',
    'content-type': 'application/json',
    'restocks-country': 'NL',
    'sec-ch-ua-platform': '"macOS"',
    'accept': '*/*',
    'origin': 'https://restocks.net',
    'sec-fetch-site': 'same-site',
    'sec-fetch-mode': 'cors',
    'sec-fetch-dest': 'empty',
    'referer': 'https://restocks.net/',
}


def login():

    global authentication_token

    session = requests.Session()

    session.headers.update(api_restocks_headers)

    try:

        print('Logging in...')

        data = {
            'email': email,
            'password': password
        }

        response = session.post(
            'https://api.restocks.net/v1/auth/login', json=data)

        account_name = response.json()['data']['user']['firstname']

        authentication_token = response.json()['data']['token']

        print('Logged in successfully as {}'.format(account_name))

        session.headers.update(
            {'authorization': 'Bearer {}'.format(authentication_token)})

        return session

    except Exception as e:

        print('Login failed, closing app')

        sys.exit()


def payment_mode(session):

    try:
        with open(sales_txt_path, 'r') as f:

            paid_ids = f.read().split('\n')

    except Exception as e:

        print(e)

        paid_ids = []

    page = 1
    sales_finished = False
    json_sales = []
    while not sales_finished:

        print('Getting sales page: {}'.format(page))
        session.headers.update(api_restocks_headers)

        response = session.get(
            f"https://api.restocks.net/v1/shop/account/sales/history?page={page}")
        for i in response.json()['data']:

            json_sale = {}
            json_sale['sale_id'] = str(i['id'])
            json_sale['price'] = i['payout'].replace('€ ', '')
            json_sale['date'] = i['date']
            json_sale['item'] = i['baseproduct']['name'] + \
                ' ' + str(i['size']['name'])
            json_sales.append(json_sale)

        if not response.json()['data']:
            print('Sales finished')
            sales_finished = True
        else:
            page += 1

    for a in sorted(json_sales, key=lambda x: dt2.strptime(x['date'], '%d/%m/%y')):

        if a['sale_id'] not in paid_ids:

            start = dt2.strptime(a['date'], '%d/%m/%y').date()
            end = dt2.today().date()
            business_days = np.busday_count(start, end)
            if business_days >= 39:
                print('{} Missing payment for price {} and product {} with id {}, business days passed: {}'.format(
                    a['date'], a['price'], a['item'], a['sale_id'], business_days))
            elif business_days >= 25 and business_days <= 38:
                print('{} Missing payment for price {} and product {} with id {}, business days passed: {}'.format(
                    a['date'], a['price'], a['item'], a['sale_id'], business_days))
            else:
                print('{} Missing payment for price {} and product {} with id {}, business days passed: {}'.format(
                    a['date'], a['price'], a['item'], a['sale_id'], business_days))
        else:
            json_sales.remove(a)

    print('Total missing {}€ for a total of {} sales '.format(
        int(sum(float(a['price']) for a in json_sales)), len(json_sales)))

    add_payment = False

    print('Insert "a" if you want to add a paid payment or insert "r" to get the restocks email version or press ENTER to close')

    new_choice = input()

    if new_choice == 'a':

        add_payment = True

    elif new_choice == 'r':

        for a in sorted(json_sales, key=lambda x: dt2.strptime(x['date'], '%d/%m/%y')):

            if a['sale_id'] not in paid_ids:

                start = dt2.strptime(a['date'], '%d/%m/%y').date()
                end = dt2.today().date()
                business_days = np.busday_count(start, end)
                if business_days >= 39:

                    print('{} Missing payment for price {} and product {} with id {}, business days passed: {}'.format(
                        a['date'], a['price'], a['item'], a['sale_id'], business_days))

    while add_payment:

        print('Input the paid ID you want to add or press ENTER to return to payments')

        paid_id = input()

        if paid_id == '':

            add_payment = False

            break

        if paid_id in paid_ids:

            print('Payment already added to list')

        else:
            for s in json_sales:
                if str(s['sale_id']) == str(paid_id):

                    print('Congrats! You got your payment of {} for product {} and id {} sold on {}'.format(
                        s['price'], s['item'], s['sale_id'], s['date']))

                    break
            try:
                with open(sales_txt_path, 'a') as f:

                    f.writelines('\n'+paid_id)

            except Exception as e:
                print('Error', e)


def main():

    session = login()

    payment_mode(session)


if __name__ == "__main__":
    main()
