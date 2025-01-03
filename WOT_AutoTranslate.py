import subprocess
import os
import polib
import asyncio
from googletrans import Translator
import shutil

# Define Languages
SOURCE_LANG = 'ru'  # Source language: Russian
TARGET_LANG = 'en'  # Target language: English

# Paths
msgfmt_exe_path = r"X:\Programs\Poedit\GettextTools\bin\msgfmt.exe"  # Absolute paths are trash but i CBA to fix it
msgunfmt_exe_path = r"X:\Programs\Poedit\GettextTools\bin\msgunfmt.exe"  # Same shit
input_mo_folder = "./Input_MO"
output_po_folder = "./Output_PO"
input_po_folder = "./Output_PO"  # Folder containing the .po files (temp)
trans_po_folder = "./Translated_PO"  # Folder to save translated .po files (temp)
translated_po = "./Translated_PO"
final_mo_folder = "./Finished_MO"  # Folder to save compiled .mo files

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

async def translate_msgstr(msgstr, translator):
    """
    Translate the msgstr asynchronously using the global source and target languages.
    """
    translated = await translator.translate(msgstr, src=SOURCE_LANG, dest=TARGET_LANG)
    return translated.text

async def translate_po_file(input_po_path, output_po_path):
    """
    Translates the 'msgstr' parts of a .po file using Google Translate.
    """
    translator = Translator()
    po = polib.pofile(input_po_path)
    tasks = []

    # Translate each entry's 'msgstr' if it is non-empty
    for entry in po:
        if entry.msgstr:  # Only translate non-empty msgstr fields
            tasks.append(translate_msgstr(entry.msgstr, translator))

    # Wait for all translations to complete
    translated_msgstrs = await asyncio.gather(*tasks)

    # Check if the number of translations matches the number of entries with msgstr
    if len(translated_msgstrs) != len([entry for entry in po if entry.msgstr]):
        print(f"Warning: Mismatch in number of translations for {input_po_path}.")
        return

    # Apply the translations back to the entries
    translated_index = 0
    for entry in po:
        if entry.msgstr and translated_index < len(translated_msgstrs):
            entry.msgstr = translated_msgstrs[translated_index]  # Update the msgstr with the translated text
            translated_index += 1

    po.save(output_po_path)
    print(f"Translated file saved as: {output_po_path}")

async def translate_all_po_files(input_folder, output_folder):
    """
    Translate all .po files in the input folder and save them to the output folder.
    """
    os.makedirs(output_folder, exist_ok=True)
    for file_name in os.listdir(input_folder):
        if file_name.endswith(".po"):
            input_po_path = os.path.join(input_folder, file_name)
            output_po_path = os.path.join(output_folder, file_name)
            await translate_po_file(input_po_path, output_po_path)

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
convert_mo_to_po(input_mo_folder, output_po_folder, msgunfmt_exe_path)

# Run the translation
asyncio.run(translate_all_po_files(input_po_folder, trans_po_folder))

# Run the reconversion
compile_po_to_mo(trans_po_folder, final_mo_folder)

# Cleanup
try:
    shutil.rmtree("./Translated_PO")
    shutil.rmtree("./Output_PO")
    print("Cleanup Successful")
except:
    print("Cleanup Error")

