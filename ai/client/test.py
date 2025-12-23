from ai.client.ClientBuilder import ClientBuilder, ClientType
client = ClientBuilder(clientType=ClientType.DeepSeek).build()
response = client.invoke("你是谁?")
print(response.content)