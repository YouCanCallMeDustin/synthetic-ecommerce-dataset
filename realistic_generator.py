#!/usr/bin/env python3
"""
Ultra-Realistic Synthetic E-commerce Dataset Generator
Creates datasets that look like they came from real e-commerce businesses
"""

import pandas as pd
import numpy as np
from faker import Faker
import random
from datetime import datetime, timedelta
import os
import argparse
import re

# Initialize Faker with seed for reproducible results
fake = Faker()
Faker.seed(42)
np.random.seed(42)
random.seed(42)

def get_size_category(num_users, num_products, num_orders, num_reviews):
    """Determine the size category based on the largest parameter."""
    max_size = max(num_users, num_products, num_orders, num_reviews)
    
    if max_size <= 1000:
        return "small"
    elif max_size <= 10000:
        return "medium"
    elif max_size <= 100000:
        return "large"
    else:
        return "xlarge"

def create_timestamped_folder(size_category, base_dir="datasets"):
    """Create a timestamped folder for the dataset."""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    folder_name = f"{size_category}_{timestamp}"
    full_path = os.path.join(base_dir, folder_name)
    return full_path

def generate_realistic_pricing(category, subcategory, brand, product_name):
    """Generate realistic pricing based on product characteristics."""
    
    # Base pricing by category and subcategory
    base_prices = {
        'Electronics': {
            'Smartphones': (299, 1299),
            'Laptops': (399, 2999),
            'Tablets': (199, 899),
            'Headphones': (29, 499),
            'Cameras': (199, 1999),
            'Gaming': (199, 999),
            'Smart Home': (19, 299),
            'Accessories': (9, 199)
        },
        'Clothing': {
            'Tops': (15, 89),
            'Bottoms': (25, 129),
            'Dresses': (29, 199),
            'Outerwear': (49, 299),
            'Shoes': (39, 199),
            'Accessories': (9, 79),
            'Underwear': (8, 39),
            'Activewear': (19, 99)
        },
        'Beauty': {
            'Skincare': (8, 89),
            'Makeup': (5, 79),
            'Fragrance': (19, 199),
            'Hair Care': (9, 69),
            'Body Care': (5, 49),
            'Tools': (3, 79),
            'Men\'s Grooming': (5, 59),
            'Nail Care': (3, 29)
        },
        'Home': {
            'Furniture': (49, 899),
            'Decor': (19, 199),
            'Kitchen': (29, 499),
            'Bedding': (24, 299),
            'Bath': (14, 149),
            'Storage': (19, 199),
            'Lighting': (24, 299),
            'Garden': (29, 399)
        },
        'Sports': {
            'Fitness': (19, 199),
            'Outdoor': (29, 299),
            'Team Sports': (14, 149),
            'Water Sports': (9, 99),
            'Winter Sports': (19, 199),
            'Cycling': (49, 499),
            'Running': (24, 199),
            'Yoga': (14, 99)
        },
        'Toys': {
            'Action Figures': (9, 49),
            'Dolls': (14, 79),
            'Building Sets': (19, 199),
            'Board Games': (24, 149),
            'Puzzles': (8, 49),
            'Educational': (14, 199),
            'Outdoor': (29, 299),
            'Electronic': (39, 399)
        }
    }
    
    # Brand premium multipliers
    brand_premiums = {
        'Apple': 1.8, 'Samsung': 1.4, 'Sony': 1.3, 'Bose': 1.5,
        'Nike': 1.4, 'Adidas': 1.3, 'Lululemon': 1.6, 'Patagonia': 1.5,
        'Chanel': 2.5, 'MAC': 1.8, 'Urban Decay': 1.4, 'Fenty Beauty': 1.3,
        'IKEA': 0.8, 'West Elm': 1.4, 'Pottery Barn': 1.6,
        'LEGO': 1.3, 'Mattel': 1.1, 'Hasbro': 1.2
    }
    
    # Get base price range
    if category in base_prices and subcategory in base_prices[category]:
        min_price, max_price = base_prices[category][subcategory]
    else:
        min_price, max_price = 10, 100
    
    # Apply brand premium
    brand_premium = brand_premiums.get(brand, 1.0)
    min_price *= brand_premium
    max_price *= brand_premium
    
    # Generate price with realistic psychology (ending in .99, .95, .00)
    base_price = np.random.uniform(min_price, max_price)
    
    # Apply price ending psychology
    price_endings = [0.99, 0.95, 0.00, 0.49, 0.79]
    ending = random.choice(price_endings)
    
    # Round to appropriate decimal places
    if base_price < 10:
        price = round(base_price, 2)
    elif base_price < 100:
        price = round(base_price, 2)
    else:
        price = round(base_price, 2)
    
    # Apply ending
    price = int(price) + ending
    
    return round(price, 2)

