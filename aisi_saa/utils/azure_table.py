from azure.cosmosdb.table.tableservice import TableService
from azure.identity import DefaultAzureCredential
from azure.keyvault.secrets import SecretClient
import os
from utils.common import *
from utils.ilogger import logger


def get_service(con_str):
    function_name = "get_service"
    table_service = None
    try:
        table_service = TableService(connection_string=con_str)
    except Exception as e:
        table_service = None
        logger.error(f"{function_name}: err: {e}")
    return table_service

def delete_table(con_str, table_name):
    function_name = "delete_table"
    res = False
    try:
        table_service = get_service(con_str)
        res = table_service.delete_table(table_name)
    except Exception as e:
        logger.error(f"{function_name}: err: {e}")
    return res

def create_table(con_str, table_name):
    function_name = "create_table"
    res = False
    try:
        table_service = get_service(con_str)
        res = table_service.create_table(table_name)
        
    except Exception as e:
        logger.error(f"{function_name}: err: {e}")
    return res

def insert_row(con_str, table_name, entity):
    function_name = "insert_row"
    res = False
    try:
        table_service = get_service(con_str)
        res = table_service.insert_entity(table_name, entity)
    except Exception as e:
        logger.error(f"{function_name}: err: {e}")
    return res

def update_row(con_str, table_name, entity):
    function_name = "update_row"
    res = False
    try:
        table_service = get_service(con_str)
        res = table_service.update_entity(table_name, entity)
    except Exception as e:
        logger.error(f"{function_name}: err: {e}")
    return res

def query_row(con_str, table_name, query=''):
    function_name = "query_row"
    res = None
    try:
        table_service = get_service(con_str)
        res = table_service.query_entities(table_name, filter=query)
    except Exception as e:
        logger.error(f"{function_name}: err: {e}")
    return res


def get_connection_string(secret_key):
    function_name = "get_connection_string"
    secret_value = ''
    try:
        # Specify KeyVault name and config
        keyVaultName = os.environ["KEY_VAULT_NAME"]
        KVUri = f"https://{keyVaultName}.vault.azure.net"

        # Authenticate App
        credential = DefaultAzureCredential()
        
        # Connect to KeyVault
        client = SecretClient(vault_url=KVUri, credential=credential)

        # Read KeyVault Secret
        secret_value = client.get_secret(secret_key).value
    except Exception as e:
        logger.error(f"{function_name}: err: {e}")
    return secret_value
    

def create_azure_table(keyname):
    function_name = "create_azure_table"
    try:
        connection_str = get_connection_string(secret_key=keyname)
        create_table(connection_str, os.environ["AZURE_TABLE_NAME"])
        create_table(connection_str, os.environ["AZURE_TABLE_DOWNLOAD_NAME"])
    except Exception as e:
        logger.error(f"{function_name}: err: {e}")