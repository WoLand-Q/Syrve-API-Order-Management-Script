import requests
import json
import uuid
import pprint
import logging
from datetime import datetime
from dotenv import load_dotenv
import os

# Загрузка переменных окружения из .env файла
load_dotenv()
API_LOGIN = os.getenv('API_LOGIN')

# Настройка логирования
logging.basicConfig(filename='script_create_order.log', level=logging.INFO,
                    format='%(asctime)s %(levelname)s %(message)s')


def get_access_token(api_login: str) -> str:
    """
    Получение токена доступа.
    """
    url = "https://api-eu.syrve.live/api/1/access_token"
    headers = {"Content-Type": "application/json"}
    payload = {"apiLogin": api_login}

    try:
        response = requests.post(url, headers=headers, json=payload)
        response.raise_for_status()
        data = response.json()
        token = data.get('token')
        if not token:
            logging.error("Не удалось получить токен из ответа.")
            print("Не удалось получить токен из ответа.")
            return None
        logging.info(f"Получен токен доступа: {token}")
        print(f"Получен токен доступа: {token}")
        return token
    except requests.HTTPError as http_err:
        logging.error(f"HTTP ошибка: {http_err} - Ответ: {response.text}")
        print(f"HTTP ошибка: {http_err} - Ответ: {response.text}")
    except Exception as err:
        logging.error(f"Произошла ошибка: {err}")
        print(f"Произошла ошибка: {err}")
    return None


def get_organizations(token: str) -> list:
    """
    Получение списка организаций.
    """
    url = "https://api-eu.syrve.live/api/1/organizations"
    headers = {"Authorization": f"Bearer {token}"}

    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        data = response.json()
        organizations = data.get('organizations', [])
        logging.info(f"Получено организаций: {len(organizations)}")
        return organizations
    except requests.HTTPError as http_err:
        logging.error(f"HTTP ошибка при получении организаций: {http_err} - Ответ: {response.text}")
        print(f"HTTP ошибка при получении организаций: {http_err} - Ответ: {response.text}")
    except Exception as err:
        logging.error(f"Произошла ошибка при получении организаций: {err}")
        print(f"Произошла ошибка при получении организаций: {err}")
    return []


def get_terminal_groups(token: str, organization_ids: list) -> list:
    """
    Получение терминальных групп для заданных организаций.
    """
    url = "https://api-eu.syrve.live/api/1/terminal_groups"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    payload = {
        "organizationIds": organization_ids,
        "includeDisabled": True,
        "returnExternalData": ["string"]
    }

    try:
        response = requests.post(url, headers=headers, json=payload)
        response.raise_for_status()
        data = response.json()
        # терминальные группы могут возвращаться в двух полях:
        # 'terminalGroups' и 'terminalGroupsInSleep'
        terminal_groups_data = data.get('terminalGroups', []) + data.get('terminalGroupsInSleep', [])
        terminal_groups = []
        for group_block in terminal_groups_data:
            items = group_block.get('items', [])
            organization_id = group_block.get('organizationId')
            for item in items:
                tg_id = item.get('id')
                tg_name = item.get('name', 'NoName')
                if tg_id:
                    terminal_groups.append({
                        'id': tg_id,
                        'name': tg_name,
                        'organizationId': organization_id
                    })
        logging.info(f"Получено терминальных групп: {len(terminal_groups)}")
        return terminal_groups
    except requests.HTTPError as http_err:
        logging.error(f"HTTP ошибка при получении терминальных групп: {http_err} - Ответ: {response.text}")
        print(f"HTTP ошибка при получении терминальных групп: {http_err} - Ответ: {response.text}")
    except Exception as err:
        logging.error(f"Произошла ошибка при получении терминальных групп: {err}")
        print(f"Произошла ошибка при получении терминальных групп: {err}")
    return []


def get_available_restaurant_sections(token: str, terminal_group_ids: list, return_schema=False, revision=0) -> list:
    """
    Получение доступных секций ресторанов (таблиц) для выбранных групп терминалов.
    """
    url = "https://api-eu.syrve.live/api/1/reserve/available_restaurant_sections"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    payload = {
        "terminalGroupIds": terminal_group_ids,
        "returnSchema": return_schema,
        "revision": revision
    }

    try:
        response = requests.post(url, headers=headers, json=payload, timeout=10)
        response.raise_for_status()
        data = response.json()
        restaurant_sections = data.get('restaurantSections', [])
        logging.info(f"Получено секций ресторанов: {len(restaurant_sections)}")
        return restaurant_sections
    except requests.HTTPError as http_err:
        logging.error(f"HTTP ошибка при получении секций ресторанов: {http_err} - Ответ: {response.text}")
        print(f"HTTP ошибка при получении секций ресторанов: {http_err} - Ответ: {response.text}")
    except Exception as err:
        logging.error(f"Произошла ошибка при получении секций ресторанов: {err}")
        print(f"Произошла ошибка при получении секций ресторанов: {err}")
    return []


