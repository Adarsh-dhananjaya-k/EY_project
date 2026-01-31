import os
from dotenv import load_dotenv
from openai import AzureOpenAI

load_dotenv()


def get_azure_client():
    return AzureOpenAI(
        api_key=os.getenv("AZURE_OPENAI_API_KEY"),
        api_version=os.getenv("AZURE_OPENAI_API_VERSION"),
        azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
    )


def get_deployment_name():
    return os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME")