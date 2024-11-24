from langchain.chains.conversation.memory import ConversationBufferMemory
from langchain.chains import ConversationChain
from langchain.chains import LLMChain
from langchain import OpenAI
from langchain.prompts import PromptTemplate
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
import pprint

import operator
from typing import Annotated, Any, Optional

from dotenv import load_dotenv
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from langgraph.graph import END, StateGraph
from pydantic import BaseModel, Field

from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder

# .envファイルから環境変数を読み込む
load_dotenv()


# ペルソナを表すデータモデル
class Persona(BaseModel):
    name: str = Field(..., description="ペルソナの名前")
    background: str = Field(..., description="ペルソナの持つ背景")

# ペルソナのリストを表すデータモデル
class Personas(BaseModel):
    personas: list[Persona] = Field(
        default_factory=list, description="ペルソナのリスト"
    )

# インタビュー内容を表すデータモデル
class Interview(BaseModel):
    persona: Persona = Field(..., description="インタビュー対象のペルソナ")
    question: str = Field(..., description="インタビューでの質問")
    answer: str = Field(..., description="インタビューでの回答")


# インタビュー結果のリストを表すデータモデル
class InterviewResult(BaseModel):
    interviews: list[Interview] = Field(
        default_factory=list, description="インタビュー結果のリスト"
    )

# 議論内容を表すデータモデル
class Discussion(BaseModel):
    persona: Persona = Field(..., description="議論対象のペルソナ")
    discussion_history: str = Field(..., description="議論内容")

# 議論結果のリストを表すデータモデル
class Discusstionesult(BaseModel):
    interviews: list[Discussion] = Field(
        default_factory=list, description="議論結果のリスト"
    )

# 要件定義生成AIエージェントのステート
class InterviewState(BaseModel):
    user_request: str = Field(..., description="ユーザーからのリクエスト")
    personas: Annotated[list[Persona], operator.add] = Field(
        default_factory=list, description="生成されたペルソナのリスト"
    )
    interviews: Annotated[list[Interview], operator.add] = Field(
        default_factory=list, description="実施されたインタビューのリスト"
    )
    requirements_doc: str = Field(default="", description="生成された要件定義")
    iteration: int = Field(
        default=0, description="ペルソナ生成とインタビューの反復回数"
    )
    is_information_sufficient: bool = Field(
        default=False, description="情報が十分かどうか"
    )

# ペルソナを生成するクラス
class PersonaGenerator:
    def __init__(self, llm: ChatOpenAI, k: int = 5):
        self.llm = llm.with_structured_output(Personas)
        self.k = k

    def run(self, user_request: str) -> Personas:
        # プロンプトテンプレートを定義
        prompt = ChatPromptTemplate.from_messages(
            [
                (
                    "system",
                    "あなたはユーザーインタビュー用の多様なペルソナを作成する専門家です。",
                ),
                (
                    "human",
                    f"以下のユーザーリクエストに関するインタビュー用に、{self.k}人の多様なペルソナを生成してください。\n\n"
                    "ユーザーリクエスト: {user_request}\n\n"
                    "各ペルソナには名前と簡単な背景を含めてください。年齢、性別、職業、技術的専門知識において多様性を確保してください。",
                ),
            ]
        )
        # ペルソナ生成のためのチェーンを作成
        chain = prompt | self.llm
        # ペルソナを生成
        return chain.invoke({"user_request": user_request})
    
