# Mapping from image filenames to document normalized names
# Organization logos and other images not associated with specific documents are mapped to None

IMAGE_TO_DOC_MAPPING = {
    # Document title images
    "doc_title_agi_governments_free_societies.png": "agi_governments_and_free_societies",
    "doc_title_gradual_disempowerment.png": "gradual_disempowerment",

    # Author/document images
    "author_dario_amodei_machines_of_loving_grace.jpg": "machines_of_loving_grace",
    "author_leopold_aschenbrenner_situational_awareness.jpg": "situational_awareness_the_decade_ahead",
    "author_paul_christiano_what_failure_looks_like.webp": "what_failure_looks_like",

    # Advanced AI scenario images
    "advanced_ai_scenarios_arms_race.jpg": "advanced_ai_possible_futures_arms_race",
    "advanced_ai_scenarios_big_ai.jpg": "advanced_ai_possible_futures_big_ai",
    "advanced_ai_scenarios_diplomacy.jpg": "advanced_ai_possible_futures_diplomacy",
    "advanced_ai_scenarios_plateau.jpg": "advanced_ai_possible_futures_plateau",
    "advanced_ai_scenarios_takeoff.jpg": "advanced_ai_possible_futures_take_off",

    # Series images
    "The_Intelligence_Curse.jpg": "the_intelligence_curse_series",

    # Organization logos (not associated with specific documents)
    "organization_logo_forethought.png": None,
    "organization_logo_miri.jpg": None,
    "organization_logo_ai_futures.jpg": None,
    "organization_logo_knight_columbia.jpg": None,
    "organization_logo_rand.png": None,
    "organization_logo_foresight_institute.jpg": None,
    "organization_logo_convergence_analysis.jpg": None,
    "organization_logo_wait_but_why.jpg": None,
    "organization_logo_open_philanthropy.jpg": None,

    # Other images
    "hammond.jpg": None,
}


def get_doc_name_from_image(image_filename):
    """
    Get the normalized document name from an image filename.

    Args:
        image_filename (str): The image filename (e.g., "doc_title_agi_governments_free_societies.png")

    Returns:
        str or None: The normalized document name, or None if not associated with a document
    """
    return IMAGE_TO_DOC_MAPPING.get(image_filename)


def get_doc_path_from_image(image_filename, docs_folder="docs"):
    """
    Get the full document path from an image filename.

    Args:
        image_filename (str): The image filename
        docs_folder (str): The base docs folder path

    Returns:
        str or None: The full path to the document .md file, or None if not found
    """
    doc_name = get_doc_name_from_image(image_filename)
    if doc_name:
        # Need to determine which folder the document is in
        # This would require additional logic to map normalized names to folder paths
        return f"{docs_folder}/{doc_name}.md"
    return None
