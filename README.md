# Voting Bot

This is the basic voting bot I coded once for fun. I am sharing it in case some code is useful for somebody.

Its main characteristics are:

* Use different IPs through Tor Network
* IP is changed after a random number of votes
* Run as many bots as wanted in parallel (each with a different IP)

## Requirements

You need to have installed:

* Python
* Stem (python library)
* PhantomJS
* Tor

In macOS:
```bash
brew install python phantomjs tor
pip install stem
```

## Use
```bash
# Run 1 bot
python bot.py 1

# Run 5 bots
python bot.py 5
```

## Configuration

The bot will assume there is `phantom.js` file (a PhantomJS script) with the instructions of how a vote is performed.
You need to write this file.
You can find an example in `phantom.example.js`. Don't forget to fill the configuration part.
