# Counter-Strike 2 player reports compilation

## Prerequisites

### API-key

A Steam Web API key is needed to look up a player's Steam ID, get yours here: https://steamcommunity.com/dev/apikey

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

## Quick start

```bash
uv venv
source .venv/bin/activate
uv sync --locked
uv run --env-file .env main.py
```

Show all options using `--help`

```
usage: main.py [-h] [-v] [--input INPUT] [--output OUTPUT] [--no-api] [--format {json,text}]

options:
  -h, --help            show this help message and exit
  -v, --verbose         verbose mode, show more info
  --input INPUT         the input file `path/to/reports.html` [DEFAULT=data/reports.html]
  --output OUTPUT       the output file `path/to/output.json` [DEFAULT=output/output.json]
  --no-api              set this flag if you DO NOT wish to use the Steam API to lookup accounts Steam IDs
  --format {json,text}  the output format [DEFAULT=json]
```

If you're feeling frisky, send Valve an email at <a href="mailto:cs2team@valvesoftware.com">
cs2team@valvesoftware.com</a>
to let them know you also feel helpless in this farm bot situation, and perhaps attach the compiled `output.json` file.
