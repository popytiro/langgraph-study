from openai import OpenAI

client = OpenAI()

prompt = """\
入力がAIに関係するか回答してください。

Q: AIの進化はすごい
A: true
Q: 今日は良い天気だ
A: false
Q: ChatGPTはとても便利だ
A: 
"""

response = client.completions.create(
    model="gpt-3.5-turbo-instruct",
    prompt=prompt,
)
print(response.choices[0].text)