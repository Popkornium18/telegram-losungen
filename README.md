# telegram-losungen

This Telegram bot allows you to subscribe to the daily [Losung](https://www.losungen.de/die-losungen/) and query the Losung of a specific date.
Please note that all texts except the documentation is in _german_.

## Usage

You can add [@die\_losungen\_bot](https://t.me/die_losungen_bot) on Telegram.
The bot provides the following commands:

- `/abo`: Subscribe
- `/deabo`: Unsubscribe
- `/heute`: Get the Losung for today
- `/datum`: Get the Losung for a specific date (The date format is `DD.MM.YYYY`)
- `/hilfe`: Print a help message

## Hosting

If you want to host this bot yourself you have to clone the repository and create a new virtual environment in the directory of the cloned repo.

```
git clone https://github.com/Popkornium18/telegram-losungen
cd telegram-losungen
python -m venv venv
. venv/bin/activate
pip install wheel
pip install -r requirements.txt
```

After that you can import all available Losungen from the official download page.
Note that while the Losungen exist for literally multiple centuries, only the last ~2 years are distributed online.

```
python
from importer import initial_import
initial_import()
```

Next you have to copy the default configuration and add the API token of your bot.
Available configuration options are documented in the example config file as comments.

```
cp config.py{.example,}
```

Now you can run the bot like this:

```
python bot.py
```

If you want to use a systemd service to autostart the bot at boot time (which is _highly_ recommended), feel free to copy this template:

```
[Unit]
Description=Telegram Losungen Bot
After=network.target

[Service]
Type=simple
User=YOUR_USER
Group=YOUR_GROUP
WorkingDirectory=/PATH/TO/telegram-losungen
ExecStart=/PATH/TO/telegram-losungen/venv/bin/python bot.py
Restart=always

[Install]
WantedBy=multi-user.target
```
