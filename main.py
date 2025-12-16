from datetime import datetime, timedelta, timezone

from ps3838api.api import PinnacleClient

client = PinnacleClient()


client.get_bets(
    betlist="SETTLED",
    from_date=datetime.now(timezone.utc) - timedelta(days=1),
    to_date=datetime.now(timezone.utc),
)
