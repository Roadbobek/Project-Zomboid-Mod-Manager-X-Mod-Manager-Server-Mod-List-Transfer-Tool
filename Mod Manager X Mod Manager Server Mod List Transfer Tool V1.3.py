import os
import shutil

seperator = "\u25B0"
sep_length = 120
# print(seperator * sep_length)
# print("BlahBlahBlah".center(sep_length))

# Function to get the current user's home directory depending on the operating system
def get_zomboid_directory():
    if os.name == 'nt':  # Windows
        user_profile = os.getenv("USERPROFILE")
        if user_profile:
            return os.path.join(user_profile, "Zomboid")
    elif os.name == 'posix':  # Linux/macOS
        user_profile = os.getenv("HOME")
        if user_profile:
            return os.path.join(user_profile, "Zomboid")
    else:
        raise Exception("Unsupported OS")
    return None

# Function to ask the user for a custom directory path
def ask_for_custom_directory():
    print("Would you like to use a custom Zomboid directory?")
    print(r"Example, Linux/MacOS: ~/Zomboid, Windows: %UserProfile%\Zomboid")

    while True:
        choice = input("Enter 'Y' for yes or 'N' for no: ").strip().lower()
        if choice == 'y':
            while True:
                custom_path = input("\nPlease enter the full path to your Zomboid directory: ").strip()
                if os.path.isdir(custom_path):
                    return custom_path
                else:
                    print("\n\u274C Invalid directory. Please make sure the directory exists.")
        elif choice == 'n':
            return None
        else:
            print("\u274C Invalid input. Please enter 'Y' for yes or 'N' for no.")

# Get mod manager paths (default or custom directory)
def get_mod_manager_paths():
    custom_path = ask_for_custom_directory()

    if custom_path:
        mod_manager_path = os.path.join(custom_path, "Lua", "saved_modlists.txt")
        mod_manager_server_path = os.path.join(custom_path, "Lua", "saved_modlists_server.txt")
    else:
        zomboid_dir = get_zomboid_directory()
        mod_manager_path = os.path.join(zomboid_dir, "Lua", "saved_modlists.txt")
        mod_manager_server_path = os.path.join(zomboid_dir, "Lua", "saved_modlists_server.txt")

    return mod_manager_path, mod_manager_server_path

# Backup original file before editing
def backup_file(file_path):
    backup_path = file_path + ".bak"
    if os.path.exists(file_path):
        if os.path.exists(backup_path):
            print(seperator * sep_length)
            overwrite = input(f"\u26a0\ufe0f The backup file {backup_path} already exists. Do you want to overwrite it? \n Please make sure everything works in game first. (Y/N): ").strip().lower()
            if overwrite == 'y':
                shutil.copy(file_path, backup_path)
                print(f"\nBackup overwritten: {backup_path}")
            else:
                print("\nKeeping the existing backup.")
        else:
            shutil.copy(file_path, backup_path)
            print(f"Backup created successfully: {backup_path}")
    else:
        print(f"\u274C File not found: {file_path}, cannot create backup.")

# Parse Mod Manager file
def parse_mod_manager(file_path):
    mod_lists = {}
    if os.path.exists(file_path):
        with open(file_path, "r", encoding="utf-8") as f:
            lines = f.readlines()
            for line in lines:
                if line.startswith("VERSION"):
                    continue
                name, mods = line.split(":", 1)
                mod_ids = mods.strip().split(";")
                mod_lists[name] = mod_ids
    return mod_lists

# Parse Mod Manager: Server file
def parse_mod_manager_server(file_path):
    mod_lists = {}
    if os.path.exists(file_path):
        with open(file_path, "r", encoding="utf-8") as f:
            lines = f.readlines()
            current_name = None
            for line in lines:
                if line.startswith("VERSION"):
                    continue
                if line.startswith("[") and line.endswith("]\n"):
                    current_name = line.strip("[]\n")
                    mod_lists[current_name] = {"WorkshopItems": [], "Mods": []}
                elif current_name and "=" in line:
                    key, value = line.strip().split("=", 1)
                    mod_lists[current_name][key] = value.split(";")
    return mod_lists

# Write Mod Manager file (adding to the list without overwriting)
def write_mod_manager(file_path, mod_lists):
    with open(file_path, "a", encoding="utf-8") as f:
        for name, mods in mod_lists.items():
            f.write(f"{name}:{';'.join(mods)}\n")
    print(f"\u2705 Mod Manager file updated successfully! Appended to: {file_path}")

# Write Mod Manager: Server file (adding to the list without overwriting)
def write_mod_manager_server(file_path, mod_lists):
    with open(file_path, "a", encoding="utf-8") as f:
        for name, data in mod_lists.items():
            f.write(f"[{name}]\n")
            f.write(f"WorkshopItems=\n")
            f.write(f"Mods={';'.join(data['Mods'])}\n")
    print(f"\u2705 Mod Manager: Server file updated successfully! Appended to: {file_path}")

