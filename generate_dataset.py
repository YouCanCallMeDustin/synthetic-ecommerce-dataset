#!/usr/bin/env python3
"""
Synthetic E-commerce Dataset Generator

This script generates realistic synthetic e-commerce data including users, products, 
orders, order items, and reviews. The dataset is designed to simulate a real 
e-commerce platform with proper relationships between entities and realistic data distributions.

Usage:
    python generate_dataset.py [--users N] [--products N] [--orders N] [--reviews N] [--output-dir DIR]
"""

import pandas as pd
import numpy as np
from faker import Faker
import random
from datetime import datetime, timedelta
import os
import argparse
import json

# Initialize Faker with seed for reproducible results
fake = Faker()
Faker.seed(42)
np.random.seed(42)
random.seed(42)

def parse_arguments():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description='Generate synthetic e-commerce dataset')
    parser.add_argument('--users', type=int, default=10_000_000, 
                       help='Number of users to generate (default: 10,000,000)')
    parser.add_argument('--products', type=int, default=100_000, 
                       help='Number of products to generate (default: 100,000)')
    parser.add_argument('--orders', type=int, default=50_000_000, 
                       help='Number of orders to generate (default: 50,000,000)')
    parser.add_argument('--reviews', type=int, default=20_000_000, 
                       help='Number of reviews to generate (default: 20,000,000)')
    parser.add_argument('--output-dir', type=str, default='ultra_large', 
                       help='Output directory for generated files (default: ultra_large)')
    parser.add_argument('--format', choices=['csv', 'json', 'both'], default='csv',
                       help='Output format (default: csv)')
    return parser.parse_args()

def generate_users(num_users):
    """Generate users dataset."""
    print(f"Generating {num_users:,} users...")
    
    user_ids = np.arange(1, num_users + 1)
    names = [fake.name() for _ in range(num_users)]
    emails = [fake.email() for _ in range(num_users)]
    phones = [fake.phone_number() for _ in range(num_users)]
    addresses = [fake.address().replace("\n", ", ") for _ in range(num_users)]
    signup_dates = pd.to_datetime(np.random.choice(pd.date_range('-3y', 'today'), num_users))
    last_logins = pd.to_datetime([fake.date_between(start_date=date, end_date='today') for date in signup_dates])
    
    membership = np.random.choice(['Bronze', 'Silver', 'Gold', 'Platinum'], num_users, p=[0.5,0.3,0.15,0.05])
    loyalty_points = np.array([
        random.randint(0, 1000) if m == 'Bronze' else
        random.randint(500, 5000) if m == 'Silver' else
        random.randint(3000, 10000) if m == 'Gold' else
        random.randint(8000, 20000) for m in membership
    ])
    preferred_payment = np.random.choice(['Credit Card', 'PayPal', 'Apple Pay', 'Google Pay'], num_users)

    return pd.DataFrame({
        "user_id": user_ids,
        "name": names,
        "email": emails,
        "phone": phones,
        "address": addresses,
        "signup_date": signup_dates,
        "last_login": last_logins,
        "loyalty_points": loyalty_points,
        "membership_status": membership,
        "preferred_payment_method": preferred_payment
    })

def generate_products(num_products):
    """Generate products dataset."""
    print(f"Generating {num_products:,} products...")
    
    product_ids = np.arange(1, num_products + 1)
    categories = np.random.choice(['Electronics', 'Clothing', 'Beauty', 'Home', 'Sports', 'Toys'], num_products)
    prices = np.round(np.random.uniform(5, 1000, num_products), 2)
    costs = np.round(prices * np.random.uniform(0.4, 0.8, num_products), 2)
    stock_qty = np.random.randint(0, 500, num_products)
    ratings = np.clip(np.round(np.random.normal(4, 0.8, num_products), 1), 1, 5)
    discounts = np.random.choice([0,5,10,15,20], num_products)

    return pd.DataFrame({
        "product_id": product_ids,
        "name": [f"{cat} Product {i}" for i, cat in zip(product_ids, categories)],
        "category": categories,
        "price": prices,
        "cost": costs,
        "stock_quantity": stock_qty,
        "rating": ratings,
        "discount": discounts
    })