def generate_realistic_product_names():
    """Generate realistic product names with proper brand-product combinations."""
    
    product_templates = {
        'Electronics': {
            'Apple': {
                'Smartphones': ['iPhone 15 Pro', 'iPhone 15', 'iPhone 14 Pro', 'iPhone 14', 'iPhone 13', 'iPhone SE'],
                'Laptops': ['MacBook Pro 16"', 'MacBook Pro 14"', 'MacBook Air 15"', 'MacBook Air 13"'],
                'Tablets': ['iPad Pro 12.9"', 'iPad Pro 11"', 'iPad Air', 'iPad mini', 'iPad'],
                'Headphones': ['AirPods Pro (2nd gen)', 'AirPods (3rd gen)', 'AirPods Max', 'Beats Studio3'],
                'Accessories': ['Lightning to USB-C Cable', 'MagSafe Charger', 'AirTag', 'Apple Watch Band']
            },
            'Samsung': {
                'Smartphones': ['Galaxy S24 Ultra', 'Galaxy S24+', 'Galaxy S24', 'Galaxy A54', 'Galaxy Z Fold5'],
                'Tablets': ['Galaxy Tab S9 Ultra', 'Galaxy Tab S9+', 'Galaxy Tab S9', 'Galaxy Tab A8'],
                'Headphones': ['Galaxy Buds2 Pro', 'Galaxy Buds2', 'Galaxy Buds Live', 'Galaxy Buds FE'],
                'Accessories': ['45W Super Fast Charger', 'Galaxy Watch6', 'Galaxy Book4 Pro']
            },
            'Sony': {
                'Headphones': ['WH-1000XM5', 'WH-1000XM4', 'WF-1000XM5', 'WF-1000XM4', 'WH-CH720N'],
                'Cameras': ['Alpha 7 IV', 'Alpha 7R V', 'Alpha 6700', 'ZV-1M2', 'FX30'],
                'Gaming': ['PlayStation 5', 'PlayStation 5 Digital', 'DualSense Controller', 'Pulse 3D Headset']
            }
        },
        'Clothing': {
            'Nike': {
                'Shoes': ['Air Force 1', 'Air Max 270', 'Air Jordan 1', 'React Element 55', 'Blazer Mid'],
                'Activewear': ['Dri-FIT T-Shirt', 'Pro Shorts', 'Leggings', 'Hoodie', 'Windbreaker'],
                'Accessories': ['Swoosh Cap', 'Dri-FIT Socks', 'Gym Bag', 'Water Bottle']
            },
            'Adidas': {
                'Shoes': ['Stan Smith', 'Ultraboost 22', 'NMD R1', 'Gazelle', 'Superstar'],
                'Activewear': ['Trefoil T-Shirt', 'Adicolor Classics', 'Tiro Pants', 'Primeblue Hoodie'],
                'Accessories': ['3-Stripes Cap', 'Adicolor Backpack', 'Trefoil Socks']
            }
        },
        'Beauty': {
            'MAC': {
                'Makeup': ['Studio Fix Foundation', 'Ruby Woo Lipstick', 'Prep + Prime Fix+', 'Eyeshadow Palette'],
                'Skincare': ['Prep + Prime Skin', 'Studio Moisture Cream', 'Lightful C Marine-Bright']
            },
            'Urban Decay': {
                'Makeup': ['Naked Eyeshadow Palette', 'All Nighter Setting Spray', 'Vice Lipstick', 'Eyeshadow Primer Potion']
            }
        }
    }
    
    return product_templates

