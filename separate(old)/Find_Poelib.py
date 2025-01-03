import winreg


def find_poedit_installation():
    possible_paths = [
        # Common locations in the registry
        r"SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall\Poedit_is1",  # Machine-wide install
        r"SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall\Poedit",  # Possible other naming
        r"SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall\Poedit_is1",  # Per-user install (CurrentUser)
        r"SOFTWARE\WOW6432Node\Microsoft\Windows\CurrentVersion\Uninstall\Poedit_is1",  # 32-bit on 64-bit systems
        r"SOFTWARE\WOW6432Node\Microsoft\Windows\CurrentVersion\Uninstall\Poedit",
        # 32-bit version (potential alternate name)
    ]

    for registry_path in possible_paths:
        try:
            reg_key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, registry_path)
            install_path, _ = winreg.QueryValueEx(reg_key, "InstallLocation")
            winreg.CloseKey(reg_key)
            return install_path
        except FileNotFoundError:
            pass  # Continue searching through other locations

    return None  # Poedit installation not found


poedit_path = find_poedit_installation()
if poedit_path:
    print(f"Poedit is installed at: {poedit_path}")
else:
    print("Poedit installation path not found.")
