import requests
import re
from bs4 import BeautifulSoup
import json
from datetime import datetime as dt2
import sys

SALES_TXT_PATH = 'path of your restocks paid ids txt'

email = 'youremail'

password = 'yourpass'

restocks_headers = {
    'Host': 'restocks.net',
    'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/101.0.4951.64 Safari/537.36',
    'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9'
}


def login():

    session = requests.Session()

    session.headers.update(restocks_headers)

    print('Logging in...')

    response = session.get('https://restocks.net/it/login')

    soup = BeautifulSoup(response.text, 'html.parser')

    csrf_token = soup.find('meta', {'name': 'csrf-token'})['content']

    data = {'_token': csrf_token,
            'email': email,
            'password': password
            }

    response = session.post('https://restocks.net/it/login', data=data)

    response = session.get('https://restocks.net/it/account/profile')

    soup = BeautifulSoup(response.text, 'html.parser')

    try:

        account_name = soup.find(
            'div', {'class': 'col-lg-3 col-md-4'}).findAll('span')[1].text

        print('Successfully logged in as {}'.format(account_name))

    except:

        print('Login failed')

        sys.exit()


    return session


def payment_mode(session):

    try:
        with open(SALES_TXT_PATH, 'r') as f:

            paid_ids = f.read().split('\n')

    except Exception as e:

        print(e)

        paid_ids = []

    def scraping_sales(session):

        raw_sales_data = ''

        page = 1

        while True:
            print('Getting sales page: {}'.format(page))
            response = session.get(
                f"https://restocks.net/it/account/sales/history?page={page}")
            if "no__listings__notice" in response.text:
                break
            else:
                formatted_str = re.sub(r'\\n', '', response.text)
                raw_sales_data += json.loads(formatted_str)["products"]
                page += 1

        return raw_sales_data

    def preprocess_data(raw_sales_data):
        raw_sales_data = re.sub(r'\\', '', raw_sales_data)
        raw_sales_data = re.sub(r"<br/>", "", raw_sales_data)
        raw_sales_data = re.sub(r"<span>", "", raw_sales_data)
        raw_sales_data = re.sub(r"</span>", "", raw_sales_data)
        raw_sales_data = re.sub(r"     ", "", raw_sales_data)
        raw_sales_data = re.sub(r"                ", " ", raw_sales_data)
        preprocessed_data = re.sub(r"            ", "", raw_sales_data)
        all_sales = BeautifulSoup(
            preprocessed_data, "html.parser").findAll("tr")
        return all_sales

    sales = preprocess_data(scraping_sales(session))
    json_sales = []
    for sale in sales[1:]:
        json_sale = {}
        sale = str(sale)
        sale = sale.replace('<td>', "pause")
        sale = sale.replace('</td>', "pause")
        sale = sale.replace('<br/>', "pause")

        parsed_sale = [i for i in sale.split("pause") if len(i) > 1]

        item = parsed_sale[2].strip()
        sale_id = parsed_sale[3].strip().replace('ID: ', '')
        price = float((parsed_sale[4].replace("€", "").strip()))
        date = parsed_sale[5].strip()

        json_sale['item'] = item
        json_sale['sale_id'] = sale_id
        json_sale['price'] = price
        json_sale['date'] = date

        json_sales.append(json_sale)

    for a in sorted(json_sales, key=lambda x: dt2.strptime(x['date'], '%d/%m/%y')):

        if a['sale_id'] not in paid_ids:

            print('{} Missing payment for price {} and product {} with id {}'.format(a['date'], a['price'], a['item'], a['sale_id']))

        else:

            json_sales.remove(a)

    print('Total missing {} €'.format(int(sum(a['price'] for a in json_sales))))

    add_payment = False
    
    print('Insert "a" if you want to add a paid payment or press ENTER to close')
    
    if input() == 'a':

        add_payment = True

    while add_payment:

        print('Input the paid ID you want to add or press ENTER to return to payments')

        paid_id = input()

        if paid_id == '':

            add_payment = False

        if paid_id in paid_ids:

            print('Payment already added to list')

        else:

            try:
                with open(SALES_TXT_PATH, 'a') as f:

                    f.writelines('\n'+paid_id)

            except Exception as e:
                print('Error', e)


def main():

    session = login()

    payment_mode(session)


if __name__ == "__main__":
    main()
