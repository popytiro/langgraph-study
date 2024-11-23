from langchain_openai import OpenAI

model = OpenAI(model="gpt-3.5-turbo-instruct", temperature=0)
ai_message = model.invoke("こんにちは")
print(ai_message)