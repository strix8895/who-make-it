import json 
import gzip
import boto3
import base64
import os
import logging
from datetime import date, datetime

class FailedEventError(Exception):
    """It's Failed Events so don't need to create tags"""
    pass

# Initialization sdk client
ec2 = boto3.client('ec2')
rds = boto3.client('rds')

# Initialization logger
logger = logging.getLogger()
logger.setLevel(logging.INFO)


def json_serial(obj):
    """datetime format"""
    if isinstance(obj, (datetime, date)):
        return obj.isoformat()
    raise TypeError ("Type %s not serializable" % type(obj))


def list_instance_volumeid(resource_list:list , instanceid:str ):
    """select volume id from instance id"""
    response = ec2.describe_instances(InstanceIds=[instanceid,],) # describe instance detail
    
    jsn_str = json.dumps(response, ensure_ascii=False, default=json_serial)
    logger.info(jsn_str)
    
    # select all volume id
    volume_list = response['Reservations'][0]['Instances'][0]['BlockDeviceMappings']
    
    # add volume id to reosurce_list
    for volume_id in volume_list:
        resource_list.append(volume_id['Ebs']['VolumeId'])
        
    logger.info(resource_list)
    
    
def lambda_handler(event, context):

    # decode messages from cloudwatch logs
    b64data = events["awslogs"]["data"]
    compressed_payload = base64.b64decode(b64data)
    uncompressed_payload = gzip.decompress(compressed_payload)
    payload = json.loads(uncompressed_payload)
    event = json.loads(payload['logEvents'][0]['message'])
    jsn_str = json.dumps(event, ensure_ascii=False, default=json_serial)
    logger.info(jsn_str)
    
    try:
        # Stop processing if api called faild.
        if event['responseElements'] is None:
            raise FailedEventError
        elif event["eventName"] == "RunInstances":
            
            # var
            resource_list = []
            
            # extract the author's arn
            useridentify=event["userIdentity"]["arn"]
            instanceid=event["responseElements"]["instancesSet"]["items"][0]["instanceId"]
            resource_list.append(instanceid)
            # logger.info("UserArn is : %s" % useridentify)
            # logger.info("Instace id is : %s" % instanceid)
            
            # List volume id
            list_instance_volumeid(resource_list, instanceid)
            
            # create author's tag to resource
            response = ec2.create_tags(
                Resources=resource_list,
                 Tags=[
                    {
                        'Key': 'Author',
                        'Value': useridentify
                    },
                ]
            )
        elif event["eventName"] == "CreateDBInstance":
            
            # extract the author's arn
            useridentify=event["userIdentity"]["arn"]
            dbarn=event["responseElements"]["dBInstanceArn"]
            # logger.info("UserArn is : %s" % useridentify)
            # logger.info("DB arn is : %s" % dbarn)
            
            # create author's tag to resource
            response = rds.add_tags_to_resource(
                ResourceName=dbarn,
                 Tags=[
                    {
                        'Key': 'Author',
                        'Value': useridentify
                    },
                ]
            )

        return response
                
    except FailedEventError as e:
        logger.info("It's Failed Events")
