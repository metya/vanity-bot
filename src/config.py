from os import getenv
from dotenv import dotenv_values

if env_var := dotenv_values('misc/token'):
    API_TOKEN = env_var["API_TOKEN"]
    TIME_OUT = env_var["TIME_OUT"]
else:
    API_TOKEN = getenv("API_TOKEN")
    TIME_OUT = getenv("TIME_OUT")

if __name__ == "__main__":
    print(API_TOKEN)
