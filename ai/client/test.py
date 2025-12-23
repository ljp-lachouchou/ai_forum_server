from ai.client.ClientBuilder import ClientBuilder, ClientType
from dotenv import load_dotenv
load_dotenv() # 这会自动把 .env 里的内容注入到 os.environ
client = ClientBuilder(ClientType.DeepSeek).build()
response = client.invoke("你是谁?")
print(response.content)