#!/usr/bin/env python3
"""
Quick dataset generator for sales
Generates datasets with proper naming and organization
"""

import subprocess
import sys
import os
from datetime import datetime

def generate_dataset(size, output_name=None):
    """Generate a dataset with the specified size"""
    
    if size == "small":
        users, products, orders, reviews = 100, 50, 200, 150
        price = "$99"
    elif size == "medium":
        users, products, orders, reviews = 1000, 500, 2000, 1500
        price = "$299"
    elif size == "large":
        users, products, orders, reviews = 5000, 2000, 10000, 8000
        price = "$799"
    else:
        print("Invalid size. Use: small, medium, or large")
        return
    
    if not output_name:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_name = f"sale_{size}_{timestamp}"
    
    print(f"Generating {size} dataset...")
    print(f"Users: {users:,}, Products: {products:,}, Orders: {orders:,}, Reviews: {reviews:,}")
    print(f"Target Price: {price}")
    print(f"Output: {output_name}")
    print("-" * 50)
    
    # Generate the dataset
    cmd = [
        "python", "realistic_generator.py",
        "--users", str(users),
        "--products", str(products),
        "--orders", str(orders),
        "--reviews", str(reviews),
        "--output", output_name
    ]
    
    try:
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        print("✅ Dataset generated successfully!")
        print(f"📁 Location: {output_name}/")
        
        # Show file sizes
        if os.path.exists(output_name):
            print("\n📊 File Sizes:")
            for file in os.listdir(output_name):
                if file.endswith('.csv'):
                    size_mb = os.path.getsize(f"{output_name}/{file}") / (1024 * 1024)
                    print(f"  {file}: {size_mb:.1f} MB")
        
        print(f"\n💰 Ready to sell for {price}!")
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Error generating dataset: {e}")
        print(f"Error output: {e.stderr}")
    except FileNotFoundError:
        print("❌ Error: realistic_generator.py not found. Make sure you're in the right directory.")

def main():
    if len(sys.argv) < 2:
        print("Usage: python generate_for_sale.py <size> [output_name]")
        print("Sizes: small, medium, large")
        print("Examples:")
        print("  python generate_for_sale.py small")
        print("  python generate_for_sale.py medium my_custom_dataset")
        print("  python generate_for_sale.py large")
        return
    
    size = sys.argv[1].lower()
    output_name = sys.argv[2] if len(sys.argv) > 2 else None
    
    generate_dataset(size, output_name)

if __name__ == "__main__":
    main()

