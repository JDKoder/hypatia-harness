# hypatia-harness
_Harness for Locally Served LLM_
Provides structure for the LLM to interact with the user and complete tasks safely.  As much as possible, will give the LLM context to previous conversations that it can access at will.

This model will be allowed to compile core memories that it may load between runs.  This is a test to give it a more comprehensive personality.


How Her Evolution Works Now
You chat with Hypatia as normal.
When you are ready to stop, you type _exit_ or _quit_.
Instead of instantly closing, the terminal will display: [System] Please wait... Hypatia is autonomously reflecting on today's conversation to grow her memory...
She writes her own thoughts down, appends them to your hypatia_memory.json file with a fresh date tag, and finishes closing.

If you would like to override the behavior and quit without allowing the reflection step, type _mushin_ ( japanese for "no mind" 無心 ).