# Transfer Mod List (adding or merging)
def transfer_mod_list(mod_lists, target_type, existing_list=None):
    print("Available Mod Lists:")
    for i, name in enumerate(mod_lists, start=1):
        print(f"  {i}. {name}")
    while True:
        try:
            choice = int(input("\nSelect the mod list to transfer (enter the number): ")) - 1
            if choice < 0 or choice >= len(mod_lists):
                print("\u274C Invalid choice. Please select a valid mod list.")
                continue
            break
        except ValueError:
            print("\u274C Invalid input. Please enter a number.")

    selected_name = list(mod_lists.keys())[choice]

    while True:
        rename_choice = input(f"Do you want to rename the mod list '{selected_name}'? (Y/N): ").strip().lower()
        if rename_choice == "y":
            new_name = input("Enter the new name for the mod list: ").strip()
            if not new_name:
                print("\u274C Invalid name. Keeping the original name.")
                continue

            if new_name in mod_lists:
                print(f"\u274C Name '{new_name}' already exists. Please choose a different name.")
                continue

            # Add the renamed mod list to the dictionary
            mod_lists[new_name] = mod_lists[selected_name]
            # Remove the old key
            del mod_lists[selected_name]
            selected_name = new_name
            break
        elif rename_choice == "n":
            break
        else:
            print("\u274C Invalid input. Please enter 'Y' for yes or 'N' for no.")

    print()
    print(seperator * sep_length)
    print(f"Selected Mod List: {selected_name}")

    mods = mod_lists[selected_name]

    if target_type == "server":
        mods = [mod for mod in mods if mod != "ModManager"]
        return {selected_name: {"WorkshopItems": [], "Mods": mods}}, "\u2705 Transferred from MM to MMS"

    elif target_type == "manager":
        mods = ["ModManager"] + mods["Mods"]
        return {selected_name: mods}, "\u2705 Transferred from MMS to MM"
    else:
        return None, "\u274C Invalid transfer type"

def main():
    print(seperator * sep_length)
    print("Project Zomboid Mod Manager X Mod Manager: Server Mod List Transfer Tool".center(sep_length))
    print("Made By Roadbobek".center(sep_length))
    print("Version 1.3".center(sep_length))
    print(seperator * sep_length)
    print("For help please visit the Github page: ".center(sep_length))
    print("https://github.com/Roadbobek/Project-Zomboid-ModManager-X-ModManager-Server-Mod-List-Transfer-Tool".center(sep_length))
    print(seperator * sep_length)

    os_type = "Unknown OS"
    user_profile = None
    if os.name == 'nt':  # Windows
        os_type = "Windows"
        user_profile = os.getenv("USERPROFILE")
    elif os.name == 'posix':  # Linux/macOS
        os_type = "Linux/MacOS"
        user_profile = os.getenv("HOME")

    print(f"Detected OS: {os_type}")
    print(f"Detected User: {os.path.basename(user_profile)}")
    print(f"Full Path to Zomboid data: {os.path.join(user_profile, 'Zomboid')}")
    print(seperator * sep_length)

    mod_manager_path, mod_manager_server_path = get_mod_manager_paths()

    backup_file(mod_manager_path)
    backup_file(mod_manager_server_path)

    while True:
        print(seperator * sep_length)
        print("Select transfer direction:")
        print("  1. Mod Manager -> Mod Manager: Server")
        print("  2. Mod Manager: Server -> Mod Manager")
        print("  3. Exit")
        direction = input("Enter your choice (1, 2, or 3): ")

        if direction == "1":
            if not os.path.exists(mod_manager_path):
                print(f"\u274C Mod Manager mod list file not found at {mod_manager_path}. Please check the directory.")
                continue
            mod_lists = parse_mod_manager(mod_manager_path)
            server_lists = parse_mod_manager_server(mod_manager_server_path)
            transferred_mod_lists, status = transfer_mod_list(mod_lists, "server", server_lists)
            write_mod_manager_server(mod_manager_server_path, transferred_mod_lists)

        elif direction == "2":
            if not os.path.exists(mod_manager_server_path):
                print(f"\u274C Mod Manager: Server mod list file not found at {mod_manager_server_path}. Please check the directory.")
                continue
            mod_lists = parse_mod_manager(mod_manager_path)
            server_lists = parse_mod_manager_server(mod_manager_server_path)
            transferred_mod_lists, status = transfer_mod_list(server_lists, "manager", mod_lists)
            write_mod_manager(mod_manager_path, transferred_mod_lists)

        elif direction == "3":
            print("Exiting program.")
            break

if __name__ == "__main__":
    main()