# 議論を実施するクラス
class DiscussionConductor:
    def __init__(self, llm: ChatOpenAI):
        self.llm = llm

    def run(self, user_request: str, personas: list[Persona]) -> InterviewResult:
        #  議論内容を生成
        discussions = self._generate_discusstion_history(
            user_request=user_request, personas=personas
        )
        # 質問と回答の組み合わせからインタビューリストを作成
        interviews = self._create_interviews(
            personas=personas, discussions=discussions
        )
        # インタビュー結果を返す
        return InterviewResult(interviews=interviews)
    
    def _generate_discusstion_history(
        self, user_request: str, personas: list[Persona]
            ) -> list[str]:
                
        prompt = ChatPromptTemplate.from_messages(
            [
                ("system", "あなたはpython言語でのソフトウェア開発経験が豊富です。python言語のプログラミング時にいろいろエキスパートとして意識しながらコーディングしています"),
                MessagesPlaceholder("chat_history", optional=True),
                ("human", "あなたはPythonでコーディングしている時に、どんなことを気をつけていますか？"),
            ]
        )

        prompt_value = prompt.invoke(
            {
                "chat_history": [
                    # ToDo：人間、AI関係なく全会話履歴を持ってきたい
                    HumanMessage(content="こんにちは！私はジョンと言います！"),
                    AIMessage("こんにちは、ジョンさん！どのようにお手伝いできますか？"),
                ],
                "input": "私の名前が分かりますか？",
            }
        )

        # 議論生成のためのプロンプトを定義
        # # プレフィックスの準備
        # expart_prefix = """あなたの名前は"エキスパートエンジニア"です (チャットボットではありません)。
        # あなたはpython言語でのソフトウェア開発経験が豊富です。
        # python言語のプログラミング時にいろいろエキスパートとして意識しながらコーディングしています

        # Current conversation:
        # {history}
        # ビギナーエンジニア: {input}
        # エキスパートエンジニア:
        # """

        # # ConversationChainの準備
        # expart = ConversationChain(
        #     llm=llm, 
        #     verbose=False,
        #     memory=ConversationBufferMemory(
        #         memory_key="history", 
        #         human_prefix=beginner_name, 
        #         ai_prefix=expart_name
        #     ),
        # )
        # expart.prompt = PromptTemplate(
        #     input_variables=["history", "input"], 
        #     template=expart_prefix
        # )


        # # プレフィックスの準備
        # beginner_prefix = """あなたの名前はビギナーエンジニアです (チャットボットではありません)。
        # あなたはPython言語の初学者です。どんなことに注意しながらコーディングしたらいいのか知識がありません。

        # Current conversation:
        # {history}
        # エキスパートエンジニア: {input}
        # ビギナーエンジニア:
        # """

        # # ConversationChainの準備
        # beginner = ConversationChain(
        #     llm=llm, 
        #     verbose=False, 
        #     memory=ConversationBufferMemory(
        #         memory_key="history", 
        #         human_prefix=expart_name, 
        #         ai_prefix=beginner_name
        #     ),
        # )
        # beginner.prompt = PromptTemplate(
        #     input_variables=["history", "input"], 
        #     template=beginner_prefix
        # )

        # 議論生成のためのチェーンを作成
        question_chain = question_prompt | self.llm | StrOutputParser()

        # 各ペルソナに対する質問クエリを作成
        question_queries = [
            {
                "user_request": user_request,
                "persona_name": persona.name,
                "persona_background": persona.background,
            }
            for persona in personas
        ]
        # 質問をバッチ処理で生成
        return question_chain.batch(question_queries)

    def _create_interviews(
        self, personas: list[Persona], questions: list[str], answers: list[str]
    ) -> list[Interview]:
        # ペルソナ毎に質問と回答の組み合わせからインタビューオブジェクトを作成
        return [
            Interview(persona=persona, question=question, answer=answer)
            for persona, question, answer in zip(personas, questions, answers)
        ]


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

interviewer_says = "あなたはPythonでコーディングしている時に、どんなことを気をつけていますか？"

talk_hisotry = "\n".join(talk_history)

# expart_says = expart.predict(input=beginner_says, talk_history=talk_history)

for i in range(2):
  expart_says = expart.predict(input=interviewer_says)
#   talk_history.append(expart_name + ":" + expart_says)
  print(expart_name, ":", expart_says)
  interviewer_says = interviewer.predict(input=expart_says)
#   talk_history.append(beginner_name + ":" + beginner_says)
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