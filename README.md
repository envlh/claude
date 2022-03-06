## Description

Claude is a bot framework to automatically add IDs from dictionaries to French lexemes on Wikidata.

Features:
* Crawls dictionaries, following redirects when relevant, and caching results.
* Matches lexemes using lemma, lexical category, and grammatical gender.
* Tracks added IDs to avoid re-adding them in case they are removed.
* Generates reports for unmatched lexemes ([example](https://www.wikidata.org/wiki/User:EnvlhBot/Reports/P10338)).

Dictionaries:
* Le Robert (file `lerobert.py`)
* Littré (file `littre.py`)
* TLFi (file `tlfi.py`, work in progress)

## Dependencies

* Python 3
* MySQL 5.7+

## Installation

### Python

Install Python. Example on a Debian-like system:

    apt install php python3 python3-pip

Download the project:

    git clone "https://github.com/envlh/claude.git"

Install the Python requirements. Example of the command to use at the root of the project:

    pip3 install -r requirements.txt

### MySQL

You can install the MySQL server using the [official repositories](https://dev.mysql.com/downloads/).

Create a new database on your MySQL server:

    CREATE DATABASE `claude` DEFAULT CHARACTER SET 'utf8mb4';

Create a user (change the password):

    CREATE USER 'claude'@'localhost' IDENTIFIED BY 'xxxxxxx';

Grant to the user all rights on the database:

    GRANT ALL ON `claude`.* TO 'claude'@'localhost';

Grant to the user the right to access files:

    GRANT FILE on *.* to 'claude'@'localhost';

Initialize the schema with the script `sql/schema.sql`.

## Configuration

Edit the file `conf/general.json`.

The bot uses [Pywikibot](https://www.mediawiki.org/wiki/Manual:Pywikibot). A way to login to Wikidata is to use a [bot password](https://www.mediawiki.org/wiki/Manual:Pywikibot/BotPasswords).

Download Pywikibot:

    git clone "https://gerrit.wikimedia.org/r/pywikibot/core"

After [creating your bot password](https://www.wikidata.org/wiki/Special:BotPasswords), generate configuration files:

    python3 pwb.py generate_user_files.py

Copy generated files `user-config.py` and `user-password.py` at the root of the `claude` project.

## Usage

    python3 bot.py

## Copyright

This project, by [Envel Le Hir](https://www.lehir.net/) (@envlh), is under AGPLv3 license. See `LICENSE`, `NOTICE`, and `CONTRIBUTORS` files for complete credits.
