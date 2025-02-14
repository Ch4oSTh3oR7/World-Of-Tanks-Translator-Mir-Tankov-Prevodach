import subprocess
import re
import os
import polib
import asyncio
from googletrans import Translator
import shutil
from dotenv import load_dotenv

load_dotenv()

# Define Languages
SOURCE_LANG = os.getenv('SOURCE_LANG', 'ru')  # Get config env value, default to russian
TARGET_LANG = os.getenv('TARGET_LANG', 'en')  # Get config env value, default to english

# Paths
msgfmt_exe_path = os.path.join(os.getenv('POEDIT_PATH'), "GettextTools", "bin", "msgfmt.exe")
msgunfmt_exe_path = os.path.join(os.getenv('POEDIT_PATH'), "GettextTools", "bin", "msgunfmt.exe")
input_mo_folder = "./Input_MO"
input_po_folder = "./Input_PO"  # Folder containing the .po files to be translated (temp)
input_src_mo_folder = "./Input_MO_context"
input_src_po_folder = "./Input_PO_context"  # Folder containing the .po files to use as translation source (temp)
output_po_folder = "./Translated_PO"  # Folder to save translated .po files (temp)
output_mo_folder = "./Translated_MO"  # Folder to save compiled .mo files

#Mapping between all similar files but named differently
#Also put the reversed mapping, in case someone wants to translate Lesta->Wargaming
files_mapping = {
    "china_tankmen.po": "china_crew.po",
    "china_crew.po": "china_tankmen.po",
    "czech_tankmen.po": "czech_crew.po",
    "czech_crew.po": "czech_tankmen.po",
    "france_tankmen.po": "france_crew.po",
    "france_crew.po": "france_tankmen.po",
    "gb_tankmen.po": "gb_crew.po",
    "gb_crew.po": "gb_tankmen.po",
    "germany_tankmen.po": "germany_crew.po",
    "germany_crew.po": "germany_tankmen.po",
    "italy_tankmen.po": "italy_crew.po",
    "italy_crew.po": "italy_tankmen.po",
    "japan_tankmen.po": "japan_crew.po",
    "japan_crew.po": "japan_tankmen.po",
    "poland_tankmen.po": "poland_crew.po",
    "poland_crew.po": "poland_tankmen.po",
    "sweden_tankmen.po": "sweden_crew.po",
    "sweden_crew.po": "sweden_tankmen.po",
    "usa_tankmen.po": "usa_crew.po",
    "usa_crew.po": "usa_tankmen.po",
    "ussr_tankmen.po": "ussr_crew.po",
    "ussr_crew.po": "ussr_tankmen.po",
}

def convert_mo_to_po(input_folder, output_folder, msgunfmt_path):
    """
    Convert all .mo files in the input folder to .po files in the output folder.
    """
    os.makedirs(output_folder, exist_ok=True)
    for file_name in os.listdir(input_folder):
        if file_name.endswith(".mo"):
            input_path = os.path.join(input_folder, file_name)
            output_path = os.path.join(output_folder, file_name.replace(".mo", ".po"))
            try:
                subprocess.run([msgunfmt_path, input_path, "-o", output_path], check=True)
                print(f"Converted {file_name} to {os.path.basename(output_path)}")
            except subprocess.CalledProcessError as e:
                print(f"Error converting {file_name}: {e.stderr.decode('utf-8')}")


async def translate_msgstr(entry, translator):
    """
    Translate the msgstr asynchronously using the global source and target languages.
    """
    text = entry.msgstr

    # Step 1: Replace variables with placeholders
    placeholder_pattern = r"%\([a-zA-Z_][a-zA-Z0-9_]*\)[a-zA-Z%]?"  # r"%\([a-zA-Z_][a-zA-Z0-9_]*\)([a-zA-Z%])?"
    placeholders = re.findall(placeholder_pattern, text)  # Extract all variables
    temp_text = re.sub(placeholder_pattern, "{_______}", text)  # Replace with a generic placeholder

    # Step 2: Translate the text (excluding variables)
    translated = await translator.translate(temp_text, src=SOURCE_LANG, dest=TARGET_LANG)
    translated_text = translated.text

    # Step 3: Restore the original variables in the translated text
    for placeholder in placeholders:
        #Note: sometimes case is changed with translation...
        translated_text = re.sub(r"\{_______}", placeholder, translated_text, count=1, flags=re.IGNORECASE)  # Replace placeholders in order

    return entry.msgid, translated_text


