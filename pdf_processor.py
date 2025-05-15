import pdfplumber
import io

def extract_text_from_pdf(pdf_file_source, save_to_file=False, output_filename="extracted_pdf_content.txt"):
    """
    Extracts raw text content from a PDF file.

    Args:
        pdf_file_source: Either a string representing the file path to the PDF,
                         or a file-like object (bytes) from a file upload.
        save_to_file (bool): If True, saves the extracted text to a local file.
        output_filename (str): The name of the file to save the text to if save_to_file is True.

    Returns:
        str: A single string containing all extracted text from the PDF.
             Returns an empty string if extraction fails.
    """
    all_text_list = []
    extracted_text = ""
    try:
        # pdfplumber.open can handle both file paths and file-like objects
        with pdfplumber.open(pdf_file_source) as pdf:
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text: # Ensure text was extracted
                    all_text_list.append(page_text)
        
        extracted_text = "\n".join(all_text_list)

        if save_to_file:
            try:
                with open(output_filename, "w", encoding="utf-8") as f:
                    f.write(extracted_text)
                print(f"Successfully saved extracted text to '{output_filename}'")
            except Exception as e:
                print(f"Error saving text to file: {e}")

    except Exception as e:
        print(f"Error processing PDF: {e}")
        return ""

    return extracted_text