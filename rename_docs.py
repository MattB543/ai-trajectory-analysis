import os
import re

# Mapping from folder names to normalized names based on names.md
folder_to_normalized = {
    "AI 2027": "ai_2027",
    "Situational Awareness_ The Decade Ahead": "situational_awareness_the_decade_ahead",
    "Gradual Disempowerment": "gradual_disempowerment",
    "Machines of Loving Grace": "machines_of_loving_grace",
    "AGI, Governments, and Free Societies": "agi_governments_and_free_societies",
    "Soft Nationalization_ How the US Government Will Control AI Labs": "soft_nationalization_how_the_us_government_will_control_ai_labs",
    "The Intelligence Curse (series)": "the_intelligence_curse_series",
    "AGI and Lock-In": "agi_and_lock_in",
    "What Failure Looks Like": "what_failure_looks_like",
    "Tool AI Pathway": "tool_ai_pathway",
    "d_acc Pathway": "d_acc_pathway",
    "Advanced AI_ Possible Futures (five scenarios)": "advanced_ai_possible_futures",
    "AI & Leviathan (Parts I–III)": "ai_and_leviathan_parts_i_to_iii",
    "AI as Normal Technology": "ai_as_normal_technology",
    "Could Advanced AI Drive Explosive Economic Growth": "could_advanced_ai_drive_explosive_economic_growth",
    "AI-Enabled Coups": "ai_enabled_coups",
    "AGI Ruin_ A List of Lethalities": "agi_ruin_a_list_of_lethalities",
    "The AI Revolution - Wait but Why": "the_ai_revolution_wait_but_why",
    "Artificial General Intelligence and the Rise and Fall of Nations_ Visions for Potential AGI Futures": "artificial_general_intelligence_and_the_rise_and_fall_of_nations"
}

# Scenario files for Advanced AI folder
scenario_normalized = {
    "arms_race": "scenario_arms_race",
    "big_ai": "scenario_big_ai",
    "diplomacy": "scenario_diplomacy",
    "plateuau": "scenario_plateau",  # Fix typo
    "take-off": "scenario_take_off"
}

docs_dir = "docs"

# Process each subfolder
for folder_name in os.listdir(docs_dir):
    folder_path = os.path.join(docs_dir, folder_name)

    if not os.path.isdir(folder_path):
        continue

    # Get normalized name for this folder
    if folder_name not in folder_to_normalized:
        print(f"Warning: No mapping found for folder '{folder_name}'")
        continue

    normalized_base = folder_to_normalized[folder_name]

    # Process files in this folder
    for filename in os.listdir(folder_path):
        # Skip summary files
        if "summary" in filename:
            continue

        old_path = os.path.join(folder_path, filename)

        # Handle full_doc.md files
        if filename == "full_doc.md":
            new_filename = f"{normalized_base}.md"
            new_path = os.path.join(folder_path, new_filename)

            print(f"Renaming: {old_path}")
            print(f"      to: {new_path}")
            os.rename(old_path, new_path)

        # Handle scenario files in Advanced AI folder
        elif folder_name == "Advanced AI_ Possible Futures (five scenarios)":
            # Extract base name without extension
            base_name = os.path.splitext(filename)[0]

            if base_name in scenario_normalized:
                new_filename = f"{scenario_normalized[base_name]}.md"
                new_path = os.path.join(folder_path, new_filename)

                print(f"Renaming: {old_path}")
                print(f"      to: {new_path}")
                os.rename(old_path, new_path)

print("\nRenaming complete!")
