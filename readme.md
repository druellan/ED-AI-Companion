# ED:AI Companion by druellan

A collection of Python scripts to monitor the Elite Dangerous journal files and provide audio feedback using OpenRouter services.

Remember to copy the `config.py.example` to `config.py` and fill in the required values.
You want to create your own parsers? Just create a new file in the parsers directory and follow the example of the existing ones.
Do you want to use Cortana/Eva voice on Windows? Use the registry patch file included: Microsoft-Eva-Mobile.reg

This script is a work in progress, primarily for personal use, as a learning experience and to have fun with OpenRouter and ED.
The idea is to provide audio feedback for the most common events in the game, such as jumps, combat, docking, etc, while using the small and free LLMs from OpenRouter, that are usually limited in prompt size.
Since each event can have a personalized parser, post-processing and web content, such as EDSM data, can be injected before triggering the AI response. This also helps to reduce the size of the prompt.
I'm also keeping a small static "status" file for the ship fuel levels, last place visited, etc, that can be used on specific events, likes undocking from a station.

For something more complete and polished, I recommend checking out the [COVAS:NEXT project](https://github.com/RatherRude/Elite-Dangerous-AI-Integration) project.

## Inspired by the work of:
- RatherRude - [Elite Dangerous AI Integration](https://github.com/RatherRude/Elite-Dangerous-AI-Integration)
- Brian Wilson - [EDDI](https://github.com/EDCD/EDDI)

## Third party APIs used:
- [EDSM](https://www.edsm.net/en/api-v1)
- [OpenRouter](https://openrouter.ai)