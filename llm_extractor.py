# llm_extractor.py

from openai import OpenAI # Updated import
import openai
import os
import json
import math
import time # To add delays between API calls if needed
from prompts import SYSTEM_PROMPT

try:
    client = OpenAI()
except Exception as e: # Handles missing API key or other client init issues
    print(f"Error initializing OpenAI client: {e}")
    print("Please ensure your OPENAI_API_KEY environment variable is set correctly.")
    exit()

def extract_colleges_from_text_file_llm(text_file_path, lines_per_chunk=10, model_name="gpt-4o"):
    """
    Reads a text file, sends chunks of lines to OpenAI ChatCompletions API,
    and extracts college names using JSON mode.

    Args:
        text_file_path (str): Path to the text file containing extracted PDF content.
        lines_per_chunk (int): Number of lines to send to the LLM in each API call.
        model_name (str): The OpenAI model to use (e.g., "gpt-3.5-turbo", "gpt-4-turbo-preview").

    Returns:
        set: A set of unique college names extracted from the entire file.
    """
    all_extracted_colleges = set()

    try:
        with open(text_file_path, "r", encoding="utf-8") as f:
            lines = f.readlines()
    except FileNotFoundError:
        print(f"Error: Text file not found at '{text_file_path}'")
        return all_extracted_colleges
    except Exception as e:
        print(f"Error reading text file: {e}")
        return all_extracted_colleges

    num_lines = len(lines)
    if num_lines == 0:
        print("Text file is empty. No colleges to extract.")
        return all_extracted_colleges

    num_iterations = math.ceil(num_lines / lines_per_chunk)
    print(f"Total lines: {num_lines}, Lines per chunk: {lines_per_chunk}, Iterations needed: {num_iterations}")

    for i in range(num_iterations):
        start_index = i * lines_per_chunk
        end_index = start_index + lines_per_chunk
        current_chunk_lines = lines[start_index:end_index]
        
        text_chunk = "".join([line.strip() + "\n" for line in current_chunk_lines if isinstance(line, str)]).strip()

        if not text_chunk:
            print(f"Skipping empty chunk for iteration {i+1}/{num_iterations}")
            continue

        
        print(f"\n--- Sending chunk {i+1}/{num_iterations} to LLM ({model_name}) ---")
        # print(f"User message content sent (first 300 chars):\n{user_message_content[:300]}...") # Optional

        try:
            # Using the ChatCompletions API with JSON mode
            response = client.chat.completions.create(
                model=model_name,
                response_format={"type": "json_object"}, # Requesting JSON mode
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": text_chunk}
                ],
                temperature=0.0,
            )
            
            llm_output_content = response.choices[0].message.content
            # print(f"LLM Raw JSON Output: {llm_output_content}") # For debugging

            if llm_output_content:
                try:
                    # With JSON mode, the content should be a parsable JSON string
                    parsed_json = json.loads(llm_output_content)
                    if "colleges" in parsed_json and isinstance(parsed_json["colleges"], list):
                        colleges_in_chunk = parsed_json["colleges"]
                        print(f"Extracted colleges in this chunk: {colleges_in_chunk}")
                        for college in colleges_in_chunk:
                            if isinstance(college, str) and college.strip():
                                all_extracted_colleges.add(college.strip())
                    else:
                        print(f"Warning: 'colleges' key missing or not a list in LLM JSON response for chunk {i+1}: {llm_output_content}")
                except json.JSONDecodeError as json_e:
                    print(f"Warning: Could not decode JSON from LLM response for chunk {i+1}: {json_e}")
                    print(f"Problematic content: '{llm_output_content}'")
            else:
                print(f"Warning: LLM returned empty content for chunk {i+1}.")

            # Optional: Add a small delay to respect API rate limits
            # time.sleep(1) # Adjust as needed, especially for models with stricter rate limits

        except openai.APIError as e: # Catch specific OpenAI errors
            print(f"OpenAI API error for chunk {i+1}: {e}")
            print("Continuing to the next chunk if possible...")
            # Consider more robust error handling, like retries with backoff
        except Exception as e:
            print(f"An unexpected error occurred during LLM call for chunk {i+1}: {e}")

    return all_extracted_colleges

if __name__ == "__main__":
    # Assumes pdf_processor.py has run and created this file.
    input_text_file = "extracted_text_from_bytes.txt" 

    print(f"\n--- Starting College Extraction from '{input_text_file}' using model gpt-4o ---")
    
    # Check if API key is likely available (client initialization doesn't guarantee it if env var empty)
    if not client.api_key: # client.api_key would be None if not set
         print("Error: OPENAI_API_KEY environment variable not set or empty.")
         print("Please set it before running the script. Skipping LLM extraction.")
    elif not os.path.exists(input_text_file):
        print(f"Error: Input text file '{input_text_file}' not found. "
              "Please run pdf_processor.py first to generate it or check the path.")
    else:
        final_college_set = extract_colleges_from_text_file_llm(input_text_file)
        
        print("\n--- Final Set of Extracted Unique College Names ---")
        if final_college_set:
            # Sort for consistent output
            sorted_colleges = sorted(list(final_college_set))
            for idx, college in enumerate(sorted_colleges):
                print(f"{idx + 1}. {college}")
            print(f"Total unique colleges found: {len(final_college_set)}")
        else:
            print("No college names were extracted.")