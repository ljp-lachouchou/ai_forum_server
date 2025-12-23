from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

# 1. 初始化模型
model = ChatOpenAI(model="gpt-4o")

# 2. 创建 Prompt 模板
prompt = ChatPromptTemplate.from_messages([
    ("system", "你是一个专业的翻译官，请将用户的句子翻译成{language}"),
    ("user", "{text}")
])

# 3. 使用管道符 | 组合成链 (LCEL)
chain = prompt | model | StrOutputParser()

# 4. 调用
response = chain.invoke({"language": "法语", "text": "今天天气真不错"})
print(response)