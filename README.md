# Synthetic E-commerce Dataset

A comprehensive synthetic e-commerce dataset generator for testing, analysis, and machine learning purposes.

## Overview

This project generates realistic synthetic e-commerce data including users, products, orders, order items, and reviews. The dataset is designed to simulate a real e-commerce platform with proper relationships between entities and realistic data distributions.

## Dataset Schema

### Users Table
- `user_id`: Unique user identifier
- `name`: Full name
- `email`: Email address
- `phone`: Phone number
- `address`: Full address
- `signup_date`: Account creation date
- `last_login`: Last login timestamp
- `loyalty_points`: Accumulated loyalty points
- `membership_status`: Bronze/Silver/Gold/Platinum
- `preferred_payment_method`: Payment preference

### Products Table
- `product_id`: Unique product identifier
- `name`: Product name
- `category`: Product category (Electronics, Clothing, Beauty, Home, Sports, Toys)
- `price`: Retail price
- `cost`: Cost price
- `stock_quantity`: Available inventory
- `rating`: Average product rating
- `discount`: Discount percentage

### Orders Table
- `order_id`: Unique order identifier
- `user_id`: Reference to user
- `order_date`: Order placement date
- `status`: Order status (pending, shipped, delivered, returned)
- `payment_method`: Payment method used
- `shipping_address`: Delivery address
- `total_amount`: Total order value

### Order Items Table
- `order_id`: Reference to order
- `product_id`: Reference to product
- `quantity`: Quantity ordered

### Reviews Table
- `review_id`: Unique review identifier
- `user_id`: Reference to user
- `product_id`: Reference to product
- `rating`: Review rating (1-5)
- `review_text`: Review content
- `review_date`: Review submission date

## Files

- `sample_dataset_1k.csv`: Sample dataset with 1,000 records per table
- `sample_dataset_1k.json`: Same sample data in JSON format
- `generate_dataset.py`: Script to generate custom-sized datasets

## Usage

### Using Sample Data
The sample files provide a small subset of the full dataset for quick testing and exploration.

### Generating Custom Datasets
Run the generator script to create datasets of any size:

```bash
python generate_dataset.py
```

The script supports various configuration options:
- Number of users (default: 10M)
- Number of products (default: 100K)
- Number of orders (default: 50M)
- Number of reviews (default: 20M)

## Data Characteristics

- **Realistic Distributions**: Uses statistical distributions to simulate real-world patterns
- **Proper Relationships**: Maintains referential integrity between tables
- **Temporal Consistency**: Ensures logical date relationships (signup before orders, etc.)
- **Scalable Generation**: Efficiently handles large datasets through batch processing

## Technical Details

- Built with Python using pandas, numpy, and faker libraries
- Uses seeded random generation for reproducible results
- Exports data in CSV format for compatibility with various tools
- Memory-efficient batch processing for large datasets

## Requirements

- Python 3.7+
- pandas
- numpy
- faker

## Installation

```bash
pip install pandas numpy faker
```

## License

This project is open source and available under the MIT License.
