# Script to batch convert all PDFs in a specified directory to text files
# using PyPDF2. Each PDF will produce a .txt file with the same base name.

import os
import re
import argparse
from PyPDF2 import PdfReader

def convert_pdf_to_txt(pdf_path: str) -> str:
    """Extract text from a PDF file, collapse whitespace, and return it."""
    print(f"Starting to read PDF: {pdf_path}")
    reader = PdfReader(pdf_path)
    text_chunks = []
    for page_num, page in enumerate(reader.pages, start=1):
        print(f"Extracting text from page {page_num}")
        text = page.extract_text() or ""
        # Remove links, page numbers, and references using regex
        text = re.sub(r'http\S+|www\.\S+', '', text)  # Remove URLs
        text = re.sub(r'\bPage \d+\b', '', text)  # Remove page numbers
        text = re.sub(r'\bReferences?\b', '', text)  # Remove references
        text_chunks.append(text)
    raw_text = "\n".join(text_chunks)
    # Collapse any run of whitespace (spaces, tabs, newlines) to a single space
    cleaned_text = re.sub(r"\s+", " ", raw_text).strip()
    print(f"Finished reading PDF: {pdf_path}")
    return cleaned_text

def main(source_directory: str, output_directory: str):
    print(f"Starting the PDF to text conversion process in directory: {source_directory}")
    print(f"Output will be saved to: {output_directory}")

    # Ensure the output directory exists
    if not os.path.exists(output_directory):
        os.makedirs(output_directory)

    # Find all PDF files in the specified directory
    for entry in os.listdir(source_directory):
        if entry.lower().endswith('.pdf') and os.path.isfile(os.path.join(source_directory, entry)):
            txt_filename = os.path.splitext(entry)[0] + '.txt'
            output_path = os.path.join(output_directory, txt_filename)
            print(f"Found PDF file: {entry}")
            print(f"Converting {entry} -> {output_path}")
            try:
                pdf_text = convert_pdf_to_txt(os.path.join(source_directory, entry))
                with open(output_path, 'w', encoding='utf-8') as f:
                    f.write(pdf_text)
                print(f"Successfully converted {entry} to {output_path}")
            except Exception as e:
                print(f"Failed to convert {entry}: {e}")

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Convert PDFs to text files.')
    parser.add_argument('source_directory', type=str, help='The directory containing the PDF files to convert.')
    parser.add_argument('output_directory', type=str, help='The directory where the text files will be saved.')
    args = parser.parse_args()
    main(args.source_directory, args.output_directory)
