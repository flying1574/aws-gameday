#!/usr/bin/env python
"""
Client which receives the requests

Args:
    API Token
    API Base (https://...)

"""
from flask import Flask, request
import logging
import argparse
import urllib2
from flywheel import Engine, EntityNotFoundException
from message import Message
import boto3

# logging.basicConfig(level=logging.DEBUG)

# parsing arguments
PARSER = argparse.ArgumentParser(description='Client message processor')
PARSER.add_argument('API_token', help="the individual API token given to your team")
PARSER.add_argument('API_base', help="the base URL for the game API")

ARGS = PARSER.parse_args()

# defining global vars
API_BASE = ARGS.API_base
# 'https://csm45mnow5.execute-api.us-west-2.amazonaws.com/dev'

APP = Flask(__name__)

DDB_ENGINE = Engine()
DDB_ENGINE.connect_to_region('eu-central-1')
Message.meta_.name = 'gameday-production'

DDB_ENGINE.register(Message)

#ELASTICACHE_CLIENT = boto3.client('elasticache')


# creating flask route for type argument
@APP.route('/ping', methods=['GET', 'POST'])
def healthcheck():
    return "ok"

@APP.route('/', methods=['GET', 'POST'])
def main_handler():
    """
    main routing for requests
    """
    if request.method == 'POST':
        return process_message(request.get_json())
    else:
        return get_message_stats()


def get_message_stats():
    """
    provides a status that players can check
    """
    resp = DDB_ENGINE.dynamo.describe_table(Message.meta_.ddb_tablename())

    msg_count = resp.response['ItemCount']

    return "There are %d messages in the MESSAGES dictionary" % msg_count


def process_message(msg):
    """
    processes the messages by combining and appending the kind code
    """
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

    # store this part of the message in the correct part of the list
    message.parts[part_number] = data

    # store the parts in MESSAGES
    DDB_ENGINE.sync(message)

    # if both parts are filled, the message is complete
    if not message.message_sent and all(message.parts):
        # app.logger.debug("got a complete message for %s" % msg_id)
        print "have all parts"
        # We can build the final message.
        result = ''.join(message.parts)
        message.message_sent = 1
        DDB_ENGINE.sync(message)
        # sending the response to the score calculator
        # format:
        #   url -> api_base/jFgwN4GvTB1D2QiQsQ8GHwQUbbIJBS6r7ko9RVthXCJqAiobMsLRmsuwZRQTlOEW
        #   headers -> x-gameday-token = API_token
        #   data -> EaXA2G8cVTj1LGuRgv8ZhaGMLpJN2IKBwC5eYzAPNlJwkN4Qu1DIaI3H1zyUdf1H5NITR
        APP.logger.debug("ID: %s" % msg_id)
        APP.logger.debug("RESULT: %s" % result)
        url = API_BASE + '/' + msg_id
        print url
        print result
        req = urllib2.Request(url, data=result, headers={'x-gameday-token': ARGS.API_token})
        resp = urllib2.urlopen(req)
        resp.close()
        print resp

    return 'OK'

if __name__ == "__main__":
    # By default, we disable threading for "debugging" purposes.
    # This will cause the app to block requests, which means that you miss out on some points,
    # and fail ALB healthchecks, but whatever I know I'm getting fired on Friday.
    APP.run(host="0.0.0.0", port="80")
    
    # Use this to enable threading:
    # APP.run(host="0.0.0.0", port="80", threaded=True)
