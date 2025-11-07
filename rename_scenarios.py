import os

# Rename scenario files to include the document name prefix
advanced_ai_folder = r"docs\Advanced AI_ Possible Futures (five scenarios)"

scenario_renames = {
    "scenario_arms_race.md": "advanced_ai_possible_futures_arms_race.md",
    "scenario_big_ai.md": "advanced_ai_possible_futures_big_ai.md",
    "scenario_diplomacy.md": "advanced_ai_possible_futures_diplomacy.md",
    "scenario_plateau.md": "advanced_ai_possible_futures_plateau.md",
    "scenario_take_off.md": "advanced_ai_possible_futures_take_off.md"
}

for old_name, new_name in scenario_renames.items():
    old_path = os.path.join(advanced_ai_folder, old_name)
    new_path = os.path.join(advanced_ai_folder, new_name)

    if os.path.exists(old_path):
        print(f"Renaming: {old_path}")
        print(f"      to: {new_path}")
        os.rename(old_path, new_path)
    else:
        print(f"File not found: {old_path}")

print("\nScenario files renamed!")
