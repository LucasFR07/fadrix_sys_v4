import requests, json
from data.repository.integrations import IntegrationsRepository as INTREP
from data.repository.api_platforms import API_PlatformsRepository as API_REP

import os
from flet.security import decrypt, encrypt
from dotenv import load_dotenv
load_dotenv(dotenv_path="controllers/.env")


class Amazon:

    """ Classe de conexão com a API da Amazon """

    def __init__(self, company:str):
        self.company = company

        self.__base_url = "https://sellingpartnerapi-na.amazon.com"
        self.__get_integration()


    def __get_integration(self):

        try:
            integration = INTREP().filter_company(name="Amazon", company=self.company)
            self.integration_id = integration.id
            self.__access_token = self.__decrypt(integration.access_token) if integration.access_token != None else None
            self.__refresh_token = self.__decrypt(integration.refresh_token) if integration.refresh_token != None else None
            self.__partner_id = self.__decrypt(integration.app_id)
            self.__partner_key = self.__decrypt(integration.app_key)

            self.headers = {
                'x-amz-access-token': self.__access_token,
                'Content-Type': 'application/json',
                'User-Agent': 'Fadrix SYS/4.0 (Language=Python/3.12.2; Platform=Windows/11)'
            }

        except Exception as exc:
            print(f'L48 (amazonApi.py) -- {exc}')


    ## Authorization Process
    def __refresh_code(self):
        path = 'https://api.amazon.com/auth/o2/token'
        payload = f'grant_type=refresh_token&refresh_token={self.__refresh_token}&client_id={self.__partner_id}&client_secret={self.__partner_key}'
        headers = {'Content-Type': 'application/x-www-form-urlencoded'}
        self.response = requests.request("POST", path, headers=headers, data=payload)
        result = json.loads(self.response.text)
        print(f'L48 (amazonApi.py) -- {result}') ##DEBUG
        if "errors" in result:
            print(result["errors"][0]["details"])

        INTREP().update(id=self.integration_id, fild="access_token", data=self.__encrypt(result["access_token"]))
        INTREP().update(id=self.integration_id, fild="refresh_token", data=self.__encrypt(result["refresh_token"]))

        API_REP().update(3, "access_token", result["access_token"])
        API_REP().update(3, "access_token_refresh", result["refresh_token"])
        self.__get_integration()
        return None
    ## ------


    def get_order(self, order):

        try:
            count_error = 0
            while count_error < 2:
                path = f'{self.__base_url}/orders/v0/orders/{order}'
                self.response = requests.request("GET", path, headers=self.headers)
                result = json.loads(self.response.text)
                print(f'AMAZON_API > get_order() ==> {result}') ##DEBUG

                if "errors" in result:
                    match result["errors"][0]["details"]:
                        case "The access token you provided is revoked, malformed or invalid.":
                            self.__refresh_code()
                            count_error +=1
                            continue
                        case "The access token you provided has expired.":
                            self.__refresh_code()
                            count_error +=1
                            continue
                        case _:
                            print(f'L80 (amazonApi.py) -- {result["errors"][0]["details"]}')
                            break
                else:
                    break
            print(f'L74 (amazonApi.py) -- {result["payload"]["EarliestShipDate"]}') ##DEBUG
            return result['payload']['EarliestShipDate']

        except Exception as exc:
            print(f'L108 (amazonApi.py) -- {exc}')


    def create_reports(self):

        count_error = 0
        while count_error < 2:        
            path = f'{self.__base_url}/reports/2021-06-30/reports'
            payload = json.dumps({
            "marketplaceIds": ["A394PSLNL4TTC4"],
            "reportType": "GET_V2_SELLER_PERFORMANCE_REPORT",
            # "reportOptions": {},
            # "dataStartTime": "1945-09-22T08:41:00.794Z",
            # "dataEndTime": "2001-11-09T11:30:10.802Z"
            })            
            self.response = requests.request("POST", path, headers=self.headers, data=payload)
            result = json.loads(self.response.text)
            print(self.response.status_code, self.response.text)

            if "errors" in result:
                match result["errors"][0]["details"]:
                    case "The access token you provided is revoked, malformed or invalid.":
                        self.__refresh_code()
                        count_error +=1
                        continue
                    case "The access token you provided has expired.":
                        self.__refresh_code()
                        count_error +=1
                        continue
                    case _:
                        print(f'L80 (amazonApi.py) -- {result["errors"][0]["details"]}')
                        break
            else:
                break            




    ## Encrypting sensitive data
    def __decrypt(self, value):
        secret_key = os.environ["secret_key"]
        decrypt_data = decrypt(value, secret_key)
        return decrypt_data

    def __encrypt(self, value):
        secret_key = os.environ["secret_key"]
        encrypted = encrypt(value, secret_key)
        return encrypted
    ## ------
