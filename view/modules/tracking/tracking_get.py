from datetime import datetime

#ACESSO A APIS:
from source.api.shopeeApi import Shopee as SHOPEE_API


class TrackingGet:

    def __init__(self, gateway:str, company:str=None, order_number:str=None, track_number:str=None) -> None:

        self.gateway = gateway
        self.company = company
        self.order_number = order_number
        self.track_number = track_number


    def get_tracking_data(self) -> dict | None:
        """Obtem os dados do rastreamento direto no gateway definido."""

        try:
            tracking_data = dict()
            tracking_events = list()

            # print(f'\n🐞 ##DEBUG >> TRANCKING_GET > get_tracking_data() == GATEWAY: {self.gateway} | {self.company}\n') ##DEBUG

            match self.gateway:

                case "correios":
                    pass

                case "shopee":
                    shopee_api = SHOPEE_API(self.company)
                    get_tracking = shopee_api.get_tracking_info(self.order_number)
                    get_tracking_number = shopee_api.get_tracking_number(self.order_number)
                    get_tracking_number = get_tracking_number["response"]["tracking_number"]
                    print(f'\n🐞 ##DEBUG >> TRANCKING_GET > get_tracking_data() == get_tracking: {get_tracking} | {type(get_tracking)}\n') ##DEBUG

                    translate_status = {
                        'LOGISTICS_READY': "AGUARDANDO ENVIO",
                        'LOGISTICS_REQUEST_CREATED': "SOLICITAÇÃO DE ENVIO CRIADA",
                        'LOGISTICS_DELIVERY_DONE': "ENTREGA REALIZADA",
                        'LOGISTICS_DELIVERY_FAILED': "FALHA NA ENTREGA",
                        'LOGISTICS_PICKUP_DONE': "ENVIO REALIZADO",
                        'ORDER_CREATED': "PREPARANDO ENVIO",
                        'PICKED_UP': "ENVIADO",
                        'DELIVERED': "ENTREGUE",
                        'RETURN_STARTED': "COMEÇANDO RETORNO",
                        'RETURN_INITIATED': "RETORNO INCIADO",
                        'RETURNED': "DEVOLVIDO",
                        'LOST': "PERDIDO OU DANIFICADO",
                        'FAILED_DELIVERED': "FALHA NA ENTREGA AO VENDEDOR"
                    }

                    for track in get_tracking["response"]["tracking_info"]:
                        logistics_status_event = translate_status[track["logistics_status"]] if track["logistics_status"] in translate_status else track["logistics_status"]
                        tracking_events.append(
                            {
                                "update_time": datetime.fromtimestamp(track["update_time"]).strftime('%d/%m/%Y\n%H:%M:%S'),
                                "description": track["description"],
                                "subdescription": logistics_status_event,
                                "add_description": None
                            }
                        )

                    logistics_status = translate_status[get_tracking["response"]["logistics_status"]] if get_tracking["response"]["logistics_status"] in translate_status else get_tracking["response"]["logistics_status"]

                    tracking_data = {
                        "tracking_gateway": self.gateway,
                        "tracking_number": get_tracking_number if get_tracking_number != None and get_tracking_number != "" else get_tracking["response"]["order_sn"],
                        "logistics_type": "Shopee Express",
                        "logistics_status": logistics_status,
                        "expected_date": "Não informado",
                        "package_info": {
                            "pack_width": None,
                            "pack_height": None,
                            "pack_length": None,
                            "pack_weight": None,
                            "pack_shape": None
                        },
                        "tracking_events": tracking_events
                    }

            return tracking_data


        except Exception as exc:
            print(f'\n❌ TRACKING_GET > get_tracking_data() == EXCEPTION: {exc}\n')
            return None
