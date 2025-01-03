import subprocess
import os
import polib
import asyncio
from googletrans import Translator
import shutil

# Language Selector
SOURCE_LANG = 'ru'  # Source language: Russian
TARGET_LANG = 'en'  # Target language: English

# Paths
msgfmt_exe_path = r"X:\Programs\Poedit\GettextTools\bin\msgfmt.exe" # Absolute paths are trash but i CBA to fix this - install Poedit from google and change this
msgunfmt_exe_path = r"X:\Programs\Poedit\GettextTools\bin\msgunfmt.exe" # same trash
input_mo_folder = "./Input_MO"
output_po_folder = "./Output_PO"
input_po_folder = "./Output_PO"  # Folder containing the .po files
trans_po_folder = "./Translated_PO"  # Folder to save translated .po files
translated_po = "./Translated_PO"  # Folder containing the .po files
final_mo_folder = "./Finished_MO"  # Folder to save compiled .mo files


def convert_mo_to_po(input_folder, output_folder, msgunfmt_path):
    """
    Convert all .mo files in the input folder to .po files in the output folder.

    Args:
        input_folder (str): Path to the folder containing .mo files.
        output_folder (str): Path to the folder to save .po files.
        msgunfmt_path (str): Path to the msgunfmt.exe tool.
    """
    # Ensure output folder exists
    os.makedirs(output_folder, exist_ok=True)

    # Iterate over all .mo files in the input folder
    for file_name in os.listdir(input_folder):
        if file_name.endswith(".mo"):
            input_path = os.path.join(input_folder, file_name)
            output_path = os.path.join(output_folder, file_name.replace(".mo", ".po"))

            # Run msgunfmt.exe to convert the file
            try:
                subprocess.run(
                    [msgunfmt_path, input_path, "-o", output_path],
                    check=True,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE
                )
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

    # Translate each entry's 'msgstr'
    for entry in po:
        if entry.msgstr:  # Only translate non-empty msgstr fields
            tasks.append(translate_msgstr(entry.msgstr, translator))

    translated_msgstrs = await asyncio.gather(*tasks)

    # Apply the translations back to the entries
    for i, entry in enumerate(po):
        if entry.msgstr:
            entry.msgstr = translated_msgstrs[i]  # Update the msgstr with the translated text

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
    Compiles .po files into .mo files using msgfmt (Poedit's tool).
    Args:
        input_folder (str): Folder containing the .po files to compile.
        output_folder (str): Folder where the compiled .mo files will be saved.
    """
    # Create output folder if it doesn't exist
    os.makedirs(output_folder, exist_ok=True)

    # Iterate through all .po files in the input folder
    for file_name in os.listdir(input_folder):
        if file_name.endswith(".po"):
            input_po_path = os.path.join(input_folder, file_name)
            output_mo_path = os.path.join(output_folder, file_name.replace('.po', '.mo'))

            # Call msgfmt to compile the .po file to .mo
            subprocess.run([msgfmt_exe_path, input_po_path, "-o", output_mo_path], check=True)
            print(f"Compiled: {file_name} -> {output_mo_path}")


# Run the conversion
convert_mo_to_po(input_mo_folder, output_po_folder, msgunfmt_exe_path)

# Run the translation
asyncio.run(translate_all_po_files(input_po_folder, trans_po_folder))

# Run the reconversion
compile_po_to_mo(translated_po, final_mo_folder)

# Cleanup
try:
    shutil.rmtree("./Translated_PO")
    shutil.rmtree("./Output_PO")
    print("Cleanup Successful")

except:
    print("Cleanup Error")
