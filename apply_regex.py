import re
from pdf_processor import extract_text_from_pdf
import os

# --- Configuration ---
PDF_FILE_PATH = "List of Chloe's Colleges for 2025 Interview Spreadsheet.pdf"
OUTPUT_TXT_FILENAME = "extracted_pdf_content_for_regex.txt"
FINAL_COLLEGE_LIST_FILENAME = "final_college_list_regex.txt"


def regex_college_names(text, save_to_file=False, output_filename="regex_results.txt"):
    """
    Args:
        text (str): The text to extract college names from.
    Returns:
        str: A string of unique, sorted college names.
    """
    # --- Regex for College Names ---
    P_MULTI_NC = r"(?:[A-Z][\w'-]+(?:\s+(?:(?:of|the|and|at|de)|[\w'-]+))+)"
    P_ACRONYM_NC = r"(?:[A-Z]{2,7})"
    P_SINGLE_NC = r"(?:[A-Z][\w'-]+)"
    college_name_capture_group = f"({P_MULTI_NC}|{P_ACRONYM_NC}|{P_SINGLE_NC})"
    commentary_consumption_part = r"(?:\s*\s-\s.*)?"
    college_name_regex = rf"^(?!\s*●\s)\s*{college_name_capture_group}\s*{commentary_consumption_part}\s*$"
    
    found_colleges = []
    for line in text.splitlines():
        stripped_line = line.strip()
        if not stripped_line:
            continue
        match = re.match(college_name_regex, stripped_line)
        if match:
            found_colleges.append(match.group(1))

    if found_colleges:
        unique_sorted_colleges = sorted(list(set(found_colleges)))

        if save_to_file:
            try:
                with open(output_filename, "w", encoding="utf-8") as f:
                    for college in unique_sorted_colleges:
                        f.write(college + "\n")
                print(f"Successfully saved the final list of unique colleges to '{FINAL_COLLEGE_LIST_FILENAME}'")
            except Exception as e:
                print(f"Error saving the final college list to file: {e}")
                
        return "\n".join(unique_sorted_colleges)
    else:
        print("No college names found in the extracted text using the regex.")
        return ""
# --- Main Processing ---
def main():
    print(f"Attempting to extract text from PDF: {PDF_FILE_PATH}")
    
    extracted_text = extract_text_from_pdf(
        PDF_FILE_PATH,
        save_to_file=True,
        output_filename=OUTPUT_TXT_FILENAME
    )

    if not extracted_text:
        print(f"Failed to extract text from '{PDF_FILE_PATH}' or the PDF was empty. Regex processing will be skipped.")
        return

    print("\\n--- Applying Regex to Find College Names in Extracted Text ---")
    regex_college_names(extracted_text)
if __name__ == "__main__":
    main()