import csv
import asyncio
import zeep
import requests
import logging
import pandas as pd

from io import StringIO
from zeep.transports import Transport
from fastapi import APIRouter, UploadFile, File
from core.config import settings
from core.logger import LoggerSetup


logging_setup = LoggerSetup()
logger = logging.getLogger('domain_api')

router = APIRouter()


async def handle_async_tasks(tasks):
    await asyncio.gather(*tasks)
    logger.info('Все асинхронные задачи выполнены.')


async def add_domain_async(client, params, chunk_counter, chunk_len):
    try:
        result = client.service.DomainInsert(member=params)
        logger.info(f"Чанк {chunk_counter} из {chunk_len}")
        logger.info('Результат:')
        logger.info(result)
        return result
    except Exception as er:
        logger.info(er)
        return {'error': 'Ошибка при добавлении данных'}


async def delete_domain_async(client, params, chunk_counter, chunk_len):
    try:
        result = client.service.DomainDelete(member=params)
        logger.info(f"Чанк {chunk_counter} из {chunk_len}")
        logger.info('Результат:')
        logger.info(result)
        return result
    except Exception as er:
        logger.info(er)
        return {'error': 'Ошибка при удалении данных'}


async def get_status_domain_async(client, params, chunk_counter, chunk_len):
    try:
        result = client.service.DomainStatus(list=params)
        logger.info(f"Чанк {chunk_counter} из {chunk_len}")
        logger.info('Результат:')
        logger.info(result)
        return result
    except Exception as er:
        logger.info(er)
        return {'error': 'Ошибка при добавлении данных'}


@router.post(
    '/add_domains',
    summary="Add domains from CSV file"
)
async def add_domains(
    file: UploadFile = File(...)
):
    try:
        transport = Transport(timeout=10, session=requests.Session())
        client = zeep.Client('https://api.sedo.com/api/v1/?wsdl', transport=transport)
        domain_entries = []

        contents = await file.read()
        csv_data = StringIO(contents.decode())
        df = pd.read_csv(csv_data, header=None)

        for index, row in df.iterrows():
            domain_entry = {
                'domain': row[0],
                'forsale': 1,
                'price': float(row[1]),
                'minprice': 0,
                'fixedprice': 1,
                'currency': 1,
                'domainlanguage': 'en',
            }
            domain_entry_xml = client.get_type('ns0:DomainEntry')(domain=domain_entry['domain'],
                                                                  forsale=domain_entry['forsale'],
                                                                  price=domain_entry['price'],
                                                                  minprice=domain_entry['minprice'],
                                                                  fixedprice=domain_entry['fixedprice'],
                                                                  currency=domain_entry['currency'],
                                                                  domainlanguage=domain_entry['domainlanguage'])
            domain_entries.append(domain_entry_xml)

        chunked_entries = [domain_entries[i:i + 50] for i in range(0, len(domain_entries), 50)]

        tasks = []

        for i, chunk in enumerate(chunked_entries, 1):
            params = {
                'partnerid': settings.partner_id,
                'signkey': settings.sign_key,
                'username': settings.api_login,
                'password': settings.api_pass,
                'domainentry': chunk,
            }
            task = asyncio.create_task(add_domain_async(client, params, i, len(chunked_entries)))
            tasks.append(task)

        asyncio.create_task(handle_async_tasks(tasks))

        return {'message': 'Запрос принят, асинхронное добавление доменов выполняется в фоне.'}

    except Exception as er:
        logger.info(er)
        return {'error': 'Ошибка при добавлении доменов'}


@router.delete(
    '/delete_domains',
    summary="Delete domains from CSV file"
)
async def delete_domains(
    file: UploadFile = File(...)
):
    try:
        transport = Transport(timeout=10, session=requests.Session())
        client = zeep.Client('https://api.sedo.com/api/v1/?wsdl', transport=transport)

        contents = await file.read()
        csv_data = StringIO(contents.decode())
        df = pd.read_csv(csv_data, header=None)

        domain_chunks = [df.iloc[i:i + 50, 0].tolist() for i in range(0, len(df), 50)]

        tasks = []

        for idx, chunk in enumerate(domain_chunks, start=1):
            params = {
                'partnerid': settings.partner_id,
                'signkey': settings.sign_key,
                'username': settings.api_login,
                'password': settings.api_pass,
                'domains': chunk,
            }

            task = asyncio.create_task(delete_domain_async(client, params, idx, len(domain_chunks)))
            tasks.append(task)

        asyncio.create_task(handle_async_tasks(tasks))
        return {'message': 'Запрос принят, асинхронное удаление доменов выполняется в фоне.'}
    except Exception as er:
        logger.info(er)
        return {'error': 'Ошибка при удалении доменов'}


@router.get(
    '/domains_list/{file_name}',
    summary="Get domains list to CSV file"
)
async def domains_list(
    file_name: str
):
    try:
        transport = Transport(timeout=10, session=requests.Session())
        client = zeep.Client('https://api.sedo.com/api/v1/?wsdl', transport=transport)
        params = {
            'username': settings.api_login,
            'password': settings.api_pass,
            'results': 1000,
            'partnerid': settings.partner_id,
            'signkey': settings.sign_key,
        }

        result = client.service.DomainList(listdomains=params)
        logger.info(result)
        with open(f'{file_name}.csv', 'w', newline='') as csvfile:
            writer = csv.writer(csvfile)
            for domain_info in result:
                writer.writerow([domain_info["domain"]])

        return result

    except zeep.exceptions.Fault as er:
        logger.info(er)
        return {'message': 'Нет данных для отображения'}

    except Exception as er:
        logger.info(er)
        return {'error': 'Ошибка при получении списка доменов'}

@router.post(
    '/domains_status',
    summary="Domains status from CSV file"
)
async def domains_status(
    file: UploadFile = File(...)
):
    try:
        transport = Transport(timeout=10, session=requests.Session())
        client = zeep.Client('https://api.sedo.com/api/v1/?wsdl', transport=transport)

        # Чтение содержимого CSV файла
        contents = await file.read()

        # Парсинг CSV файла
        csv_data = StringIO(contents.decode())
        df = pd.read_csv(csv_data, header=None)

        # Разбивка доменов на списки по 50
        domain_chunks = [df.iloc[i:i + 50, 0].tolist() for i in range(0, len(df), 50)]

        tasks = []

        for idx, chunk in enumerate(domain_chunks, start=1):
            logger.info(f"Запуск получения статуса доменов. Чанк {idx} из {len(domain_chunks)}")
            logger.info(chunk)

            params = {
                'partnerid': settings.partner_id,
                'signkey': settings.sign_key,
                'domainlist': chunk,
            }

            task = asyncio.create_task(get_status_domain_async(client, params, idx, len(domain_chunks)))
            tasks.append(task)

        asyncio.create_task(handle_async_tasks(tasks))
        return {'message': 'Запрос принят, асинхронное получение статусов доменов выполняется в фоне.'}
    except Exception as er:
        logger.info(er)
        return {'error': 'Ошибка при получении статусов доменов'}
