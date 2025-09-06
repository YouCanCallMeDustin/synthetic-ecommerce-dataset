#!/usr/bin/env python3
"""
Simple Synthetic E-commerce Dataset Generator
"""

import pandas as pd
import numpy as np
from faker import Faker
import random
from datetime import datetime, timedelta
import os
import argparse

# Initialize Faker with seed for reproducible results
fake = Faker()
Faker.seed(42)
np.random.seed(42)
random.seed(42)

def generate_creative_email():
    """Generate creative email addresses with diverse patterns."""
    
    # Real email domains with realistic distribution
    domains = ['gmail.com', 'yahoo.com', 'hotmail.com', 'outlook.com', 'aol.com', 
               'icloud.com', 'protonmail.com', 'live.com', 'msn.com', 'comcast.net',
               'verizon.net', 'att.net', 'sbcglobal.net', 'bellsouth.net']
    
    # Creative patterns for more realistic email variety
    creative_patterns = [
        # Sports teams and interests
        lambda: f"{random.choice(['cowboys', 'patriots', 'lakers', 'warriors', 'yankees', 'dodgers', 'packers', 'steelers', 'bulls', 'heat', 'celtics', 'spurs', 'nets', 'knicks', 'clippers', 'suns', 'nuggets', 'jazz', 'blazers', 'thunder'])}fan{random.randint(1, 99)}",
        lambda: f"{random.choice(['football', 'basketball', 'baseball', 'soccer', 'hockey', 'tennis', 'golf', 'boxing', 'mma', 'racing', 'swimming', 'running', 'cycling', 'skating', 'skiing', 'surfing', 'climbing', 'yoga', 'fitness', 'gym'])}lover{random.randint(10, 99)}",
        lambda: f"{random.choice(['game', 'gamer', 'player', 'pro', 'master', 'king', 'queen', 'legend', 'hero', 'champ', 'boss', 'chief', 'captain', 'commander', 'leader', 'winner', 'champion', 'ace', 'star', 'superstar'])}{random.randint(1, 999)}",
        
        # Colors and descriptive words
        lambda: f"{random.choice(['red', 'blue', 'green', 'purple', 'orange', 'yellow', 'pink', 'black', 'white', 'silver', 'gold', 'bronze', 'copper', 'navy', 'maroon', 'teal', 'turquoise', 'crimson', 'emerald', 'sapphire'])}{random.randint(1, 999)}",
        lambda: f"{random.choice(['cool', 'hot', 'fire', 'ice', 'storm', 'thunder', 'lightning', 'shadow', 'moon', 'star', 'bright', 'dark', 'shiny', 'glowing', 'sparkling', 'dazzling', 'brilliant', 'radiant', 'luminous', 'vibrant'])}{random.randint(10, 99)}",
        
        # Hobbies and interests
        lambda: f"{random.choice(['music', 'artist', 'singer', 'dancer', 'writer', 'reader', 'bookworm', 'poet', 'actor', 'director', 'musician', 'composer', 'producer', 'performer', 'entertainer', 'creator', 'designer', 'painter', 'sculptor', 'photographer'])}{random.randint(1, 99)}",
        lambda: f"{random.choice(['tech', 'geek', 'nerd', 'hacker', 'coder', 'developer', 'engineer', 'scientist', 'inventor', 'creator', 'programmer', 'analyst', 'architect', 'consultant', 'specialist', 'expert', 'guru', 'master', 'wizard', 'genius'])}{random.randint(10, 99)}",
        lambda: f"{random.choice(['travel', 'adventure', 'explorer', 'wanderer', 'nomad', 'pilot', 'captain', 'sailor', 'driver', 'rider', 'backpacker', 'globetrotter', 'voyager', 'journeyer', 'wayfarer', 'roamer', 'rambler', 'hiker', 'trekker', 'mountaineer'])}{random.randint(1, 99)}",
        lambda: f"{random.choice(['cooking', 'baking', 'chef', 'foodie', 'gourmet', 'cuisine', 'recipe', 'kitchen', 'culinary', 'gastronomy', 'epicure', 'connoisseur', 'aficionado', 'enthusiast', 'lover', 'fan', 'addict', 'obsessed', 'passionate', 'devoted'])}{random.randint(1, 99)}",
        lambda: f"{random.choice(['fitness', 'gym', 'workout', 'training', 'exercise', 'bodybuilding', 'crossfit', 'yoga', 'pilates', 'meditation', 'wellness', 'health', 'strength', 'power', 'endurance', 'flexibility', 'balance', 'mindfulness', 'zen', 'peaceful'])}{random.randint(1, 99)}",
        
        # Animals and nature
        lambda: f"{random.choice(['cat', 'dog', 'tiger', 'lion', 'eagle', 'wolf', 'bear', 'fox', 'owl', 'dragon', 'phoenix', 'unicorn', 'pegasus', 'griffin', 'kraken', 'leviathan', 'serpent', 'falcon', 'hawk', 'raven'])}{random.randint(1, 999)}",
        lambda: f"{random.choice(['mountain', 'river', 'ocean', 'forest', 'desert', 'valley', 'canyon', 'peak', 'lake', 'island', 'volcano', 'glacier', 'waterfall', 'meadow', 'prairie', 'tundra', 'jungle', 'savanna', 'tundra', 'wetland'])}{random.randint(10, 99)}",
        lambda: f"{random.choice(['flower', 'rose', 'lily', 'tulip', 'daisy', 'sunflower', 'orchid', 'jasmine', 'lavender', 'violet', 'iris', 'peony', 'magnolia', 'cherry', 'blossom', 'petal', 'garden', 'botanical', 'floral', 'bloom'])}{random.randint(1, 99)}",
        
        # Food and drinks
        lambda: f"{random.choice(['pizza', 'burger', 'coffee', 'tea', 'beer', 'wine', 'chocolate', 'candy', 'sweet', 'spicy', 'pasta', 'sushi', 'taco', 'sandwich', 'salad', 'soup', 'steak', 'chicken', 'fish', 'vegetarian'])}{random.randint(1, 99)}",
        lambda: f"{random.choice(['espresso', 'latte', 'cappuccino', 'mocha', 'americano', 'macchiato', 'frappuccino', 'coldbrew', 'iced', 'hot', 'steaming', 'frothy', 'creamy', 'smooth', 'rich', 'bold', 'aromatic', 'fragrant', 'delicious', 'tasty'])}{random.randint(1, 99)}",
        
        # Gaming and entertainment
        lambda: f"{random.choice(['playstation', 'xbox', 'nintendo', 'steam', 'epic', 'blizzard', 'riot', 'valve', 'ubisoft', 'ea', 'activision', 'bethesda', 'cdprojekt', 'naughtydog', 'insomniac', 'guerrilla', 'suckerpunch', 'santa', 'monica', 'crystal'])}lover{random.randint(1, 99)}",
        lambda: f"{random.choice(['marvel', 'dc', 'disney', 'pixar', 'netflix', 'hulu', 'amazon', 'google', 'apple', 'microsoft', 'sony', 'warner', 'paramount', 'universal', 'fox', 'hbo', 'discovery', 'espn', 'cnn', 'bbc'])}fan{random.randint(10, 99)}",
        lambda: f"{random.choice(['rock', 'metal', 'pop', 'jazz', 'blues', 'country', 'rap', 'hiphop', 'electronic', 'classical', 'reggae', 'funk', 'soul', 'r&b', 'indie', 'alternative', 'punk', 'grunge', 'emo', 'folk'])}{random.randint(1, 99)}",
        lambda: f"{random.choice(['anime', 'manga', 'cosplay', 'otaku', 'weeb', 'kawaii', 'cute', 'moe', 'tsundere', 'yandere', 'dere', 'senpai', 'kohai', 'sempai', 'sensei', 'master', 'student', 'pupil', 'apprentice'])}{random.randint(1, 99)}",
        
        # Technology and digital
        lambda: f"{random.choice(['cyber', 'digital', 'virtual', 'online', 'internet', 'web', 'net', 'data', 'code', 'byte', 'bit', 'pixel', 'binary', 'algorithm', 'software', 'hardware', 'cloud', 'ai', 'ml', 'blockchain'])}{random.randint(10, 99)}",
        lambda: f"{random.choice(['crypto', 'bitcoin', 'ethereum', 'nft', 'defi', 'dao', 'web3', 'metaverse', 'vr', 'ar', 'xr', 'iot', '5g', 'wifi', 'bluetooth', 'nfc', 'rfid', 'gps', 'satellite', 'drone'])}{random.randint(1, 99)}",
        lambda: f"{random.choice(['startup', 'entrepreneur', 'founder', 'ceo', 'cto', 'cfo', 'coo', 'vp', 'director', 'manager', 'lead', 'senior', 'junior', 'intern', 'freelancer', 'consultant', 'contractor', 'employee', 'worker', 'staff'])}{random.randint(1, 99)}",
        
        # Abstract concepts and emotions
        lambda: f"{random.choice(['dream', 'hope', 'love', 'peace', 'joy', 'happy', 'smile', 'laugh', 'fun', 'magic', 'wonder', 'amazement', 'awe', 'inspiration', 'motivation', 'passion', 'enthusiasm', 'excitement', 'thrill', 'adventure'])}{random.randint(1, 999)}",
        lambda: f"{random.choice(['night', 'day', 'sun', 'moon', 'sky', 'cloud', 'rain', 'snow', 'wind', 'fire', 'earth', 'water', 'air', 'spirit', 'soul', 'heart', 'mind', 'body', 'energy', 'power'])}{random.randint(10, 99)}",
        
        # Space and science
        lambda: f"{random.choice(['nova', 'cosmos', 'galaxy', 'planet', 'comet', 'asteroid', 'meteor', 'satellite', 'orbit', 'space', 'universe', 'multiverse', 'dimension', 'quantum', 'relativity', 'gravity', 'electromagnetism', 'nuclear', 'atomic', 'molecular'])}{random.randint(10, 99)}",
        lambda: f"{random.choice(['alpha', 'beta', 'gamma', 'delta', 'omega', 'sigma', 'theta', 'phi', 'psi', 'lambda', 'epsilon', 'zeta', 'eta', 'iota', 'kappa', 'mu', 'nu', 'xi', 'omicron', 'pi'])}{random.randint(1, 99)}",
        
        # Gaming and competitive terms
        lambda: f"{random.choice(['noob', 'pro', 'elite', 'veteran', 'rookie', 'expert', 'genius', 'wizard', 'ninja', 'samurai', 'warrior', 'fighter', 'combatant', 'gladiator', 'champion', 'hero', 'legend', 'myth', 'icon', 'idol'])}{random.randint(1, 999)}",
        lambda: f"{random.choice(['guild', 'clan', 'team', 'squad', 'crew', 'gang', 'group', 'alliance', 'federation', 'empire', 'kingdom', 'realm', 'world', 'universe', 'dimension', 'reality', 'existence', 'being', 'entity', 'creature'])}{random.randint(1, 99)}",
        
        # Year-based and era patterns
        lambda: f"{random.choice(['retro', 'vintage', 'classic', 'modern', 'future', 'new', 'old', 'ancient', 'timeless', 'eternal', 'millennial', 'genz', 'genx', 'boomer', 'silent', 'greatest', 'lost', 'beat', 'hippie', 'punk'])}{random.randint(1980, 2025)}",
        lambda: f"{random.choice(['y2k', 'dotcom', 'web2', 'social', 'mobile', 'smart', 'digital', 'cyber', 'tech', 'ai', 'ml', 'blockchain', 'crypto', 'nft', 'metaverse', 'vr', 'ar', 'quantum', 'fusion', 'renewable'])}{random.randint(1, 99)}",
        
        # Random creative combinations
        lambda: f"{random.choice(['super', 'mega', 'ultra', 'hyper', 'turbo', 'max', 'extreme', 'ultimate', 'supreme', 'epic', 'legendary', 'mythical', 'divine', 'celestial', 'cosmic', 'universal', 'infinite', 'eternal', 'immortal', 'godlike'])}{random.choice(['man', 'woman', 'guy', 'girl', 'dude', 'bro', 'sis', 'kid', 'teen', 'adult', 'person', 'being', 'entity', 'creature', 'soul', 'spirit', 'heart', 'mind', 'body', 'self'])}{random.randint(1, 99)}"
    ]
    
    # Name-based patterns (for some variety)
    name_patterns = [
        lambda: f"{fake.first_name().lower()}.{fake.last_name().lower()}",
        lambda: f"{fake.first_name().lower()}_{fake.last_name().lower()}",
        lambda: f"{fake.first_name().lower()}{fake.last_name().lower()}",
        lambda: f"{fake.first_name().lower()}{random.randint(1, 999)}",
        lambda: f"{fake.first_name().lower()}{random.choice(['', '.', '_'])}{random.choice(['cool', 'awesome', 'pro', 'master'])}{random.randint(1, 99)}"
    ]
    
    # Choose between creative (75%) and name-based (25%) patterns
    if random.random() < 0.75:
        # Use creative patterns
        selected_pattern = random.choice(creative_patterns)
        email_prefix = selected_pattern()
    else:
        # Use name-based patterns
        selected_pattern = random.choice(name_patterns)
        email_prefix = selected_pattern()
    
    # Clean up the email prefix (remove any spaces, special chars)
    email_prefix = ''.join(c for c in email_prefix if c.isalnum() or c in '._-')
    
    # Select a random domain
    domain = random.choice(domains)
    
    return f"{email_prefix}@{domain}"

