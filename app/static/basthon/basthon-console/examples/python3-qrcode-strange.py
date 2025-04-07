import qrcode
from urllib.parse import quote

script = quote(__eval_data__["code"])
url = f"https://console.basthon.fr/?script={script}"

img = qrcode.make(url)

img.show()
