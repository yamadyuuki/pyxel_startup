import requests

cities = [
    "Saitama", "Kawagoe", "Tokorozawa", "Koshigaya",
    "Kumagaya", "Kasukabe", "Honjo", "Chichibu"
]

def main():
    print("現在の東京の天気情報を取得します...")
    for city in cities:
        url = f"https://wttr.in/{city}?format=3"
        try:
            response = requests.get(url)
            print(response.text)
        except Exception as e:
            print(f"{city} の取得に失敗: {e}")

if __name__ == "__main__":
    main()


# def main():
#     print("現在の東京の天気情報を取得します...")

#     url = "https://wttr.in/Tokyo?format=3"  # APIキー不要のシンプル天気API
#     try:
#         response = requests.get(url)
#         print(f"天気情報：{response.text}")
#     except Exception as e:
#         print(f"エラーが発生しました: {e}")