def generate_simple_dataset(num_users=1000, num_products=1000, num_orders=1000, num_reviews=1000, output_dir='dataset'):
    """Generate a simple synthetic e-commerce dataset."""
    
    print(f"Generating dataset with {num_users} users, {num_products} products, {num_orders} orders, {num_reviews} reviews")
    
    # Generate Users
    print("Generating users...")
    user_ids = np.arange(1, num_users + 1)
    df_users = pd.DataFrame({
        'user_id': user_ids,
        'name': [fake.name() for _ in range(num_users)],
        'email': [generate_creative_email() for _ in range(num_users)],
        'phone': [fake.phone_number() for _ in range(num_users)],
        'address': [fake.address().replace('\n', ', ') for _ in range(num_users)],
        'signup_date': pd.to_datetime([fake.date_between(start_date='-2y', end_date='today') for _ in range(num_users)]),
        'membership_status': np.random.choice(['Bronze', 'Silver', 'Gold', 'Platinum'], num_users, p=[0.5,0.3,0.15,0.05]),
        'loyalty_points': np.random.randint(0, 20000, num_users)
    })
    
    # Generate Products
    print("Generating products...")
    product_ids = np.arange(1, num_products + 1)
    categories = ['Electronics', 'Clothing', 'Beauty', 'Home', 'Sports', 'Toys']
    df_products = pd.DataFrame({
        'product_id': product_ids,
        'name': [f'{np.random.choice(categories)} Product {i}' for i in product_ids],
        'category': np.random.choice(categories, num_products),
        'price': np.round(np.random.uniform(5, 1000, num_products), 2),
        'stock_quantity': np.random.randint(0, 500, num_products),
        'rating': np.clip(np.round(np.random.normal(4, 0.8, num_products), 1), 1, 5)
    })
    
    # Generate Orders
    print("Generating orders...")
    order_ids = np.arange(1, num_orders + 1)
    order_user_ids = np.random.choice(user_ids, num_orders)
    df_orders = pd.DataFrame({
        'order_id': order_ids,
        'user_id': order_user_ids,
        'order_date': pd.to_datetime([fake.date_between(start_date='-1y', end_date='today') for _ in range(num_orders)]),
        'status': np.random.choice(['pending', 'shipped', 'delivered', 'returned'], num_orders, p=[0.05,0.15,0.75,0.05]),
        'total_amount': np.round(np.random.uniform(10, 500, num_orders), 2)
    })
    
    # Generate Order Items
    print("Generating order items...")
    order_items = []
    for order_id in order_ids:
        num_items = np.random.poisson(2) + 1  # 1-3 items per order
        items = np.random.choice(product_ids, min(num_items, len(product_ids)), replace=False)
        for product_id in items:
            order_items.append({
                'order_id': order_id,
                'product_id': product_id,
                'quantity': np.random.randint(1, 4)
            })
    df_order_items = pd.DataFrame(order_items)
    
    # Generate Reviews
    print("Generating reviews...")
    df_reviews = pd.DataFrame({
        'review_id': np.arange(1, num_reviews + 1),
        'user_id': np.random.choice(user_ids, num_reviews),
        'product_id': np.random.choice(product_ids, num_reviews),
        'rating': np.clip(np.round(np.random.normal(4, 0.8, num_reviews), 1), 1, 5),
        'review_text': [fake.sentence(nb_words=15) for _ in range(num_reviews)],
        'review_date': pd.to_datetime([fake.date_between(start_date='-1y', end_date='today') for _ in range(num_reviews)])
    })
    
    # Save datasets
    os.makedirs(output_dir, exist_ok=True)
    print(f"Saving datasets to {output_dir}/...")
    
    df_users.to_csv(f'{output_dir}/users.csv', index=False)
    df_products.to_csv(f'{output_dir}/products.csv', index=False)
    df_orders.to_csv(f'{output_dir}/orders.csv', index=False)
    df_order_items.to_csv(f'{output_dir}/order_items.csv', index=False)
    df_reviews.to_csv(f'{output_dir}/reviews.csv', index=False)
    
    print("✅ Dataset generation completed!")
    print(f"Files created in '{output_dir}/' directory:")
    print("  - users.csv")
    print("  - products.csv")
    print("  - orders.csv")
    print("  - order_items.csv")
    print("  - reviews.csv")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Generate synthetic e-commerce dataset')
    parser.add_argument('--users', type=int, default=1000, help='Number of users')
    parser.add_argument('--products', type=int, default=1000, help='Number of products')
    parser.add_argument('--orders', type=int, default=1000, help='Number of orders')
    parser.add_argument('--reviews', type=int, default=1000, help='Number of reviews')
    parser.add_argument('--output-dir', type=str, default='dataset', help='Output directory')
    
    args = parser.parse_args()
    
    generate_simple_dataset(
        num_users=args.users,
        num_products=args.products,
        num_orders=args.orders,
        num_reviews=args.reviews,
        output_dir=args.output_dir
    )
