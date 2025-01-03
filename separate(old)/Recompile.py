import os
import subprocess

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

# Example usage
translated_po = "./translated_po"  # Folder containing the .po files
final_mo_folder = "./finished_mo"  # Folder to save compiled .mo files
msgfmt_exe_path = r"X:\Programs\Poedit\GettextTools\bin\msgfmt.exe" #Absolute paths are trash but i CBA to fix this - install Poedit from google and change this

# Run the compilation process
compile_po_to_mo(translated_po, final_mo_folder)
