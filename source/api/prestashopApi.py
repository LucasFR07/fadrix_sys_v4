import re
import requests, json, base64
from decimal import Decimal, getcontext
from datetime import datetime
from pytz import timezone

from source.api.api import API
from source.api.magis5 import Magis5


class Prestashop(API):

    """
    Classe para gerenciamento e controle da integração com a API da PrestaShop.

    Cada método abaixo representa um recurso da api disponibilizado pela PrestaShop,
    com excessão dos métodos terminados em "pattern" e "rule", que são métodos para
    padronizar a resposta da chamada para uso adequado no sistema.

    @author: Douglas Leal <https://github.com/douleal>
    @copyright: 2024 Douglas Leal
    @license: ****
    """

    def __init__(self) -> None:
        super().__init__(developer_account=None, api_platform="PrestaShop")
        self.get_access()

        self.__headers = {
            'Authorization': f'Basic {base64.b64encode(self.access_token.encode()).decode()}',
            'Content-Type': 'application/json',
        }



    def __check_api_call(call): ## DECORADOR DE CHECAGEM
        """ Verifica a chamada da API, padronizando e resolvendo retornos de erro. """

        try:
            def wrapper(self, *args, **kwargs):
                request_call = call(self, *args, **kwargs)

                if request_call == None:
                    return {"Error": {"Code": "INTERNAL_ERROR", "Message": "Houve um erro interno ao solicitar essa chamada, consulte o suporte do sistema."}}

                print(f'\n🐞 PRESTASHOP_API > CHECK_CALL > {call.__name__}() ==> RESPONSE: {request_call.status_code} | {request_call.text}\n') ##DEBUG

                if request_call.status_code == 404:
                    return {"Error": {"Code": "NOT_FOUND", "Message": "Pedido não encontrado. Favor, verifique o número do pedido informado e tente novamente."}}

                deserialize_response = json.loads(request_call.text)

                return deserialize_response

            return wrapper

        except Exception as exc:
            print(f'\n❌ PRESTASHOP_API > __check_api_call() == EXCEPTION: {exc}\n')
            return None



    ## RECURSOS DA API ------

    @__check_api_call
    def get_api_resources(self) -> requests.Response | None:
        """ Obtem os recursos disponíveis da API. """

        try:
            path = f'{self.api_production_environment}?output_format=JSON'
            request_resource = requests.get(url=path, headers=self.__headers)
            return request_resource

        except Exception as exc:
            print(f'\n❌ PRESTASHOP_API > get_api_resources() ==> EXCEPTION IN REQUEST RESOURCE: {exc}\n')
            return None


    @__check_api_call
    def order_payments(self, payment_id:str) -> requests.Response | None:
        """ Recursos para buscar informações de pedidos pelo ID. """

        try:
            path = f'{self.api_production_environment}/order_payments/{payment_id}?output_format=JSON'
            request_resource = requests.get(url=path, headers=self.__headers)
            return request_resource

        except Exception as exc:
            print(f'\n❌ PRESTASHOP_API > __order_payments() ==> EXCEPTION IN REQUEST RESOURCE: {exc}\n')
            return None


    @__check_api_call
    def __order_id(self, order_number:str, shop_id:str) -> requests.Response | None:
        """ Recursos para buscar informações de pedidos pelo ID. """

        try:
            path = f'{self.api_production_environment}/orders/{order_number}?output_format=JSON&id_shop={shop_id}'
            request_resource = requests.get(url=path, headers=self.__headers)
            return request_resource

        except Exception as exc:
            print(f'\n❌ PRESTASHOP_API > __orders_id() ==> EXCEPTION IN REQUEST RESOURCE: {exc}\n')
            return None


    @__check_api_call
    def __customer_id(self, customer_id:str, shop_id:str) -> requests.Response | None:
        """ Recursos para buscar informações de cliente pelo ID. """

        try:
            path = f'{self.api_production_environment}/customers/{customer_id}?output_format=JSON&id_shop={shop_id}'
            request_resource = requests.get(url=path, headers=self.__headers)
            return request_resource

        except Exception as exc:
            print(f'\n❌ PRESTASHOP_API > __customers_id() ==> EXCEPTION IN REQUEST RESOURCE: {exc}\n')
            return None


    @__check_api_call
    def __address_id(self, address_id:str, shop_id:str) -> requests.Response | None:
        """ Recursos para buscar informações do endereço de envio pelo ID. """

        try:
            path = f'{self.api_production_environment}/addresses/{address_id}?output_format=JSON&id_shop={shop_id}'
            request_resource = requests.get(url=path, headers=self.__headers)
            return request_resource

        except Exception as exc:
            print(f'\n❌ PRESTASHOP_API > __addresses_id() ==> EXCEPTION IN REQUEST RESOURCE: {exc}\n')
            return None


    @__check_api_call
    def __state_id(self, state_id:str, shop_id:str) -> requests.Response | None:
        """ Recursos para buscar informações do estado (UF) do endereço de envio pelo ID. """

        try:
            path = f'{self.api_production_environment}/states/{state_id}?output_format=JSON&id_shop={shop_id}'
            request_resource = requests.get(url=path, headers=self.__headers)
            return request_resource

        except Exception as exc:
            print(f'\n❌ PRESTASHOP_API > __state_id() ==> EXCEPTION IN REQUEST RESOURCE: {exc}\n')
            return None


    @__check_api_call
    def __carrier_id(self, carrier_id:str, shop_id:str) -> requests.Response | None:
        """ Recursos para buscar informações do modo (transportadora) de envio pelo ID. """

        try:
            path = f'{self.api_production_environment}/carriers/{carrier_id}?output_format=JSON&id_shop={shop_id}'
            request_resource = requests.get(url=path, headers=self.__headers)
            return request_resource

        except Exception as exc:
            print(f'\n❌ PRESTASHOP_API > __carrier_id() ==> EXCEPTION IN REQUEST RESOURCE: {exc}\n')
            return None


    @__check_api_call
    def __product_id(self, product_id:str, shop_id:str) -> requests.Response | None:
        """ Recursos para buscar informações do produto pelo ID. """

        try:
            path = f'{self.api_production_environment}/products/{product_id}?output_format=JSON&id_shop={shop_id}'
            request_resource = requests.get(url=path, headers=self.__headers)
            return request_resource

        except Exception as exc:
            print(f'\n❌ PRESTASHOP_API > __product_id() ==> EXCEPTION IN REQUEST RESOURCE: {exc}\n')
            return None


    @__check_api_call
    def __combination_id(self, combination_id:str, shop_id:str) -> requests.Response | None:
        """ Recursos para buscar informações de variação do produto pelo ID. """

        try:
            path = f'{self.api_production_environment}/combinations/{combination_id}?output_format=JSON&id_shop={shop_id}'
            request_resource = requests.get(url=path, headers=self.__headers)
            return request_resource

        except Exception as exc:
            print(f'\n❌ PRESTASHOP_API > __combination_id() ==> EXCEPTION IN REQUEST RESOURCE: {exc}\n')
            return None


    @__check_api_call
    def __customization_id(self, customization_id:str, shop_id:str) -> requests.Response | None:
        """ Recursos para buscar informações de personalização produto pelo ID. """

        try:
            path = f'{self.api_production_environment}/customizations/{customization_id}?output_format=JSON&id_shop={shop_id}'
            request_resource = requests.get(url=path, headers=self.__headers)
            return request_resource

        except Exception as exc:
            print(f'\n❌ PRESTASHOP_API > __customization() ==> EXCEPTION IN REQUEST RESOURCE: {exc}\n')
            return None


    @__check_api_call
    def __module_dynamic_input(self, customization_value:str, shop_id:str) -> requests.Response | None:
        """ Recursos para buscar informações de personalização do produto gerado pelo módulo Dynamic Product. """

        try:
            path = f'{self.api_production_environment}/dynamic_inputs/{customization_value}?output_format=JSON&id_shop={shop_id}'
            request_resource = requests.get(url=path, headers=self.__headers)
            return request_resource

        except Exception as exc:
            print(f'\n❌ PRESTASHOP_API > __module_dynamic_input() ==> EXCEPTION IN REQUEST RESOURCE: {exc}\n')
            return None

    ## ------



    ## MÉTODOS DO SISTEMA ------

    def order_pattern(self, order_number:str, shop_id:str) -> dict:
        """ Padroniza as informações do pedido para importação no sistema. """

        try:
            set_order = self.__order_id(order_number, shop_id)

            if set_order["order"]["id_shop"] != shop_id:
                return {"Error": {"Code": "NOT_FOUND_IN_SHOP", "Message": "Pedido não encontrado na loja selecionada, verfique e tente novamente."}}

            set_customer = self.__customer_id(set_order["order"]["id_customer"], shop_id)
            set_address = self.__address_id(set_order["order"]["id_address_delivery"], shop_id)
            set_state_address = self.__state_id(set_address["address"]["id_state"], shop_id)

            payload_fsystem = {
                "orderDate": datetime.fromisoformat(set_order["order"]["date_add"]),
                "orderNumber": set_order["order"]["id"],
                "orderReference": set_order["order"]["reference"],
                "orderChannel": "E-commerce Fadrix",
                "orderChannelID": "ecommerce",
                "orderCompany": "",
                "customer": f'{set_customer["customer"]["firstname"]} {set_customer["customer"]["lastname"]}'.title(),
                "customerID": set_order["order"]["id_customer"],
                "customerNickname": None,
                "customerPhone": None,
                "order_customerEmail": None,
                "shippingAddress": {

                    "enderecoCompleto": f'{set_address["address"]["address1"]}, n {set_address["address"]["number"]}, {set_address["address"]["other"]}, {set_address["address"]["address2"]}, {set_address["address"]["city"]}, {set_state_address["state"]["name"]}, {set_address["address"]["postcode"]}',

                    "endereco": set_address["address"]["address1"],

                    "numero": set_address["address"]["number"],

                    "complemento": set_address["address"]["other"],

                    "bairro": set_address["address"]["address2"],

                    "cidade": set_address["address"]["city"],

                    "uf": set_state_address["state"]["name"],

                    "cep": set_address["address"]["postcode"],

                    "destinatario": "",
                },
                "shippingMethod": set_order["order"]["id_carrier"],
                "shippingDate": None,
                "original_shippingDate": None,
                "shippingTracking": "",
                "Products": [
                    {
                        "id": product["product_id"],

                        "produto": product["product_name"],

                        "sku": product["product_reference"],

                        "qtd": product["product_quantity"],

                        "icon": self.__image_product_pattern(shop_id=set_order["order"]["id_shop"], product_id=product["product_id"], combination_id=product["product_attribute_id"]) if product["product_attribute_id"] != "0" else self.__image_product_pattern(shop_id=set_order["order"]["id_shop"], product_id=product["product_id"]),

                        "personalizacao": self.__customization_product_pattern(shop_id=set_order["order"]["id_shop"], customization_id=product["id_customization"]) if product["id_customization"] not in [0,"0",None] else None
                    }
                    for product in set_order["order"]["associations"]["order_rows"]
                ],
            }

            return payload_fsystem


        except Exception as exc:
            print(f'\n❌ PRESTASHOP_API > order_pattern() ==> EXCEPTION: {exc}\n')
            return None


    def __image_product_pattern(self, shop_id:str, product_id:str, combination_id:str=None) -> str:
        """ Padroniza a busca de imagem do produto para importação no sistema. """

        try:
            set_product = self.__product_id(product_id, shop_id)
            image_product = set_product["product"]["id_default_image"]

            if combination_id != None:
                set_combination = self.__combination_id(combination_id, shop_id)
                image_product = set_combination["combination"]["associations"]["images"][0]["id"] if "images" in set_combination["combination"]["associations"] else set_product["product"]["id_default_image"]

            return f'https://fadrix.com.br/{image_product}-large_default/{set_product["product"]["link_rewrite"]}.jpg' if shop_id == "1" else f'https://revenda.fadrix.com.br/{image_product}-large_default/{set_product["product"]["link_rewrite"]}.jpg'

        except Exception as exc:
            print(f'\n❌ PRESTASHOP_API > __image_product_pattern() ==> EXCEPTION: {exc}\n')
            return None


    def __customization_product_pattern(self, shop_id:str, customization_id:str) -> str | None:
        """ Padroniza a busca de personalização do produto para importação no sistema. """

        try:
            set_customization = self.__customization_id(customization_id, shop_id)
            set_customization_value = set_customization["customization"]["associations"]["customized_data_text_fields"][0]["value"]

            if set_customization_value == None:
                return None

            set_dynamic_input = self.__module_dynamic_input(customization_value=set_customization_value, shop_id=shop_id)

            dynamic_value = set_dynamic_input["dynamic_input"]["associations"]["dynamic_input_fields"]
            dynamic_customization = ""
            for input in dynamic_value:
                dynamic_customization += f'{input["label"]}: {input["display_value"]} '

            return dynamic_customization

        except Exception as exc:
            print(f'\n❌ PRESTASHOP_API > __customization_product_pattern() ==> EXCEPTION: {exc}\n')
            return None


    def create_order_in_magis5(self, order_number:str, shop_id:str):
        """ Padroniza as informações para criar o pedido no Magis5. """

        try:
            set_order = self.__order_id(order_number, shop_id)

            if set_order["order"]["id_shop"] != shop_id:
                return {"Error": {"Code": "NOT_FOUND_IN_SHOP", "Message": "Pedido não encontrado na loja selecionada, verfique e tente novamente."}}

            set_customer = self.__customer_id(set_order["order"]["id_customer"], shop_id)
            set_address = self.__address_id(set_order["order"]["id_address_delivery"], shop_id)
            set_state_address = self.__state_id(set_address["address"]["id_state"], shop_id)

            set_shipping = {
                '55':{"mode":"custom", "type":"SEDEX", "logistic":"34028316347219", "logistic_type":"self_service", "status":"approved", "status_payments":"approved"}, #SEDEX
                '56':{"mode":"custom", "type":"PAC", "logistic":"34028316347219", "logistic_type":"self_service", "status":"approved", "status_payments":"approved"}, #PAC
                '57':{"mode":"Pickup", "type":"retirada a combinar", "logistic":"30010432000144", "logistic_type":None, "status":"awaiting_payment", "status_payments":"approved"}, #JADLOG
                '60':{"mode":"Pickup", "type":"retirada a combinar", "logistic":"30010432000144", "logistic_type":None, "status":"awaiting_payment", "status_payments":"approved"} #RETIRADA
                # '60':{"mode":"custom", "type":"PAC", "logistic":"34028316347219", "logistic_type":"self_service", "status":"approved", "status_payments":"approved"}, #TESTE
            }

            match set_order["order"]["payment"]:
                case "PIX - PagBank" | "Pix - PagBank":
                    set_payment_method = 'pix'
                case "Pagamento em dinheiro na retirada":
                    set_payment_method = 'account_money'
                case "Boleto Bancário - PagBank":
                    set_payment_method = 'bolbradeco'
                case _:
                    if 'VISA' in set_order["order"]["payment"] or 'MASTERCARD' in set_order["order"]["payment"]:
                        set_payment_method = 'credit_card'
                    else:
                        set_payment_method = 'UNKNOWN'

            def set_itens() -> list:
                """ Padroniza os produtos (informações e quantidades) da Prestashop P/ padrão de importarção no Magis5 HUB. """

                get_itens_in_prestashop = set_order["order"]["associations"]["order_rows"]
                list_new_organized_itens = dict()
                list_itens_for_magis5 = list()
                set_check_skus = set()

                for product in get_itens_in_prestashop:

                    product["product_quantity"] = Decimal(product["product_quantity"])
                    product["product_price"] = Decimal(product["product_price"])
                    product["total_product_price"] = Decimal(product["product_price"]) * Decimal(product["product_quantity"])

                    if product["product_reference"] in set_check_skus:
                        list_new_organized_itens[product["product_reference"]]["product_quantity"] += Decimal(product["product_quantity"])
                        list_new_organized_itens[product["product_reference"]]["product_price"] += Decimal(product["product_price"])
                        list_new_organized_itens[product["product_reference"]]["total_product_price"] += Decimal(product["total_product_price"])
                        continue

                    set_check_skus.add(product["product_reference"])
                    list_new_organized_itens[product["product_reference"]] = product

                for product in list_new_organized_itens.values():
                    list_itens_for_magis5.append(
                        {
                            "quantity": int(product["product_quantity"]),
                            "unit_price": self.__precise_calculation(value=product["total_product_price"], divisor=product["product_quantity"]),
                            "unitMeasurement": "UN",
                            "item": {
                                "seller_custom_field": product["product_reference"],
                                "id": product["product_id"],
                                "title": product["product_name"],
                                "defaultPicture": self.__image_product_pattern(shop_id=set_order["order"]["id_shop"], product_id=product["product_id"], combination_id=product["product_attribute_id"]) if product["product_attribute_id"] != "0" else self.__image_product_pattern(shop_id=set_order["order"]["id_shop"], product_id=product["product_id"])
                            }
                        }
                    )

                return list_itens_for_magis5

            payload_magis5 = {
                "id": f'{set_order["order"]["reference"]}',
                "dateCreated": str(datetime.strptime(set_order["order"]["date_add"], "%Y-%m-%d %H:%M:%S").astimezone(timezone("America/Sao_Paulo")).strftime("%Y-%m-%dT%H:%M:%S%z")[:-2]),
                #"packId": 0,
                #"expeditionBlock": None,
                #"totalTax": 0,
                "quantityPackage": 1,
                "status": set_shipping[set_order["order"]["id_carrier"]]["status"],
                #"subStatus": None,
                #"subStatusExpedition": None,
                #"externalIdInvoice": None,
                #"integrationType": None,
                "channel": "api-507bbb7da02946eba5861665d24957d6",
                "discount": float(set_order["order"]["total_discounts"]),
                #"fulfilled": False,
                "erpId": "artemis5-829f955afd94438ba475a61f61089923",
                #"expeditionLevel": "normal",
                #"dateDelivered": "string",
                #"dateExpedition": "string",
                "dateApproved": str(datetime.strptime(set_order["order"]["date_add"], "%Y-%m-%d %H:%M:%S").astimezone(timezone("America/Sao_Paulo")).strftime("%Y-%m-%dT%H:%M:%S%z")[:-2]),
                #"datePackingList": "string",
                "additionalNoteInvoice": "Loja Virtual Fadrix",
                "invoiceVolume": 1,
                #"saleFee": 0,
                #"queueStatus": "string",
                #"sellerCommissionId": "string",
                #"orderChannelType": "string",
                "buyer": {
                    "last_name": set_customer["customer"]["lastname"].title(),
                    "first_name": set_customer["customer"]["firstname"].title(),
                    #"email": "string",
                    "full_name": f'{set_customer["customer"]["firstname"]} {set_customer["customer"]["lastname"]}'.title(),
                    "billing_info": {
                        "doc_number": set_customer["customer"]["siret"],
                        #"ie": "string"
                    },
                    #"phone": { "number": "string" },
                    #"alternative_phone": { "number": "string" }
                },
                # "intermediary": {
                #     "salesDocument": None,
                #     "salesName": None,
                #     "paymentDocument": None,
                #     "paymentName": None
                # },
                # "tags": [{ "url": "string" }],
                "orderConciliation": {
                    "freight": float(set_order["order"]["total_shipping"]),
                    # "freightToPay": 0,
                    # "totalTax": 0,
                    "discount": float(set_order["order"]["total_discounts"]),
                    "totalValueWithFreight": float(set_order["order"]["total_products"]) + float(set_order["order"]["total_shipping"]),
                    "totalValueWithoutFreight": float(set_order["order"]["total_products"]),
                    # "totalCost": 0,
                    # "unitCost": 0,
                    # "unitValueItem": 0,
                    "totalValueItem": float(set_order["order"]["total_products"]),
                    # "percentageComission": 0,
                    # "comissionValue": 0,
                    # "totalNetWithoutCostProduct": 0,
                    "totalNet": float(set_order["order"]["total_products"]) - float(set_order["order"]["total_discounts"]),
                    # "percentageNetWithoutProduct": 0,
                    # "percentageNet": 0
                },
                "order_items": set_itens(),
                # "invoices": [],
                "payments": [
                    {
                        "status": set_shipping[set_order["order"]["id_carrier"]]["status_payments"],
                        "payment_type": set_payment_method,
                        "installments": 1,
                        "payment_method_id": set_payment_method,
                        "installment_amount": float(set_order["order"]["total_products"]) + float(set_order["order"]["total_shipping"]),
                        "shipping_cost": float(set_order["order"]["total_shipping"]),
                        "total_paid_amount": float(set_order["order"]["total_products"]) + float(set_order["order"]["total_shipping"]),
                        #"channel": "string",
                        #"digitable_line": "string",
                        #"url_slip": "string",
                        #"url_slip_pdf": "string",
                        "dueDate": str(datetime.strptime(set_order["order"]["date_add"], "%Y-%m-%d %H:%M:%S").astimezone(timezone("America/Sao_Paulo")).strftime("%Y-%m-%dT%H:%M:%S%z")[:-2]),
                        "payment_type_channel": set_payment_method,
                        #"installment_id": "string",
                        "payment_method_id_channel": set_payment_method
                    }
                ],
                "shipping": {
                    "created": str(datetime.strptime(set_order["order"]["date_add"], "%Y-%m-%d %H:%M:%S").astimezone(timezone("America/Sao_Paulo")).strftime("%Y-%m-%dT%H:%M:%S%z")[:-2]),
                    #"shipping_number": "string",
                    "shipping_mode": set_shipping[set_order["order"]["id_carrier"]]["mode"],
                    "shipment_type": set_shipping[set_order["order"]["id_carrier"]]["type"],
                    #"logistic_type": set_shipping[set_order["order"]["id_carrier"]]["logistic_type"],
                    #"logistic": {"logisticId": set_shipping[set_order["order"]["id_carrier"]]["logistic"]},
                    # "shipping_option": {
                    #     "list_cost": 0,
                    #     "cost": 0,
                    #     "comission": 0
                    # },
                    "receiver_address": {
                        "street_number": set_address["address"]["number"],
                        "zip_code": set_address["address"]["postcode"],
                        "street_name": set_address["address"]["address1"],
                        "comment": set_address["address"]["other"],
                        "neighborhood": {"name": set_address["address"]["address2"]},
                        "city": {"name": set_address["address"]["city"]},
                        "state": {"name": set_state_address["state"]["name"]}
                    }
                }
            }

            print(f'\n🐞 PRESTASHOP_API > PAYLOAD MAGIS5 ==> {payload_magis5}\n'.replace("'",'"'))

            MAGIS5HUB = Magis5()
            create_order = MAGIS5HUB.create_order(order_json=payload_magis5)

            if 'Error' in create_order:
                message_error = create_order['Error']['Message']

                if 'O(s) SKU(s):' in message_error and 'não foi(foram) encontrado(s)' in message_error:
                    padrao = r'SKU\(s\):\s*([\w\s,]+?)\s*não foi'
                    match = re.search(padrao, message_error, re.IGNORECASE)

                    if match:
                        # Quebra a string em lista, elimina espaços e remove duplicatas usando set
                        skus = sorted(set(sku.strip() for sku in match.group(1).split(',')))

                        for product in payload_magis5["order_items"]:
                            create_product = None

                            if product["item"]["seller_custom_field"] in skus:
                                get_product = self.__product_id(product_id=product["item"]["id"], shop_id=shop_id)

                                payload_product = {
                                "id": get_product["product"]["reference"],
                                "title": get_product["product"]["name"],
                                "externalId": get_product["product"]["id"],
                                "condition": "new",
                                #"stock": 0,
                                #"cost": 0,
                                "description": get_product["product"]["description_short"],
                                #"technicalSpecification": "string",
                                #"price": 0,
                                "warranty": "30",
                                "business": get_product["product"]["manufacturer_name"],
                                #"ean": get_product["product"]["ean13"],
                                #"eanInvoice": get_product["product"]["ean13"],
                                "height": get_product["product"]["height"],
                                "weight": get_product["product"]["weight"],
                                "weightGross": get_product["product"]["weight"],
                                "depth": get_product["product"]["depth"],
                                "width": get_product["product"]["width"],
                                "brand": get_product["product"]["manufacturer_name"],
                                #"model": "string",
                                #"ncm": "string",
                                #"anp": "string",
                                #"cest": "string",
                                #"origin": 0,
                                #"deadlineCrossdocking": 2,
                                #"youtubeId": "string",
                                #"location": "string",
                                #"isVariation": False,
                                #"warrantyProvider": "30",
                                #"quantityItemsSamePackaging": 1,
                                "erpId": "artemis5-829f955afd94438ba475a61f61089923",
                                #"stockFixed": 0,
                                #"operationalCost": 0,
                                #"percentageProfit": 0,
                                # "productsComposition": [
                                #     {
                                #     "id": "string",
                                #     "quantity": 0,
                                #     "unitValue": 0,
                                #     "percentagePriceValue": 0
                                #     }
                                # ],
                                # "productsCategory": [
                                #     {
                                #     "id": 0,
                                #     "name": "string",
                                #     "parentId": 0,
                                #     "categoryDescription": "string"
                                #     }
                                # ],
                                # "productsVariation": [
                                #     {
                                #     "sku": "string",
                                #     "attributes": [
                                #         {
                                #         "id": "string",
                                #         "value_name": "string",
                                #         "value_id": "string",
                                #         "allowed_units": [
                                #             {
                                #             "name": "string"
                                #             }
                                #         ],
                                #         "descriptionUnit": "string"
                                #         }
                                #     ],
                                #     "categoryId": "string"
                                #     }
                                # ],
                                # "productsCode": [
                                #     {
                                #     "code": "string"
                                #     }
                                # ],
                                # "productsRootCharacteristic": [
                                #     {
                                #     "id": 0,
                                #     "key": "string",
                                #     "status": "string"
                                #     }
                                # ],
                                # "categories": [
                                #     {
                                #     "id": "string"
                                #     }
                                # ],
                                "pictures": [
                                    {
                                    "url": product["item"]["defaultPicture"]
                                    }
                                ],
                                "plainTextDescription": get_product["product"]["description_short"]
                                }

                                create_product = MAGIS5HUB.create_product(product_json=payload_product)

                                if 'Error' in create_product:
                                    continue

                            MAGIS5HUB.create_order(order_json=payload_magis5)

                    else:
                        print("Nenhum SKU encontrado.")

            return

        except Exception as exc:
            print(f'\n❌ PRESTASHOP_API > create_order_in_magis5() ==> EXCEPTION: {exc}\n')
            return None


    def __precise_calculation(self, value:Decimal, divisor:Decimal) -> float:
        """ Faz o calculo decimal preciso da soma dos valores unitários dos produtos e a posterior divisão pela quantidade. """

        try:
            getcontext().prec = 28
            set_division = value / divisor
            set_multiplication = set_division * divisor

            result_division = set_division.quantize(Decimal('1.00'))
            result_multiplication = set_multiplication.quantize(Decimal('1.00'))

            print(f'\n🐞 PRESTASHOP_API > __precise_calculation() ==> RESULTS\n → ➡️ VALOR ORIGINAL: {value}\n → ➡️ DIVISOR: {divisor}\n → ✅ RESULTADO DIVISÃO: {result_division}\n → ✅ RESULTADO MULTIPLICAÇÃO: {result_multiplication}\n')

            if result_multiplication == value:
                print("🎯 Tudo certo! A prova real bateu perfeitamente.")
            else:
                print("⚠️ Atenção: pequena diferença na prova real.")

            return float(result_division)

        except Exception as exc:
            print(f'\n❌ PRESTASHOP_API > __precise_calculation() ==> EXCEPTION: {exc}\n')
            return None

    ## ------