def generate_orders_and_items(num_orders, user_ids, product_ids, df_users, df_products):
    """Generate orders and order items datasets."""
    print(f"Generating {num_orders:,} orders...")
    
    order_ids = np.arange(1, num_orders + 1)
    order_user_ids = np.random.choice(user_ids, num_orders)
    order_dates = pd.to_datetime([fake.date_between(start_date=df_users.loc[df_users['user_id']==uid-1,'signup_date'].values[0], end_date='today') for uid in order_user_ids])
    order_status = np.random.choice(['pending', 'shipped', 'delivered', 'returned'], num_orders, p=[0.05,0.15,0.75,0.05])
    payment_methods = df_users.loc[order_user_ids-1, 'preferred_payment_method'].values
    shipping_addresses = df_users.loc[order_user_ids-1, 'address'].values

    # Generate order items in batches for memory efficiency
    print("Generating order items...")
    batch_size = 1_000_000
    order_items_list = []
    for start in range(0, num_orders, batch_size):
        end = min(start + batch_size, num_orders)
        batch_orders = order_ids[start:end]
        batch_items = []
        for oid in batch_orders:
            num_items = np.random.poisson(2) + 1
            items = np.random.choice(product_ids, num_items, replace=False)
            for pid in items:
                batch_items.append({"order_id": oid, "product_id": pid, "quantity": random.randint(1,3)})
        order_items_list.append(pd.DataFrame(batch_items))

    df_order_items = pd.concat(order_items_list, ignore_index=True)
    
    # Calculate total_amount per order
    df_orders_temp = df_order_items.merge(df_products[['product_id','price']], on='product_id', how='left')
    df_order_total = df_orders_temp.groupby('order_id')['price'].sum().reset_index().rename(columns={'price':'total_amount'})

    df_orders = pd.DataFrame({
        "order_id": order_ids,
        "user_id": order_user_ids,
        "order_date": order_dates,
        "status": order_status,
        "payment_method": payment_methods,
        "shipping_address": shipping_addresses
    }).merge(df_order_total, on='order_id')

    return df_orders, df_order_items

def generate_reviews(num_reviews, user_ids, product_ids):
    """Generate reviews dataset."""
    print(f"Generating {num_reviews:,} reviews...")
    
    review_user_ids = np.random.choice(user_ids, num_reviews)
    review_product_ids = np.random.choice(product_ids, num_reviews)
    review_ratings = np.clip(np.round(np.random.normal(4,0.8, num_reviews),1),1,5)
    review_dates = pd.to_datetime([fake.date_between(start_date='-1y', end_date='today') for _ in range(num_reviews)])
    review_texts = [fake.sentence(nb_words=15) for _ in range(num_reviews)]

    return pd.DataFrame({
        "review_id": np.arange(1, num_reviews+1),
        "user_id": review_user_ids,
        "product_id": review_product_ids,
        "rating": review_ratings,
        "review_text": review_texts,
        "review_date": review_dates
    })

def save_datasets(df_users, df_products, df_orders, df_order_items, df_reviews, output_dir, output_format):
    """Save datasets in specified format(s)."""
    os.makedirs(output_dir, exist_ok=True)
    
    datasets = {
        'users': df_users,
        'products': df_products,
        'orders': df_orders,
        'order_items': df_order_items,
        'reviews': df_reviews
    }
    
    print(f"Exporting datasets to {output_dir}/...")
    
    for name, df in datasets.items():
        if output_format in ['csv', 'both']:
            df.to_csv(f'{output_dir}/{name}.csv', index=False)
            print(f"  ✓ {name}.csv exported")
        
        if output_format in ['json', 'both']:
            df.to_json(f'{output_dir}/{name}.json', orient='records', indent=2)
            print(f"  ✓ {name}.json exported")

def main():
    """Main function to generate the synthetic e-commerce dataset."""
    args = parse_arguments()
    
    print("=" * 60)
    print("SYNTHETIC E-COMMERCE DATASET GENERATOR")
    print("=" * 60)
    print(f"Configuration:")
    print(f"  Users: {args.users:,}")
    print(f"  Products: {args.products:,}")
    print(f"  Orders: {args.orders:,}")
    print(f"  Reviews: {args.reviews:,}")
    print(f"  Output Directory: {args.output_dir}")
    print(f"  Output Format: {args.format}")
    print("=" * 60)
    
    # Generate datasets
    df_users = generate_users(args.users)
    df_products = generate_products(args.products)
    df_orders, df_order_items = generate_orders_and_items(
        args.orders, df_users['user_id'], df_products['product_id'], df_users, df_products
    )
    df_reviews = generate_reviews(args.reviews, df_users['user_id'], df_products['product_id'])
    
    # Save datasets
    save_datasets(df_users, df_products, df_orders, df_order_items, df_reviews, args.output_dir, args.format)
    
    print("=" * 60)
    print("DATASET GENERATION COMPLETED SUCCESSFULLY!")
    print("=" * 60)
    print(f"Generated files in '{args.output_dir}/' directory:")
    for filename in ['users', 'products', 'orders', 'order_items', 'reviews']:
        if args.format in ['csv', 'both']:
            print(f"  - {filename}.csv")
        if args.format in ['json', 'both']:
            print(f"  - {filename}.json")

if __name__ == "__main__":
    main()
