import pdfplumber
import io

def extract_text_from_pdf(pdf_file_source):
    """
    Extracts raw text content from a PDF file.

    Args:
        pdf_file_source: Either a string representing the file path to the PDF,
                         or a file-like object (bytes) from a file upload.

    Returns:
        str: A single string containing all extracted text from the PDF.
             Returns an empty string if extraction fails or the file is not a PDF.
    """
    all_text = []
    try:
        # pdfplumber.open should handle both file paths and file-like objects
        with pdfplumber.open(pdf_file_source) as pdf:
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text: # check if text was extracted
                    all_text.append(page_text)
    except Exception as e:
        print(f"Error processing PDF: {e}")
        return ""

    return "\n".join(all_text)

# --- Tests ---

if __name__ == "__main__":
    print("Testing the PDF parsing module...")

    # **Test Case 1: Using a local file path**
    # Replace 'path/to/your/List of Chloe's Colleges for 2025 Interview Spreadsheet.pdf'
    # with the actual path to your uploaded PDF file.
    # For this test to run, you need to download the PDF provided by the user and place it
    # in a known location, then update the path below.
    # Example: local_pdf_path = "List of Chloe's Colleges for 2025 Interview Spreadsheet.pdf"
    local_pdf_path = "List of Chloe's Colleges for 2025 Interview Spreadsheet.pdf" # IMPORTANT: Update this path

    print(f"\n--- Test Case 1: Processing PDF from path: {local_pdf_path} ---")
    try:
        # This assumes the PDF file is in the same directory as pdf_processor.py
        # If not, provide the full or relative path.
        extracted_text_from_path = extract_text_from_pdf(local_pdf_path)
        if extracted_text_from_path:
            print(f"Successfully extracted text. Total characters: {len(extracted_text_from_path)}")
            # Save the full output to a .txt file
            output_path_filename = "extracted_text_from_path.txt"
            with open(output_path_filename, "w", encoding="utf-8") as f:
                f.write(extracted_text_from_path)
            print(f"Full extracted text saved to {output_path_filename} for review.")
        else:
            print("No text extracted or an error occurred.")
    except FileNotFoundError:
        print(f"ERROR: The file '{local_pdf_path}' was not found. "
              "Please ensure it's in the correct directory or update the path.")
    except Exception as e:
        print(f"An unexpected error occurred during Test Case 1: {e}")


    # **Test Case 2: Simulating bytes input (like from Streamlit)**
    print("\n--- Test Case 2: Processing PDF from simulated bytes input ---")
    # Again, update this path to where you have the PDF stored for testing
    try:
        with open(local_pdf_path, "rb") as f:
            pdf_bytes = io.BytesIO(f.read()) # Wrap bytes in BytesIO to make it file-like

        extracted_text_from_bytes = extract_text_from_pdf(pdf_bytes)
        if extracted_text_from_bytes:
            print(f"Successfully extracted text using bytes. Total characters: {len(extracted_text_from_bytes)}")
            # Save the full output to a .txt file
            output_bytes_filename = "extracted_text_from_bytes.txt"
            with open(output_bytes_filename, "w", encoding="utf-8") as f:
                f.write(extracted_text_from_bytes)
            print(f"Full extracted text saved to {output_bytes_filename} for review.")
        else:
            print("No text extracted from bytes or an error occurred.")
    except FileNotFoundError:
        print(f"ERROR: The file '{local_pdf_path}' was not found for Test Case 2. "
              "Please ensure it's in the correct directory or update the path.")
    except Exception as e:
        print(f"An unexpected error occurred during Test Case 2: {e}")


    # **Test Case 3: Non-existent file path**
    print("\n--- Test Case 3: Processing non-existent PDF path ---")
    non_existent_path = "path/to/non_existent_file.pdf"
    extracted_text_non_existent = extract_text_from_pdf(non_existent_path)
    if not extracted_text_non_existent:
        print(f"Correctly handled non-existent file: '{non_existent_path}'. No text extracted.")
    else:
        print(f"ERROR: Expected no text for non-existent file, but got output for '{non_existent_path}'.")

    # **Test Case 4: Invalid PDF source type**
    print("\n--- Test Case 4: Processing with invalid source type ---")
    invalid_source = 12345 # An integer, not a path or bytes
    extracted_text_invalid_source = extract_text_from_pdf(invalid_source)
    if not extracted_text_invalid_source:
        print("Correctly handled invalid source type. No text extracted.")
    else:
        print("ERROR: Expected no text for invalid source type, but got output.")