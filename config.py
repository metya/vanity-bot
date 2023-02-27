from os import getenv
from dotenv import dotenv_values

if env_var := dotenv_values('token'):
    API_TOKEN = env_var["API_TOKEN"]
else:
    API_TOKEN = getenv("API_TOKEN")

print(API_TOKEN)

if __name__ == "__main__":
    print(API_TOKEN)