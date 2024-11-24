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
expart_name = "エキスパートエンジニア"
beginner_name = "ビギナーエンジニア"

# プレフィックスの準備
expart_prefix = """あなたの名前は"エキスパートエンジニア"です (チャットボットではありません)。
あなたはpython言語でのソフトウェア開発経験が豊富です。
python言語のプログラミング時にいろいろエキスパートとして意識しながらコーディングしています

Current conversation:
{history}
ビギナーエンジニア: {input}
エキスパートエンジニア:
"""

# ConversationChainの準備
expart = ConversationChain(
    llm=llm, 
    verbose=False,
    memory=ConversationBufferMemory(
        memory_key="history", 
        human_prefix=beginner_name, 
        ai_prefix=expart_name
    ),
)
expart.prompt = PromptTemplate(
    input_variables=["history", "input"], 
    template=expart_prefix
)


# プレフィックスの準備
beginner_prefix = """あなたの名前はビギナーエンジニアです (チャットボットではありません)。
あなたはPython言語の初学者です。どんなことに注意しながらコーディングしたらいいのか知識がありません。

Current conversation:
{history}
エキスパートエンジニア: {input}
ビギナーエンジニア:
"""

# ConversationChainの準備
beginner = ConversationChain(
    llm=llm, 
    verbose=False, 
    memory=ConversationBufferMemory(
        memory_key="history", 
        human_prefix=expart_name, 
        ai_prefix=beginner_name
    ),
)
beginner.prompt = PromptTemplate(
    input_variables=["history", "input"], 
    template=beginner_prefix
)

beginner_says = "あなたはPythonでコーディングしている時に、どんなことを気をつけていますか？"

talk_history = []

first_talk = beginner_name + ":" + beginner_says
print(beginner_name + ":" + beginner_says)

talk_history.append(first_talk)

for i in range(2):
  expart_says = expart.predict(input=beginner_says)
  talk_history.append(expart_name + ":" + expart_says)
  print(expart_name, ":", expart_says)
  beginner_says = expart.predict(input=expart_says)
  talk_history.append(beginner_name + ":" + beginner_says)
  print(beginner_name, ":", beginner_says)

# print(expart.message)

print("---")
# print(talk_history)

for talk in  talk_history:
  print(talk)

## インタビューを追加

# 名前の準備
interviewer_name = "コードインタビュアー"

# プレフィックスの準備
expart_prefix = """あなたの名前は"エキスパートエンジニア"です (チャットボットではありません)。
あなたはpython言語でのソフトウェア開発経験が豊富です。
python言語のプログラミング時にいろいろエキスパートとして意識しながらコーディングしています

Current conversation:
{history}
コードインタビュアー: {input}
エキスパートエンジニア:
"""

# ConversationChainの準備
expart.memory.human_prefix=interviewer_name

# プレフィックスの準備
interviewer_prefix = """あなたの名前は"コードインタビュアー"です (チャットボットではありません)。
あなたはpython言語のプログラマーの会話履歴から、エキスパートエンジニアのノウハウを聞き出します。

History conversation:
{}
""".format(talk_history)

interviewer_prefix += """
Current conversation:
{history}
エキスパートエンジニア: {input}
コードインタビュアー:
"""

# print("")
# print("ああああ")
# print("interviewer_prefix: {}".format(interviewer_prefix))
# print("ああああ")
# print("")

# ConversationChainの準備
interviewer = ConversationChain(
    llm=llm, 
    verbose=False,
    memory=ConversationBufferMemory(
        memory_key="history", 
        human_prefix=expart_name, 
        ai_prefix=interviewer_name
    ),
)
interviewer.prompt = PromptTemplate(
    input_variables=["history", "input"], 
    template=interviewer_prefix
)

interview_history = []

interviewer_says = "あなたはPythonでコーディングしている時に、どんなことを気をつけていますか？"

interview_history.append(interviewer_says)

talk_history = "\n".join(talk_history)

# expart_says = expart.predict(input=beginner_says, talk_history=talk_history)

for i in range(2):
  expart_says = expart.predict(input=interviewer_says)
  interview_history.append(expart_name + ":" + expart_says)
  print(expart_name, ":", expart_says)
  interview_says = interviewer.predict(input=expart_says)
  interview_history.append(beginner_name + ":" + beginner_says)
  print(interviewer_name, ":", interviewer_says)


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
                    "インタビュー結果:\n{interview_history}\n"
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
    "interview_history": interview_history
  }
)
print("=======")
print(message)