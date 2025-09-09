import tweepy
import os
import time

# --- GitHubのSecretsからキーとトークンを読み込む ---
API_KEY = os.environ.get("API_KEY")
API_KEY_SECRET = os.environ.get("API_KEY_SECRET")
ACCESS_TOKEN = os.environ.get("ACCESS_TOKEN")
ACCESS_TOKEN_SECRET = os.environ.get("ACCESS_TOKEN_SECRET")
# ----------------------------------------------------

def main():
    """過去のリプライをさかのぼって鍵アカウントをブロックする"""
    print("過去リプライのブロックプログラムを開始します。")

    client = tweepy.Client(
        consumer_key=API_KEY,
        consumer_secret=API_KEY_SECRET,
        access_token=ACCESS_TOKEN,
        access_token_secret=ACCESS_TOKEN_SECRET,
        wait_on_rate_limit=True # レートリミット時に自動で待機する設定
    )

    try:
        my_info = client.get_me(user_fields=["id"])
        my_user_id = my_info.data.id
        print(f"ログイン成功: @{my_info.data.username} (ID: {my_user_id})")
    except Exception as e:
        print(f"エラー: ログインに失敗。APIキーの設定を確認してください。")
        print(e)
        return

    print("\n過去のリプライをさかのぼって確認中...")

    total_blocked_count = 0

    try:
        # Paginatorを使い、最大2000件を上限として過去のメンションをさかのぼる
        # 無料APIの制限により、これより少ない件数しか取得できない場合が多いです
        paginator = tweepy.Paginator(
            client.get_users_mentions,
            id=my_user_id,
            expansions=["author_id"],
            user_fields=["protected"],
            max_results=100 # 1ページあたり100件取得
        ).flatten(limit=2000)

        for tweet in paginator:
            # ユーザー情報を取得 (API v2の仕様上、別途取得が必要)
            author_id = tweet.author_id
            if author_id == my_user_id:
                continue

            user_info = client.get_user(id=author_id, user_fields=["protected"])
            author = user_info.data

            if not author:
                continue

            print(f"--- チェック中: @{author.username} (ツイートID: {tweet.id}) ---")

            if author.protected:
                print(f"🚨 @{author.username} は鍵アカウントです。ブロックします。")
                try:
                    client.block(target_user_id=author.id)
                    print(f"✅ @{author.username} をブロックしました。")
                    total_blocked_count += 1
                    time.sleep(1) # 連続ブロックを避けるために1秒待機
                except Exception as e:
                    if "403 Forbidden" in str(e):
                        print(f"ℹ️ @{author.username} は既にブロック済みか、ブロックできないユーザーです。")
                    else:
                        print(f"❌ @{author.username} のブロックに失敗しました: {e}")
            else:
                print(f"🔓 @{author.username} は公開アカウントです。スキップします。")

    except Exception as e:
        print(f"エラー: リプライの取得中に問題が発生しました。")
        print(e)

    finally:
        print(f"\n--- 処理完了 ---")
        print(f"合計 {total_blocked_count} 人のユーザーをブロックしました。")


if __name__ == "__main__":
    main()
