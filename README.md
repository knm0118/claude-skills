# Claude Skills

日常を効率化するための自作 Claude スキル集です。GitHub Pages でカテゴリ別に一覧できます。

## フォルダ構成

```
skills/
  <カテゴリ>/
    <スキル名>/
      SKILL.md
categories.json   カテゴリの表示名と並び順
scripts/build.py  一覧ページと zip を _site/ に作る
```

## スキルを追加するとき

1. `skills/<カテゴリ>/<スキル名>/SKILL.md` を作る（フロントマターの `name` はフォルダ名と同じにする）
2. 新しいカテゴリなら `categories.json` に追加する
3. main ブランチに push すると、GitHub Actions がサイトを更新する

手元で確認するときは `python scripts/build.py` を実行し、`_site/index.html` を開きます。

## 使い方

サイトから zip をダウンロードし、claude.ai の「設定 → 機能 → スキル」からアップロードします。
