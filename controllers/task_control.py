import os, shutil, requests, qrcode
from pathlib import Path
from PIL import Image
from source.api.asanaApi import AsanaAPI
from controllers.image_control import ImageControl as IMAGE


class TaskControl:
    """ Controle de Criação de Tarefas no sistema de gestão ASANA """

    def __init__(self, app:str="Asana"):
        self.app_task = app


    def create(self, type_body:str, task_data:dict, partition:str=None) -> dict | None:
        """ Cria uma nova tarefa no app selecionado. """

        try:
            task_info_data = task_data

            tags_dict = task_info_data.get('tags', {})
            active_tag = next((tag for tag, is_active in tags_dict.items() if is_active), None)
            print(f'\n🐞 TASK_CONTROL > ORDER {task_info_data["info"]["number"]} WITH TAG: {active_tag}\n')

            match type_body:

                case "order":
                    name_task = f'{task_info_data["info"]["number"]} - {task_info_data["info"]["customer"]}' if partition == None else f'{task_info_data["info"]["number"]} - {task_info_data["info"]["customer"]} {partition}'

                    task_json_data = {
                        "data": {
                            "approval_status": "pending",
                            "due_on": str(task_info_data["completion_date"].date()),
                            "memberships": [self.__set_project(task_info_data["project"])],
                            "custom_fields": {
                                "1202887017424348": task_info_data["custom_fields"]["channel"], # CANAL DE VENDA
                                "1204585380463794": task_info_data["custom_fields"]["company"], # EMPRESA
                                "1202884793721450": task_info_data["custom_fields"]["attendant"], # ATENDENTE
                                "1202996802045806": task_info_data["custom_fields"]["shippingMethod"], # FORMA DE ENVIO
                            },
                            "name": name_task if active_tag == None else f'[{active_tag}] {name_task}',
                            "resource_type": "task",
                            "resource_subtype": "default_task",
                            "workspace": "1128098916536904"
                        }
                    }                    

                case "warranty":
                    name_task = f'GARANTIA #{task_info_data["info"]["number"]} - {task_info_data["info"]["customer"]}'

                    task_json_data = {
                        "data": {
                            "approval_status": "pending",
                            "due_on": str(task_info_data["completion_date"].date()),
                            "memberships": [self.__set_project(task_info_data["project"])],
                            "custom_fields": {
                                "1202887017424348": task_info_data["custom_fields"]["channel"], # CANAL DE VENDA
                                "1204585380463794": task_info_data["custom_fields"]["company"], # EMPRESA
                                "1202884793721450": task_info_data["custom_fields"]["attendant"], # ATENDENTE
                                "1202996802045806": task_info_data["custom_fields"]["shippingMethod"], # FORMA DE ENVIO
                                "1211627442120662": task_info_data["custom_fields"]["warranty_reason"]
                            },
                            "name": name_task if active_tag == None else f'[{active_tag}] {name_task}',
                            "resource_type": "task",
                            "resource_subtype": "task",
                            "workspace": "1128098916536904"
                        }
                    }

            ASANA_OBJ = AsanaAPI()
            create = ASANA_OBJ.create_a_task(data_object=task_json_data)

            generate_qrcode = self.__create_qrcode_image(order_number=task_info_data["info"]["number"])
            if generate_qrcode != None:
                upload_qrcode = ASANA_OBJ.upload_an_attachment(
                    task_gid = create["data"]["gid"],
                    file_path = Path(generate_qrcode)
                )
                IMAGE().clear_path(path=Path(generate_qrcode).parent)

            set_description = self.__pattern_body(type_body=type_body, task_data=task_data, qrcode_gid=upload_qrcode["data"]["gid"] if generate_qrcode != None else None)

            ASANA_OBJ.update_a_task(
                task_gid = create["data"]["gid"],
                data_object={"data":{"html_notes": set_description["body"]}}
            )

            for comment in task_info_data["comments"]:
                if comment["text"] != None and comment["text"] != "":
                    ASANA_OBJ.create_a_story_on_a_task(
                        task_gid = create["data"]["gid"],
                        text = comment["text"],
                        is_pinned = comment["pinned"]
                    )

            for attachment in set_description["attachments"]:
                ASANA_OBJ.upload_an_attachment(
                    task_gid = create["data"]["gid"],
                    file_path = Path(attachment["path"]),
                    is_img = attachment["is_img"]
                )

            IMAGE().clear_path(path=f"D:/FADRIX/DEVELOPER/FADRIX-SYS/V4/download/{task_info_data["info"]["number"]}")
            return create

        except Exception as exc:
            print(f'\n❌ TASK_CONTROL > create() ==> EXCEPTION: {exc}\n')
            return None


    def __pattern_body(self, type_body:str, task_data:dict, qrcode_gid:str):
        """ Padroniza o conteúdo da descrição (body) das tarefas. """

        try:
            task_info_data = task_data
            match type_body:

                case "order":
                    order_number = f'<h1>PEDIDO #{task_info_data["info"]["number"]}</h1>'
                    order_customer = f'De <strong>{task_info_data["info"]["customer"]}</strong>'
                    order_date = task_info_data["info"]["date"]
                    order_sales_channel = f'🛒 <strong>CANAL DE VENDA:</strong> {task_info_data["info"]["channel"]}'
                    order_company = f'💼 <strong>EMPRESA:</strong> {task_info_data["info"]["company"]}'
                    order_shipping_method = f'🚚 <strong>FORMA DE ENVIO:</strong> {task_info_data["info"]["shippingMethod"]}'
                    order_shipping_date = f'📅 <strong>DATA DE ENVIO:</strong> {task_info_data["completion_date"].strftime('%d/%m/%Y %H:%M:%S')}'
                    # order_attendant = f'📞 <strong>ATENDIMENTO:</strong> {task_info_data["info"]["attendant"]}'
                    # order_shipping_address = f'🏠 <strong>ENDEREÇO DE ENVIO:</strong>\n→ {task_info_data["info"]["address"]}'
                    order_qrcode = f'<img data-asana-gid="{qrcode_gid}" style="width:20px">' if qrcode_gid != None else " --- FAILED TO GENERATE QRCODE --- "

                    product_table_lines = list()
                    product_table_lines.append("<tr><td><strong>PRODUTO</strong>\n</td><td><strong>QTD\n</strong></td><td><strong>ARTE\n</strong></td></tr>")

                    for product in task_info_data["info"]["products"]:
                        product_table_lines.append(f'<tr><td>{product["produto"]} | <em>{product["sku"]}</em></td><td>{product["qtd"]} UNID</td><td>{product["personalizacao"]}</td></tr>')

                        self.__download_product_attachments(
                            order_number =task_info_data["info"]["number"],
                            product_sku = product["sku"],
                            product_img = product["icon"]
                        )

                    body_description = f'<body>{order_number}{order_customer}, em {order_date}\n\n{order_sales_channel}\n{order_company}\n{order_shipping_method}\n{order_shipping_date}\n\n{order_qrcode}<table>{'\n'.join(product_table_lines)}</table></body>'

                    set_attachments = [{"path": self.__create_preview_image(order_number=task_info_data["info"]["number"]), "is_img":True}]

                case "warranty":
                    warranty_number = f'<h1>GARANTIA #{task_info_data["info"]["number"]}</h1>'
                    warranty_customer = f'Para <strong>{task_info_data["info"]["customer"]}</strong>'
                    warranty_date = task_info_data["info"]["date"]
                    warranty_sales_channel = f'🛒 <strong>CANAL DE VENDA:</strong> {task_info_data["info"]["channel"]}'
                    warranty_company = f'💼 <strong>EMPRESA:</strong> {task_info_data["info"]["company"]}'
                    warranty_shipping_method = f'🚚 <strong>FORMA DE ENVIO:</strong> {task_info_data["info"]["shippingMethod"]}'
                    warranty_shipping_date = f'📅 <strong>DATA DE ENVIO:</strong> {task_info_data["completion_date"].strftime('%d/%m/%Y %H:%M:%S')}'
                    # warranty_attendant = f'📞 <strong>ATENDIMENTO:</strong> {task_info_data["info"]["attendant"]}'
                    warranty_shipping_address = f'🏠 <strong>ENDEREÇO PARA ENVIO:</strong>\n→ {task_info_data["info"]["address"]}'
                    warranty_reason = f'📋 <strong>MOTIVO DA GARANTIA:</strong>\n→ {task_info_data["warranty_reason"]}'
                    warranty_notes = f'💬 <strong>NOTA DE OBSERVAÇÃO:</strong>\n→ {task_info_data["warranty_notes"]}'
                    warranty_qrcode = f'<img data-asana-gid="{qrcode_gid}" style="width:20px">' if qrcode_gid != None else " --- FAILED TO GENERATE QRCODE --- "

                    product_table_lines = list()
                    product_table_lines.append("<tr><td><strong>PRODUTO</strong>\n</td><td><strong>OBSERVAÇÃO\n</strong></td><td><strong>QTD\n</strong></td></tr>")

                    for product in task_info_data["info"]["products"]:
                        product_table_lines.append(f'<tr><td>{product["produto"]} | <em>{product["sku"]}</em></td><td>{product["personalizacao"]}</td><td>{product["qtd"]} UNID</td></tr>')

                        self.__download_product_attachments(
                            order_number =task_info_data["info"]["number"],
                            product_sku = product["sku"],
                            product_img = product["icon"]
                        )

                    body_description = f'<body>{warranty_number}{warranty_customer}, feita em {warranty_date}\n\n{warranty_sales_channel}\n{warranty_company}\n{warranty_shipping_method}\n{warranty_shipping_date}\n\n{warranty_qrcode}\n\n{warranty_reason}\n\n{warranty_notes}\n\n{warranty_shipping_address}\n<table>{'\n'.join(product_table_lines)}</table></body>'

                    set_attachments = list()

                    for image in task_info_data["warranty_images"]:
                        set_attachments.append({"path": image, "is_img":True})

                    set_attachments.append({"path": self.__create_preview_image(order_number=task_info_data["info"]["number"]), "is_img":True})

            return {"body":body_description, "attachments":set_attachments}

        except Exception as exc:
            print(f'\n❌ TASK_CONTROL > __pattern_body() ==> EXCEPTION: {exc}\n')
            return None


    def __download_product_attachments(self, order_number:str, product_sku:str, product_img:str):
        """ Faz o download das imagens dos produtos. """

        try:
            download_directory = Path(f"D:/FADRIX/DEVELOPER/FADRIX-SYS/V4/download/{order_number}".strip())
            if not download_directory.exists():
                os.mkdir(download_directory)

            if 'assets\\attachment\\warranty' in product_img:
                shutil.copy2(src=product_img, dst=download_directory)

            else:
                download_image = Image.open(requests.get(url=product_img, stream=True).raw)
                download_image.save(f'{download_directory}/{product_sku}.jpg')

        except Exception as exc:
            print(f'\n❌ TASK_CONTROL > __download_product_attachments() ==> EXCEPTION: {exc}\n')
            self.__get_default_image(order_number)
            return None


    def __get_default_image(self, order_number:str) -> str:
        """ Pega a imagem de produto padrão do sistema quando o produto não tem imagem ou em caso de erro. """

        try:
            download_directory = Path(f"D:/FADRIX/DEVELOPER/FADRIX-SYS/V4/download/{order_number}".strip())
            if not download_directory.exists():
                os.mkdir(download_directory)

            else:
                shutil.copy(src="D:/FADRIX/DEVELOPER/FADRIX-SYS/V4/assets/images/system/nopreview.png", dst=download_directory)

            return f'{download_directory}/nopreview.png'

        except Exception as exc:
            print(f'\n❌ TASK_CONTROL > __get_default_image() ==> EXCEPTION: {exc}\n')
            return None


    def __create_preview_image(self, order_number:str) -> str:
        """ Cria a imagem padrão de preview para a upload na tarefa no Asana. """

        try:
            directory_name = Path(f"D:/FADRIX/DEVELOPER/FADRIX-SYS/V4/download/{order_number}".strip())
            preview = IMAGE().new_image(path=directory_name)
            return f'{directory_name}/{preview}'

        except Exception as exc:
            print(f'\n❌ TASK_CONTROL > __create_preview_image() ==> EXCEPTION: {exc}\n')
            return self.__get_default_image(order_number)


    def __create_qrcode_image(self, order_number:str) -> str | None:
        """ Cria uma imagem com qrcode do número do pedido. """

        try:
            qrcode_data = order_number
            qrcode_obj = qrcode.QRCode(version=1, box_size=5, border=4)
            qrcode_obj.add_data(qrcode_data)
            qrcode_obj.make(fit=True)

            download_directory = Path(f"D:/FADRIX/DEVELOPER/FADRIX-SYS/V4/download/{order_number}".strip())
            if not download_directory.exists():
                os.mkdir(download_directory)

            save_path = f'{download_directory}/QRCODE_{qrcode_data}.png'.replace("\\", "/")
            qrcode_img = qrcode_obj.make_image(fill="black", back_color="white")
            qrcode_img.save(stream=save_path)
            return save_path

        except Exception as exc:
            print(f'\n❌ TASK_CONTROL > __create_qrcode() ==> EXCEPTION: {exc}\n')
            return None


    def __set_project(self, project_name:str) -> dict:
        """ Define e retorna os IDs do projeto e sessão de acordo como o nome do projeto informado. """

        try:
            set_project_name = project_name
            match set_project_name:

                case "arte_final":
                    return {"project": "1202199922998942", "section": "1202199922998943"}

                case "controle_estoque":
                    return {"project": None, "section": None}

                case "conferencia":
                    return {"project": None, "section": None}

                case "expedicao":
                    return {"project": None, "section": None}

                case "teste_sistema":
                    return {"project": "1202829879736233", "section": "1202829879736234"}

        except Exception as exc:
            print(f'\n❌ TASK_CONTROL > __set_project() ==> EXCEPTION: {exc}\n')
            return None
