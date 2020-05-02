import os
from resizer import DailyResize

def lambda_handler(event, context):
    operation = event['Operation']
    resizer = DailyResize(table_prefix=os.environ['TABLE_NAME'])
    if operation == 'create_new':
        resizer.create_new()
    elif operation == 'resize_old':
        resizer.resize_old()
    else:
        raise ValueError("Invalid operation")

