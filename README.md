# ZeroAuth Discord Bot

Authorization helper for friends in our ZeroTier network

### Setup

1. Clone/download this repo.

2. Use a virtual environment (`python -m venv venv`) and install the dependencies using `pip install -r requirements.txt`

3. Configuration of this bot is done by creating a `config.py` file in the root directory where the bot is with the following template:

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

4. Run the bot using `python bot.py`