def generate_realistic_review_text(rating, category, subcategory, product_name, brand):
    """Generate realistic, product-specific review text."""
    
    # Review templates by category and rating
    review_templates = {
        'Electronics': {
            'high_rating': [
                "Absolutely love this {product}! The quality is outstanding and it works exactly as described.",
                "Best {category} purchase I've made in years. Highly recommend to anyone looking for quality.",
                "Perfect! Fast shipping, great packaging, and the {product} exceeded my expectations.",
                "Worth every penny. The {product} is exactly what I needed and works flawlessly.",
                "Amazing product! Great value for money and the quality is top-notch."
            ],
            'medium_rating': [
                "Good {product}, works as expected. Nothing extraordinary but gets the job done.",
                "Decent quality for the price. The {product} is okay but could be better.",
                "It's fine. Does what it's supposed to do but I've seen better in this price range.",
                "Average {product}. Not bad but not great either. Would consider other options next time.",
                "Works well enough. The {product} is functional but has some minor issues."
            ],
            'low_rating': [
                "Disappointed with this {product}. Quality is not what I expected for the price.",
                "Had issues with this {product} from day one. Customer service was not helpful.",
                "Poor quality. The {product} broke after just a few weeks of use.",
                "Not worth the money. The {product} doesn't work as advertised.",
                "Would not recommend. The {product} is cheaply made and doesn't last."
            ]
        },
        'Clothing': {
            'high_rating': [
                "Perfect fit and great quality! The {product} looks exactly like the picture.",
                "Love this {product}! Comfortable, stylish, and true to size.",
                "Excellent quality fabric and construction. Very happy with this purchase.",
                "Great {product}! Fits perfectly and the material is soft and comfortable.",
                "Beautiful {product}! The color and fit are perfect. Will definitely buy again."
            ],
            'medium_rating': [
                "Nice {product} but the sizing runs a bit small. Good quality overall.",
                "Decent {product}. The material is okay but not as soft as I expected.",
                "It's fine. The {product} fits okay but the color is slightly different than pictured.",
                "Good quality but the {product} is a bit overpriced for what you get.",
                "Average {product}. Nothing special but it serves its purpose."
            ],
            'low_rating': [
                "Poor quality. The {product} ripped after just one wash.",
                "Terrible fit. The {product} is way too small despite ordering the correct size.",
                "Cheap material. The {product} doesn't look anything like the picture.",
                "Waste of money. The {product} is poorly made and uncomfortable.",
                "Would not recommend. The {product} is overpriced for such poor quality."
            ]
        },
        'Beauty': {
            'high_rating': [
                "Amazing {product}! The quality is fantastic and it works exactly as described.",
                "Love this {product}! Great pigmentation and long-lasting wear.",
                "Perfect! The {product} exceeded my expectations and arrived quickly.",
                "Excellent {product}! Great value for money and the results are outstanding.",
                "Best {product} I've tried! Highly recommend to anyone looking for quality beauty products."
            ],
            'medium_rating': [
                "Good {product}. Works well but the packaging could be better.",
                "Decent quality. The {product} is okay but I've used better in this price range.",
                "It's fine. The {product} does what it's supposed to do but nothing special.",
                "Average {product}. Not bad but not great either. Would consider other options.",
                "Works okay. The {product} is functional but has some minor issues."
            ],
            'low_rating': [
                "Disappointed with this {product}. Quality is not what I expected.",
                "Poor quality. The {product} doesn't work as advertised and was a waste of money.",
                "Terrible {product}. The formula is bad and it doesn't last at all.",
                "Would not recommend. The {product} is cheaply made and doesn't deliver results.",
                "Waste of money. The {product} is overpriced for such poor quality."
            ]
        }
    }
    
    # Get appropriate template based on rating
    if rating >= 4.5:
        rating_key = 'high_rating'
    elif rating >= 3.0:
        rating_key = 'medium_rating'
    else:
        rating_key = 'low_rating'
    
    # Get category templates
    if category in review_templates:
        templates = review_templates[category][rating_key]
    else:
        templates = review_templates['Electronics'][rating_key]  # Default fallback
    
    # Select random template and format it
    template = random.choice(templates)
    review_text = template.format(
        product=product_name,
        category=category.lower(),
        subcategory=subcategory.lower()
    )
    
    return review_text

