from openai import OpenAI

client = OpenAI()

response = client.chat.completions.create(
    model="gpt-4o-mini",
    messages=[
        {
            "role": "system",
            "content": "入力をポジティブ・ネガティブ・中立のどれかに分類してください。",
        },
        {
            "role": "user",
            "content": "ChatGPTはとても便利だ",
        },
    ],
)
print(response.choices[0].message.content)