async def translate_po_file(input_po_path, input_src_po_path, output_po_path):
    """
    Translates the 'msgstr' parts of a .po file using Google Translate.
    """
    translator = Translator()
    po = polib.pofile(input_po_path)
    po_src = None
    if input_src_po_path:
        po_src = polib.pofile(input_src_po_path)

    tasks = []

    # Translate each entries, with priority to use official translation file
    for entry in po:
        flag_translated = False

        if po_src:
            src_entry = po_src.find(entry.msgid, include_obsolete_entries=True)
            if src_entry and src_entry.msgstr:  # We have an entry in source then no need for Google Translate
                entry.msgstr = src_entry.msgstr
                flag_translated = True

        if not flag_translated and entry.msgstr:  # Only translate non-empty msgstr fields
            print(f"Key '{entry.msgid}' not found in translation sources, translate with Google Translate")
            tasks.append(translate_msgstr(entry, translator))

    # Wait for all translations to complete
    translated_msgstrs = await asyncio.gather(*tasks)

    # Apply the translations back to the entries
    for translated_entry_id, translated_entry_text in translated_msgstrs:
        entry = po.find(translated_entry_id, include_obsolete_entries=True)
        if entry:
            entry.msgstr = translated_entry_text

    po.save(output_po_path)
    print(f"Translated file saved as: {output_po_path}")


async def translate_all_po_files(input_folder, input_src_folder, output_folder):
    """
    Translate all .po files in the input folder and save them to the output folder.
    """
    os.makedirs(output_folder, exist_ok=True)
    for file_name in os.listdir(input_folder):
        if file_name.endswith(".po"):
            input_po_path = os.path.join(input_folder, file_name)
            output_po_path = os.path.join(output_folder, file_name)

            input_src_po_path = os.path.join(input_src_folder, file_name)
            if os.path.isfile(input_src_po_path):
                await translate_po_file(input_po_path, input_src_po_path, output_po_path)
                continue

            if file_name in files_mapping:
                input_src_po_path = os.path.join(input_src_folder, files_mapping[file_name])
                if os.path.isfile(input_src_po_path):
                    await translate_po_file(input_po_path, input_src_po_path, output_po_path)
                    continue

            await translate_po_file(input_po_path, None, output_po_path)


def compile_po_to_mo(input_folder, output_folder):
    """
    Compile .po files into .mo files using msgfmt (Poedit's tool).
    """
    os.makedirs(output_folder, exist_ok=True)
    for file_name in os.listdir(input_folder):
        if file_name.endswith(".po"):
            input_po_path = os.path.join(input_folder, file_name)
            output_mo_path = os.path.join(output_folder, file_name.replace('.po', '.mo'))
            subprocess.run([msgfmt_exe_path, input_po_path, "-o", output_mo_path], check=True)
            print(f"Compiled: {file_name} -> {output_mo_path}")


# Run the conversion
convert_mo_to_po(input_mo_folder, input_po_folder, msgunfmt_exe_path)
convert_mo_to_po(input_src_mo_folder, input_src_po_folder, msgunfmt_exe_path)

# Run the translation
asyncio.run(translate_all_po_files(input_po_folder, input_src_po_folder, output_po_folder))

# Run the reconversion
compile_po_to_mo(output_po_folder, output_mo_folder)

# Cleanup
try:
    shutil.rmtree(input_po_folder)
    shutil.rmtree(input_src_po_folder)
    shutil.rmtree(output_po_folder)
    print("Cleanup Successful")
except:
    print("Cleanup Error")
