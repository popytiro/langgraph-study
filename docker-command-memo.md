# Docker環境構築手順
## Dockerイメージ作成
```
docker image build -t {イメージ名}
```
例
```
docker image build -t ubuntu24 .
```
## Dockerコンテナ作成
```
docker container run --name {コンテナ名} -v {ホストのパス}:{コンテナ内のパス} --env-file {変数書いているファイル} -it {image名}
```
- 例
```
docker container run --name elicitoron -v $(pwd)/src:/elicitoron/src --env-file .env -it ubuntu24
```

## chapter10を動かすために追加したライブラリ
```
pip install --break-system-packages python-dotenv
```
```
pip install --break-system-packages langchain_core
```
```
pip install --break-system-packages langchain_openai
```
```
pip install --break-system-packages langgraph
```

## chapter5を動かすために追加したライブラリ
```
pip install --break-system-packages langchain_community
```

## chapter6を動かすために追加したライブラリ
```
pip install --break-system-packages GitPython
```
```
apt install -y git
```
```
pip install --break-system-packages langchain_chroma
```

## two agentを実行するために入れた
```
pip install --break-system-packages langchain_anthropic
```

## コンテナ内で日本語をサポート(うまくいかなかった)
```
apt-get update
```
```
apt-get install -y locales
```
```
locale-gen ja_JP.UTF-8
```
```
update-locale LANG=ja_JP.UTF-8
```
```
exec bash
```

- 最後にコンテナ再起動
```
docker container restart {コンテナ名orコンテナid}
```

### chapter10の実行コマンド例
```
python3 main.py --task "スマートフォン向けの健康管理アプリを開発したい"
```