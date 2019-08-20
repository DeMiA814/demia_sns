# To22

## 注
- staticファイルはAWSで管理
- データベースはpostgreSQL
- herokuでデプロイ

## ファイル構造
- django-to22
  - config  \プロジェクト全体の設定
    - backends.py
    - local_settings.py
    - settings.py \各種設定
    - urls.py \URL
    - wsgi.py
  - templates  \admin画面のhtml（使わない）
  - to22  \twitter認証以外の部分のメインフォルダ
    - migrations  \マイグレーション
    - templates
      - register  \ '/register/'下のhtmlファイル
      - to22  \ '/to22/'下のhtmlファイル
    - init.py
    - admin.py
    - apps.py
    - forms.py
    - models.py \データベースの定義
    - tests.py
    - urls.py
    - views.py
  - .gitignore
  - Procfile
  - manage.py
  - pip-selfcheck.json
  - requirements.txt  \デプロイ時にインストールするパッケージ
  - runtime.txt  \pythonのバージョン
