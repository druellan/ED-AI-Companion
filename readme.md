# ED:AI Companion
A collection of Python scripts to monitor the Elite Dangerous journal files and provide audio feedback using *OpenRouter* services.

*This script is a work in progress, primarily for personal use, as a learning experience, and to have fun with LLMs and ED. For something more complete and polished, I recommend checking out the [COVAS:NEXT project](https://github.com/RatherRude/Elite-Dangerous-AI-Integration).*

### Goal
The idea is to provide audio feedback for the most common events in the game, such as jumps, combat, docking, etc., while using the small and *free* LLMs from *OpenRouter*. Unlike COVAS:NEXT, this project does not provide interactivity with the AI, and the intention is to have an intelligence that can provide really useful information to the player without any input.

### Features
* A minimal but descriptive prompt tailored specifically for the game. The AI can decide to analyze the events and provide feedback or just remain silent.
* Works well with free and small models.
* Each event can have a personalized parser that can be used to preprocess and enrich the information with web content and third-party APIs.
* Grouping of consecutive events to send them in bulk to the AI.
* The AI can make use of tools; we are injecting them directly in the system prompt to bypass the restrictions free LLMs usually have, so results can vary.
* Memory bank:
  - `ship-state.json` - (fuel levels, last place visited, etc)
  - `missions_memory.json` - active missions
  - `event_memory.json` - list of the last 20.000 events in the game
  - `response_memory.json` - list of the last 20.000 AI responses
* Automatic retrieval of the last 20 events and AI responses on each prompt. Access to 100 more via the tools.
* Average token count of 3.000 tokens per event.

### Demo Videos
[Reacting to undock, new destination, radio chatter, and system arrival](https://vimeo.com/1074661030) (Edge TTS without audio filters)

[Reacting to mining: core found](https://vimeo.com/1074660573) (Edge TTS with audio filters)

### To make it work
You might need Python 3.x installed in the system.
 - Install the requirements with ```pip install -r requirements.txt```
 - Copy or rename the `config.py.example` file to `config.py`
 - Open the `config.py` and paste your OpenRouter key on the `LLM_API_KEY` variable. The script should work without any other modification, but take a look at the settings in case you want to change something.
 - To run the script use `python start.py` You can run the script right from the start or when ED: Dangerous is already running.

You want to create your own parsers? Just create a new file in the `/parsers` directory using the exact name of the event you want to parse. I recommend copying another parser that provides a similar functionality to use as a template. 
Do you want to use Cortana/Eva voice on Windows? Use the registry patch file included: `Microsoft-Eva-Mobile.reg` to make that voice available.

### About the config file
I'm changing the configurations a LOT, so new versions of the project might require update the config.py file.

### Inspired by the work of:
- RatherRude - [Elite Dangerous AI Integration](https://github.com/RatherRude/Elite-Dangerous-AI-Integration)
- Brian Wilson - [EDDI](https://github.com/EDCD/EDDI)

### Third party APIs used:
- [EDSM](https://www.edsm.net/en/api-v1)
- [OpenRouter](https://openrouter.ai)
