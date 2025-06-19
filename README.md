# ZeroAuth Discord Bot

Authorization helper for friends in our ZeroTier network <br>

Currently supports the ZeroTier Central API. There is an [older commit/version that supports ZTNET](https://github.com/jerichosy/ZeroAuth-Discord-Bot/tree/5542062d87133049539ee843a77de4602bcd05eb) instead.

### Setup

1. Clone/download this repo.

2. Configuration of this bot is done by creating a `config.py` file in the root of the repo with the following template:

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
zt_ctrl_api_token = "" # your ZT Ctrl API access token
zt_ctrl_api_url = "" # your ZT Ctrl API url with `/api/v1` at the end
```

3. Use a virtual environment with `python -m venv venv` and install the dependencies using `pip install -r requirements.txt`. Then, run the bot using `python bot.py`. <br>
Alternatively, use Docker and run with `docker compose up`.
