from ps3838api.api.client import PinnacleClient

client = PinnacleClient()
print("Balance:", client.get_client_balance()['availableBalance'])