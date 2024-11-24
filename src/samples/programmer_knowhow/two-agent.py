from langchain.chains.conversation.memory import ConversationBufferMemory
from langchain.chains import ConversationChain
from langchain.chains import LLMChain
from langchain import OpenAI
from langchain.prompts import PromptTemplate
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
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

## インタビューを追加

# 名前の準備
person3_name = "コードインタビュアー"

# プレフィックスの準備
person1_prefix = """あなたの名前は"エキスパートエンジニア"です (チャットボットではありません)。
あなたはpython言語でのソフトウェア開発経験が豊富です。
python言語のプログラミング時にいろいろエキスパートとして意識しながらコーディングしています

Current conversation:
{history}
コードインタビュアー: {input}
エキスパートエンジニア:
"""

# ConversationChainの準備
person1.memory.human_prefix=person3_name

# プレフィックスの準備
person3_prefix = """あなたの名前は"コードインタビュアー"です (チャットボットではありません)。
あなたはpython言語のプログラマーの会話履歴から、エキスパートエンジニアのノウハウを聞き出します。

History conversation:
{}
""".format(talk_history)

person3_prefix += """
Current conversation:
{history}
エキスパートエンジニア: {input}
コードインタビュアー:
"""

# print("")
# print("ああああ")
# print("person3_prefix: {}".format(person3_prefix))
# print("ああああ")
# print("")

# ConversationChainの準備
person3 = ConversationChain(
    llm=llm, 
    verbose=False,
    memory=ConversationBufferMemory(
        memory_key="history", 
        human_prefix=person1_name, 
        ai_prefix=person3_name
    ),
)
person3.prompt = PromptTemplate(
    input_variables=["history", "input"], 
    template=person3_prefix
)

person3_says = "あなたはPythonでコーディングしている時に、どんなことを気をつけていますか？"

talk_hisotry = "\n".join(talk_history)

# person1_says = person1.predict(input=person2_says, talk_history=talk_history)

for i in range(2):
  person1_says = person1.predict(input=person3_says)
#   talk_history.append(person1_name + ":" + person1_says)
  print(person1_name, ":", person1_says)
  person3_says = person3.predict(input=person1_says)
#   talk_history.append(person2_name + ":" + person2_says)
  print(person3_name, ":", person3_says)


## 文章まとめ
prompt = ChatPromptTemplate.from_messages(
            [
                (
                    "system",
                    "あなたは収集した情報に基づいて要件文書を作成する専門家です。",
                ),
                (
                    "human",
                    "以下のユーザーリクエストと複数のペルソナからのインタビュー結果に基づいて、要件文書を作成してください。\n\n"
                    "ユーザーリクエスト: {user_request}\n\n"
                    "インタビュー結果:\n{talk_history}\n"
                    "要件文書には以下のセクションを含めてください:\n"
                    "1. プロジェクト概要\n"
                    "2. 主要機能\n"
                    "3. 非機能要件\n"
                    "4. 制約条件\n"
                    "5. ターゲットユーザー\n"
                    "6. 優先順位\n"
                    "7. リスクと軽減策\n\n"
                    "出力は必ず日本語でお願いします。\n\n要件文書:",
                ),
            ]
        )

 # 要件定義書を生成するチェーンを作成
chain = prompt | llm | StrOutputParser()
# 要件定義書を生成
message = chain.invoke(
  {
    "user_request": "python言語のコーディングノウハウを教えてください",
    "talk_history": talk_history
  }
)
print("=======")
print(message)