import requests
import msal

# api_url = 'https://mflowv1qa.westus2.cloudapp.azure.com/gw/management/api/'
api_url = 'https://mflow.jnj.com/gw/management/api/'
token='eyJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiIsImtpZCI6Imwzc1EtNTBjQ0g0eEJWWkxIVEd3blNSNzY4MCJ9.eyJhdWQiOiIzNDk1MWU2Mi1lNjQ1LTRhYWEtYTJlYi00Y2JlOWE3OWIzYjQiLCJpc3MiOiJodHRwczovL2xvZ2luLm1pY3Jvc29mdG9ubGluZS5jb20vM2FjOTRiMzMtOTEzNS00ODIxLTk1MDItZWFmZGE2NTkyYTM1L3YyLjAiLCJpYXQiOjE2MzY2NjUwODcsIm5iZiI6MTYzNjY2NTA4NywiZXhwIjoxNjM2NjY4OTg3LCJhaW8iOiJBVlFBcS84VEFBQUFVT0ZPQlY1MnFCSnl6MWhSM3NzZFlyNVJIODVqSUFMMUJwVWIxNmdXajVwL1Z5WVVvS3QwbnVQbUFZOGdhcnFmcHp5MCtkUWFMOVgxOFdCVm9xR0VJNDJuN1dCeVJiREJ4SjBDVEl4WEx0WT0iLCJuYW1lIjoiQ3UsIE1pbmd5aSBbSkpDVVMgTk9OLUpcdTAwMjZKXSIsIm5vbmNlIjoiNjNiOTVjYjUtY2E2OS00NTYxLThmNzMtOWY3YzI3NzBjNWU2Iiwib2lkIjoiNTY0Yjc5ZTYtZTBkMi00YjA4LWJiY2YtNGVhZmMyMWFmNTk1IiwicHJlZmVycmVkX3VzZXJuYW1lIjoiTUN1M0BpdHMuam5qLmNvbSIsInJoIjoiMC5BUVFBTTB2Sk9qV1JJVWlWQXVyOXBsa3FOV0llbFRSRjVxcEtvdXRNdnBwNXM3UUVBTFkuIiwic3ViIjoiaXhkVnZUaTBvOEV6MGMxV0FiZE1yTUV6S3hqcENoNWt0QXYwNm9aOUp1USIsInRpZCI6IjNhYzk0YjMzLTkxMzUtNDgyMS05NTAyLWVhZmRhNjU5MmEzNSIsInV0aSI6ImFJUUZGTjBLeFVHWEtvZDFEVkY5QUEiLCJ2ZXIiOiIyLjAifQ.YvILgvxGr9NrzIj1q7iCG4Sp55w0re_apkbPBlAQrEXn3LdXvZ9cV-gwnB2KUT7enqmA8GuiE8MqSCOwjDw88yvAfMqOu-KfAG9rYHqI_3ADCwS_sNz2E5mTekcLqfWju2yTjSgyij27HOI6OACslW5b4RuCahwxV-wsMhJjjEME8u6GmICVj9UbO90XNCqXFS08zs1oktBC0ZHZzMUcrWMOQLjJq2zdeMQ5VdwyiAQ-Ou3EBiTsBWV2ia4RtS7dbMxx3ZebQhsiHkvR7Ul_6gsT2OARmqTSYSlrTam8W6CFpij9-KmFeURY-y4fJKgkFHFYxxIFoMamrueT_UkZjA'

# def build_msal_app(cache=None):
#     return msal.ConfidentialClientApplication(
#         '34951e62-e645-4aaa-a2eb-4cbe9a79b3b4', authority='https://login.microsoftonline.com/3ac94b33-9135-4821-9502-eafda6592a35',
#         client_credential='wGx7Q~1KJ8cMUWWyvFE5oTDcuu-leTcxKIDb7', token_cache=cache)

def build_msal_app(client_id, cache=None):
    return msal.ConfidentialClientApplication(
        client_id, 
        authority='https://login.microsoftonline.com/3ac94b33-9135-4821-9502-eafda6592a35',
        client_credential='wGx7Q~1KJ8cMUWWyvFE5oTDcuu-leTcxKIDb7', 
        token_cache=cache)

def get_token(client_id, scope,token):
    application = build_msal_app(client_id, cache=None)
    result = application.acquire_token_on_behalf_of(token, scopes=[scope])
    # print(f'result: {result}')
    return result

def get_data(url, token):
    # token_format = 'Bearer {0}'
    # response = requests.get(api_url+url, headers={
    # 'authorization': token_format.format(token)}, verify=False)
    # print(response.text)

    # json_response = json.load(response.text)
    # return json_response
    try:
        token = token["access_token"]
    except:
        token = ''
    response = requests.get(f'{api_url}{url}', headers={"authorization": "Bearer "+ token})
    print(response.text)
    # pass
    
get_data('algos', get_token("34951e62-e645-4aaa-a2eb-4cbe9a79b3b4", "api://0760e066-b56d-46f4-8f4c-cfe38effca0b/user_impersonation", token))
# get_data('algos', token)
# print(get_token(token)['id_token'])