import boto3
import json
import logging

log = logging.getLogger("folder_for_lambda/lambda_saving_files")
logging.basicConfig(level=logging.INFO)

lambda_client = boto3.client(
    "lambda",
    region_name="eu-north-1"
)
path_to_file = "/data/game_sessions.json"
with open(path_to_file, "r", encoding="utf-8") as f:
    game_sessions_dict = json.load(f)



  
def push_game_sessions_to_lambda(game_sessions_dict):
    lambda_client.invoke(
        FunctionName="arn:aws:lambda:eu-north-1:404497321503:function:lambda_pull_to_s3",
        InvocationType="Event",  # async
        Payload=json.dumps(game_sessions_dict, ensure_ascii= False, indent = 2).encode("utf-8") #invoke waits for bytes not for strings thats why we do decode
    )

push_game_sessions_to_lambda(game_sessions_dict)