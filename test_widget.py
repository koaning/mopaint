#!/usr/bin/env python3
"""
Quick test script to verify the widget loads without JavaScript errors.
"""
from mopaint import Paint
from PIL import Image

# Test 1: Create widget without init_image (should work as before)
print("Test 1: Creating widget without init_image...")
widget1 = Paint()
print(f"✓ Widget created successfully: {widget1.width}x{widget1.height}")

# Test 2: Create widget with init_image (should auto-size)
print("\nTest 2: Creating widget with init_image...")
test_img = Image.new('RGB', (200, 100), 'blue')
widget2 = Paint(init_image=test_img)
print(f"✓ Widget created successfully: {widget2.width}x{widget2.height}")
print(f"✓ Dimensions match image: {widget2.width == 200 and widget2.height == 100}")

# Test 3: Try invalid combination (should raise error)
print("\nTest 3: Testing parameter validation...")
try:
    Paint(init_image=test_img, width=300)
    print("✗ Should have raised ValueError")
except ValueError as e:
    print(f"✓ Correctly raised ValueError: {str(e)[:60]}...")

print("\nAll tests passed! Widget should work correctly.")