from langchain.chains.conversation.memory import ConversationBufferMemory
from langchain.chains import ConversationChain
from langchain.chains import LLMChain
from langchain import OpenAI
from langchain.prompts import PromptTemplate
import pprint

# LLMの準備
llm = OpenAI(temperature=1.2, max_tokens=300, request_timeout=20)

# 名前の準備
person1_name = "エキスパートエンジニア"
person2_name = "ビギナーエンジニア"

# プレフィックスの準備
person1_prefix = """あなたの名前は"エキスパートエンジニア"です (チャットボットではありません)。
あなたはpython言語でのソフトウェア開発経験が豊富です。
python言語のプログラミング時にいろいろエキスパートとして意識しながらコーディングしています

Current conversation:
{history}
ビギナーエンジニア: {input}
エキスパートエンジニア:
"""

# ConversationChainの準備
person1 = ConversationChain(
    llm=llm, 
    verbose=False,
    memory=ConversationBufferMemory(
        memory_key="history", 
        human_prefix=person2_name, 
        ai_prefix=person1_name
    ),
)
person1.prompt = PromptTemplate(
    input_variables=["history", "input"], 
    template=person1_prefix
)


# プレフィックスの準備
person2_prefix = """あなたの名前はビギナーエンジニアです (チャットボットではありません)。
あなたはPython言語の初学者です。どんなことに注意しながらコーディングしたらいいのか知識がありません。

Current conversation:
{history}
エキスパートエンジニア: {input}
ビギナーエンジニア:
"""

# ConversationChainの準備
person2 = ConversationChain(
    llm=llm, 
    verbose=False, 
    memory=ConversationBufferMemory(
        memory_key="history", 
        human_prefix=person1_name, 
        ai_prefix=person2_name
    ),
)
person2.prompt = PromptTemplate(
    input_variables=["history", "input"], 
    template=person2_prefix
)

person2_says = "あなたはPythonでコーディングしている時に、どんなことを気をつけていますか？"

talk_history = []

first_talk = person2_name + ":" + person2_says
print(person2_name + ":" + person2_says)

talk_history.append(first_talk)

for i in range(2):
  person1_says = person1.predict(input=person2_says)
  talk_history.append(person1_name + ":" + person1_says)
  print(person1_name, ":", person1_says)
  person2_says = person1.predict(input=person1_says)
  talk_history.append(person2_name + ":" + person2_says)
  print(person2_name, ":", person2_says)

# print(person1.message)

print("---")
# print(talk_history)

for talk in  talk_history:
  print(talk)
