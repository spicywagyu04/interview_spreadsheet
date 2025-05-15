import os
import utils
from pdf_processor import extract_text_from_pdf
from apply_regex import regex_college_names 
from llm import llm_gemini
from highlight import process_college_data_to_new_sheet
from prompts import SYSTEM_PROMPT_FILTER

def workflow(input_excel_path, input_pdf_path, output_excel_path="output.xlsx", column="A", start_row=3):
    """
    Main orchestration function to run the college list processing workflow.
    """
    print("--- Starting Orchestration Workflow ---")
    # --- Extract text from PDF ---
    pdf_text = extract_text_from_pdf(input_pdf_path)
    
    # --- Apply regex to extract potential college names ---
    regex_results = regex_college_names(pdf_text)
    
    # --- Process regex results with LLM ---
    llm_results = llm_gemini(user_prompt=regex_results, system_prompt=SYSTEM_PROMPT_FILTER)
    
    # --- Normalize LLM results with utils ---
    ground_truth_college_names = utils.extract_column_data_as_string(input_excel_path, column, start_row)
    normalized_college_names = utils.parse_college_names(ground_truth_college_names, llm_results)
    
    # --- Highlight results in Excel ---
    process_college_data_to_new_sheet(input_excel_path, normalized_college_names, output_excel_path)
    
    print("--- Orchestration Workflow Completed ---")

def main():
    print("Starting workflow...")
    workflow("../SAMPLE 2025 College Bound Interview Spreadsheet.xlsx", "../List of Chloe's Colleges for 2025 Interview Spreadsheet.pdf")
    
if __name__ == "__main__":
    main()
    