def generate_enhanced_products(num_products):
    """Generate ultra-realistic e-commerce products."""
    
    product_templates = generate_realistic_product_names()
    
    # Flatten all available products
    all_products = []
    for category, brands in product_templates.items():
        for brand, subcategories in brands.items():
            for subcategory, products in subcategories.items():
                for product in products:
                    all_products.append({
                        'category': category,
                        'brand': brand,
                        'subcategory': subcategory,
                        'name': product
                    })
    
    # Add more products from other categories
    additional_products = [
        # Home & Garden
        {'category': 'Home', 'brand': 'IKEA', 'subcategory': 'Furniture', 'name': 'HEMNES Dresser'},
        {'category': 'Home', 'brand': 'IKEA', 'subcategory': 'Furniture', 'name': 'BILLY Bookcase'},
        {'category': 'Home', 'brand': 'West Elm', 'subcategory': 'Decor', 'name': 'Marble Table Lamp'},
        {'category': 'Home', 'brand': 'Pottery Barn', 'subcategory': 'Bedding', 'name': 'Organic Cotton Sheet Set'},
        
        # Beauty & Personal Care
        {'category': 'Beauty', 'brand': 'L\'Oréal', 'subcategory': 'Makeup', 'name': 'True Match Foundation'},
        {'category': 'Beauty', 'brand': 'Maybelline', 'subcategory': 'Makeup', 'name': 'Great Lash Mascara'},
        {'category': 'Beauty', 'brand': 'CeraVe', 'subcategory': 'Skincare', 'name': 'Foaming Facial Cleanser'},
        {'category': 'Beauty', 'brand': 'The Ordinary', 'subcategory': 'Skincare', 'name': 'Niacinamide 10% + Zinc 1%'},
        
        # Sports & Outdoors
        {'category': 'Sports', 'brand': 'Patagonia', 'subcategory': 'Outdoor', 'name': 'Better Sweater Jacket'},
        {'category': 'Sports', 'brand': 'North Face', 'subcategory': 'Outdoor', 'name': 'Denali Fleece Jacket'},
        {'category': 'Sports', 'brand': 'Under Armour', 'subcategory': 'Fitness', 'name': 'Tech 2.0 T-Shirt'},
        
        # Toys & Games
        {'category': 'Toys', 'brand': 'LEGO', 'subcategory': 'Building Sets', 'name': 'Creator 3-in-1 Set'},
        {'category': 'Toys', 'brand': 'Mattel', 'subcategory': 'Dolls', 'name': 'Barbie Fashionista Doll'},
        {'category': 'Toys', 'brand': 'Hasbro', 'subcategory': 'Board Games', 'name': 'Monopoly Classic'},
    ]
    
    all_products.extend(additional_products)
    
    # Generate products
    products = []
    selected_products = random.sample(all_products, min(num_products, len(all_products)))
    
    for i, product_info in enumerate(selected_products):
        product_id = i + 1
        category = product_info['category']
        brand = product_info['brand']
        subcategory = product_info['subcategory']
        name = product_info['name']
        
        # Generate realistic pricing
        price = generate_realistic_pricing(category, subcategory, brand, name)
        
        # Generate stock quantity (realistic inventory levels)
        if price < 50:
            stock_quantity = random.randint(50, 500)
        elif price < 200:
            stock_quantity = random.randint(20, 200)
        else:
            stock_quantity = random.randint(5, 100)
        
        # Generate realistic rating (weighted toward higher ratings)
        rating_weights = [0.05, 0.10, 0.15, 0.25, 0.45]  # More 5-star ratings
        rating = random.choices([1, 2, 3, 4, 5], weights=rating_weights)[0]
        rating += random.uniform(0, 0.9)  # Add decimal for more realistic ratings
        rating = min(5.0, rating)
        
        # Generate product description
        description = generate_product_description(category, subcategory, name, brand)
        
        products.append({
            'product_id': product_id,
            'name': name,
            'brand': brand,
            'category': category,
            'subcategory': subcategory,
            'price': price,
            'stock_quantity': stock_quantity,
            'rating': round(rating, 1),
            'description': description
        })
    
    return pd.DataFrame(products)

