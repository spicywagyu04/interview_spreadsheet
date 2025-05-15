import pandas as pd
from prompts import SYSTEM_PROMPT_LIST_PROCESSING
import llm
import json

def _col_letter_to_index(letter_col):
    """
    Converts an Excel column letter (e.g., 'A', 'B', 'AA') to a 0-based integer index.

    Args:
        letter_col (str): The Excel column letter. Case-insensitive.

    Returns:
        int: The 0-based column index.

    Raises:
        ValueError: If the column letter is invalid (e.g., empty, contains non-alphabetic chars).
    """
    if not isinstance(letter_col, str) or not letter_col:
        raise ValueError("Column letter must be a non-empty string.")
    
    index = 0
    for char_val in letter_col.upper():
        if not 'A' <= char_val <= 'Z':
            raise ValueError(f"Invalid character '{char_val}' in column letter '{letter_col}'. Only A-Z allowed.")
        index = index * 26 + (ord(char_val) - ord('A')) + 1
    if index == 0: # Should not happen if letter_col is not empty and valid
        raise ValueError("Column letter evaluated to an invalid index (0 before 0-indexing).")
    return index - 1 # Return 0-indexed (A=0, B=1, ...)


def extract_column_data_as_string(excel_file_path, column_letter, row_to_start_after):
    """
    Extracts entries from a specified column of an Excel file,
    starting after a specified row number, and returns them as a single
    newline-separated string.

    Args:
        excel_file_path (str): The path to the Excel file.
        column_letter (str): The column letter (e.g., 'A', 'B', 'AA'). Case-insensitive.
        row_to_start_after (int): The 1-based row number *after which* to start
                                  extracting. For example, if 3, extraction
                                  starts from row 4. If 0, extraction starts
                                  from row 1.

    Returns:
        str: A string containing the specified entries, each separated by
             a newline. Returns an empty string if no data is found under
             the conditions, or if an error occurs.
    """
    try:
        if not isinstance(row_to_start_after, int) or row_to_start_after < 0:
            raise ValueError("'row_to_start_after' must be a non-negative integer (0 or greater).")

        col_idx = _col_letter_to_index(column_letter)
        df = pd.read_excel(excel_file_path, usecols=[col_idx], header=None, engine='openpyxl')
        slicing_start_index_0_based = row_to_start_after

        if len(df) > slicing_start_index_0_based:
            column_values = [str(item) for item in df.iloc[slicing_start_index_0_based:, 0].tolist()]
            return "\n".join(column_values)
        else:
            return ""

    except FileNotFoundError:
        print(f"Error: The file '{excel_file_path}' was not found.")
        return ""
    except ValueError as ve:
        print(f"Input or File Error: {ve}")
        return ""
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        return ""
    
def parse_college_names(ground_truth_college_names, extracted_college_names):
    """
    Modifies same college with different names in extracted_college_names
    to be the same college name in ground_truth_college_names.

    Args:
        ground_truth_college_names (str): A string containing newline-separated college names.
        extracted_college_names (str): A string of a JSON object containing newline-separated college names.
    """
    
    user_message = f"""
    <ground truth list>
    {ground_truth_college_names}
    </ground truth list>

    <JSON list>:
    {extracted_college_names}
    </JSON list>
    """
    
    res = llm.llm_gemini(
        user_prompt=user_message,
        system_prompt=SYSTEM_PROMPT_LIST_PROCESSING,
        temperature=0.0
    )
    return res

if __name__ == "__main__":
    print("--- Test Case for parse_college_names ---")

    # 1. Prepare ground_truth_college_names
    excel_file = "SAMPLE 2025 College Bound Interview Spreadsheet.xlsx"
    ground_truth_column = "A"
    ground_truth_row_after = 3
    print(f"Extracting ground truth colleges from '{excel_file}', column '{ground_truth_column}', after row {ground_truth_row_after}...")
    ground_truth_input = extract_column_data_as_string(excel_file, ground_truth_column, ground_truth_row_after)

    if not ground_truth_input:
        print(f"Could not extract ground truth data from '{excel_file}'. Please check the file and parameters.")
        print("Skipping test for parse_college_names.")
        exit()
    # print(f"Ground Truth Input (first 300 chars):\n{ground_truth_input[:300]}...\n")

    # 2. Prepare extracted_college_names (as a JSON string)
    json_file_path = "sample_res.json"
    extracted_json_input_string = None
    print(f"Loading extracted college names from JSON file: '{json_file_path}'...")
    try:
        with open(json_file_path, 'r', encoding='utf-8') as f:
            # Load the JSON object from file
            json_data_object = json.load(f)
            # Convert the Python object back to a JSON formatted string
            extracted_json_input_string = json.dumps(json_data_object)
        # print(f"Extracted JSON String (first 300 chars):\n{extracted_json_input_string[:300]}...\n")
    except FileNotFoundError:
        print(f"Error: The JSON file '{json_file_path}' was not found.")
        extracted_json_input_string = "{\"colleges\": []}" # Default to empty list JSON string
        print(f"Using default empty JSON string: {extracted_json_input_string}")
    except json.JSONDecodeError as e:
        print(f"Error decoding JSON from '{json_file_path}': {e}")
        extracted_json_input_string = "{\"colleges\": []}" # Default to empty list JSON string
        print(f"Using default empty JSON string: {extracted_json_input_string}")
    except Exception as e:
        print(f"An unexpected error occurred while reading '{json_file_path}': {e}")
        extracted_json_input_string = "{\"colleges\": []}" # Default to empty list JSON string
        print(f"Using default empty JSON string: {extracted_json_input_string}")

    if extracted_json_input_string is None: # Should be caught by specific exceptions but as a safeguard
        print(f"Failed to prepare extracted_json_input_string from '{json_file_path}'.")
        print("Skipping test for parse_college_names.")
        exit()
        
    # 3. Call parse_college_names
    print("Calling parse_college_names with the prepared inputs...")
    # Ensure your GOOGLE_API_KEY and/or GEMINI_API_KEY (depending on llm.py) is set
    processed_list = parse_college_names(ground_truth_input, extracted_json_input_string)

    # 4. Print the result
    print("\n--- Result from parse_college_names ---")
    if processed_list:
        print(processed_list)
    else:
        print("parse_college_names returned no result or an empty result.")
    print("\n--- Test Case End ---")
    
    
    