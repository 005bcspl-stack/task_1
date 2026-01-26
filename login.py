from kiteconnect import KiteConnect
from key import api_k, api_s

kite = KiteConnect(api_key=api_k)

print("Open this URL in your browser:")
print(kite.login_url())

request_token = input("\nPaste request_token here: ").strip()

data = kite.generate_session(request_token, api_secret=api_s)

print("\nYour ACCESS TOKEN is:")
print(data["access_token"])