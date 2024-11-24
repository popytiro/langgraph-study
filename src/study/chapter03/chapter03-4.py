from openai import OpenAI

client = OpenAI()

prompt = """\
ユーザーが入力した料理のレシピを考えてください。

料理名: '''
{dish}
'''
"""


def generate_recipe(dish: str) -> str:
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "ユーザーが入力した料理のレシピを考えてください。"},
            {"role": "user", "content": f"{dish}"},
        ],
    )
    return response.choices[0].message.content


recipe = generate_recipe("カレー")
print(recipe)