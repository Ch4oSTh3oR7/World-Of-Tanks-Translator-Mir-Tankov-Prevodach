# World Of Tanks <-> Mir Tankov Translator

A simple tool for world of tanks or мир танков (mir tankov / tanki) from wargaming or lesta respectivelly.

It is a simple script that will translate the game files ( no pictures or audio) into the language of your choice. If you desire to play on the russian branch of the game and dont understand russian you can change it with this script.
It uses google translate as its a free API that you dont have to pay with but it has some jank with certain translations.

## How to use

You can watch the youtube video here:
https://youtu.be/q9J8jGmOOJc (deprecated)

1. Download project zip and extract it
2. Get the required libraries and [python version 3+](https://www.python.org/downloads/) (you can find many good tutorials on YouTube)
    - Python https://www.python.org/downloads/
    - libs: polib, googletrans, python-dotenv
3. Install [Poelib](https://poedit.net/) in an easily accessible directory
4. Grab the MO files you want to translate and put them in `Input_MO/` (ie if you want to translate Lesta Mir Tankov, take MO files from `World_of_Tanks_RU\res\text\ru\lc_messages` (note: "World_of_Tanks_RU" is sometimes named "Tanki"))
5. (OPTIONAL) Grab already translated context MO files and put them in `Input_MO_context/` (ie if you want to use translations from Wargaming WoT, take MO files from `World_of_Tanks_EU\res\text\lc_messages`)
    - During the translation process of a file in `Input_MO/`, if a similar file (same name) exists in `Input_MO_context/` then translation keys will be compared an all equal keys will be copied from the contextual MO file (instead of being translated)
    - Take note that a mapping was done to consider that WG' `<nation>_crew.mo` files will be the same as Lesta' `<nation>_tankmen.mo`
    - You can also use an existing translation as base (eg, for english on Lesta you can use [BangAverageTanker](https://www.twitch.tv/bangaveragetanker) translation as base: http://guild-extra.co.uk/bangaverage/ see "Lesta Tanki EN_GB" tab)
6. Duplicate `default.env` file and rename it `.env`, then edit needed variables with needed values (like path to POEdit and the wanted source/target languages)
7. Now you can run `WOT_AutoTranslate.py`, if no errors this process should take around 5 - 10 minutes depending on your internet and Google Translate
8. Go to your game `res_mod/<currentVersion>` folder and create folders the following path:
    - For Lesta: `text/ru/lc_messages/` (example full path for 1.32.0.0 version: `Tanki/res_mods/1.32.0.0/text/ru/lc_messages`)
    - For WG: `text/lc_messages/` (example full path for 1.27.1.0 version: `Tanki/res_mods/1.27.1.0/text/lc_messages`)
    - FYI, path in `res_mod/<version>/` should follow the same path as `res/` folder
9. Copy the files from the `Finished_Mo/` folder to the previously created folder
10. Now you can just run the game
    - Keep in mind that any update which create a new folder mod will loose the translations
    - You can just retrieve the translation from the previous version `res_mod/` folder
    - If translations were added in the update, you can re-do steps above while putting your previous translation result in `Input_MO_context/` (thus only new lines/files will be translated)


You can take a look at the older or separate files if you wish to do so - Run order is Convert -> Translate -> Recompile
I am not good at coding so a lot was written with chatGPT in python

Tags:
World of tanks lesta english
Mir tankov english
tanki translator
mir tankov translate
lesta english