def generate_product_description(category, subcategory, product_name, brand):
    """Generate realistic product descriptions."""
    
    descriptions = {
        'Electronics': f"High-quality {subcategory.lower()} from {brand}. {product_name} features premium materials and cutting-edge technology. Perfect for both personal and professional use.",
        'Clothing': f"Stylish and comfortable {subcategory.lower()} from {brand}. {product_name} is made with premium materials and designed for everyday wear. Available in multiple sizes and colors.",
        'Beauty': f"Professional-grade {subcategory.lower()} from {brand}. {product_name} delivers exceptional results with long-lasting wear. Perfect for creating your signature look.",
        'Home': f"Beautiful and functional {subcategory.lower()} from {brand}. {product_name} combines style and practicality to enhance your living space. Easy to assemble and maintain.",
        'Sports': f"High-performance {subcategory.lower()} from {brand}. {product_name} is designed for athletes and fitness enthusiasts. Durable construction and superior comfort.",
        'Toys': f"Fun and educational {subcategory.lower()} from {brand}. {product_name} encourages creativity and learning through play. Safe for children and built to last."
    }
    
    return descriptions.get(category, f"Quality {subcategory.lower()} from {brand}. {product_name} offers great value and performance.")

def generate_enhanced_users(num_users):
    """Generate realistic user profiles with proper demographics and behavior patterns."""
    
    users = []
    
    # Simulate a real e-commerce business with 100,000+ users
    # User IDs should be scattered across the entire range, not sequential 1-100
    total_user_base = 100000  # Simulate 100k+ user base
    
    # Generate realistic user IDs scattered across the range
    # Weight toward more recent users (higher IDs) but include some older users
    user_ids = []
    
    # 70% recent users (last 20,000 users)
    recent_users = random.sample(range(total_user_base - 20000, total_user_base + 1), 
                                min(int(num_users * 0.7), 20000))
    user_ids.extend(recent_users)
    
    # 20% middle-range users (users 20,000 - 80,000)
    middle_users = random.sample(range(20000, total_user_base - 20000), 
                                min(int(num_users * 0.2), 60000))
    user_ids.extend(middle_users)
    
    # 10% older users (first 20,000 users)
    older_users = random.sample(range(1, 20001), 
                               min(int(num_users * 0.1), 20000))
    user_ids.extend(older_users)
    
    # If we need more users, fill with random distribution
    while len(user_ids) < num_users:
        user_ids.append(random.randint(1, total_user_base))
    
    # Shuffle to randomize the order
    random.shuffle(user_ids)
    user_ids = user_ids[:num_users]  # Take exactly what we need
    
    # Realistic name patterns by region
    regions = ['US', 'CA', 'UK', 'AU', 'DE', 'FR', 'IT', 'ES', 'NL', 'SE']
    region_weights = [0.60, 0.08, 0.06, 0.04, 0.05, 0.04, 0.03, 0.03, 0.03, 0.04]
    
    for i in range(num_users):
        user_id = user_ids[i]
        
        # Select region
        region = random.choices(regions, weights=region_weights)[0]
        
        # Generate name based on region
        if region == 'US':
            first_name = fake.first_name()
            last_name = fake.last_name()
        elif region == 'CA':
            first_name = fake.first_name()
            last_name = fake.last_name()
        elif region == 'UK':
            first_name = fake.first_name()
            last_name = fake.last_name()
        else:
            first_name = fake.first_name()
            last_name = fake.last_name()
        
        name = f"{first_name} {last_name}"
        
        # Generate realistic email
        email_domains = ['gmail.com', 'yahoo.com', 'hotmail.com', 'outlook.com', 'icloud.com', 'aol.com']
        email_domain = random.choice(email_domains)
        
        # Create email variations
        email_variations = [
            f"{first_name.lower()}.{last_name.lower()}@{email_domain}",
            f"{first_name.lower()}{last_name.lower()}@{email_domain}",
            f"{first_name.lower()}{random.randint(1, 99)}@{email_domain}",
            f"{first_name.lower()}.{last_name.lower()}{random.randint(1, 99)}@{email_domain}"
        ]
        email = random.choice(email_variations)
        
        # Generate realistic phone number
        phone = fake.phone_number()
        
        # Generate realistic address
        address = fake.address().replace('\n', ', ')
        
        # Generate signup date (weighted toward recent dates)
        signup_date = fake.date_between(start_date='-2y', end_date='today')
        
        # Generate membership status based on realistic patterns
        membership_weights = [0.50, 0.30, 0.15, 0.05]  # Bronze, Silver, Gold, Platinum
        membership_status = random.choices(['Bronze', 'Silver', 'Gold', 'Platinum'], weights=membership_weights)[0]
        
        # Generate loyalty points based on membership
        if membership_status == 'Bronze':
            loyalty_points = random.randint(0, 5000)
        elif membership_status == 'Silver':
            loyalty_points = random.randint(5000, 15000)
        elif membership_status == 'Gold':
            loyalty_points = random.randint(15000, 30000)
        else:  # Platinum
            loyalty_points = random.randint(30000, 50000)
        
        users.append({
            'user_id': user_id,
            'name': name,
            'email': email,
            'phone': phone,
            'address': address,
            'signup_date': signup_date.strftime('%Y-%m-%d'),
            'membership_status': membership_status,
            'loyalty_points': loyalty_points
        })
    
    return pd.DataFrame(users)

