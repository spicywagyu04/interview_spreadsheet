import streamlit as st
import os
import tempfile # To handle temporary file creation for uploaded files
from orchestrator import workflow # Assuming your backend script is named orchestrator.py

# --- Page Configuration (Optional but Recommended) ---
st.set_page_config(
    page_title="College List Processor",
    page_icon="📄", # You can use an emoji or a URL to an image
    layout="centered" # You can also try "wide" if you prefer
)

# --- Main Streamlit App ---
st.title("📄 College List Processor")

st.markdown("""
Upload an Excel spreadsheet (containing a list of colleges) and a PDF document.
The system will process the PDF to find college names, compare them against the list in the Excel sheet,
and highlight the matching colleges in a new Excel file.
""")

# --- File Uploaders (Main Page) ---
st.header("📤 1. Upload Files")
uploaded_excel_file = st.file_uploader("Upload Excel Spreadsheet (e.g., college_list.xlsx)", type=["xlsx", "xls"])
uploaded_pdf_file = st.file_uploader("Upload PDF Document (e.g., course_catalog.pdf)", type=["pdf"])

# --- Output Configuration (Main Page) ---
st.header("⚙️ 2. Output Settings")
output_filename = st.text_input("Enter desired output file name:", "processed_colleges.xlsx")

# --- Ensure output filename has .xlsx extension ---
if output_filename and not output_filename.endswith(".xlsx"):
    # Check if output_filename is not empty before trying to append
    output_filename_with_ext = output_filename + ".xlsx"
else:
    output_filename_with_ext = output_filename if output_filename else "processed_colleges.xlsx"


# --- Processing Logic (Main Page) ---
st.header("🚀 3. Process and Download")

if uploaded_excel_file is not None and uploaded_pdf_file is not None:
    if st.button("Process Files", type="primary", use_container_width=True):
        with st.spinner("Processing... please wait. This may take a few moments."):
            try:
                # Create temporary files to store uploaded data, as the backend expects file paths
                with tempfile.NamedTemporaryFile(delete=False, suffix=".xlsx") as tmp_excel:
                    tmp_excel.write(uploaded_excel_file.getvalue())
                    input_excel_path = tmp_excel.name

                with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_pdf:
                    tmp_pdf.write(uploaded_pdf_file.getvalue())
                    input_pdf_path = tmp_pdf.name

                # Define a temporary path for the output file
                output_dir = tempfile.mkdtemp()
                # Use the filename potentially corrected with .xlsx extension
                final_output_filename = os.path.basename(output_filename_with_ext)
                output_excel_path = os.path.join(output_dir, final_output_filename)


                st.info(f"Excel input: {uploaded_excel_file.name}")
                st.info(f"PDF input: {uploaded_pdf_file.name}")
                st.info(f"Output will be: {final_output_filename}")
                st.info("Processing started...")

                # --- Call your backend workflow ---
                workflow(
                    input_excel_path=input_excel_path,
                    input_pdf_path=input_pdf_path,
                    output_excel_path=output_excel_path
                )

                st.success("✅ Workflow completed successfully!")

                # --- Provide Download Link ---
                with open(output_excel_path, "rb") as file:
                    st.download_button(
                        label=f"⬇️ Download {final_output_filename}",
                        data=file,
                        file_name=final_output_filename, # Use the user-defined or default output name
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                        use_container_width=True
                    )

            except Exception as e:
                st.error(f"An error occurred: {e}")
                st.error("Please check the console for more detailed error messages if running locally.")
                import traceback
                st.text_area("Error Traceback:", traceback.format_exc(), height=300)

            finally:
                # Clean up temporary files
                if 'input_excel_path' in locals() and os.path.exists(input_excel_path):
                    os.remove(input_excel_path)
                if 'input_pdf_path' in locals() and os.path.exists(input_pdf_path):
                    os.remove(input_pdf_path)
                # Output file in temp dir will be cleaned up eventually, or can be explicitly if needed
                # For Streamlit Cloud, temp dirs are managed.

else:
    st.warning("Please upload both an Excel file and a PDF file above to enable processing.")
    # You can add a placeholder image or message if you like
    # st.image("your_placeholder_image_url_here", width=200)
    st.markdown("<p style='text-align: center;'>Waiting for files...</p>", unsafe_allow_html=True)

st.markdown("---")
st.markdown("Created with Streamlit")