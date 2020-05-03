import os
import boto3
import json
import decimal
import datetime
import python_bitbankcc

region = os.environ.get('AWS_DEFAULT_REGION', 'ap-northeast-1')
dynamodb = boto3.resource('dynamodb', region_name=region)
pair = 'btc_jpy'

class BitbankApi(object):

    def __init__(self, table_prefix):
        self.table_prefix = table_prefix

    def ingest_new(self):
        # ingest new item
        today = datetime.date.today()
        table_name = "{}_{}".format(self.table_prefix, self._format_date(today))

        pub = python_bitbankcc.public()
        tic = pub.get_ticker(pair)
        dep = pub.get_depth(pair)
        if (tic is None) & (dep is None):
            return {
                'statusCode': 200,
                'body': json.dumps('Calling API did not succeed')
            }
        else:
            dt = datetime.datetime.utcfromtimestamp(int(str(tic['timestamp'])[:10]))
            timestamp = dt.strftime("%Y/%m/%d %H:%M:%S")
            try:
                current_table = dynamodb.Table(table_name)
                response = current_table.put_item(
                    Item = {
                        'name': pair,
                        'datetime': timestamp,
                        'sell': int(tic['sell']),
                        'buy': int(tic['buy']),
                        'last': int(tic['last']),
                        'volume': int(float(tic['vol'])),
                        'depth': dep
                    }
                )
                print('PutItem succeeded')
            except Exception as e:
                print('PutItem failed', e.args)

    @staticmethod
    def _format_date(d):
        return d.strftime("%Y-%m-%d")

    def _float_to_decimal(f):
        return json.loads(json.dumps(f), parse_float=decimal.Decimal)
