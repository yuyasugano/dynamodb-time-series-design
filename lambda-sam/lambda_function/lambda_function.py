import os
from bitbank import BitbankApi

def lambda_handler(event, context):
    operation = event['Operation']
    obj = BitbankApi(table_prefix=os.environ['TABLE_NAME'])
    if operation == 'ingest_new':
        obj.ingest_new()
    else:
        raise ValueError('Invalid operation')

