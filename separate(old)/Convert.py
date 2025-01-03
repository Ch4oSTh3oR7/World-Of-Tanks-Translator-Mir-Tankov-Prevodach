import subprocess
import os

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


# Define paths
input_mo_folder = "./Input_MO"
output_po_folder = "./Output_PO"
msgunfmt_exe_path = r"X:\Programs\Poedit\GettextTools\bin\msgunfmt.exe" #Absolute paths are trash but i CBA to fix this - install Poedit from google and change this


# Run the conversion
convert_mo_to_po(input_mo_folder, output_po_folder, msgunfmt_exe_path)



