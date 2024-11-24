from openai import OpenAI

client = OpenAI()

response = client.chat.completions.create(
    model="gpt-4o-mini",
    messages=[
        {"role": "system", "content": "ステップバイステップで考えてください。"},
        {"role": "user", "content": "10 + 2 * 3 - 4 * 2"},
    ],
)
print(response.choices[0].message.content)