# ZeroAuth Discord Bot

Authorization helper for friends in our ZeroTier network

Configuration of this bot is done by creating a `config.py` file in the root directory where the bot is with the following template:

```python
# Discord Bot
client_id = "" # your bot's client/application ID
token = "" # your bot's token
debug = False # used to enable debug print statements
webhook_url = "" # Discord webhook URL for audit logging self-authorizations

# ZT
joinable_networks = [
    {"name": "", "network_id": ""}, # your ZeroTier network name and 16-digit network ID
    # add more dict for more networks
]
ztnet_api_token = "" # your ZTNET Rest API access token
ztnet_api_url = "" # your ZTNET Rest API url with `/api/v1` at the end
ztnet_orgid = "" # your ZTNET network's organization ID
```
