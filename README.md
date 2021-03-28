# arxiv-vanity-bot for telegram

Telegram for some reason doesn't show snippets for links from arxiv.org site. This bot created to get work around of this problem. It is useful to having this bot in chats where you can share links from arxiv and bot will replying on that messages with some kind of snippets with title and description of paper and link to mobile friendly service for arxiv papers - arxiv-vanity.com

Ready to use bot: t.me/arxiv_vanity_bot

## Installation

```bash
git clone https://github.com/metya/vanity-bot
```

After that create file in the root of repository with name "token" and put there text below

```plaintext
API_TOKEN=your_bot_token
```

And after that just

```bash
docker compose up -d
```

or use enviroments variable with compose instead of token file

```bash
docker-compose run -d -e API_TOKEN=your_bot_token bot
```

## Usage

Add your bot in chat where you disscuss arxiv papers and enjoy. Or use my bot t.me/arxiv_vanity_bot

## Illustration

![](assets/bot.png)