import polib
import asyncio
from googletrans import Translator
import os

async def translate_msgstr(msgstr, translator, source_lang='ru', target_lang='en'):
    """
    Translate the msgstr asynchronously.
    Args:
        msgstr (str): The string to translate.
        translator (Translator): An instance of the Translator class.
        source_lang (str): Source language (default 'ru').
        target_lang (str): Target language (default 'en').
    """
    # Translate the msgstr from Russian to English
    translated = await translator.translate(msgstr, src=source_lang, dest=target_lang)
    return translated.text

async def translate_po_file(input_po_path, output_po_path, source_lang='ru', target_lang='en'):
    """
    Translates the 'msgstr' parts of a .po file from one language to another using Google Translate.
    Args:
        input_po_path (str): Path to the input .po file.
        output_po_path (str): Path where the translated .po file will be saved.
        source_lang (str): Source language code (default is Russian 'ru').
        target_lang (str): Target language code (default is English 'en').
    """
    # Initialize the Google Translate API
    translator = Translator()

    # Load the original .po file
    po = polib.pofile(input_po_path)

    # List to hold translation tasks
    tasks = []

    # Translate each entry's 'msgstr'
    for entry in po:
        if entry.msgstr:  # Only translate non-empty msgstr fields
            tasks.append(translate_msgstr(entry.msgstr, translator, source_lang, target_lang))

    # Wait for all translations to complete
    translated_msgstrs = await asyncio.gather(*tasks)

    # Apply the translations back to the entries
    for i, entry in enumerate(po):
        if entry.msgstr:
            entry.msgstr = translated_msgstrs[i]  # Update the msgstr with the translated text

    # Save the translated .po file
    po.save(output_po_path)
    print(f"Translated file saved as: {output_po_path}")

async def translate_all_po_files(input_folder, output_folder, source_lang='ru', target_lang='en'):
    """
    Translate all .po files in the input folder and save them to the output folder.
    Args:
        input_folder (str): Folder containing .po files to translate.
        output_folder (str): Folder where the translated .po files will be saved.
        source_lang (str): Source language code (default is Russian 'ru').
        target_lang (str): Target language code (default is English 'en').
    """
    # Create output folder if it doesn't exist
    os.makedirs(output_folder, exist_ok=True)

    # Iterate through all .po files in the input folder
    for file_name in os.listdir(input_folder):
        if file_name.endswith(".po"):
            input_po_path = os.path.join(input_folder, file_name)
            output_po_path = os.path.join(output_folder, file_name)

            # Translate the file
            await translate_po_file(input_po_path, output_po_path, source_lang, target_lang)

# Example usage
input_po_folder = "./Output_PO"  # Folder containing the .po files
trans_po_folder = "./Translated_PO"  # Folder to save translated .po files


# Run the translation asynchronously
asyncio.run(translate_all_po_files(input_po_folder, trans_po_folder))