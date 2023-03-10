import boto3
import datetime

ec2 = boto3.client('ec2')
dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('instance_schedule')

def is_weekday_and_time(date):
    if date.weekday() >= 5:  # Saturday = 5, Sunday = 6
        return False
    start_time = datetime.time(6, 0)
    end_time = datetime.time(21, 0)
    instance_time = date.time()
    return instance_time >= start_time and instance_time <= end_time

def lambda_handler(event, context):
    # Query DynamoDB to retrieve all stopped instances with the 'Schedule' tag set to '6-21'
    response = table.query(
        IndexName='state-schedule-index',
        KeyConditionExpression='#s = :state AND #sch = :schedule',
        ExpressionAttributeNames={
            '#s': 'State',
            '#sch': 'Schedule'
        },
        ExpressionAttributeValues={
            ':state': {'S': 'stopped'},
            ':schedule': {'S': '6-21'}
        }
    )

    # Start each stopped instance that matches the filter
    for item in response['Items']:
        launch_time = datetime.datetime.fromisoformat(item['LaunchTime'])
        if is_weekday_and_time(launch_time):
            instance_id = item['InstanceId']
            ec2.start_instances(InstanceIds=[instance_id])
            print(f"Started instance: {instance_id}")
