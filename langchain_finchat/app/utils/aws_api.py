import boto3
from botocore.client import BaseClient

class AWSService:
    def __init__(self, service_name):
        self.client: BaseClient = boto3.client(service_name)

class SSMService(AWSService):
    def __init__(self):
        super().__init__("ssm")

    def get_parameter(self, name: str, with_decryption=True) -> str:
        response = self.client.get_parameter(
            Name=name,
            WithDecryption=with_decryption
        )
        return response['Parameter']['Value']
    
    def put_parameter(self, name: str, value: str, param_type='String', overwrite=True):
       response = self.ssm.put_parameter(
           Name=name,
           Value=value,
           Type=param_type,
           Overwrite=overwrite
       )
       return response
