from openai import OpenAI

client = OpenAI()

response = client.completions.create(
    model="gpt-3.5-turbo-instruct",
    prompt="こんにちは！私はジョンと言います！",
)
print(response.to_json(indent=2))