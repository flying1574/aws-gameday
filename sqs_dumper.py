import boto3

sqs = boto3.resource('sqs')

queue = sqs.get_queue_by_name(QueueName='production')

print(queue)