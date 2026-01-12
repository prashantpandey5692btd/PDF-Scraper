"""
Comprehensive PDF Reader
Extracts text, images, tables, URLs, and numbers from PDF files.
"""

import pdfplumber
import pytesseract
from PIL import Image
import re
import os
from pathlib import Path


class PDFReader:
    def __init__(self, pdf_path):
        """Initialize PDF reader with file path."""
        self.pdf_path = pdf_path
        self.data = {
            'text': [],
            'tables': [],
            'images': [],
            'urls': [],
            'numbers': []
        }

    def extract_all(self, save_images=True, output_dir='extracted_images'):
        """
        Extract all content from PDF.

        Args:
            save_images: Whether to save extracted images to disk
            output_dir: Directory to save images
        """
        if save_images:
            os.makedirs(output_dir, exist_ok=True)

        with pdfplumber.open(self.pdf_path) as pdf:
            for page_num, page in enumerate(pdf.pages, start=1):
                print(f"Processing page {page_num}...")

                # Extract text
                text = page.extract_text()
                if text:
                    self.data['text'].append({
                        'page': page_num,
                        'content': text
                    })

                    # Extract URLs from text
                    urls = self._extract_urls(text)
                    if urls:
                        self.data['urls'].extend([{
                            'page': page_num,
                            'url': url
                        } for url in urls])

                    # Extract numbers from text
                    numbers = self._extract_numbers(text)
                    if numbers:
                        self.data['numbers'].append({
                            'page': page_num,
                            'numbers': numbers
                        })

                # Extract tables
                tables = page.extract_tables()
                if tables:
                    for table_num, table in enumerate(tables, start=1):
                        self.data['tables'].append({
                            'page': page_num,
                            'table_number': table_num,
                            'data': table
                        })

                # Extract images
                if save_images:
                    images = page.images
                    for img_num, img in enumerate(images, start=1):
                        self.data['images'].append({
                            'page': page_num,
                            'image_number': img_num,
                            'saved_as': f"{output_dir}/page{page_num}_img{img_num}.png"
                        })

        return self.data

    def _extract_urls(self, text):
        """Extract URLs from text using regex."""
        url_pattern = r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+'
        urls = re.findall(url_pattern, text)
        return list(set(urls))  # Remove duplicates

    def _extract_numbers(self, text):
        """Extract numbers from text (integers and floats)."""
        number_pattern = r'-?\d+\.?\d*'
        numbers = re.findall(number_pattern, text)
        return [float(n) if '.' in n else int(n) for n in numbers if n]

    def print_summary(self):
        """Print a summary of extracted content."""
        print("\n" + "=" * 60)
        print("PDF EXTRACTION SUMMARY")
        print("=" * 60)

        # Text summary
        total_text = sum(len(item['content']) for item in self.data['text'])
        print(f"\n📄 TEXT:")
        print(f"   Pages with text: {len(self.data['text'])}")
        print(f"   Total characters: {total_text}")

        # Tables summary
        print(f"\n📊 TABLES:")
        print(f"   Total tables found: {len(self.data['tables'])}")
        for table in self.data['tables']:
            rows = len(table['data'])
            cols = len(table['data'][0]) if table['data'] else 0
            print(f"   - Page {table['page']}, Table {table['table_number']}: {rows}x{cols}")

        # Images summary
        print(f"\n🖼️  IMAGES:")
        print(f"   Total images found: {len(self.data['images'])}")

        # URLs summary
        print(f"\n🔗 URLs:")
        print(f"   Total URLs found: {len(self.data['urls'])}")
        unique_urls = set(item['url'] for item in self.data['urls'])
        for url in list(unique_urls)[:5]:  # Show first 5
            print(f"   - {url}")
        if len(unique_urls) > 5:
            print(f"   ... and {len(unique_urls) - 5} more")

        # Numbers summary
        total_numbers = sum(len(item['numbers']) for item in self.data['numbers'])
        print(f"\n🔢 NUMBERS:")
        print(f"   Total numbers found: {total_numbers}")

        print("\n" + "=" * 60)

    def save_text_to_file(self, output_file='extracted_text.txt'):
        """Save all extracted text to a file."""
        with open(output_file, 'w', encoding='utf-8') as f:
            for item in self.data['text']:
                f.write(f"\n{'=' * 60}\n")
                f.write(f"PAGE {item['page']}\n")
                f.write(f"{'=' * 60}\n")
                f.write(item['content'])
                f.write("\n")
        print(f"\n✅ Text saved to: {output_file}")

    def save_tables_to_csv(self, output_dir='extracted_tables'):
        """Save all tables to CSV files."""
        import csv
        os.makedirs(output_dir, exist_ok=True)

        for table in self.data['tables']:
            filename = f"{output_dir}/page{table['page']}_table{table['table_number']}.csv"
            with open(filename, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerows(table['data'])

        if self.data['tables']:
            print(f"\n✅ Tables saved to: {output_dir}/")


def main():
    """Main function to demonstrate usage."""

    # Replace with your PDF file path
    pdf_file = r"C:\Users\DELL\Downloads\70000000108876651_142915841_2025_AST_AAICC5750E_Show Cause Notice_1079790412(1)_20082025.pdf"  # Change this to your PDF file

    # Check if file exists
    if not os.path.exists(pdf_file):
        print(f"❌ Error: File '{pdf_file}' not found!")
        print("\nPlease update the 'pdf_file' variable with your PDF path.")
        return

    print(f"📖 Reading PDF: {pdf_file}\n")

    # Create reader instance
    reader = PDFReader(pdf_file)

    # Extract all content
    data = reader.extract_all(save_images=True, output_dir='extracted_images')

    # Print summary
    reader.print_summary()

    # Save extracted content
    reader.save_text_to_file('extracted_text.txt')
    reader.save_tables_to_csv('extracted_tables')

    # Example: Access specific data
    print("\n" + "=" * 60)
    print("SAMPLE EXTRACTED DATA")
    print("=" * 60)

    # Show first page text (first 500 characters)
    if data['text']:
        print("\n📄 First page text (preview):")
        print(data['text'][0]['content'][:500] + "...")

    # Show first table
    if data['tables']:
        print("\n📊 First table (first 3 rows):")
        first_table = data['tables'][0]['data']
        for row in first_table[:3]:
            print(row)

    # Show all URLs
    if data['urls']:
        print("\n🔗 All URLs found:")
        for item in data['urls']:
            print(f"   Page {item['page']}: {item['url']}")


if __name__ == "__main__":
    main()