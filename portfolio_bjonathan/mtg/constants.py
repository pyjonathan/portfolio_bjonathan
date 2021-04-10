from portfolio_bjonathan.models import AuthToken
from settings import USER_AGENT

BEARER_TOKEN_QUERY = AuthToken.query.first()
BEARER_TOKEN = BEARER_TOKEN_QUERY.token

URL_PREFIX = f"https://api.tcgplayer.com/v1.37.0/catalog"
PRICING_PREFIX = f"https://api.tcgplayer.com/v1.37.0/pricing/product"

PAYLOAD = {}
HEADERS = {
  'Authorization': f"Bearer {BEARER_TOKEN}",
  'User-Agent': USER_AGENT,
}

CATEGORY_ID = 1