def get_payment_types(token: str, organization_ids: list) -> list:
    """
    Получение списка типов оплат для указанных организаций.
    """
    url = "https://api-eu.syrve.live/api/1/payment_types"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    payload = {
        "organizationIds": organization_ids
    }

    try:
        response = requests.post(url, headers=headers, json=payload, timeout=10)
        response.raise_for_status()
        data = response.json()
        payment_types = data.get('paymentTypes', [])
        logging.info(f"Получено типов оплаты: {len(payment_types)}")
        return payment_types
    except requests.HTTPError as http_err:
        logging.error(f"HTTP ошибка при получении типов оплаты: {http_err} - Ответ: {response.text}")
        print(f"HTTP ошибка при получении типов оплаты: {http_err} - Ответ: {response.text}")
    except Exception as err:
        logging.error(f"Произошла ошибка при получении типов оплаты: {err}")
        print(f"Произошла ошибка при получении типов оплаты: {err}")
    return []


def create_order(token: str, organization_id: str, terminal_group_id: str, table_id: str,
                 customer_name: str, customer_phone: str,
                 product_id: str, product_price: float, product_quantity: float,
                 payment_type_id: str, payment_sum: float) -> dict:
    """
    Создание заказа на выбранную организацию, терминальную группу, стол.
    С минимальным набором полей.
    """
    url = "https://api-eu.syrve.live/api/1/order/create"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }

    # Вы можете генерировать positionId, id заказа и т.п. (GUID) заранее
    order_id = str(uuid.uuid4())
    position_id = str(uuid.uuid4())

    payload = {
        "organizationId": organization_id,
        "terminalGroupId": terminal_group_id,
        "order": {
            # Можем задать наш сгенерированный ID (не обязательно)
            "id": order_id,

            # Таблица, на которую создаётся заказ
            "tableIds": [table_id],

            # Информация о клиенте (минимум: имя, type)
            "customer": {
                "name": customer_name,
                "type": "regular"
            },
            # Можно дополнительно передать телефон в "phone" на верхнем уровне заказа
            "phone": customer_phone,

            # Список позиций (минимум: productId, type=Product, price, amount)
            "items": [
                {
                    "positionId": position_id,
                    "productId": product_id,
                    "type": "Product",
                    "price": product_price,
                    "amount": product_quantity
                }
            ],
            # Платёж (в примере — единственный)
            "payments": [
                {
                    "paymentTypeKind": "Cash",   # или другое значение, если в списке другая логика
                    "sum": payment_sum,
                    "paymentTypeId": payment_type_id,
                    "isProcessedExternally": False,
                    "isFiscalizedExternally": False,
                    "isPrepay": False
                }
            ]
        },
        # Доп. настройки создания заказа (можно убрать/добавить)
        "createOrderSettings": {
            "servicePrint": False,
            "transportToFrontTimeout": 15,
            "checkStopList": False
        }
    }

    try:
        response = requests.post(url, headers=headers, json=payload, timeout=15)
        response.raise_for_status()
        data = response.json()
        logging.info(f"Заказ создан успешно. Ответ: {data}")
        print("\n--- Ответ сервера при создании заказа ---")
        pprint.pprint(data)
        return data
    except requests.HTTPError as http_err:
        logging.error(f"HTTP ошибка при создании заказа: {http_err} - Ответ: {response.text}")
        print(f"HTTP ошибка при создании заказа: {http_err} - Ответ: {response.text}")
    except Exception as err:
        logging.error(f"Произошла ошибка при создании заказа: {err}")
        print(f"Произошла ошибка при создании заказа: {err}")

    return {}