def generate_enhanced_orders(num_orders, user_ids, products_df):
    """Generate realistic orders with proper business logic."""
    
    orders = []
    
    # Generate order dates with realistic patterns
    start_date = datetime.now() - timedelta(days=365)
    end_date = datetime.now()
    
    # Weight orders toward recent dates
    date_weights = np.linspace(0.1, 1.0, 365)
    
    # Simulate realistic user behavior - not all users from our sample will order
    # Some users might order multiple times, others might not order at all
    total_user_base = 100000
    
    for i in range(num_orders):
        order_id = i + 1
        
        # 80% chance to use a user from our sample, 20% chance to use any user from the base
        if random.random() < 0.8 and len(user_ids) > 0:
            user_id = random.choice(user_ids)
        else:
            # Use a random user from the entire user base (simulating other customers)
            user_id = random.randint(1, total_user_base)
        
        # Generate order date with realistic distribution
        days_ago = random.choices(range(365), weights=date_weights)[0]
        order_date = end_date - timedelta(days=days_ago)
        
        # Generate order status with realistic business logic
        days_since_order = (end_date - order_date).days
        
        if days_since_order < 1:
            status = random.choice(['pending', 'processing'])
        elif days_since_order < 3:
            status = random.choice(['processing', 'shipped'])
        elif days_since_order < 7:
            status = random.choice(['shipped', 'delivered'])
        else:
            status_weights = [0.85, 0.10, 0.05]  # delivered, returned, cancelled
            status = random.choices(['delivered', 'returned', 'cancelled'], weights=status_weights)[0]
        
        # Generate realistic order amount
        # Use log-normal distribution for realistic order values
        order_amount = np.random.lognormal(mean=3.5, sigma=1.0)
        order_amount = max(15.99, min(999.99, order_amount))
        
        # Apply realistic price endings
        price_endings = [0.99, 0.95, 0.00, 0.49, 0.79]
        ending = random.choice(price_endings)
        order_amount = int(order_amount) + ending
        
        orders.append({
            'order_id': order_id,
            'user_id': user_id,
            'order_date': order_date.strftime('%Y-%m-%d'),
            'status': status,
            'total_amount': round(order_amount, 2)
        })
    
    return pd.DataFrame(orders)

