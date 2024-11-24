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

from typing import Iterator


def upper(input_stream: Iterator[str]) -> Iterator[str]:
    for text in input_stream:
        yield text.upper()


chain = prompt | model | StrOutputParser() | upper

for chunk in chain.stream({"input": "Hello!"}):
    print(chunk, end="", flush=True)