import requests, json, os
from datetime import datetime
from data.repository.integrations import IntegrationsRepository as INTREP
from flet.security import decrypt, encrypt
from dotenv import load_dotenv
load_dotenv(dotenv_path="controllers/.env")


class Tiny:

    def __init__(self, company:str):
        self.company = company
        self.__base_url = "https://api.tiny.com.br/api2"
        self.order = None
        self.order_tiny = None
        self.__search_response = None
        self.__order_response = None
        self.product_sku = None        
        self.__product_response = None
        self.__get_integration()


    def __get_integration(self):

        try:
            integration = INTREP().filter_company(name="TinyERP", company=self.company)
            self.integration_id = integration.id
            self.__access_token = self.__decrypt(integration.access_token)
        except Exception as exc:
            print(f'L42 (shopeeApi.py) -- {exc}')



    ## PEDIDOS ----

    def __pesquisar_pedido(self):
        path = f'{self.__base_url}/pedidos.pesquisa.php'
        payload = dict(token=self.__access_token, numeroEcommerce=self.order, numero=self.order_tiny, formato="json")
        response = requests.get(path, payload)
        request_response = json.loads(response.text)
        self.__search_response = request_response


    def obter_pedido(self, pedido:str=None, pedidoTiny:str=None):
        self.order=pedido
        self.order_tiny=pedidoTiny
        self.__pesquisar_pedido()
        if (self.__search_response["retorno"]["status_processamento"] == "2"):
            return self.__error(self.__search_response["retorno"]["codigo_erro"], self.__search_response["retorno"]["erros"][0]["erro"])
        order_id = self.__search_response["retorno"]["pedidos"][0]["pedido"]["id"]
        path = f'{self.__base_url}/pedido.obter.php'
        payload = dict(token=self.__access_token, id=order_id, formato="json")
        response = requests.get(path, payload)
        print(f'\nTINYERP > obter_pedido() ==> {response.status_code} | {response.text}\n') ##DEBUG
        request_response = json.loads(response.text)

        if request_response["retorno"]["status"] == "Erro":
            return self.__error(code=f'TINY CODE: {request_response["retorno"]["codigo_erro"]}', msg=f'{request_response["retorno"]["erros"][0]["erro"]}')
        
        if request_response["retorno"]["pedido"]['ecommerce']['nomeEcommerce'] == "PrestaShop":
            return self.__error(code="", msg="Pedido não encontrado")


        self.__order_response = request_response["retorno"]["pedido"]
        return {
                "orderDate": datetime.strptime(self.__order_response['data_pedido'], "%d/%m/%Y"),
                "orderNumber": self.__order_response['numero_ecommerce'],
                "orderReference": None,
                "orderChannel": self.clear_name(mode="string", channel=self.__order_response['ecommerce']['nomeEcommerce']),
                "orderChannelID": self.__order_response['ecommerce']['id'],
                "orderCompany":None,
                "customer": f'{self.__order_response["cliente"]["nome"]}'.title(),
                "customerID": None,
                "customerNickname": None,
                "customerPhone": self.__order_response["cliente"]["fone"],
                "order_customerEmail": self.__order_response["cliente"]["email"],
                "shippingAddress": self.__get_shipping_address(),
                "shippingMethod": None,
                "shippingDate": None,
                "original_shippingDate": None,
                "shippingTracking": None,
                "Products": self.__get_products(),
        }


    def __get_shipping_address(self):

        try:
            if "endereco_entrega" in self.__order_response:
                dict_shipping_address = {
                    "enderecoCompleto": f'{self.__order_response["endereco_entrega"]["endereco"]}, n{self.__order_response["endereco_entrega"]["numero"]}, {self.__order_response["endereco_entrega"]["complemento"]}, {self.__order_response["endereco_entrega"]["bairro"]}, {self.__order_response["endereco_entrega"]["cidade"]}, {self.__order_response["endereco_entrega"]["uf"]}, CEP: {self.__order_response["endereco_entrega"]["cep"]} - Quem Recebe: ----',

                    "endereco": self.__order_response["endereco_entrega"]["endereco"],
                    "numero": self.__order_response["endereco_entrega"]["numero"],
                    "complemento": self.__order_response["endereco_entrega"]["complemento"],
                    "bairro": self.__order_response["endereco_entrega"]["bairro"],
                    "cidade": self.__order_response["endereco_entrega"]["cidade"],
                    "uf": self.__order_response["endereco_entrega"]["uf"],
                    "cep": self.__order_response["endereco_entrega"]["cep"],
                    "destinatario": "----",
                }
            else:
                dict_shipping_address = {
                    "enderecoCompleto": f'{self.__order_response["cliente"]["endereco"]}, n{self.__order_response["cliente"]["numero"]}, {self.__order_response["cliente"]["complemento"]}, {self.__order_response["cliente"]["bairro"]}, {self.__order_response["cliente"]["cidade"]}, {self.__order_response["cliente"]["uf"]}, CEP: {self.__order_response["cliente"]["cep"]} - Quem Recebe: ----',

                    "endereco": self.__order_response["cliente"]["endereco"],
                    "numero": self.__order_response["cliente"]["numero"],
                    "complemento": self.__order_response["cliente"]["complemento"],
                    "bairro": self.__order_response["cliente"]["bairro"],
                    "cidade": self.__order_response["cliente"]["cidade"],
                    "uf": self.__order_response["cliente"]["uf"],
                    "cep": self.__order_response["cliente"]["cep"],
                    "destinatario": self.__order_response["cliente"]["nome"],
                }

            return dict_shipping_address

        except Exception as exc:
            print(f'L126 (tinyApi) -- {exc}')
            return None


    def __get_products(self):

        self.products = []
        self.products_response = self.__order_response["itens"]
        for product in self.products_response:
            self.products.append(
                {
                    "id": product['item']["id_produto"],
                    "produto": product['item']["descricao"],
                    "sku": product['item']["codigo"],
                    "qtd": int(float(product['item']["quantidade"])),
                    "icon": "#",
                    "personalizacao": ""
                }
            )

        return self.products


    def __get_tracking_code(self):
        if self.__order_response["forma_envio"] == "C":
            tracking = self.__order_response["codigo_rastreamento"]
            return tracking
        else:
            return None

    ## (END) ----



    ## PRODUTOS ----

    def __pesquisar_produto(self):
        path = f'{self.__base_url}/produtos.pesquisa.php'
        payload = dict(token=self.__access_token, pesquisa=self.product_sku, formato="json")
        response = requests.get(path, payload)
        request_response = json.loads(response.text)
        self.__search_response = request_response


    def obter_produto(self, sku:str):
        self.product_sku=sku
        self.__pesquisar_produto()
        if (self.__search_response["retorno"]["status_processamento"] == "2"):
            return self.__error(self.__search_response["retorno"]["codigo_erro"], self.__search_response["retorno"]["erros"][0]["erro"])
        product_id = self.__search_response["retorno"]["produtos"][0]["produto"]["id"]
        path = f'{self.__base_url}/produto.obter.php'
        payload = dict(token=self.__access_token, id=product_id, formato="json")
        response = requests.get(path, payload)
        request_response = json.loads(response.text)
        self.__product_response = request_response["retorno"]["produto"]
        # return self.__product_response
        return {
                "nome": self.__product_response["nome"],
                "sku": self.__product_response["codigo"],                
                "unidade": self.__product_response["unidade"],
                "preco": self.__product_response["preco"],
                "peso_bruto": self.__product_response["peso_bruto"],
                "alturaEmbalagem": self.__product_response["alturaEmbalagem"],
                "comprimentoEmbalagem": self.__product_response["comprimentoEmbalagem"],
                "larguraEmbalagem": self.__product_response["larguraEmbalagem"],
            }    

    ## (END) ----    



    ## PRODUTOS ----

    # def incluir_nota_fiscal(self, dados_nota:dict):
    #     path = f'{self.__base_url}/nota.fiscal.incluir.php'
    #     payload = dict(token=self.__access_token, nota=dados_nota, formato="json")
    #     response = requests.get(path, payload)
    #     request_response = json.loads(response.text)
    #     return request_response

    ## (END) ----    



    def clear_name(self, mode, channel):

        match mode:

            case "list":
                list_channel = list()
                for chn in channel:
                    if chn["descricao"].find("-") != -1:
                        name = chn["descricao"].split("-")
                        name_replace = name[1].replace(" ", "", 1)
                        if name_replace == 'Outros marketplaces':
                            continue
                        else:
                            list_channel.append(name_replace)
                    else:
                        name = chn["descricao"]
                        list_channel.append(name)
                return list_channel

            case "string":
                if channel.find("-") != -1:
                    name = channel.split(" ")
                    name_replace = name[0].replace(" ", "", 1)
                    return name_replace
                else:
                    return channel
                

    def __error(self, code:str, msg:str):

        """ Função padrão para retornar mensagens de erros e exeções nas consultas. """
        error = { "Error": {"Code": code, "Message": msg}}
        return error


    def __str__(self) -> str:
        return self.__search_response


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
