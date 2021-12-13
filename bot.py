from os import write
import discord
from datetime import datetime
import requests
import csv
import itertools

potty_word_file = "potty_words.txt"
self_depr_file = "self_depr.txt"
API_KEY = 'KEY GOES HERE'
responses = "data.csv"


def run_bot(bot_data):
    # Loading in words
    potty_words = load_file(potty_word_file)
    self_depr = load_file(potty_word_file).extend(load_file(self_depr_file))

    client = discord.Client()
    discord.Activity(name="Beep boop. I am wackymaster's bot", type=5)

    @client.event
    async def on_ready():
        print('We have logged in as {0.user}'.format(client))

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

        # Key word responses
        for word in bot_data:
            # i variables are internal, and have an integer value attached
            if word.startswith('i'):
                continue
            if word in message.content.lower():
                await message.channel.send(bot_data[word])
                break

        # No mean words on my watch
        if str(message.author.name) == "eszlàc":
            for word in potty_words:
                if word in message.content.lower():
                    bot_data['icount'] += 1
                    count = bot_data['icount']
                    await message.channel.send('charles_says_disabled_count++')
                    await message.channel.send(f'Occurences: {count} :(')
                    update_csv(bot_data)
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


def update_csv(bot_data):
    with open(responses, "w") as csv_file:
        writer = csv.writer(csv_file)
        for key in bot_data:
            writer.writerow((key, bot_data[key]))
    csv_file.close()
    return


def load_data():
    bot_data = {}
    with open(responses) as csv_file:
        reader = csv.reader(csv_file)
        for line in reader:
            if not line:
                continue
            bot_data[line[0]] = int(
                line[1]) if line[0].startswith('i') else line[1]
    csv_file.close()
    return bot_data


def main():
    bot_data = load_data()
    print(bot_data)
    run_bot(bot_data)


if __name__ == "__main__":
    main()
