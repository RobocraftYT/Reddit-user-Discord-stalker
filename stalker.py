import sys
import time

import praw
import praw.exceptions
import prawcore
import prawcore.exceptions
import requests

# Backwards compatibility up until Python 3.7
if sys.version_info >= (3, 11):
    import tomllib
else:
    import tomli as tomllib

script_version_number = "1.1"

with open("config.toml", "rb") as config_file:
    configuration = tomllib.load(config_file)

reddit_user_agent = f'discord-webhook:com.{configuration["credentials"]["reddit_user_agent"]}:{script_version_number}'

stalked_users_number = len(configuration["users"]["stalked-users"])

reddit = praw.Reddit(
    client_id = configuration["credentials"]["reddit_client_id"],
    client_secret = configuration["credentials"]["reddit_client_secret"],
    user_agent = reddit_user_agent,
    ratelimit_seconds=840,
)

# Main loop
def main():
    print(f"Logged in as: {reddit.config.user_agent}")
    # Only do this if there's more than 1 user since it's less optimal than the method for a single user
    if stalked_users_number > 1:
        print("Multiple usernames detected, entering multi-user mode")
        user_streams = []
        for user in configuration["users"]["stalked-users"]:
            try:
                user_streams.append(reddit.redditor(user).stream.submissions(skip_existing = True, pause_after = -1))
            except prawcore.exceptions.NotFound:
                print(f"WARNING: USER {user} IS NOT A VALID REDDIT USER AND HAS BEEN IGNORED")
        if not user_streams:
            print(f'ERROR: NO VALID USERS, EXITING...\nAttempted users: {configuration["users"]["stalked-users"]}\n\nChange the value of \"stalked-users\" inside config.toml')
            sys.exit(1)
        while True:
            try:
                for user_submission_stream in user_streams:
                    for submission in user_submission_stream:
                        if submission == None or submission.created_utc < (time.time() - 300):
                            break
                        for webhook_url, webhook_message in configuration["webhooks"].items(): # i should have named it whurl for the bit
                            data = {"content": webhook_message.format(author = submission.author.name, title = submission.title, url = submission.url, selftext = submission.selftext)}
                            response = requests.post(webhook_url, json=data,)
                            if response.status_code == 204:
                                print(f'Post {submission.id} was sent succesfully to the webhook {webhook_url.split("/")[5]}')
                            else:
                                print(f'\nERROR: WEB HOOKEN\'T\nFailed to send post {submission.id} to webhook {webhook_url.split("/")[5]}, return code was {response.status_code}')
                        print("\n")

            except praw.exceptions.RedditAPIException as error:
                print(f"ERROR: {error}\n(usually happens when the ratelimit time is greater than the allowed time (shouldnt really happen but PRAW hates me so...))")

            except Exception as error:                                                                                      # look
                print(f"ERROR: {error}\n(imma be honest this shouldnt happen but its just here so it doesnt shit itself)")  # im too lazy to fix it or restart the program
    
    # Do it more efficiently if its just a single user
    elif stalked_users_number == 1:
        print("One username detected, entering single-user mode")
        while True:
            try:
                user = configuration["users"]["stalked-users"][0]
                for submission in reddit.redditor(user).stream.submissions(skip_existing = True):
                    if submission.created_utc >= (time.time() - 300):
                        for webhook_url, webhook_message in configuration["webhooks"].items():
                            data = {"content": webhook_message.format(author = submission.author.name, title = submission.title, url = submission.url, selftext = submission.selftext)}
                            response = requests.post(webhook_url, json=data,)
                            if response.status_code == 204:
                                print(f'Post {submission.id} was sent succesfully to the webhook {webhook_url.split("/")[5]}')
                            else:
                                print(f'\nERROR: WEB HOOKEN\'T\nFailed to send post {submission.id} to webhook {webhook_url.split("/")[5]}, return code was {response.status_code}')
                        print("\n")

            except prawcore.exceptions.NotFound:
                print(f'ERROR: NO VALID USERS, EXITING...\nAttempted user: {configuration["users"]["stalked-users"][0]}\n\nChange the value of\"stalked-users inside config.toml')

            except praw.exceptions.RedditAPIException as error:
                print(f'ERROR: {error}\n(usually happens when the ratelimit time is greater than the allowed time but that shouldnt happen)')

            except Exception as error:
                print(f"ERROR: {error}\n(imma be honest this shouldnt happen but its just here so it doesnt shit itself)")

    else:
        print("ERROR: NO USERNAMES DETECTED\nMake sure to set all of the usernames on \"stalked-users\" inside config.toml")



if __name__ == "__main__":
    if len(sys.argv) > 1:
        if "--create-app-name" == sys.argv[1]:
            reddit_user = input("Input your raw Reddit username (without the u/ and all lowercase) (can only include normal letters, numbers, - and _) (doesnt matter if it doesnt exactly match your username): ")
            reddit_app_name = input("Input your desired Reddit app name (can only include normal letters and -): ")
            print(f"\nHere is the app name for your Reddit app (go to https://www.reddit.com/prefs/apps, create a *SCRIPT* app, set the name to it, and set redirect url to http://localhost/):\ncom.{reddit_user}.{reddit_app_name}\n\nAnd here is what you need to put in \"reddit_user_agent\" (inside config.toml):\n{reddit_user}.{reddit_app_name}")

        elif "-v" in sys.argv or "--version" in sys.argv[1]:
            print(f"Version number: {script_version_number}")

        elif "--user-agent" in sys.argv[1]:
            print(reddit_user_agent)

        elif "-h" in sys.argv or "--help" in sys.argv[1]:
            print(f'''Reddit user Discord stalker {script_version_number}
By @robocraft. on discordu

USAGE: run the script with a python interpreter in the command line like so:
    python3 stalker.py [option1] [option2]...u

OPTIONS:
    --create-app-name   Guided setup for the Reddit app name
    -v --version        Print the script version number
    --user-agent        Print the full reddit user agent
    -h --help           Print this message

Special thanks to @feltmacaroon389 on discord for putting up with my shit during development of this script.
May god have mercy on the souls of those who dare look at the source code.''') # so how was it :)
        
        else:
            print(f"Invalid option {sys.argv[1]}, run \"python3 stalker.py -h\" for help")
            sys.exit(1)

        sys.exit(0)
    else:
        try:        # i dont trust my code
            main()  # was gonna say im surprised it works but im writing this after changing like 100 lines and i havent tested it at all yet so...
                    # update: it doesnt work. like at all. idk wtf happened. update 2: i accidentally set the reddit client id as the client secret. woopsies
        except KeyboardInterrupt:
            sys.exit(0)

        except Exception as error:
            print(f"you fucked it up big time (outside the main loop): {error}")
            sys.exit(1)
            # no you're not getting traceback fuck you
