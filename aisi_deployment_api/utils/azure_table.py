from azure.cosmosdb.table.tableservice import TableService
from azure.identity import DefaultAzureCredential
from azure.keyvault.secrets import SecretClient
import os
from utils.common import *


def get_service(con_str):
    function_name = "azure_table.get_service"
    table_service = None
    try:
        table_service = TableService(connection_string=con_str)
    except Exception as e:
        table_service = None
        logger.error(f"{function_name} - get_service err: {e}")
    return table_service


def delete_table(con_str, table_name):
    function_name = "azure_table.delete_table"
    res = False
    try:
        table_service = get_service(con_str)
        res = table_service.delete_table(table_name)
    except Exception as e:
        logger.error(f"{function_name} - delete_table err: {e}")
    return res


def create_table(con_str, table_name):
    function_name = "azure_table.create_table"
    res = False
    try:
        table_service = get_service(con_str)
        res = table_service.create_table(table_name)
    except Exception as e:
        logger.error(f"{function_name} - create table err: {e}")
    return res


def insert_row(con_str, table_name, entity):
    table_service = get_service(con_str)
    try:
        table_service.get_entity(table_name, entity['PartitionKey'], entity['RowKey'])
        logger.debug(f'{json.dumps(entity)} exists.')
    except Exception as e:
        table_service.insert_entity(table_name, entity)


def update_row(con_str, table_name, entity):
    table_service = get_service(con_str)
    table_service.update_entity(table_name, entity)


def query_row(con_str, table_name, query=''):
    table_service = get_service(con_str)
    return table_service.query_entities(table_name, filter=query)


@func_wrapper()
def get_connection_string(secret_key, **kwargs):
    # Specify KeyVault name and config
    keyVaultName = os.environ["KEY_VAULT_NAME"]
    KVUri = f"https://{keyVaultName}.vault.azure.net"

    # Authenticate App
    credential = DefaultAzureCredential()

    # Connect to KeyVault
    client = SecretClient(vault_url=KVUri, credential=credential)

    # Read KeyVault Secret
    secret_value = client.get_secret(secret_key).value
    return secret_value

@func_wrapper()
def create_azure_table(**kwargs):
    # Get connection string
    connection_str = get_connection_string(secret_key=common.key_name)
    
    # create Azure Table
    create_table(connection_str, common.REQ_TABLE)
    create_table(connection_str, common.DB_TABLE)
    create_table(connection_str, common.COPY_TABLE)
    # create_table(connection_str, common.MODEL_HISTORY_TABLE)
    

def get_urls_from_table(table_name, conn_str):
    '''
        Returns all urls with [siteId, trayID] list
    '''
    try:
        urls = {}
        table_service = get_service(conn_str)
        res = list(table_service.query_entities(table_name, filter=""))
        
        for row in res:
            url = row['url']
            site_id = row['PartitionKey']
            tray_id = row['RowKey']
            if url not in urls:
                urls[url] = []
            urls[url].append(
                {
                    "siteId": site_id,
                    "trayId": tray_id
                })
        return urls
    except Exception as e:
        logger.debug(f"get_urls_from_table:{e}")
    return {}
    