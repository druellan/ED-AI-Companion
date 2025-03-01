# ED:AI Companion by druellan

A collection of Python scripts to monitor the Elite Dangerous journal files and provide audio feedback using OpenRouter services.

Remember to copy the `config.py.example` to `config.py` and fill in the required values.

You want to create your own parsers? Just create a new file in the parsers directory and follow the example of the existing ones.

This script is a work in progress, primarily for personal use, as a learning experience and to have fun with OpenRouter and ED.
The idea is to provide audio feedback for the most common events in the game, such as jumps, combat, docking, etc, while using small and free LLMs from OpenRouter.
Those events can be expanded to laverage web contents, such as EDSM data, or to pre-process the information before triggering the AI response.

For something more complete and polished, I recommend checking out the [COVAS:NEXT project](https://github.com/RatherRude/Elite-Dangerous-AI-Integration).

## Inspired by the work of:
- RatherRude - [Elite Dangerous AI Integration](https://github.com/RatherRude/Elite-Dangerous-AI-Integration)
- Brian Wilson - [EDDI](https://github.com/EDCD/EDDI)

## Third party APIs used:
- [EDSM](https://www.edsm.net/en/api-v1)
- [OpenRouter](https://openrouter.ai)