def main():
    # 1) Получаем токен
    token = get_access_token(API_LOGIN)
    if not token:
        print("Не удалось получить токен доступа.")
        return

    # 2) Получаем список организаций
    organizations = get_organizations(token)
    if not organizations:
        print("Не удалось получить список организаций.")
        return

    print("\nСписок доступных организаций:")
    for idx, org in enumerate(organizations, 1):
        print(f"{idx}. {org.get('name')} (ID: {org.get('id')})")

    # Пользователь выбирает организацию
    org_index = input("\nВведите номер организации: ")
    try:
        org_index = int(org_index)
        if org_index < 1 or org_index > len(organizations):
            print("Некорректный номер организации.")
            return
    except ValueError:
        print("Пожалуйста, введите целое число.")
        return

    organization_id = organizations[org_index - 1].get('id')

    # 3) Получаем терминальные группы для выбранной организации
    terminal_groups = get_terminal_groups(token, [organization_id])
    if not terminal_groups:
        print("Не удалось получить терминальные группы.")
        return

    print("\nДоступные терминальные группы:")
    for idx, tg in enumerate(terminal_groups, 1):
        print(f"{idx}. {tg.get('name')} (ID: {tg.get('id')})")

    # Пользователь выбирает терминальную группу
    tg_index = input("\nВведите номер терминальной группы: ")
    try:
        tg_index = int(tg_index)
        if tg_index < 1 or tg_index > len(terminal_groups):
            print("Некорректный номер терминальной группы.")
            return
    except ValueError:
        print("Пожалуйста, введите целое число.")
        return

    terminal_group_id = terminal_groups[tg_index - 1].get('id')

    # 4) Получаем доступные столы для выбранной терминальной группы
    sections = get_available_restaurant_sections(token, [terminal_group_id])
    if not sections:
        print("Не удалось получить секции ресторанов.")
        return

    table_dict = {}
    counter = 1
    print("\nДоступные столы:")
    for section in sections:
        section_name = section.get('name', 'NoSectionName')
        tables = section.get('tables', [])
        print(f"\n--- Секция: {section_name} ---")
        for tbl in tables:
            table_id = tbl.get('id')
            table_name = tbl.get('name')
            print(f"{counter}. {table_name} (ID: {table_id})")
            table_dict[counter] = table_id
            counter += 1

    if not table_dict:
        print("Нет доступных столов.")
        return

    table_index = input("\nВведите номер стола: ")
    try:
        table_index = int(table_index)
        if table_index < 1 or table_index > len(table_dict):
            print("Некорректный номер стола.")
            return
    except ValueError:
        print("Пожалуйста, введите целое число.")
        return

    table_id = table_dict[table_index]

    # 5) Получаем список типов оплат (опционально)
    payment_types = get_payment_types(token, [organization_id])
    if payment_types:
        print("\nДоступные типы оплат:")
        for idx, pt in enumerate(payment_types, 1):
            print(f"{idx}. {pt.get('name')} (kind: {pt.get('paymentTypeKind')}) (ID: {pt.get('id')})")

        pt_index = input("\nВведите номер типа оплаты (или Enter для пропуска, тогда возьмём 1-й): ")
        if pt_index.strip():
            try:
                pt_index = int(pt_index)
                if pt_index < 1 or pt_index > len(payment_types):
                    print("Некорректный номер типа оплаты.")
                    return
                payment_type_id = payment_types[pt_index - 1].get('id')
            except ValueError:
                print("Введено некорректное значение, будет использован первый тип оплаты.")
                payment_type_id = payment_types[0].get('id')
        else:
            payment_type_id = payment_types[0].get('id')
    else:
        print("\nНе удалось получить типы оплат или список пуст. Зададим paymentTypeId вручную!")
        payment_type_id = input("Введите UUID типа оплаты (paymentTypeId): ")

    # 6) Сбор данных о клиенте
    customer_name = input("\nВведите имя клиента (необязательно, Enter = 'Guest'): ")
    if not customer_name.strip():
        customer_name = "Guest"

    customer_phone = input("Введите телефон клиента (необязательно, Enter = без телефона): ")

    # 7) Сбор данных о товаре (упрощённо – один товар)
    # В реальном сценарии вы бы либо получали nomenclature и предлагали выбор, либо спрашивали у пользователя.
    product_id = input("\nВведите UUID товара (productId): ")
    if not product_id.strip():
        print("productId обязателен для добавления позиции в заказ.")
        return

    try:
        product_price = float(input("Введите цену за единицу товара: "))
        product_quantity = float(input("Введите количество (например, 1, 2.5 и т.п.): "))
    except ValueError:
        print("Цена или количество введены некорректно.")
        return

    # 8) Сбор данных о сумме платежа
    # В упрощённом случае считаем, что sum = product_price * product_quantity
    payment_sum_input = input("\nВведите сумму платежа (или Enter для автоподстановки цены): ")
    if payment_sum_input.strip():
        try:
            payment_sum = float(payment_sum_input)
        except ValueError:
            print("Некорректная сумма. Будет рассчитана автоматически.")
            payment_sum = product_price * product_quantity
    else:
        payment_sum = product_price * product_quantity

    # 9) Создание заказа
    print("\n==== ОТПРАВЛЯЕМ ЗАПРОС НА СОЗДАНИЕ ЗАКАЗА ====")
    result = create_order(
        token=token,
        organization_id=organization_id,
        terminal_group_id=terminal_group_id,
        table_id=table_id,
        customer_name=customer_name,
        customer_phone=customer_phone,
        product_id=product_id,
        product_price=product_price,
        product_quantity=product_quantity,
        payment_type_id=payment_type_id,
        payment_sum=payment_sum
    )

    if result:
        print("\nСоздание заказа завершено. См. подробности выше.")
    else:
        print("\nНе удалось создать заказ.")


if __name__ == "__main__":
    main()
