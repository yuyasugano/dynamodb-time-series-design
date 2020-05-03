import os
import boto3
import datetime

region = os.environ.get('AWS_DEFAULT_REGION', 'ap-northeast-1')
dynamodb = boto3.client('dynamodb', region_name=region)

class DailyResize(object):

    FIRST_DAY_RCU, FIRST_DAY_WCU = 3, 3
    OLD_DAY_RCU, OLD_DAY_WCU = 1, 1

    def __init__(self, table_prefix):
        self.table_prefix = table_prefix

    def create_new(self):
        # create new table
        today = datetime.date.today()
        tomorrow = datetime.date.today() + datetime.timedelta(1)
        new_table_name = "{}_{}".format(self.table_prefix, self._format_date(tomorrow))
        dynamodb.create_table(
            TableName = new_table_name,
            KeySchema = [
                {
                    'AttributeName': 'name',
                    'KeyType': 'HASH' # Partition Key
                },
                {
                    'AttributeName': 'datetime',
                    'KeyType': 'RANGE' # Sort Key
                }
            ],
            AttributeDefinitions = [
                {
                    'AttributeName': 'name',
                    'AttributeType': 'S',
                },
                {
                    'AttributeName': 'datetime',
                    'AttributeType': 'S'
                }
            ],
            ProvisionedThroughput = {
                'ReadCapacityUnits': self.FIRST_DAY_RCU,
                'WriteCapacityUnits': self.FIRST_DAY_WCU
            },
        )

        print("Table created with name {}".format(new_table_name))
        return new_table_name

    def resize_old(self):
        # update older table
        yesterday = datetime.date.today() - datetime.timedelta(1)
        old_table_name = "{}_{}".format(self.table_prefix, self._format_date(yesterday))
        self._update_table(old_table_name, self.OLD_DAY_RCU, self.OLD_DAY_WCU)

        return 'OK'

    def _update_table(self, table_name, RCU, WCU):
        """ Update RCU/WCU of the given table (if exists) """
        print("Updating table with name {}".format(table_name))
        try:
            dynamodb.update_table(
                TableName = table_name,
                ProvisionedThroughput = {
                    'ReadCapacityUnits': RCU,
                    'WriteCapacityUnits': WCU,
                },
            )
        except dynamodb.exceptions.ResourceNotFoundException as e:
            print("DynamoDB Table {} not found".format(table_name))

    @staticmethod
    def _format_date(d):
        return d.strftime("%Y-%m-%d")


