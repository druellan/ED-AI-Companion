
# ED:AI Companion by druellan
A collection of Python scripts to monitor the Elite Dangerous journal files and provide audio feedback using *OpenRouter* services.

*This script is a work in progress, primarily for personal use, as a learning experience and to have fun with LLMs and ED. For something more complete and polished, I recommend checking out the [COVAS:NEXT project](https://github.com/RatherRude/Elite-Dangerous-AI-Integration).*

The idea is to provide audio feedback for the most common events in the game, such as jumps, combat, docking, etc., while using the small and free LLMs from *OpenRouter*, that are usually limited in prompt size.

Since each event can have a personalized parser, post-processing and web content, such as *EDSM* data, can be injected before triggering the AI response. This also helps to reduce the size of the prompt.

I'm also keeping a small static `ship-state.json` file for the ship fuel levels, last place visited, etc, that can be used to enrich the information on specific events.

### To make it work
You might need Python 3.x installed in the system.
 - Install the requirements with ```pip install -r requirements.txt```
 - Copy or rename the `config.py.example` file to `config.py`
 - Open the `config.py` and paste your OpenRouter key on the `LLM_API_KEY` variable. The script should work without any other modification, but take a look at the settings in case you want to change something.
 - To run the script use `python start.py` You can run the script right from the start or when ED: Dangerous is already working.

You want to create your own parsers? Just create a new file in the `/parsers` directory using the exact name of the event you want to parse. I recommend copying another parser that provides a similar functionality to use as a template. 
Do you want to use Cortana/Eva voice on Windows? Use the registry patch file included: `Microsoft-Eva-Mobile.reg` to make that voice available.

### Inspired by the work of:
- RatherRude - [Elite Dangerous AI Integration](https://github.com/RatherRude/Elite-Dangerous-AI-Integration)
- Brian Wilson - [EDDI](https://github.com/EDCD/EDDI)

### Third party APIs used:
- [EDSM](https://www.edsm.net/en/api-v1)
- [OpenRouter](https://openrouter.ai)