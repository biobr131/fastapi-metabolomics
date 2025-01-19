FastAPI App

`FastAPI`を用いてAPI開発するためのテンプレートリポジトリです。
データベースは`PostgreSQL`を使用します。
開発環境，本番環境をそれぞれ準備しています。

# 主要ライブラリ一覧

## 本番環境

インストールされる主なライブラリは以下の通りです。

- fastapi
- uvicorn
- psycopg
- sqlalchemy
- pydantic
- sqlmodel
- sqladmin
- alembic
- sqlacodegen
- fastapi-structlog
- sentry-sdk

なお，`sentry`は本番環境のみにインストールされます。


## 開発環境

本番環境にインストールされている主要ライブラリに加え，`pytest`，`sphinx`，`fastapi-debug-toolbar`などがインストールされます。

また，`JupyterLab`をインストールしたDocker imageも開発環境のみに含まれています。
このDocker imageには，一般的なデータサイエンスライブラリに加え，以下のバイオインフォマティクス・ケモインフォマティクス用のライブラリも含まれています。

- rdkit
- biopython
- bioinfokit
- scanpy
- pyopenms
- pyteomics
- bioconductor-deseq2
- bioconductor-edger


# セットアップ方法

## Dockerを使用する場合

まず，`app/db/`に`.env`を作成してください。記載内容は`.env.example`を参考にしてください。
以下のコマンドを実行することでDocker imageがビルドされます。

```
docker compose build
```

開発環境をビルドする場合は，`/app/db/.env.dev`を作成のうえ，以下のコマンドを実行してください。

```
docker compose -f compose.dev.yaml build
```

## ローカル環境を使用する場合(Windows)

`Python 3.12`の`venv`モジュールを用いて仮想環境を構築することを推奨します。
ルートディレクトリに置かれている`requirements.txt`では，開発環境用のライブラリがインストールされます。
本番環境用のライブラリをインストールしたい場合は，`dev.txt`の箇所を`prod.txt`に書き換えてください。

```
python -m venv .venv
.venv¥Scripts¥activate
pip install --upgrade pip
pip install -r requirements.txt
```

# 使用方法

## Dockerを使用する場合

以下のコマンドで本番環境のコンテナが起動します。

```
docker compose up -d
```
`localhost:80`がトップページになります。

以下のコマンドで各サービスのログを確認することができます。
```
docker compose logs postgres
docker compose logs fastapi
docker compose logs nginx
```

以下のコマンドでコンテナを停止します。
```
docker compose down
```

開発環境のコンテナの起動・停止は以下の通りです。ログを見る際も同様に`compose`ファイル名を明示します。
なお，`JupyterLab`は`localhost:8888`でアクセスできます。
```
docker compose -f compose.dev.yaml up -d
docker compose -f compose.dev.yaml down
```

## ローカル環境 (Windows) を使用する場合

本番環境，開発環境ともに`FastAPI`サーバーは以下のコマンドで起動します。
仮想環境を起動し，`main.py`に記載した`app`（`FastAPI`インスタンス）を呼び出します。
```
.¥.venv¥Scripts¥activate
cd app
uvicorn main:app
```

開発環境の`JupyterLab`は以下のコマンドで起動します。
自動起動したブラウザか，`localhost:8888`にアクセスすると，notebookを利用できます。
```
.¥.venv¥Scripts¥activate
jupyter lab
```
