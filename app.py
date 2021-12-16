import os
import discord
from datetime import datetime
import requests
import csv
import itertools
import random
from discord.ext import tasks
from flask import Flask
app = Flask(__name__)


potty_word_file = "potty_words.txt"
self_depr_file = "self_depr.txt"
API_KEY = os.environ['API_KEY']
ezslac_count = "ICOUNT"
env_variables = [ezslac_count]
responses_file = "responses.csv"
RESPONSE_RATE = 0.15


def run_bot(bot_data, responses):
    # Loading in words
    potty_words = load_file(potty_word_file)
    self_depr = load_file(potty_word_file).extend(load_file(self_depr_file))

    client = discord.Client()
    discord.Activity(name="Beep boop. I am wackymaster's bot", type=5)

    # Update responses each minute
    @tasks.loop(seconds=60)
    async def refresh_responses():
        nonlocal responses
        responses = load_data(responses_file)

    @client.event
    async def on_ready():
        print('We have logged in as {0.user}'.format(client))
        refresh_responses.start()

    @client.event
    async def on_message(message):
        # No infinite loops please
        if message.author == client.user:
            return

        # Basic commands to get running
        if message.content.startswith('$commit'):
            URL = "http://whatthecommit.com"
            r = requests.get(url=URL)
            commit = r.text.split('<p>')[1].split('</p>')[0].strip()
            await message.channel.send(commit)
        if 'joke' in message.content.lower():
            URL = "https://icanhazdadjoke.com/slack"
            r = requests.get(url=URL)
            await message.channel.send("Ahh, you have requested a joke I see...")
            await message.channel.send(r.json()['attachments'][0]['text'])
        if message.content.startswith('$stupidcommit'):
            await message.channel.send(f"Don't mess with me {message.author}")
        if message.content.startswith('$time'):
            current_time = datetime.now().strftime("%H:%M:%S")
            await message.channel.send(f'Current Time is {current_time}')

        # No mean words
        if str(message.author.name) == "eszlàc":
            for word in potty_words:
                if word in message.content.lower():
                    bot_data[ezslac_count] += 1
                    count = bot_data[ezslac_count]
                    await message.channel.send('charles_says_disabled_count++')
                    await message.channel.send(f'Occurences: {count} :(')
                    update_env(bot_data)
                    break

        # Adding rng to be less spammy
        if random.random() > RESPONSE_RATE:
            return

        # Key word responses
        for word in responses:
            if word in message.content.lower():
                await message.channel.send(random.choice(responses[word]))
                break

        if str(message.author.name) == "QLF9":
            for word in itertools.chain(potty_words, self_depr):
                if word in message.content.lower():
                    await message.channel.send('It\'s ok ')
                    break

    client.run(API_KEY)


def load_file(filename):
    words = []
    with open(filename, "r") as file:
        for line in file:
            words.append(line.strip())
    return words


def update_env(data):
    for key in data:
        os.environ[key] = data[key]
    return


def load_env(vars):
    data = {}
    for key in vars:
        val = os.environ[key]
        data[key] = int(val) if val.isdigit() else val
    return data


def load_data(filename):
    data = {}
    with open(filename) as csv_file:
        reader = csv.reader(csv_file)
        for line in reader:
            if not line:
                continue
            if line[1].isdigit():
                data[line[0]] = int(line[1])
            else:
                data[line[0]] = line[1:]
    csv_file.close()
    return data


@app.route("/")
def main():
    bot_data = load_env(env_variables)
    response_data = load_data(responses_file)
    print(bot_data, response_data)
    run_bot(bot_data, response_data)


if __name__ == "__main__":
    main()
