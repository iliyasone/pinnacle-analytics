from datetime import datetime, timedelta, timezone

from ps3838api.api import PinnacleClient

from app.core.config import settings

client = PinnacleClient(settings.PS3838_LOGIN, settings.PS3838_PASSWORD, settings.PS3838_API_BASE_URL)


bets = client.get_bets(
    betlist="SETTLED",
    from_date=datetime.now(timezone.utc) - timedelta(days=30),
    to_date=datetime.now(timezone.utc),
)

print(len(bets))

client.get_client_balance()
