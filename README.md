# Freelancer Data Extractor

This Python script takes in a Discord bot token and returns a CSV file containing the usernames, 
IDs, service type, and forum status of the members in a specified Discord server.

## Requirements
- Python 3
- 'setuptools'
- `discord.py`
- `colorlog`

## Installation

### Nix (If you're using NixOS or a Nix environment)
```bash
nix run github::smpsales/freelancer-data-extractor <DISCORD_TOKEN> <OUTPUT_DIR>
```

### Standalone
```bash
git clone github.com:smpsales/freelancer-data-extractor.git
cd freelancer-data-extractor
pip install -r requirements.txt
python main.py <DISCORD_TOKEN> <OUTPUT_DIR>
```

## Arguments

- `<DISCORD_TOKEN>`: Your Discord bot token.
- `<OUTPUT_DIR>`: The directory where the CSV file will be saved.