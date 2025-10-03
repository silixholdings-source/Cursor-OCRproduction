"""
Create a test image with text for OCR testing
"""
from PIL import Image, ImageDraw, ImageFont
import os

def create_test_image():
    """Create a simple test image with text for OCR testing"""
    
    # Create a white image
    width, height = 800, 600
    image = Image.new('RGB', (width, height), color='white')
    draw = ImageDraw.Draw(image)
    
    # Try to use a system font, fallback to default
    try:
        font = ImageFont.truetype("arial.ttf", 24)
    except:
        try:
            font = ImageFont.truetype("C:/Windows/Fonts/arial.ttf", 24)
        except:
            font = ImageFont.load_default()
    
    # Sample text for OCR testing
    test_text = [
        "OCR TEST DOCUMENT",
        "Invoice #: INV-2024-001",
        "Date: January 15, 2024",
        "Vendor: Test Company Ltd",
        "Amount: $1,234.56",
        "Description: Office Supplies",
        "This is a test document for OCR processing.",
        "The text should be extracted accurately.",
        "Confidence score should be high."
    ]
    
    # Draw text on image
    y_position = 50
    for line in test_text:
        draw.text((50, y_position), line, fill='black', font=font)
        y_position += 40
    
    # Save the image
    filename = "test_ocr_image.png"
    image.save(filename)
    print(f"✅ Test image created: {filename}")
    print(f"📁 File size: {os.path.getsize(filename)} bytes")
    print(f"🖼️  Dimensions: {width}x{height} pixels")
    
    return filename

if __name__ == "__main__":
    create_test_image()
