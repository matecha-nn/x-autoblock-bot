import tweepy
import os # osモジュールを追加

# --- GitHubのSecretsからキーとトークンを読み込む ---
API_KEY = os.environ.get("API_KEY")
API_KEY_SECRET = os.environ.get("API_KEY_SECRET")
ACCESS_TOKEN = os.environ.get("ACCESS_TOKEN")
ACCESS_TOKEN_SECRET = os.environ.get("ACCESS_TOKEN_SECRET")
# ----------------------------------------------------

def main():
    """メインの処理"""
    print("日次自動ブロックプログラムを開始します。")

    client = tweepy.Client(
        consumer_key=API_KEY,
        consumer_secret=API_KEY_SECRET,
        access_token=ACCESS_TOKEN,
        access_token_secret=ACCESS_TOKEN_SECRET
    )

    try:
        my_info = client.get_me(user_fields=["id"])
        my_user_id = my_info.data.id
        print(f"ログイン成功: @{my_info.data.username} (ID: {my_user_id})")
    except Exception as e:
        print(f"エラー: ログインに失敗。APIキーの設定を確認してください。")
        print(e)
        return

    print("新しいリプライを確認中...")
    try:
        mentions = client.get_users_mentions(
            id=my_user_id,
            expansions=["author_id"],
            user_fields=["protected"]
        )

        if not mentions.data:
            print("新しいリプライはありませんでした。")
            return

        users_dict = {user["id"]: user for user in mentions.includes.get("users", [])}

        for tweet in mentions.data:
            author = users_dict.get(tweet.author_id)
            if not author or author.id == my_user_id:
                continue

            print(f"--- リプライID: {tweet.id}, ユーザー: @{author.username} ---")

            if author.protected:
                print(f"🚨 @{author.username} は鍵アカウントです。ブロックします。")
                try:
                    client.block(target_user_id=author.id)
                    print(f"✅ @{author.username} をブロックしました。")
                except Exception as e:
                    if "403 Forbidden" in str(e):
                        print(f"ℹ️ @{author.username} は既にブロック済みか、ブロックできないユーザーです。")
                    else:
                        print(f"❌ @{author.username} のブロックに失敗しました: {e}")
            else:
                print(f"🔓 @{author.username} は公開アカウントです。スキップします。")

        print("\n処理が完了しました。")
    except Exception as e:
        print(f"エラー: リプライの取得中に問題が発生しました。")
        print(e)

if __name__ == "__main__":
    main()