def generate_enhanced_order_items(orders_df, products_df, target_rows=100):
    """Generate realistic order items with exactly target_rows data rows."""
    
    order_items = []
    
    # Calculate how many orders we need to reach target_rows
    # Most orders have 1-3 items, so we need fewer orders
    orders_needed = max(1, target_rows // 2)  # Start with half the target
    
    # If we don't have enough orders, use all available orders
    if orders_needed > len(orders_df):
        orders_needed = len(orders_df)
    
    # Take only the first orders_needed orders
    orders_to_process = orders_df.head(orders_needed)
    
    for _, order in orders_to_process.iterrows():
        order_id = order['order_id']
        total_amount = order['total_amount']
        
        # Determine number of items (1-3 items per order for more realistic distribution)
        num_items = random.choices([1, 2, 3], weights=[0.50, 0.35, 0.15])[0]
        
        # Select products for this order
        selected_products = random.sample(products_df.to_dict('records'), num_items)
        
        for product in selected_products:
            # Generate realistic quantity (1-2 for most items)
            quantity = random.choices([1, 2], weights=[0.80, 0.20])[0]
            
            # Adjust quantity for low-priced items
            if product['price'] < 20:
                quantity = random.randint(1, 3)
            
            order_items.append({
                'order_id': order_id,
                'product_id': product['product_id'],
                'quantity': quantity
            })
            
            # Stop if we've reached our target
            if len(order_items) >= target_rows:
                break
        
        # Stop if we've reached our target
        if len(order_items) >= target_rows:
            break
    
    # If we still don't have enough items, add more single-item orders
    while len(order_items) < target_rows and len(orders_df) > len(orders_to_process):
        # Get next order
        next_order_idx = len(orders_to_process)
        if next_order_idx >= len(orders_df):
            break
            
        order = orders_df.iloc[next_order_idx]
        order_id = order['order_id']
        
        # Add single item
        product = random.choice(products_df.to_dict('records'))
        quantity = random.choices([1, 2], weights=[0.80, 0.20])[0]
        
        order_items.append({
            'order_id': order_id,
            'product_id': product['product_id'],
            'quantity': quantity
        })
        
        orders_to_process = orders_df.head(next_order_idx + 1)
    
    # Trim to exact target if we went over
    order_items = order_items[:target_rows]
    
    return pd.DataFrame(order_items)

def generate_enhanced_reviews(num_reviews, users_df, products_df):
    """Generate realistic product reviews."""
    
    reviews = []
    
    # Get user and product IDs
    user_ids = users_df['user_id'].tolist()
    product_ids = products_df['product_id'].tolist()
    
    for i in range(num_reviews):
        review_id = i + 1
        user_id = random.choice(user_ids)
        product_id = random.choice(product_ids)
        
        # Get product info
        product = products_df[products_df['product_id'] == product_id].iloc[0]
        
        # Generate realistic rating (weighted toward higher ratings)
        rating_weights = [0.05, 0.10, 0.15, 0.25, 0.45]
        rating = random.choices([1, 2, 3, 4, 5], weights=rating_weights)[0]
        rating += random.uniform(0, 0.9)
        rating = min(5.0, rating)
        
        # Generate realistic review text
        review_text = generate_realistic_review_text(
            rating, 
            product['category'], 
            product['subcategory'], 
            product['name'], 
            product['brand']
        )
        
        # Generate review date (within last year)
        review_date = fake.date_between(start_date='-1y', end_date='today')
        
        reviews.append({
            'review_id': review_id,
            'user_id': user_id,
            'product_id': product_id,
            'rating': round(rating, 1),
            'review_text': review_text,
            'review_date': review_date.strftime('%Y-%m-%d')
        })
    
    return pd.DataFrame(reviews)

def generate_realistic_dataset(num_users=100, num_products=50, num_orders=200, num_reviews=150, output_dir=None):
    """Generate a complete realistic e-commerce dataset."""
    
    # Make product count more realistic (not round numbers)
    if num_products == 100:
        # Generate realistic product count between 85-115
        num_products = random.randint(85, 115)
    elif num_products == 50:
        # Generate realistic product count between 45-65
        num_products = random.randint(45, 65)
    elif num_products == 200:
        # Generate realistic product count between 180-220
        num_products = random.randint(180, 220)
    
    print(f"Generating realistic e-commerce dataset...")
    print(f"Users: {num_users}, Products: {num_products}, Orders: {num_orders}, Reviews: {num_reviews}")
    
    # Create output directory
    if output_dir is None:
        size_category = get_size_category(num_users, num_products, num_orders, num_reviews)
        output_dir = create_timestamped_folder(size_category)
    
    os.makedirs(output_dir, exist_ok=True)
    
    # Generate datasets
    print("Generating users...")
    users_df = generate_enhanced_users(num_users)
    
    print("Generating products...")
    products_df = generate_enhanced_products(num_products)
    
    print("Generating orders...")
    user_ids = users_df['user_id'].tolist()
    orders_df = generate_enhanced_orders(num_orders, user_ids, products_df)
    
    print("Generating order items...")
    order_items_df = generate_enhanced_order_items(orders_df, products_df, target_rows=100)
    
    print("Generating reviews...")
    reviews_df = generate_enhanced_reviews(num_reviews, users_df, products_df)
    
    # Save datasets
    print("Saving datasets...")
    users_df.to_csv(os.path.join(output_dir, 'users.csv'), index=False)
    products_df.to_csv(os.path.join(output_dir, 'products.csv'), index=False)
    orders_df.to_csv(os.path.join(output_dir, 'orders.csv'), index=False)
    order_items_df.to_csv(os.path.join(output_dir, 'order_items.csv'), index=False)
    reviews_df.to_csv(os.path.join(output_dir, 'reviews.csv'), index=False)
    
    # Generate metadata
    metadata = f"""Dataset Generation Metadata
==========================
Generated: {datetime.now().strftime('%Y-%m-%dT%H:%M:%S')}
Size Category: {get_size_category(num_users, num_products, num_orders, num_reviews)}

Parameters:
  Users: {num_users}
  Products: {num_products}
  Orders: {num_orders}
  Reviews: {num_reviews}

File Sizes:
  users.csv: {os.path.getsize(os.path.join(output_dir, 'users.csv')):,} bytes
  products.csv: {os.path.getsize(os.path.join(output_dir, 'products.csv')):,} bytes
  orders.csv: {os.path.getsize(os.path.join(output_dir, 'orders.csv')):,} bytes
  order_items.csv: {os.path.getsize(os.path.join(output_dir, 'order_items.csv')):,} bytes
  reviews.csv: {os.path.getsize(os.path.join(output_dir, 'reviews.csv')):,} bytes

Features:
- Realistic product names with proper brands
- Category-appropriate pricing
- Human-like review text
- Realistic user demographics
- Business-logic order patterns
- Seasonal and behavioral variations
"""
    
    with open(os.path.join(output_dir, 'metadata.txt'), 'w') as f:
        f.write(metadata)
    
    print(f"Dataset generated successfully in: {output_dir}")
    return output_dir

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Generate realistic e-commerce datasets')
    parser.add_argument('--users', type=int, default=100, help='Number of users')
    parser.add_argument('--products', type=int, default=50, help='Number of products')
    parser.add_argument('--orders', type=int, default=200, help='Number of orders')
    parser.add_argument('--reviews', type=int, default=150, help='Number of reviews')
    parser.add_argument('--output', type=str, help='Output directory')
    
    args = parser.parse_args()
    
    generate_realistic_dataset(
        num_users=args.users,
        num_products=args.products,
        num_orders=args.orders,
        num_reviews=args.reviews,
        output_dir=args.output
    )
