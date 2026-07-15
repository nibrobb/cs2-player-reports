# Counter-Strike 2 player reports compilation

## Prerequisites

### API-key
A Steam Web API key is needed to lookup a player's Steam ID, get yours here: https://steamcommunity.com/dev/apikey

Rename the `.env.template` file to `.env`, then paste your key after the equal sign
```bash
mv .env.template .env
```

### Player reports
Go to `https://steamcommunity.com/id/YOUR_USERNAME_HERE/gcpd/730/?tab=playerreports`

1. Scroll to the bottom
2. Click "LOAD MORE HISTORY"
3. Repeat steps 1-2 until you have enough
4. <kbd>Ctrl</kbd> + <kbd>S</kbd> to save the dump, name it `reports.html`
5. Copy `reports.html` into `data/`

## Generate JSON dump with player IDs

```bash
uv sync --locked
source .venv/bin/activate
uv run --env-file .env main.py
```

If you're feeling frisky, send Valve an email at <a href="mailto:cs2team@valvesoftware.com">cs2team@valvesoftware.com</a> to let them know you also feel helpless in this farm bot situation, and perhaps attach the compiled `output.json` file.
