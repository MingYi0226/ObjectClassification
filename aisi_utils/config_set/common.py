from azure.cosmosdb.table.tableservice import TableService
from azure.identity import DefaultAzureCredential
from azure.keyvault.secrets import SecretClient
import os
import requests

# Authorization key
INFERENCE_HEADER = {
    'X-Api-Key': '46f3d27c-c8d4-11eb-b8bc-0242ac130003'
}
SAA_HEADER = {
    'X-Api-Key': '896d35d2-a352-4705-b4f5-e8d86724fe52'
}
DEPLOYMENT_HEADER = {
    'X-Api-Key': '0337a9de-9340-4ee3-8d20-86fbc75b0c8e'
}
CONFIG_ALL = 'config_all.json'

def get_connection_string(secret_key):
    '''
        Retrieves connecttion string from key vault
    '''
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
        print(f"get_connection_string error: {e}")
    return secret_value

def get_urls_from_table(table_name, conn_str):
    '''
        Returns all urls with [siteId, trayID] list
    '''
    urls = {}
    is_fetched = True
    try:
        table_service = TableService(connection_string=conn_str)
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
    except Exception as e:
        is_fetched = False
        print(f'get_urls_from_table err:{e}')
    return urls, is_fetched

def get_matched_workspace(config_json, ws_name):
    matched_ws = []
    try:
        matched_ws = [_ws for _ws in config_json['workspaces'] if _ws['workspace'] == ws_name]
    except Exception as e:
        print(f'Failed to get matched workspace: {e}')

    if not len(matched_ws):
        raise Exception(f"workspace name was not found in config_all")
    return matched_ws
