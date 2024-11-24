from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI

prompt = ChatPromptTemplate.from_messages(
    [
        ("system", "You are a helpful assistant."),
        ("human", "{input}"),
    ]
)

model = ChatOpenAI(model="gpt-4o-mini", temperature=0)

output_parser = StrOutputParser()

from langchain_core.runnables import chain

def upper(text: str) -> str:
    return text.upper()


chain = prompt | model | upper

# 以下のコードを実行するとエラーになります
# output = chain.invoke({"input": "Hello!"})

chain = prompt | model | StrOutputParser() | upper

output = chain.invoke({"input": "Hello!"})
print(output)