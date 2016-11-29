#!/usr/bin/env python
"""
Client which receives the requests

Args:
    API Token
    API Base (https://...)

"""
import requests
from flywheel import Engine, EntityNotFoundException
from message import Message
import boto3
import json
import base64


API_BASE = 'https://dashboard.cash4code.net/score'
API_TOKEN = 'ecfb7f4745'

DDB_ENGINE = Engine()
DDB_ENGINE.connect_to_region('eu-central-1')
Message.meta_.name = 'gameday-production'

DDB_ENGINE.register(Message)

def unpack_message(event):
    # {
    #     "Records": [
    #         {
    #             "eventID": "shardId-000000000000:49545115243490985018280067714973144582180062593244200961",
    #             "eventVersion": "1.0",
    #             "kinesis": {
    #                 "approximateArrivalTimestamp": 1428537600,
    #                 "partitionKey": "partitionKey-3",
    #                 "data": "SGVsbG8sIHRoaXMgaXMgYSB0ZXN0IDEyMy4=",
    #                 "kinesisSchemaVersion": "1.0",
    #                 "sequenceNumber": "49545115243490985018280067714973144582180062593244200961"
    #             },
    #             "invokeIdentityArn": "arn:aws:iam::EXAMPLE",
    #             "eventName": "aws:kinesis:record",
    #             "eventSourceARN": "arn:aws:kinesis:EXAMPLE",
    #             "eventSource": "aws:kinesis",
    #             "awsRegion": "us-east-1"
    #         }
    #     ]
    # }
    kinesis_msg = event.get('Records', [{}])[0].get('kinesis', {}).get('data')

    s3_msg = event.get('Records', [{}])[0].get('s3')

    if kinesis_msg:
        print("Received Kinesis event for - {}".format(kinesis_msg))

        return json.loads(base64.decodestring(kinesis_msg))
    elif s3_msg:
        s3_bucket = s3_msg['bucket']['name']
        s3_key = s3_msg['object']['key']

        print("Received S3 event for - {}".format(s3_key))

        s3_client = boto3.client('s3', region_name='eu-central-1')
        s3_msg = json.loads(s3_client.get_object(Bucket=s3_bucket, Key=s3_key)['Body'].read())
        return s3_msg

    return event


def handler(msg, context):
    """
    processes the messages by combining and appending the kind code
    """

    msg = unpack_message(msg)

    if not msg:
        return

    msg_id = msg.get('Id') # The unique ID for this message
    part_number = msg.get('PartNumber') # Which part of the message it is
    data = msg.get('Data') # The data of the message
    total_parts = msg.get('TotalParts') # The data of the message

    if not msg_id or not data:
        return None

    # Try to get the parts of the message from the MESSAGES dictionary.
    # If it's not there, create one that has None in both parts
    try:
        message = DDB_ENGINE(Message).filter(Message.id == msg_id).one()
    except EntityNotFoundException:
        message = Message(id=msg_id, total_parts=total_parts)
    except Exception as e:
        print(str(e))
        return

    # store this part of the message in the correct part of the list
    message.parts[part_number] = data

    # store the parts in MESSAGES
    DDB_ENGINE.sync(message)

    # if both parts are filled, the message is complete
    if all(message.parts):
        # app.logger.debug("got a complete message for %s" % msg_id)
        print "have all parts"
        # We can build the final message.
        result = ''.join(message.parts)
        # sending the response to the score calculator
        # format:
        #   url -> api_base/jFgwN4GvTB1D2QiQsQ8GHwQUbbIJBS6r7ko9RVthXCJqAiobMsLRmsuwZRQTlOEW
        #   headers -> x-gameday-token = API_token
        #   data -> EaXA2G8cVTj1LGuRgv8ZhaGMLpJN2IKBwC5eYzAPNlJwkN4Qu1DIaI3H1zyUdf1H5NITR
        url = API_BASE + '/' + msg_id
        print url
        print result
        resp = requests.post(url, data=result, headers={'x-gameday-token': API_TOKEN})
        print resp.status_code
        print
    return 'OK'

if __name__ == "__main__":
    handler({
      "Records": [
        {
          "eventID": "shardId-000000000000:49545115243490985018280067714973144582180062593244200961",
          "eventVersion": "1.0",
          "kinesis": {
            "approximateArrivalTimestamp": 1428537600,
            "partitionKey": "partitionKey-3",
            "data": "SGVsbG8sIHRoaXMgaXMgYSB0ZXN0IDEyMy4=",
            "kinesisSchemaVersion": "1.0",
            "sequenceNumber": "49545115243490985018280067714973144582180062593244200961"
          },
          "invokeIdentityArn": "arn:aws:iam::EXAMPLE",
          "eventName": "aws:kinesis:record",
          "eventSourceARN": "arn:aws:kinesis:EXAMPLE",
          "eventSource": "aws:kinesis",
          "awsRegion": "us-east-1"
        }
      ]
    }, None)
