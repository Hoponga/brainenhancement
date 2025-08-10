"""
PDF Processing Module
Handles extraction of text from PDF files
"""

import logging
from pathlib import Path
from typing import Optional
import pdfplumber

logger = logging.getLogger(__name__)


class PDFProcessor:
    """Handles PDF text extraction and processing"""
    
    def __init__(self):
        self.max_pages = 50  # Limit for performance
        
    def extract_text(self, pdf_path: str) -> Optional[str]:
        """
        Extract text from PDF file
        
        Args:
            pdf_path: Path to PDF file
            
        Returns:
            Extracted text or None if error
        """
        try:
            pdf_path = Path(pdf_path)
            if not pdf_path.exists():
                logger.error(f"PDF file not found: {pdf_path}")
                return None
                
            if not pdf_path.suffix.lower() == '.pdf':
                logger.error(f"File is not a PDF: {pdf_path}")
                return None
                
            text_content = []
            
            with pdfplumber.open(pdf_path) as pdf:
                # Check if PDF has readable text
                if len(pdf.pages) == 0:
                    logger.error("PDF has no pages")
                    return None
                    
                # Extract text from each page
                for i, page in enumerate(pdf.pages[:self.max_pages]):
                    try:
                        page_text = page.extract_text()
                        if page_text:
                            text_content.append(page_text)
                            logger.debug(f"Extracted text from page {i+1}")
                    except Exception as e:
                        logger.warning(f"Failed to extract text from page {i+1}: {e}")
                        continue
                        
            if not text_content:
                logger.error("No text could be extracted from PDF")
                return None
                
            # Join all pages with double newline
            full_text = "\n\n".join(text_content)
            
            # Clean up excessive whitespace
            full_text = self._clean_text(full_text)
            
            logger.info(f"Successfully extracted {len(full_text)} characters from PDF")
            return full_text
            
        except Exception as e:
            logger.error(f"Error processing PDF: {e}")
            return None
            
    def _clean_text(self, text: str) -> str:
        """
        Clean extracted text
        
        Args:
            text: Raw extracted text
            
        Returns:
            Cleaned text
        """
        # Remove excessive newlines
        while '\n\n\n' in text:
            text = text.replace('\n\n\n', '\n\n')
            
        # Remove excessive spaces
        while '  ' in text:
            text = text.replace('  ', ' ')
            
        # Strip leading/trailing whitespace
        text = text.strip()
        
        return text
        
    def validate_pdf(self, pdf_path: str) -> tuple[bool, str]:
        """
        Validate PDF file before processing
        
        Args:
            pdf_path: Path to PDF file
            
        Returns:
            Tuple of (is_valid, message)
        """
        try:
            pdf_path = Path(pdf_path)
            
            if not pdf_path.exists():
                return False, "File does not exist"
                
            if not pdf_path.suffix.lower() == '.pdf':
                return False, "File is not a PDF"
                
            # Check file size (limit to 50MB)
            file_size_mb = pdf_path.stat().st_size / (1024 * 1024)
            if file_size_mb > 50:
                return False, f"File too large ({file_size_mb:.1f}MB > 50MB)"
                
            # Try to open and check if it has pages
            with pdfplumber.open(pdf_path) as pdf:
                if len(pdf.pages) == 0:
                    return False, "PDF has no pages"
                    
                # Check if first page has extractable text
                first_page_text = pdf.pages[0].extract_text()
                if not first_page_text or len(first_page_text.strip()) < 10:
                    return False, "PDF appears to be image-only or has no extractable text"
                    
            return True, "PDF is valid"
            
        except Exception as e:
            return False, f"Error validating PDF: {e}"