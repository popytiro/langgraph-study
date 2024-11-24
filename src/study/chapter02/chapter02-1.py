import tiktoken

text = "ChatGPT"

encoding = tiktoken.encoding_for_model("gpt-4o")
tokens = encoding.encode(text)
for token in tokens:
    print(encoding.decode([token]))