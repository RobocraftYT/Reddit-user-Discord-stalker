# Reddit-user-Discord-stalker
Disclaimer: the name is for shits and giggles, this script isn't intended to actually stalk people, its more for communities where people want to be notified when someone important posts

## Installation and running
- Clone the repo: `git clone https://github.com/RobocraftYT/Reddit-user-Discord-stalker.git`
- Change working directory to the repo: `cd Reddit-user-Discord-stalker`
- Install dependencies: `pip3 install -r requirements.txt`
- Run `python3 stalker.py` (Python 3.7+ required)

## Configuration
- All of the configuration is done inside the `config.toml` file
- Change the values inside the `[credentials]` table accordingly
  - Run `python3 stalker.py --create-app-name` to get a proper app name and follow the steps it tells you to create the app
  - You can run `python3 stalker.py -h` for a list of miscellaneous options
- Add users inside `stalked-users` to make the webhook notify you when they post
- Add webhook urls and their messages on a new line after `[webhooks]` to make them notify you when users inside `stalked-users` post
  - Webhook urls and messages must be inside quotation marks like so: `"https://webhook.example/" = "message"`
  - You can put special arguments inside `{}` which will get replaced with the respective value, here's a list of all of them:
    - `{author}`: will get replaced with the author of the post
    - `{title}`: will get replaced with the title of the post
    - `{url}`: will get replaced with the url of the post
    - `{selftext}`: will get replaced with the selftext of the post (fancy way of saying the post body)

## Example configuration
```
[credentials]
reddit_client_id = "<your reddit client id"
reddit_client_secret = "<your reddit client secret>"
reddit_user_agent = "<your reddit user agent>"

[users]
stalked-users = [
  "spez",
  "felt389",
]

[webhooks]
"<webhook 1>" = "u/{author} just posted! ||@everyone||\n\n[{title}](<{url}>)\n{selftext}"
"<webhook 2>" = "an admin just posted on reddit:\n\n{url}"
```

## License
idk do whatever the fuck you want i dont care foss for the win babyyy
