#!/usr/bin/env python3
"""
Enhanced Synthetic E-commerce Dataset Generator
Creates organized folders by size and timestamp for each run
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

def calculate_customer_activity_weights(existing_users, orders_df=None):
    """Calculate weights for customer selection based on activity."""
    if orders_df is None:
        # Equal weights if no order history
        return np.ones(len(existing_users)) / len(existing_users)
    
    # Weight by number of orders (more active customers are more likely to order again)
    user_order_counts = orders_df['user_id'].value_counts()
    weights = np.array([user_order_counts.get(user_id, 1) for user_id in existing_users])
    return weights / weights.sum()

def generate_realistic_user_ids(num_orders, num_users, existing_orders=None):
    """Generate user IDs that reflect real customer behavior patterns."""
    user_ids = []
    
    # Simulate a larger user base (100,000+ users) for realistic e-commerce
    total_user_base = 100000
    
    # 20% new customers (from the generated users 1 to num_users)
    new_customers = min(int(num_orders * 0.2), num_users)
    if new_customers > 0:
        user_ids.extend(random.sample(range(1, num_users + 1), new_customers))
    
    # 60% repeat customers (from larger user base, weighted toward recent users)
    repeat_customers = int(num_orders * 0.6)
    
    # Weight toward more recent user IDs (simulating active customers)
    # Recent users (last 10,000) get higher probability
    recent_user_range = range(max(1, total_user_base - 10000), total_user_base + 1)
    recent_weights = np.ones(len(recent_user_range))
    recent_weights = recent_weights / recent_weights.sum()
    
    # Select from recent users with higher probability
    recent_selections = int(repeat_customers * 0.7)  # 70% from recent users
    recent_user_ids = np.random.choice(list(recent_user_range), recent_selections, p=recent_weights)
    user_ids.extend(recent_user_ids.tolist())
    
    # Remaining repeat customers from broader user base
    remaining_repeat = repeat_customers - recent_selections
    if remaining_repeat > 0:
        # Weight toward middle-range users (simulating established customers)
        middle_range = range(10000, total_user_base - 10000)
        middle_weights = np.ones(len(middle_range))
        middle_weights = middle_weights / middle_weights.sum()
        middle_user_ids = np.random.choice(list(middle_range), remaining_repeat, p=middle_weights)
        user_ids.extend(middle_user_ids.tolist())
    
    # 20% occasional customers (random from entire user base)
    occasional = num_orders - len(user_ids)
    if occasional > 0:
        # Uniform distribution across entire user base
        occasional_user_ids = random.sample(range(1, total_user_base + 1), occasional)
        user_ids.extend(occasional_user_ids)
    
    return user_ids

def generate_realistic_order_times(num_orders, start_date, end_date):
    """Generate order times that reflect real e-commerce patterns."""
    order_times = []
    
    for _ in range(num_orders):
        # Base date
        order_date = fake.date_between(start_date=start_date, end_date=end_date)
        
        # Add realistic time patterns
        hour_weights = [
            0.01, 0.01, 0.01, 0.01, 0.01, 0.01,  # 12am-6am: Very low
            0.02, 0.05, 0.08, 0.10, 0.12, 0.15,  # 6am-12pm: Morning rush
            0.18, 0.20, 0.22, 0.25, 0.28, 0.30,  # 12pm-6pm: Afternoon peak
            0.25, 0.20, 0.15, 0.10, 0.05, 0.02   # 6pm-12am: Evening decline
        ]
        
        # Normalize weights to sum to 1
        hour_weights = np.array(hour_weights)
        hour_weights = hour_weights / hour_weights.sum()
        
        hour = np.random.choice(24, p=hour_weights)
        minute = random.randint(0, 59)
        second = random.randint(0, 59)
        
        # Weekend vs weekday patterns
        if order_date.weekday() >= 5:  # Weekend
            # More evening orders on weekends
            if hour < 10:
                hour = random.randint(10, 23)
        
        # Convert date to datetime and add time
        order_datetime = datetime.combine(order_date, datetime.min.time().replace(hour=hour, minute=minute, second=second))
        order_times.append(order_datetime)
    
    return order_times

def determine_realistic_order_status(order_time, order_value, user_id):
    """Determine order status based on realistic business patterns."""
    
    days_since_order = (datetime.now() - order_time).days
    
    # New orders (last 24 hours)
    if days_since_order == 0:
        return 'pending' if random.random() < 0.3 else 'processing'
    
    # Recent orders (1-7 days)
    elif days_since_order <= 7:
        if days_since_order <= 2:
            return 'processing' if random.random() < 0.4 else 'shipped'
        else:
            return 'shipped' if random.random() < 0.7 else 'delivered'
    
    # Older orders (8+ days)
    else:
        # Most should be delivered, some returned
        if random.random() < 0.05:  # 5% return rate
            return 'returned'
        elif random.random() < 0.02:  # 2% still in transit
            return 'shipped'
        else:
            return 'delivered'

def determine_shipping_method(order_value, order_time):
    """Determine shipping method based on order value and timing."""
    if order_value > 200:
        methods = ['express', 'standard', 'overnight']
        weights = [0.4, 0.5, 0.1]
    elif order_value > 100:
        methods = ['standard', 'express', 'economy']
        weights = [0.6, 0.3, 0.1]
    else:
        methods = ['economy', 'standard']
        weights = [0.7, 0.3]
    
    return np.random.choice(methods, p=weights)

def generate_customer_notes():
    """Generate realistic customer notes."""
    notes = [
        "Please leave package at front door",
        "Ring doorbell twice",
        "Leave with neighbor if not home",
        "Gift - please wrap",
        "Call before delivery",
        "Leave in mailbox",
        "Deliver to back door",
        "Gift message: Happy Birthday!",
        "Fragile - handle with care",
        "Rush delivery needed"
    ]
    return random.choice(notes)

def determine_order_priority(order_value, user_id):
    """Determine order priority based on value and customer tier."""
    if order_value > 500:
        return 'high'
    elif order_value > 200:
        return 'medium'
    else:
        return 'standard'

def generate_realistic_email_enhanced(name, signup_date, customer_tier):
    """Generate realistic emails based on customer demographics and era."""
    
    # Real email domains with realistic distribution
    domains = {
        'gmail.com': 0.35,      # Most popular
        'yahoo.com': 0.15,      # Older demographic
        'hotmail.com': 0.10,    # Legacy
        'outlook.com': 0.12,    # Microsoft users
        'icloud.com': 0.08,     # Apple users
        'aol.com': 0.05,        # Older users
        'protonmail.com': 0.03, # Privacy-conscious
        'live.com': 0.04,       # Microsoft legacy
        'msn.com': 0.02,        # Very old
        'comcast.net': 0.02,    # ISP emails
        'verizon.net': 0.02,    # ISP emails
        'att.net': 0.01,        # ISP emails
        'sbcglobal.net': 0.01   # ISP emails
    }
    
    # Choose domain based on customer tier and signup era
    if customer_tier in ['Gold', 'Platinum']:
        # Premium customers more likely to use modern domains
        premium_domains = {'gmail.com': 0.4, 'icloud.com': 0.2, 'outlook.com': 0.2, 'protonmail.com': 0.1, 'yahoo.com': 0.1}
        domain = np.random.choice(list(premium_domains.keys()), p=list(premium_domains.values()))
    else:
        domain = np.random.choice(list(domains.keys()), p=list(domains.values()))
    
    # Generate email based on name and patterns
    name_parts = name.lower().split()
    first_name = name_parts[0] if name_parts else 'user'
    last_name = name_parts[-1] if len(name_parts) > 1 else ''
    
    # Creative patterns for more realistic email variety
    creative_patterns = [
        # Sports teams and interests (expanded)
        lambda: f"{random.choice(['cowboys', 'patriots', 'lakers', 'warriors', 'yankees', 'dodgers', 'packers', 'steelers', 'bulls', 'heat', 'celtics', 'spurs', 'nets', 'knicks', 'clippers', 'suns', 'nuggets', 'jazz', 'blazers', 'thunder'])}fan{random.randint(1, 99)}",
        lambda: f"{random.choice(['football', 'basketball', 'baseball', 'soccer', 'hockey', 'tennis', 'golf', 'boxing', 'mma', 'racing', 'swimming', 'running', 'cycling', 'skating', 'skiing', 'surfing', 'climbing', 'yoga', 'fitness', 'gym'])}lover{random.randint(10, 99)}",
        lambda: f"{random.choice(['game', 'gamer', 'player', 'pro', 'master', 'king', 'queen', 'legend', 'hero', 'champ', 'boss', 'chief', 'captain', 'commander', 'leader', 'winner', 'champion', 'ace', 'star', 'superstar'])}{random.randint(1, 999)}",
        lambda: f"{random.choice(['soccer', 'football', 'basketball', 'baseball', 'hockey', 'tennis', 'golf', 'boxing', 'mma', 'racing', 'swimming', 'running', 'cycling', 'skating', 'skiing', 'surfing', 'climbing', 'yoga', 'fitness', 'gym'])}pro{random.randint(1, 99)}",
        
        # Colors and descriptive words (expanded)
        lambda: f"{random.choice(['red', 'blue', 'green', 'purple', 'orange', 'yellow', 'pink', 'black', 'white', 'silver', 'gold', 'bronze', 'copper', 'navy', 'maroon', 'teal', 'turquoise', 'crimson', 'emerald', 'sapphire'])}{random.randint(1, 999)}",
        lambda: f"{random.choice(['cool', 'hot', 'fire', 'ice', 'storm', 'thunder', 'lightning', 'shadow', 'moon', 'star', 'bright', 'dark', 'shiny', 'glowing', 'sparkling', 'dazzling', 'brilliant', 'radiant', 'luminous', 'vibrant'])}{random.randint(10, 99)}",
        lambda: f"{random.choice(['neon', 'electric', 'plasma', 'crystal', 'diamond', 'pearl', 'ruby', 'emerald', 'sapphire', 'amethyst', 'topaz', 'jade', 'opal', 'garnet', 'citrine', 'peridot', 'aquamarine', 'tanzanite', 'tourmaline', 'zircon'])}{random.randint(1, 99)}",
        
        # Hobbies and interests (expanded)
        lambda: f"{random.choice(['music', 'artist', 'singer', 'dancer', 'writer', 'reader', 'bookworm', 'poet', 'actor', 'director', 'musician', 'composer', 'producer', 'performer', 'entertainer', 'creator', 'designer', 'painter', 'sculptor', 'photographer'])}{random.randint(1, 99)}",
        lambda: f"{random.choice(['tech', 'geek', 'nerd', 'hacker', 'coder', 'developer', 'engineer', 'scientist', 'inventor', 'creator', 'programmer', 'analyst', 'architect', 'consultant', 'specialist', 'expert', 'guru', 'master', 'wizard', 'genius'])}{random.randint(10, 99)}",
        lambda: f"{random.choice(['travel', 'adventure', 'explorer', 'wanderer', 'nomad', 'pilot', 'captain', 'sailor', 'driver', 'rider', 'backpacker', 'globetrotter', 'voyager', 'journeyer', 'wayfarer', 'roamer', 'rambler', 'hiker', 'trekker', 'mountaineer'])}{random.randint(1, 99)}",
        lambda: f"{random.choice(['cooking', 'baking', 'chef', 'foodie', 'gourmet', 'cuisine', 'recipe', 'kitchen', 'culinary', 'gastronomy', 'epicure', 'connoisseur', 'aficionado', 'enthusiast', 'lover', 'fan', 'addict', 'obsessed', 'passionate', 'devoted'])}{random.randint(1, 99)}",
        lambda: f"{random.choice(['fitness', 'gym', 'workout', 'training', 'exercise', 'bodybuilding', 'crossfit', 'yoga', 'pilates', 'meditation', 'wellness', 'health', 'strength', 'power', 'endurance', 'flexibility', 'balance', 'mindfulness', 'zen', 'peaceful'])}{random.randint(1, 99)}",
        
        # Animals and nature (expanded)
        lambda: f"{random.choice(['cat', 'dog', 'tiger', 'lion', 'eagle', 'wolf', 'bear', 'fox', 'owl', 'dragon', 'phoenix', 'unicorn', 'pegasus', 'griffin', 'kraken', 'leviathan', 'serpent', 'falcon', 'hawk', 'raven'])}{random.randint(1, 999)}",
        lambda: f"{random.choice(['mountain', 'river', 'ocean', 'forest', 'desert', 'valley', 'canyon', 'peak', 'lake', 'island', 'volcano', 'glacier', 'waterfall', 'meadow', 'prairie', 'tundra', 'jungle', 'savanna', 'tundra', 'wetland'])}{random.randint(10, 99)}",
        lambda: f"{random.choice(['flower', 'rose', 'lily', 'tulip', 'daisy', 'sunflower', 'orchid', 'jasmine', 'lavender', 'violet', 'iris', 'peony', 'magnolia', 'cherry', 'blossom', 'petal', 'garden', 'botanical', 'floral', 'bloom'])}{random.randint(1, 99)}",
        
        # Food and drinks (expanded)
        lambda: f"{random.choice(['pizza', 'burger', 'coffee', 'tea', 'beer', 'wine', 'chocolate', 'candy', 'sweet', 'spicy', 'pasta', 'sushi', 'taco', 'sandwich', 'salad', 'soup', 'steak', 'chicken', 'fish', 'vegetarian'])}{random.randint(1, 99)}",
        lambda: f"{random.choice(['espresso', 'latte', 'cappuccino', 'mocha', 'americano', 'macchiato', 'frappuccino', 'coldbrew', 'iced', 'hot', 'steaming', 'frothy', 'creamy', 'smooth', 'rich', 'bold', 'aromatic', 'fragrant', 'delicious', 'tasty'])}{random.randint(1, 99)}",
        lambda: f"{random.choice(['cocktail', 'martini', 'whiskey', 'vodka', 'rum', 'gin', 'tequila', 'bourbon', 'scotch', 'brandy', 'champagne', 'prosecco', 'sangria', 'margarita', 'mojito', 'cosmopolitan', 'manhattan', 'oldfashioned', 'negroni', 'daiquiri'])}{random.randint(1, 99)}",
        
        # Gaming and entertainment (expanded)
        lambda: f"{random.choice(['playstation', 'xbox', 'nintendo', 'steam', 'epic', 'blizzard', 'riot', 'valve', 'ubisoft', 'ea', 'activision', 'bethesda', 'cdprojekt', 'naughtydog', 'insomniac', 'guerrilla', 'suckerpunch', 'santa', 'monica', 'crystal'])}lover{random.randint(1, 99)}",
        lambda: f"{random.choice(['marvel', 'dc', 'disney', 'pixar', 'netflix', 'hulu', 'amazon', 'google', 'apple', 'microsoft', 'sony', 'warner', 'paramount', 'universal', 'fox', 'hbo', 'discovery', 'espn', 'cnn', 'bbc'])}fan{random.randint(10, 99)}",
        lambda: f"{random.choice(['rock', 'metal', 'pop', 'jazz', 'blues', 'country', 'rap', 'hiphop', 'electronic', 'classical', 'reggae', 'funk', 'soul', 'r&b', 'indie', 'alternative', 'punk', 'grunge', 'emo', 'folk'])}{random.randint(1, 99)}",
        lambda: f"{random.choice(['anime', 'manga', 'cosplay', 'otaku', 'weeb', 'kawaii', 'kawaii', 'cute', 'moe', 'tsundere', 'yandere', 'dere', 'senpai', 'kohai', 'sempai', 'sensei', 'master', 'student', 'pupil', 'apprentice'])}{random.randint(1, 99)}",
        
        # Technology and digital (expanded)
        lambda: f"{random.choice(['cyber', 'digital', 'virtual', 'online', 'internet', 'web', 'net', 'data', 'code', 'byte', 'bit', 'pixel', 'binary', 'algorithm', 'software', 'hardware', 'cloud', 'ai', 'ml', 'blockchain'])}{random.randint(10, 99)}",
        lambda: f"{random.choice(['crypto', 'bitcoin', 'ethereum', 'nft', 'defi', 'dao', 'web3', 'metaverse', 'vr', 'ar', 'xr', 'iot', '5g', 'wifi', 'bluetooth', 'nfc', 'rfid', 'gps', 'satellite', 'drone'])}{random.randint(1, 99)}",
        lambda: f"{random.choice(['startup', 'entrepreneur', 'founder', 'ceo', 'cto', 'cfo', 'coo', 'vp', 'director', 'manager', 'lead', 'senior', 'junior', 'intern', 'freelancer', 'consultant', 'contractor', 'employee', 'worker', 'staff'])}{random.randint(1, 99)}",
        
        # Abstract concepts and emotions (expanded)
        lambda: f"{random.choice(['dream', 'hope', 'love', 'peace', 'joy', 'happy', 'smile', 'laugh', 'fun', 'magic', 'wonder', 'amazement', 'awe', 'inspiration', 'motivation', 'passion', 'enthusiasm', 'excitement', 'thrill', 'adventure'])}{random.randint(1, 999)}",
        lambda: f"{random.choice(['night', 'day', 'sun', 'moon', 'sky', 'cloud', 'rain', 'snow', 'wind', 'fire', 'earth', 'water', 'air', 'spirit', 'soul', 'heart', 'mind', 'body', 'energy', 'power'])}{random.randint(10, 99)}",
        lambda: f"{random.choice(['freedom', 'liberty', 'justice', 'truth', 'honor', 'courage', 'bravery', 'strength', 'wisdom', 'knowledge', 'learning', 'growth', 'progress', 'success', 'achievement', 'victory', 'triumph', 'conquest', 'domination', 'supremacy'])}{random.randint(1, 99)}",
        
        # Space and science (expanded)
        lambda: f"{random.choice(['nova', 'cosmos', 'galaxy', 'planet', 'comet', 'asteroid', 'meteor', 'satellite', 'orbit', 'space', 'universe', 'multiverse', 'dimension', 'quantum', 'relativity', 'gravity', 'electromagnetism', 'nuclear', 'atomic', 'molecular'])}{random.randint(10, 99)}",
        lambda: f"{random.choice(['alpha', 'beta', 'gamma', 'delta', 'omega', 'sigma', 'theta', 'phi', 'psi', 'lambda', 'epsilon', 'zeta', 'eta', 'iota', 'kappa', 'mu', 'nu', 'xi', 'omicron', 'pi'])}{random.randint(1, 99)}",
        lambda: f"{random.choice(['astronaut', 'cosmonaut', 'pilot', 'navigator', 'explorer', 'discoverer', 'researcher', 'scientist', 'physicist', 'astronomer', 'cosmologist', 'theorist', 'experimenter', 'observer', 'analyst', 'investigator', 'detective', 'sleuth', 'sherlock', 'holmes'])}{random.randint(1, 99)}",
        
        # Gaming and competitive terms (expanded)
        lambda: f"{random.choice(['noob', 'pro', 'elite', 'veteran', 'rookie', 'expert', 'genius', 'wizard', 'ninja', 'samurai', 'warrior', 'fighter', 'combatant', 'gladiator', 'champion', 'hero', 'legend', 'myth', 'icon', 'idol'])}{random.randint(1, 999)}",
        lambda: f"{random.choice(['guild', 'clan', 'team', 'squad', 'crew', 'gang', 'group', 'alliance', 'federation', 'empire', 'kingdom', 'realm', 'world', 'universe', 'dimension', 'reality', 'existence', 'being', 'entity', 'creature'])}{random.randint(1, 99)}",
        lambda: f"{random.choice(['quest', 'mission', 'adventure', 'journey', 'expedition', 'exploration', 'discovery', 'conquest', 'victory', 'triumph', 'success', 'achievement', 'accomplishment', 'milestone', 'breakthrough', 'innovation', 'revolution', 'evolution', 'transformation', 'metamorphosis'])}{random.randint(1, 99)}",
        
        # Year-based and era patterns (expanded)
        lambda: f"{random.choice(['retro', 'vintage', 'classic', 'modern', 'future', 'new', 'old', 'ancient', 'timeless', 'eternal', 'millennial', 'genz', 'genx', 'boomer', 'silent', 'greatest', 'lost', 'beat', 'hippie', 'punk'])}{random.randint(1980, 2025)}",
        lambda: f"{random.choice(['y2k', 'dotcom', 'web2', 'social', 'mobile', 'smart', 'digital', 'cyber', 'tech', 'ai', 'ml', 'blockchain', 'crypto', 'nft', 'metaverse', 'vr', 'ar', 'quantum', 'fusion', 'renewable'])}{random.randint(1, 99)}",
        
        # Random creative combinations (expanded)
        lambda: f"{random.choice(['super', 'mega', 'ultra', 'hyper', 'turbo', 'max', 'extreme', 'ultimate', 'supreme', 'epic', 'legendary', 'mythical', 'divine', 'celestial', 'cosmic', 'universal', 'infinite', 'eternal', 'immortal', 'godlike'])}{random.choice(['man', 'woman', 'guy', 'girl', 'dude', 'bro', 'sis', 'kid', 'teen', 'adult', 'person', 'being', 'entity', 'creature', 'soul', 'spirit', 'heart', 'mind', 'body', 'self'])}{random.randint(1, 99)}",
        lambda: f"{random.choice(['mystic', 'magic', 'enchanted', 'spellbound', 'bewitched', 'charmed', 'blessed', 'cursed', 'hexed', 'jinxed', 'lucky', 'unlucky', 'fortunate', 'unfortunate', 'blessed', 'cursed', 'sacred', 'profane', 'holy', 'unholy'])}{random.choice(['warrior', 'mage', 'rogue', 'paladin', 'priest', 'monk', 'druid', 'shaman', 'warlock', 'sorcerer', 'wizard', 'necromancer', 'enchanter', 'illusionist', 'conjurer', 'summoner', 'elementalist', 'pyromancer', 'cryomancer', 'electromancer'])}{random.randint(1, 99)}",
        lambda: f"{random.choice(['shadow', 'light', 'dark', 'bright', 'dim', 'glowing', 'shining', 'radiant', 'luminous', 'brilliant', 'dazzling', 'sparkling', 'twinkling', 'flickering', 'flashing', 'blinking', 'pulsing', 'throbbing', 'beating', 'rhythmic'])}{random.choice(['blade', 'sword', 'dagger', 'axe', 'hammer', 'mace', 'staff', 'wand', 'orb', 'crystal', 'gem', 'stone', 'rock', 'metal', 'steel', 'iron', 'gold', 'silver', 'bronze', 'copper'])}{random.randint(1, 99)}"
    ]
    
    # Name-based patterns
    name_patterns = [
        lambda: f"{first_name}.{last_name}",
        lambda: f"{first_name}_{last_name}",
        lambda: f"{first_name}{last_name}",
        lambda: f"{first_name[0]}{last_name}",
        lambda: f"{first_name}{last_name[0] if last_name else ''}",
        lambda: f"{first_name}{random.randint(1, 999)}",
        lambda: f"{first_name}{random.choice(['', '.', '_'])}{random.choice(['cool', 'awesome', 'pro', 'master'])}{random.randint(1, 99)}",
        lambda: f"{random.choice(['the', 'real', 'official'])}{first_name}{last_name}",
        lambda: f"{first_name}.{last_name}.{random.randint(10, 99)}"
    ]
    
    # Email patterns based on signup era and customer tier
    year = signup_date.year
    
    # Adjust creative vs name-based ratio based on era and customer tier
    if year < 2020:
        # Older users: 50% creative, 50% name-based (increased from 30%)
        creative_ratio = 0.5
    elif customer_tier in ['Gold', 'Platinum']:
        # Premium customers: 85% creative, 15% name-based (increased from 70%)
        creative_ratio = 0.85
    else:
        # Modern regular users: 75% creative, 25% name-based (increased from 60%)
        creative_ratio = 0.75
    
    # Choose between creative and name-based patterns
    if random.random() < creative_ratio:
        # Use creative patterns
        selected_pattern = random.choice(creative_patterns)
        username = selected_pattern()
    else:
        # Use name-based patterns
        selected_pattern = random.choice(name_patterns)
        username = selected_pattern()
    
    # Clean up the username (remove any spaces, special chars)
    username = ''.join(c for c in username if c.isalnum() or c in '._-')
    
    return f"{username}@{domain}"

def determine_lifecycle_stage(days_since_signup, loyalty_points):
    """Determine customer lifecycle stage based on tenure and engagement."""
    if days_since_signup < 30:
        return 'new'
    elif days_since_signup < 90:
        return 'developing'
    elif days_since_signup < 365:
        if loyalty_points > 5000:
            return 'loyal'
        else:
            return 'at_risk'
    else:
        if loyalty_points > 10000:
            return 'champion'
        elif loyalty_points > 3000:
            return 'loyal'
        else:
            return 'at_risk'

def generate_realistic_customer_segments(num_users):
    """Generate realistic customer segments based on business patterns."""
    
    segments = []
    
    for i in range(num_users):
        # Customer lifecycle stage
        signup_date = fake.date_between(start_date='-3y', end_date='today')
        days_since_signup = (datetime.now().date() - signup_date).days
        
        # Determine customer tier based on realistic patterns
        if days_since_signup < 30:
            # New customers - mostly Bronze
            tier_weights = {'Bronze': 0.8, 'Silver': 0.15, 'Gold': 0.05, 'Platinum': 0.0}
        elif days_since_signup < 180:
            # 6-month customers
            tier_weights = {'Bronze': 0.6, 'Silver': 0.25, 'Gold': 0.12, 'Platinum': 0.03}
        elif days_since_signup < 365:
            # 1-year customers
            tier_weights = {'Bronze': 0.4, 'Silver': 0.35, 'Gold': 0.20, 'Platinum': 0.05}
        else:
            # Long-term customers
            tier_weights = {'Bronze': 0.2, 'Silver': 0.30, 'Gold': 0.35, 'Platinum': 0.15}
        
        membership_status = np.random.choice(list(tier_weights.keys()), p=list(tier_weights.values()))
        
        # Generate loyalty points based on tier and tenure
        base_points = {
            'Bronze': random.randint(0, 2000),
            'Silver': random.randint(1000, 8000),
            'Gold': random.randint(5000, 15000),
            'Platinum': random.randint(10000, 25000)
        }
        
        # Add tenure bonus
        tenure_bonus = min(days_since_signup * 2, 5000)
        loyalty_points = base_points[membership_status] + tenure_bonus
        
        segments.append({
            'membership_status': membership_status,
            'loyalty_points': loyalty_points,
            'signup_date': signup_date,
            'customer_lifecycle': determine_lifecycle_stage(days_since_signup, loyalty_points)
        })
    
    return segments

def generate_realistic_demographics(num_users):
    """Generate realistic demographic and geographic data."""
    
    demographics = []
    
    # US state distribution (realistic population-based)
    state_weights = {
        'CA': 0.12, 'TX': 0.09, 'FL': 0.07, 'NY': 0.06, 'PA': 0.04,
        'IL': 0.04, 'OH': 0.04, 'GA': 0.03, 'NC': 0.03, 'MI': 0.03,
        'NJ': 0.03, 'VA': 0.03, 'WA': 0.03, 'AZ': 0.02, 'MA': 0.02,
        'TN': 0.02, 'IN': 0.02, 'MO': 0.02, 'MD': 0.02, 'WI': 0.02,
        'CO': 0.02, 'MN': 0.02, 'SC': 0.02, 'AL': 0.02, 'LA': 0.02,
        'KY': 0.01, 'OR': 0.01, 'OK': 0.01, 'CT': 0.01, 'UT': 0.01,
        'IA': 0.01, 'NV': 0.01, 'AR': 0.01, 'MS': 0.01, 'KS': 0.01,
        'NM': 0.01, 'NE': 0.01, 'WV': 0.01, 'ID': 0.01, 'HI': 0.01,
        'NH': 0.01, 'ME': 0.01, 'RI': 0.01, 'MT': 0.01, 'DE': 0.01,
        'SD': 0.01, 'ND': 0.01, 'AK': 0.01, 'VT': 0.01, 'WY': 0.01
    }
    
    # Normalize weights to sum to 1
    total_weight = sum(state_weights.values())
    state_weights = {k: v/total_weight for k, v in state_weights.items()}
    
    for _ in range(num_users):
        # Geographic data
        state = np.random.choice(list(state_weights.keys()), p=list(state_weights.values()))
        city = fake.city()
        
        # Timezone based on state
        timezone_map = {
            'CA': 'PST', 'NV': 'PST', 'WA': 'PST', 'OR': 'PST',
            'TX': 'CST', 'IL': 'CST', 'MO': 'CST', 'AR': 'CST',
            'NY': 'EST', 'FL': 'EST', 'PA': 'EST', 'OH': 'EST',
            'CO': 'MST', 'AZ': 'MST', 'UT': 'MST', 'NM': 'MST'
        }
        timezone = timezone_map.get(state, 'EST')
        
        # Age distribution (realistic e-commerce demographics)
        age_weights = {
            '18-24': 0.15, '25-34': 0.25, '35-44': 0.20, '45-54': 0.18,
            '55-64': 0.12, '65+': 0.10
        }
        age_group = np.random.choice(list(age_weights.keys()), p=list(age_weights.values()))
        
        # Gender distribution
        gender = np.random.choice(['M', 'F', 'Other'], p=[0.48, 0.50, 0.02])
        
        # Income level (affects purchasing behavior)
        income_levels = {
            'Low': 0.20, 'Lower-Middle': 0.30, 'Middle': 0.30, 
            'Upper-Middle': 0.15, 'High': 0.05
        }
        income_level = np.random.choice(list(income_levels.keys()), p=list(income_levels.values()))
        
        demographics.append({
            'state': state,
            'city': city,
            'timezone': timezone,
            'age_group': age_group,
            'gender': gender,
            'income_level': income_level
        })
    
    return demographics

def generate_customer_preferences():
    """Generate realistic customer preferences."""
    categories = ['Electronics', 'Clothing', 'Beauty', 'Home', 'Sports', 'Toys', 'Books', 'Health']
    preferred_categories = random.sample(categories, random.randint(2, 5))
    
    return {
        'preferred_categories': preferred_categories,
        'price_sensitivity': random.choice(['low', 'medium', 'high']),
        'brand_loyalty': random.choice(['low', 'medium', 'high']),
        'shopping_frequency': random.choice(['occasional', 'regular', 'frequent']),
        'preferred_payment': random.choice(['credit_card', 'paypal', 'apple_pay', 'debit_card'])
    }

def generate_customer_acquisition_data(num_users, signup_dates):
    """Generate realistic customer acquisition and behavior data."""
    
    acquisition_data = []
    
    for i, signup_date in enumerate(signup_dates):
        # Acquisition channels (realistic distribution)
        channels = {
            'organic_search': 0.35,    # SEO
            'paid_search': 0.20,       # Google Ads
            'social_media': 0.15,      # Facebook, Instagram, etc.
            'email_marketing': 0.10,   # Email campaigns
            'referral': 0.08,          # Word of mouth
            'direct': 0.07,            # Direct traffic
            'affiliate': 0.03,         # Affiliate marketing
            'influencer': 0.02         # Influencer marketing
        }
        
        acquisition_channel = np.random.choice(list(channels.keys()), p=list(channels.values()))
        
        # Referral source (if applicable)
        referral_source = None
        if acquisition_channel == 'referral':
            referral_sources = ['friend', 'family', 'colleague', 'social_media_post', 'review_site']
            referral_source = random.choice(referral_sources)
        
        # Customer preferences (affects product recommendations)
        preferences = generate_customer_preferences()
        
        # Engagement level
        engagement_levels = ['low', 'medium', 'high', 'very_high']
        engagement_weights = [0.30, 0.40, 0.25, 0.05]
        engagement_level = np.random.choice(engagement_levels, p=engagement_weights)
        
        # Communication preferences
        comm_preferences = {
            'email': random.choice([True, False]),
            'sms': random.choice([True, False]),
            'push_notifications': random.choice([True, False]),
            'phone_calls': random.choice([True, False])
        }
        
        acquisition_data.append({
            'acquisition_channel': acquisition_channel,
            'referral_source': referral_source,
            'preferences': preferences,
            'engagement_level': engagement_level,
            'communication_preferences': comm_preferences,
            'is_newsletter_subscriber': random.random() < 0.6,
            'is_sms_subscriber': random.random() < 0.3,
            'last_login_date': fake.date_between(start_date=signup_date, end_date='today'),
            'total_logins': random.randint(1, 100)
        })
    
    return acquisition_data

def generate_realistic_phone(state):
    """Generate realistic phone number based on state."""
    # Simplified area code mapping (in reality, this would be more complex)
    area_codes = {
        'CA': ['213', '310', '323', '408', '415', '510', '562', '619', '626', '650', '661', '707', '714', '760', '805', '818', '831', '858', '909', '916', '925', '949', '951'],
        'TX': ['214', '254', '281', '325', '361', '409', '430', '432', '469', '512', '713', '726', '737', '806', '817', '830', '832', '903', '915', '936', '940', '956', '972', '979'],
        'NY': ['212', '315', '347', '516', '518', '585', '607', '631', '646', '680', '716', '718', '845', '914', '917', '929', '934'],
        'FL': ['239', '305', '321', '352', '386', '407', '561', '727', '754', '772', '786', '813', '850', '863', '904', '941', '954']
    }
    
    if state in area_codes:
        area_code = random.choice(area_codes[state])
    else:
        area_code = f"{random.randint(200, 999)}"
    
    # Generate remaining digits
    exchange = f"{random.randint(200, 999)}"
    number = f"{random.randint(1000, 9999)}"
    
    return f"({area_code}) {exchange}-{number}"

def generate_realistic_address(state, city):
    """Generate realistic address based on state and city."""
    street_number = random.randint(1, 9999)
    street_names = ['Main St', 'Oak Ave', 'First St', 'Second St', 'Park Ave', 'Washington St', 'Lincoln Ave', 'Broadway', 'Cedar St', 'Elm St']
    street_name = random.choice(street_names)
    
    # Add apartment/suite info (30% chance)
    apt_info = ""
    if random.random() < 0.3:
        apt_types = ['Apt', 'Suite', 'Unit', 'Ste']
        apt_number = random.randint(1, 999)
        apt_info = f" {random.choice(apt_types)} {apt_number}"
    
    return f"{street_number} {street_name}{apt_info}, {city}, {state} {random.randint(10000, 99999)}"

def estimate_customer_lifetime_value(segment, demographics, acquisition_data):
    """Estimate customer lifetime value based on multiple factors."""
    base_clv = {
        'Bronze': random.uniform(50, 200),
        'Silver': random.uniform(200, 500),
        'Gold': random.uniform(500, 1000),
        'Platinum': random.uniform(1000, 2500)
    }
    
    clv = base_clv[segment['membership_status']]
    
    # Adjust based on income level
    income_multipliers = {
        'Low': 0.7, 'Lower-Middle': 0.9, 'Middle': 1.0, 
        'Upper-Middle': 1.3, 'High': 1.8
    }
    clv *= income_multipliers[demographics['income_level']]
    
    # Adjust based on engagement level
    engagement_multipliers = {
        'low': 0.6, 'medium': 1.0, 'high': 1.4, 'very_high': 1.8
    }
    clv *= engagement_multipliers[acquisition_data['engagement_level']]
    
    # Adjust based on acquisition channel
    channel_multipliers = {
        'organic_search': 1.2, 'paid_search': 1.0, 'social_media': 1.1,
        'email_marketing': 1.3, 'referral': 1.4, 'direct': 1.1,
        'affiliate': 1.0, 'influencer': 1.2
    }
    clv *= channel_multipliers[acquisition_data['acquisition_channel']]
    
    return round(clv, 2)

def generate_enhanced_users(num_users):
    """Generate realistic users with comprehensive business context."""
    
    print("Generating enhanced users...")
    
    # Generate basic user data
    user_ids = np.arange(1, num_users + 1)
    names = [fake.name() for _ in range(num_users)]
    
    # Generate customer segments
    segments = generate_realistic_customer_segments(num_users)
    
    # Generate demographics
    demographics = generate_realistic_demographics(num_users)
    
    # Generate acquisition data
    signup_dates = [seg['signup_date'] for seg in segments]
    acquisition_data = generate_customer_acquisition_data(num_users, signup_dates)
    
    # Build comprehensive user records
    users = []
    for i in range(num_users):
        # Generate realistic email
        email = generate_realistic_email_enhanced(names[i], signup_dates[i], segments[i]['membership_status'])
        
        # Generate phone number based on state
        phone = generate_realistic_phone(demographics[i]['state'])
        
        # Generate address based on state and city
        address = generate_realistic_address(demographics[i]['state'], demographics[i]['city'])
        
        # Customer lifetime value estimation
        clv = estimate_customer_lifetime_value(segments[i], demographics[i], acquisition_data[i])
        
        user_record = {
            'user_id': user_ids[i],
            'name': names[i],
            'email': email,
            'phone': phone,
            'address': address,
            'signup_date': signup_dates[i].strftime('%Y-%m-%d'),
            'membership_status': segments[i]['membership_status'],
            'loyalty_points': segments[i]['loyalty_points'],
            'customer_lifecycle': segments[i]['customer_lifecycle'],
            'state': demographics[i]['state'],
            'city': demographics[i]['city'],
            'timezone': demographics[i]['timezone'],
            'age_group': demographics[i]['age_group'],
            'gender': demographics[i]['gender'],
            'income_level': demographics[i]['income_level'],
            'acquisition_channel': acquisition_data[i]['acquisition_channel'],
            'referral_source': acquisition_data[i]['referral_source'],
            'engagement_level': acquisition_data[i]['engagement_level'],
            'is_newsletter_subscriber': acquisition_data[i]['is_newsletter_subscriber'],
            'is_sms_subscriber': acquisition_data[i]['is_sms_subscriber'],
            'last_login_date': acquisition_data[i]['last_login_date'].strftime('%Y-%m-%d'),
            'total_logins': acquisition_data[i]['total_logins'],
            'estimated_clv': clv,
            'customer_preferences': str(acquisition_data[i]['preferences']),
            'communication_preferences': str(acquisition_data[i]['communication_preferences'])
        }
        
        users.append(user_record)
    
    return pd.DataFrame(users)

def generate_enhanced_review_metadata(rating, category, order_value, days_since_purchase, customer_tier):
    """Generate realistic review metadata based on various factors."""
    
    # Helpful votes based on review quality factors
    base_helpful_votes = 0
    
    # Higher ratings get more helpful votes
    if rating >= 4.5:
        base_helpful_votes += random.randint(5, 25)
    elif rating >= 4.0:
        base_helpful_votes += random.randint(2, 15)
    elif rating >= 3.0:
        base_helpful_votes += random.randint(0, 8)
    else:
        base_helpful_votes += random.randint(0, 3)
    
    # Premium customers' reviews get more engagement
    if customer_tier in ['Gold', 'Platinum']:
        base_helpful_votes = int(base_helpful_votes * random.uniform(1.2, 1.8))
    
    # Add some randomness
    helpful_votes = max(0, base_helpful_votes + random.randint(-2, 5))
    
    # Verified purchase (higher chance for recent orders and premium customers)
    verified_purchase = False
    if days_since_purchase <= 30:  # Recent purchase
        verified_purchase = random.random() < 0.85
    elif customer_tier in ['Gold', 'Platinum']:
        verified_purchase = random.random() < 0.70
    else:
        verified_purchase = random.random() < 0.60
    
    # Review length (longer reviews for higher value items and better ratings)
    if order_value > 200 and rating >= 4.0:
        review_length = random.choice(['short', 'medium', 'long', 'long'])
    elif order_value > 100:
        review_length = random.choice(['short', 'medium', 'long'])
    else:
        review_length = random.choice(['short', 'short', 'medium'])
    
    # Review images (more likely for higher value items and positive reviews)
    has_images = False
    image_count = 0
    if order_value > 150 and rating >= 4.0:
        has_images = random.random() < 0.35
        if has_images:
            image_count = random.randint(1, 5)
    elif order_value > 75:
        has_images = random.random() < 0.20
        if has_images:
            image_count = random.randint(1, 3)
    else:
        has_images = random.random() < 0.10
        if has_images:
            image_count = random.randint(1, 2)
    
    # Reviewer experience level
    if customer_tier in ['Gold', 'Platinum']:
        experience_level = random.choice(['expert', 'expert', 'experienced', 'experienced'])
    else:
        experience_level = random.choice(['new', 'experienced', 'experienced', 'expert'])
    
    return {
        'helpful_votes': helpful_votes,
        'verified_purchase': verified_purchase,
        'review_length': review_length,
        'has_images': has_images,
        'image_count': image_count,
        'experience_level': experience_level
    }

def generate_realistic_review(rating, category, product_name):
    """Generate a realistic product review based on rating and category."""
    
    # Review templates organized by category and sentiment
    review_templates = {
        'Electronics': {
            'positive': [
                "This {product} is absolutely amazing! The quality is outstanding and it works perfectly.",
                "I've been using this {product} for a few weeks now and I'm really impressed with the performance.",
                "Great {product}! Fast delivery and exactly as described. Highly recommend!",
                "Excellent {product}. The build quality is solid and it's very user-friendly.",
                "Love this {product}! It exceeded my expectations and the price was reasonable.",
                "Outstanding {product}! Works flawlessly and the design is sleek and modern.",
                "This {product} is fantastic! Great value for money and excellent functionality.",
                "Perfect {product}! Easy to set up and works exactly as advertised.",
                "Amazing {product}! The quality is top-notch and I use it daily.",
                "This {product} is incredible! Fast, reliable, and well-designed.",
                "I'm so happy with this {product}! The features are exactly what I needed.",
                "This {product} has exceeded all my expectations. Worth every penny!",
                "Excellent purchase! This {product} works better than I could have hoped.",
                "I've tried many similar products, but this {product} is by far the best.",
                "This {product} is a game-changer! It has made my life so much easier.",
                "Outstanding quality and performance. This {product} is built to last.",
                "I'm thoroughly impressed with this {product}. It's exactly what I was looking for.",
                "This {product} delivers on every promise. Highly satisfied with my purchase.",
                "The attention to detail in this {product} is remarkable. Very well made.",
                "I can't believe how well this {product} works. It's simply fantastic!",
                "This {product} has become an essential part of my daily routine.",
                "The performance of this {product} is outstanding. No complaints at all.",
                "I'm amazed by the quality and functionality of this {product}.",
                "This {product} is worth every dollar. It's reliable and efficient.",
                "I've been recommending this {product} to all my friends. It's that good!",
                "The design of this {product} is both beautiful and functional.",
                "This {product} has solved all my problems. Couldn't be happier!",
                "I'm genuinely impressed with the build quality of this {product}.",
                "This {product} works exactly as advertised. No false promises here.",
                "I love everything about this {product}. It's perfect for my needs.",
                "The user experience with this {product} is exceptional.",
                "This {product} has proven to be an excellent investment.",
                "I'm so glad I chose this {product}. It's exceeded my expectations.",
                "The functionality of this {product} is impressive and intuitive.",
                "This {product} is a perfect example of quality engineering.",
                "I've been using this {product} for months and it's still like new.",
                "The performance and reliability of this {product} is outstanding.",
                "This {product} has made my work so much more efficient.",
                "I'm completely satisfied with this {product}. It's exactly what I needed.",
                "The quality and craftsmanship of this {product} is top-notch.",
                "This {product} is a must-have for anyone serious about quality.",
                "I'm impressed by how well this {product} handles everything I throw at it.",
                "The attention to detail in this {product} is truly remarkable.",
                "This {product} has become my go-to choice. Highly recommended!",
                "I love the sleek design and powerful performance of this {product}.",
                "This {product} delivers consistent results every time I use it.",
                "The build quality and materials used in this {product} are excellent.",
                "I'm thrilled with this {product}. It's everything I hoped for and more.",
                "This {product} is a perfect blend of form and function.",
                "I've never been happier with a purchase. This {product} is amazing!"
            ],
            'negative': [
                "This {product} stopped working after just a few days. Very disappointed.",
                "Poor quality {product}. Doesn't work as advertised and feels cheap.",
                "Not impressed with this {product}. It's slow and the interface is confusing.",
                "This {product} is overpriced for what you get. Would not recommend.",
                "Terrible {product}. Broke within a week and customer service was unhelpful.",
                "This {product} is a waste of money. Doesn't meet expectations at all.",
                "Very disappointed with this {product}. Poor build quality and functionality.",
                "This {product} is not worth the price. Many better options available.",
                "Regret buying this {product}. It's unreliable and poorly made.",
                "This {product} is disappointing. Doesn't work properly and feels cheap.",
                "This {product} is a complete letdown. The quality is terrible.",
                "I expected much better from this {product}. It's poorly designed.",
                "This {product} is not user-friendly at all. Very frustrating to use.",
                "The performance of this {product} is subpar. Not worth the money.",
                "This {product} has too many issues. I wouldn't recommend it to anyone.",
                "The build quality of this {product} is shockingly poor.",
                "This {product} doesn't live up to its promises. Very misleading.",
                "I'm extremely disappointed with this {product}. It's not what I expected.",
                "This {product} is unreliable and breaks down frequently.",
                "The customer service for this {product} is terrible. No help at all.",
                "This {product} is overpriced and underperforms. Save your money.",
                "I've had nothing but problems with this {product}. Very frustrating.",
                "The design of this {product} is flawed and impractical.",
                "This {product} is not durable at all. Broke after minimal use.",
                "I'm not satisfied with this {product}. It's not worth the investment.",
                "This {product} has compatibility issues. Doesn't work with other devices.",
                "The software for this {product} is buggy and crashes frequently.",
                "This {product} is poorly manufactured. Quality control is lacking.",
                "I'm frustrated with this {product}. It doesn't work as intended.",
                "This {product} is a disappointment. The features don't work properly.",
                "The battery life of this {product} is terrible. Dies too quickly.",
                "This {product} is not intuitive to use. The interface is confusing.",
                "I'm unhappy with this {product}. It's not reliable for daily use.",
                "This {product} has connectivity issues. Doesn't stay connected.",
                "The materials used in this {product} feel cheap and flimsy.",
                "This {product} is not worth the hassle. Too many problems.",
                "I'm dissatisfied with this {product}. It's not meeting my needs.",
                "This {product} is poorly engineered. Design flaws are obvious.",
                "The performance of this {product} is inconsistent and unreliable.",
                "This {product} is not suitable for professional use. Too unreliable.",
                "I'm disappointed with the overall quality of this {product}.",
                "This {product} is not durable. Shows wear and tear quickly.",
                "The functionality of this {product} is limited and disappointing.",
                "This {product} is not user-friendly. Difficult to operate.",
                "I'm not impressed with this {product}. It's overpriced for what it offers.",
                "This {product} is not reliable. Malfunctions occur frequently.",
                "The build quality of this {product} is substandard.",
                "This {product} is not worth the money. Poor value for the price.",
                "I'm frustrated with this {product}. It's not working as advertised.",
                "This {product} is not recommended. Too many issues to ignore."
            ]
        },
        'Clothing': {
            'positive': [
                "Love this {product}! Perfect fit and great quality material.",
                "This {product} is exactly what I was looking for. Comfortable and stylish.",
                "Excellent {product}! Great quality and true to size. Will buy again.",
                "Amazing {product}! Soft fabric and perfect fit. Highly recommend!",
                "This {product} is fantastic! Comfortable, stylish, and well-made.",
                "Perfect {product}! Great quality and looks exactly like the picture.",
                "Love this {product}! Comfortable to wear and great value for money.",
                "This {product} is outstanding! Excellent quality and perfect fit.",
                "Great {product}! Soft, comfortable, and exactly as described.",
                "This {product} is incredible! Beautiful design and high-quality material.",
                "I'm so happy with this {product}! The fabric is soft and comfortable.",
                "This {product} fits perfectly and looks great on me. Very satisfied!",
                "Excellent quality and craftsmanship. This {product} is well worth the price.",
                "I've been wearing this {product} for weeks and it still looks brand new.",
                "The material of this {product} is top-notch. Feels luxurious to wear.",
                "This {product} is exactly what I needed. Perfect for my wardrobe.",
                "I love the style and fit of this {product}. It's become my favorite piece.",
                "The attention to detail in this {product} is impressive. Very well made.",
                "This {product} is comfortable all day long. Great for daily wear.",
                "I'm impressed with the quality and durability of this {product}.",
                "This {product} has exceeded my expectations. Beautiful and functional.",
                "The fit of this {product} is perfect. True to size and flattering.",
                "I've received so many compliments while wearing this {product}.",
                "This {product} is versatile and can be dressed up or down easily.",
                "The fabric quality of this {product} is excellent. Feels premium.",
                "I'm thrilled with this {product}. It's comfortable and stylish.",
                "This {product} is well-constructed and built to last. Great investment.",
                "The design of this {product} is timeless and elegant.",
                "I love how this {product} feels against my skin. Very comfortable.",
                "This {product} is perfect for any occasion. Very versatile piece.",
                "The sizing of this {product} is accurate. Fits exactly as expected.",
                "I'm completely satisfied with this {product}. Quality is outstanding.",
                "This {product} has become a staple in my wardrobe. Love it!",
                "The color and style of this {product} are exactly what I wanted.",
                "I'm amazed by the comfort and quality of this {product}.",
                "This {product} is perfect for my lifestyle. Comfortable and practical.",
                "The craftsmanship of this {product} is excellent. Very well made.",
                "I love everything about this {product}. Style, fit, and quality.",
                "This {product} is worth every penny. Excellent value for money.",
                "The material of this {product} is breathable and comfortable.",
                "I'm so glad I purchased this {product}. It's perfect for me.",
                "This {product} is stylish and comfortable. Perfect combination.",
                "The fit and finish of this {product} are impeccable.",
                "I'm impressed with the overall quality of this {product}.",
                "This {product} is exactly as described. No surprises, just satisfaction.",
                "The style of this {product} is modern and flattering.",
                "I love the attention to detail in this {product}. Very thoughtful design.",
                "This {product} is comfortable enough for all-day wear.",
                "The quality of this {product} is consistent throughout. Well made.",
                "I'm delighted with this {product}. It's everything I hoped for."
            ],
            'negative': [
                "This {product} doesn't fit well at all. The sizing is completely off.",
                "Poor quality {product}. The material feels cheap and it's uncomfortable.",
                "This {product} is not as described. The color is different and it's poorly made.",
                "Very disappointed with this {product}. It's uncomfortable and overpriced.",
                "This {product} is terrible quality. Fell apart after one wash.",
                "Not happy with this {product}. Poor fit and cheap material.",
                "This {product} is a waste of money. Doesn't look like the picture at all.",
                "Terrible {product}. Uncomfortable and the quality is very poor.",
                "This {product} is disappointing. Poor quality and doesn't fit properly.",
                "Regret buying this {product}. It's uncomfortable and poorly made.",
                "The sizing of this {product} is completely wrong. Way too small.",
                "This {product} is poorly constructed. Stitching is coming apart.",
                "The material of this {product} is scratchy and uncomfortable to wear.",
                "This {product} shrunk significantly after the first wash. Very disappointing.",
                "The color of this {product} faded after just one wash. Poor quality.",
                "This {product} is not breathable at all. Makes me sweat uncomfortably.",
                "The fit of this {product} is unflattering. Doesn't look good on me.",
                "This {product} is overpriced for the quality. Not worth the money.",
                "The fabric of this {product} pills easily. Looks worn out quickly.",
                "This {product} is not suitable for the intended use. Poor design.",
                "The construction of this {product} is shoddy. Threads are loose.",
                "This {product} is not comfortable to wear for extended periods.",
                "The sizing chart for this {product} is inaccurate. Very misleading.",
                "This {product} is not durable. Shows wear and tear immediately.",
                "The material of this {product} feels rough and uncomfortable.",
                "This {product} is not true to size. Much smaller than expected.",
                "The quality control for this {product} is lacking. Defects are visible.",
                "This {product} is not suitable for my body type. Poor fit.",
                "The fabric of this {product} wrinkles easily and looks messy.",
                "This {product} is not worth the price. Quality is substandard.",
                "The design of this {product} is impractical and uncomfortable.",
                "This {product} is not suitable for the climate. Too hot/cold.",
                "The material of this {product} is not suitable for sensitive skin.",
                "This {product} is not well-made. Construction is poor.",
                "The fit of this {product} is inconsistent. Some parts too tight.",
                "This {product} is not comfortable for daily wear. Too restrictive.",
                "The quality of this {product} is not what I expected. Very disappointed.",
                "This {product} is not suitable for the intended purpose. Poor design.",
                "The fabric of this {product} is not durable. Tears easily.",
                "This {product} is not flattering. Makes me look bigger than I am.",
                "The construction of this {product} is weak. Seams are coming apart.",
                "This {product} is not suitable for my lifestyle. Too delicate.",
                "The material of this {product} is not comfortable against the skin.",
                "This {product} is not worth the investment. Poor value for money.",
                "The sizing of this {product} is inconsistent. Different parts fit differently.",
                "This {product} is not suitable for the season. Wrong material choice.",
                "The quality of this {product} is below expectations. Not recommended.",
                "This {product} is not comfortable for all-day wear. Too tight.",
                "The design of this {product} is not practical. Impractical features.",
                "This {product} is not suitable for my needs. Poor functionality."
            ]
        },
        'Beauty': {
            'positive': [
                "This {product} is amazing! Works exactly as promised and great results.",
                "Love this {product}! Perfect for my skin type and easy to use.",
                "Excellent {product}! Great quality and I can see the difference already.",
                "This {product} is fantastic! Gentle on skin and very effective.",
                "Amazing {product}! Great value and it really works. Highly recommend!",
                "Perfect {product}! Easy to apply and gives great results.",
                "This {product} is outstanding! High quality and very effective.",
                "Love this {product}! Great for daily use and excellent results.",
                "This {product} is incredible! Works better than expected and great quality.",
                "Excellent {product}! Perfect for my routine and great value for money.",
                "I'm so impressed with this {product}! It's gentle yet effective.",
                "This {product} has transformed my skin. I can see real improvements.",
                "The formula of this {product} is perfect for my sensitive skin.",
                "I've been using this {product} for weeks and my skin looks amazing.",
                "This {product} is worth every penny. The results speak for themselves.",
                "I love how this {product} feels on my skin. Smooth and non-greasy.",
                "This {product} has become a staple in my beauty routine. Love it!",
                "The packaging of this {product} is beautiful and the product works great.",
                "I'm thrilled with the results from this {product}. Highly effective.",
                "This {product} is perfect for my skin concerns. Exactly what I needed.",
                "I've tried many similar products, but this {product} is the best.",
                "The texture of this {product} is perfect. Absorbs quickly and feels great.",
                "This {product} has improved my skin texture significantly.",
                "I'm amazed by how well this {product} works. Visible results quickly.",
                "This {product} is gentle enough for daily use and very effective.",
                "The ingredients in this {product} are high-quality and effective.",
                "I love the scent of this {product}. Pleasant and not overpowering.",
                "This {product} has helped with my skin issues. Very satisfied!",
                "The application of this {product} is easy and the results are great.",
                "I'm completely satisfied with this {product}. It delivers on its promises.",
                "This {product} is perfect for my skin type. No irritation at all.",
                "The results from this {product} are noticeable and long-lasting.",
                "I've been recommending this {product} to all my friends. It's that good!",
                "This {product} has made my skin look healthier and more radiant.",
                "The quality of this {product} is exceptional. Worth the investment.",
                "I'm impressed with how quickly this {product} shows results.",
                "This {product} is perfect for my morning routine. Quick and effective.",
                "The formula of this {product} is well-balanced and effective.",
                "I love how this {product} makes my skin feel. Soft and smooth.",
                "This {product} has exceeded my expectations. Excellent quality.",
                "The packaging of this {product} is practical and the product is great.",
                "I'm delighted with this {product}. It's become my go-to choice.",
                "This {product} is perfect for sensitive skin. No adverse reactions.",
                "The results from this {product} are consistent and impressive.",
                "I've been using this {product} for months and still love it.",
                "This {product} has improved my confidence. My skin looks great!",
                "The texture and feel of this {product} are perfect for me.",
                "I'm so happy I found this {product}. It's exactly what I needed.",
                "This {product} is a game-changer for my skincare routine.",
                "The effectiveness of this {product} is remarkable. Highly recommend!"
            ],
            'negative': [
                "This {product} caused irritation and didn't work as advertised.",
                "Poor quality {product}. Doesn't work and feels cheap.",
                "This {product} is not effective at all. Waste of money.",
                "Very disappointed with this {product}. It's harsh and doesn't work.",
                "This {product} is terrible. Caused breakouts and poor quality.",
                "Not impressed with this {product}. It's ineffective and overpriced.",
                "This {product} is disappointing. Doesn't work and poor quality.",
                "Terrible {product}. Ineffective and caused skin problems.",
                "This {product} is not worth the price. Poor results and quality.",
                "Regret buying this {product}. It's ineffective and harsh on skin.",
                "This {product} caused allergic reactions. Not suitable for sensitive skin.",
                "The formula of this {product} is too harsh. Caused redness and irritation.",
                "This {product} doesn't work as promised. No visible results at all.",
                "The texture of this {product} is unpleasant. Feels sticky and heavy.",
                "This {product} is overpriced for what it does. Not effective.",
                "I'm disappointed with this {product}. It made my skin worse.",
                "This {product} has a terrible smell. Unpleasant to use.",
                "The packaging of this {product} is poor and the product is ineffective.",
                "This {product} is not suitable for my skin type. Caused problems.",
                "I'm not satisfied with this {product}. It's not worth the money.",
                "This {product} is too harsh for daily use. Caused irritation.",
                "The ingredients in this {product} seem cheap and ineffective.",
                "This {product} doesn't absorb well. Leaves a greasy residue.",
                "I'm frustrated with this {product}. It doesn't deliver on promises.",
                "This {product} is not gentle enough. Too harsh for sensitive skin.",
                "The results from this {product} are minimal and not worth it.",
                "This {product} has an unpleasant texture. Difficult to apply.",
                "I'm unhappy with this {product}. It's not effective at all.",
                "This {product} is not suitable for my skin concerns. Wrong formula.",
                "The quality of this {product} is poor. Doesn't work as expected.",
                "This {product} is not worth the investment. Poor value for money.",
                "I'm dissatisfied with this {product}. It's not meeting my needs.",
                "This {product} is not gentle on skin. Caused dryness and irritation.",
                "The formula of this {product} is not effective. No improvement seen.",
                "This {product} is not suitable for daily use. Too strong.",
                "I'm disappointed with the overall quality of this {product}.",
                "This {product} is not effective for my skin type. Wrong choice.",
                "The application of this {product} is difficult and unpleasant.",
                "This {product} is not worth the price. Poor results and quality.",
                "I'm not impressed with this {product}. It's overpriced and ineffective.",
                "This {product} is not suitable for my routine. Doesn't work well.",
                "The ingredients in this {product} seem low-quality and ineffective.",
                "This {product} is not gentle enough. Caused skin sensitivity.",
                "I'm frustrated with this {product}. It's not working as advertised.",
                "This {product} is not effective for my skin concerns. Disappointing.",
                "The texture of this {product} is unpleasant. Hard to work with.",
                "This {product} is not suitable for my skin. Caused adverse reactions.",
                "I'm not satisfied with this {product}. It's not worth the money.",
                "This {product} is not effective. No improvement in my skin.",
                "The quality of this {product} is substandard. Not recommended."
            ]
        },
        'Home': {
            'positive': [
                "This {product} is perfect for my home! Great quality and exactly what I needed.",
                "Love this {product}! Well-made and looks great in my space.",
                "Excellent {product}! High quality and perfect for the intended use.",
                "This {product} is fantastic! Great value and excellent quality.",
                "Amazing {product}! Perfect size and great quality. Highly recommend!",
                "This {product} is outstanding! Well-designed and very functional.",
                "Perfect {product}! Great quality and exactly as described.",
                "This {product} is incredible! Beautiful design and excellent craftsmanship.",
                "Love this {product}! Perfect for my needs and great quality.",
                "This {product} is excellent! Well-made and great value for money.",
                "I'm so happy with this {product}! It fits perfectly in my home.",
                "This {product} has transformed my space. Looks amazing and works great.",
                "The quality of this {product} is exceptional. Built to last.",
                "I've been using this {product} for months and it's still like new.",
                "This {product} is exactly what I was looking for. Perfect addition to my home.",
                "The design of this {product} is beautiful and functional. Love it!",
                "This {product} is well-constructed and durable. Great investment.",
                "I'm impressed with the craftsmanship of this {product}. Very well made.",
                "This {product} has made my home more comfortable and stylish.",
                "The materials used in this {product} are high-quality and durable.",
                "This {product} is perfect for my lifestyle. Practical and beautiful.",
                "I love how this {product} looks in my space. Exactly what I envisioned.",
                "This {product} is versatile and can be used in multiple ways.",
                "The functionality of this {product} is excellent. Does exactly what I need.",
                "This {product} has exceeded my expectations. Quality is outstanding.",
                "I'm thrilled with this {product}. It's become a favorite in my home.",
                "The attention to detail in this {product} is remarkable. Very thoughtful.",
                "This {product} is perfect for my needs. Comfortable and practical.",
                "I'm amazed by the quality and design of this {product}.",
                "This {product} is worth every penny. Excellent value for money.",
                "The build quality of this {product} is impressive. Very sturdy.",
                "I've been recommending this {product} to friends. It's that good!",
                "This {product} has improved my daily routine. Very functional.",
                "The style of this {product} is timeless and elegant.",
                "I'm completely satisfied with this {product}. It's perfect for me.",
                "This {product} is easy to assemble and use. Great design.",
                "The durability of this {product} is impressive. Built to last.",
                "I love everything about this {product}. Style, quality, and functionality.",
                "This {product} is perfect for my home decor. Matches perfectly.",
                "The craftsmanship of this {product} is top-notch. Very well made.",
                "I'm delighted with this {product}. It's exactly what I needed.",
                "This {product} has made my home more organized and efficient.",
                "The materials of this {product} are premium quality. Feels luxurious.",
                "I'm impressed with the overall quality of this {product}.",
                "This {product} is perfect for my space. Fits beautifully.",
                "The functionality of this {product} is exactly what I was looking for.",
                "I'm so glad I purchased this {product}. It's perfect for my home.",
                "This {product} is well-designed and practical. Great addition to my home.",
                "The quality of this {product} is consistent throughout. Excellent workmanship.",
                "I'm thrilled with this {product}. It's everything I hoped for and more."
            ],
            'negative': [
                "This {product} is poorly made and doesn't work as expected.",
                "Poor quality {product}. Cheap materials and poor construction.",
                "This {product} is not as described. Poor quality and doesn't work properly.",
                "Very disappointed with this {product}. It's flimsy and overpriced.",
                "This {product} is terrible quality. Broke easily and poor design.",
                "Not happy with this {product}. Poor quality and doesn't meet expectations.",
                "This {product} is a waste of money. Poor quality and doesn't work.",
                "Terrible {product}. Cheap materials and poor construction.",
                "This {product} is disappointing. Poor quality and doesn't function properly.",
                "Regret buying this {product}. It's poorly made and doesn't work.",
                "This {product} is not durable at all. Broke after minimal use.",
                "The construction of this {product} is shoddy. Poor workmanship.",
                "This {product} doesn't fit properly in my space. Poor design.",
                "The materials used in this {product} are cheap and flimsy.",
                "This {product} is not suitable for its intended purpose. Poor design.",
                "I'm disappointed with this {product}. It's not worth the money.",
                "This {product} is poorly designed. Difficult to use and assemble.",
                "The quality control for this {product} is lacking. Defects are visible.",
                "This {product} is not functional. Doesn't work as advertised.",
                "I'm not satisfied with this {product}. It's poorly made.",
                "This {product} is not suitable for my needs. Wrong size/design.",
                "The assembly of this {product} was difficult and instructions were poor.",
                "This {product} is not durable. Shows wear and tear quickly.",
                "I'm frustrated with this {product}. It doesn't work properly.",
                "This {product} is not worth the investment. Poor value for money.",
                "The design of this {product} is impractical and uncomfortable.",
                "This {product} is not suitable for my home. Poor quality materials.",
                "I'm unhappy with this {product}. It's not meeting my expectations.",
                "This {product} is not well-made. Construction is poor and weak.",
                "The functionality of this {product} is limited and disappointing.",
                "This {product} is not suitable for daily use. Too fragile.",
                "I'm disappointed with the overall quality of this {product}.",
                "This {product} is not functional. Doesn't serve its intended purpose.",
                "The materials of this {product} are not suitable for home use.",
                "This {product} is not worth the price. Poor quality and design.",
                "I'm not impressed with this {product}. It's overpriced and poorly made.",
                "This {product} is not suitable for my lifestyle. Too delicate.",
                "The construction of this {product} is weak and unreliable.",
                "This {product} is not practical. Doesn't work as expected.",
                "I'm dissatisfied with this {product}. It's not worth the money.",
                "This {product} is not durable enough for home use. Breaks easily.",
                "The design of this {product} is flawed and impractical.",
                "This {product} is not suitable for my space. Wrong dimensions.",
                "I'm frustrated with this {product}. It's not working as advertised.",
                "This {product} is not well-constructed. Poor quality control.",
                "The materials used in this {product} are substandard.",
                "This {product} is not recommended. Too many issues to ignore.",
                "I'm not satisfied with this {product}. It's not meeting my needs.",
                "This {product} is not suitable for my home. Poor quality and design."
            ]
        },
        'Sports': {
            'positive': [
                "This {product} is perfect for my workouts! Great quality and very durable.",
                "Love this {product}! Excellent for training and well-made.",
                "This {product} is fantastic! Great performance and excellent quality.",
                "Amazing {product}! Perfect for my fitness routine and very durable.",
                "This {product} is outstanding! Great quality and exactly what I needed.",
                "Perfect {product}! Excellent for sports and very well-made.",
                "This {product} is incredible! Great performance and high quality.",
                "Love this {product}! Perfect for my training and excellent durability.",
                "This {product} is excellent! Great quality and perfect for my needs.",
                "This {product} is fantastic! Well-made and perfect for sports activities.",
                "I'm so impressed with this {product}! It's built for serious athletes.",
                "This {product} has improved my performance significantly. Highly recommend!",
                "The durability of this {product} is outstanding. Built to last.",
                "I've been using this {product} for months and it's still in perfect condition.",
                "This {product} is exactly what I needed for my training. Perfect fit and function.",
                "The quality of this {product} is exceptional. Worth every penny.",
                "I love how this {product} performs during intense workouts. Reliable and effective.",
                "This {product} has become essential to my fitness routine. Love it!",
                "The materials used in this {product} are top-quality and durable.",
                "I'm amazed by the performance and comfort of this {product}.",
                "This {product} is perfect for my sport. Excellent design and functionality.",
                "The craftsmanship of this {product} is impressive. Very well made.",
                "I've been recommending this {product} to my teammates. It's that good!",
                "This {product} has enhanced my training experience. Highly effective.",
                "The design of this {product} is both functional and comfortable.",
                "I'm thrilled with this {product}. It's exceeded my expectations.",
                "This {product} is perfect for serious athletes. Professional quality.",
                "The performance of this {product} is consistent and reliable.",
                "I love everything about this {product}. Quality, comfort, and performance.",
                "This {product} has made my workouts more effective and enjoyable.",
                "The build quality of this {product} is excellent. Very sturdy.",
                "I'm completely satisfied with this {product}. It's perfect for my needs.",
                "This {product} is ideal for my training goals. Highly functional.",
                "The materials of this {product} are premium quality. Feels great.",
                "I'm impressed with the overall quality and performance of this {product}.",
                "This {product} is perfect for my sport. Excellent value for money.",
                "The functionality of this {product} is exactly what I was looking for.",
                "I'm so glad I purchased this {product}. It's perfect for my training.",
                "This {product} is well-designed and practical. Great for athletes.",
                "The durability of this {product} is impressive. Built to withstand heavy use.",
                "I'm delighted with this {product}. It's everything I hoped for.",
                "This {product} has improved my athletic performance. Highly effective.",
                "The quality of this {product} is consistent throughout. Excellent workmanship.",
                "I'm thrilled with this {product}. It's perfect for my fitness goals.",
                "This {product} is ideal for serious training. Professional-grade quality.",
                "The performance of this {product} is outstanding. Highly recommend!",
                "I'm impressed with how well this {product} holds up during intense use.",
                "This {product} is perfect for my athletic needs. Excellent quality and design.",
                "The materials and construction of this {product} are top-notch.",
                "I'm completely satisfied with this {product}. It's perfect for my sport."
            ],
            'negative': [
                "This {product} is poorly made and doesn't hold up during use.",
                "Poor quality {product}. Broke easily and doesn't work properly.",
                "This {product} is not durable at all. Poor quality materials.",
                "Very disappointed with this {product}. It's flimsy and overpriced.",
                "This {product} is terrible quality. Doesn't work and poor construction.",
                "Not impressed with this {product}. Poor quality and doesn't meet expectations.",
                "This {product} is disappointing. Poor durability and doesn't work properly.",
                "Terrible {product}. Cheap materials and poor performance.",
                "This {product} is not worth the price. Poor quality and doesn't work.",
                "Regret buying this {product}. It's poorly made and doesn't function properly.",
                "This {product} is not suitable for athletic use. Too fragile.",
                "The construction of this {product} is weak. Poor workmanship.",
                "This {product} doesn't perform as advertised. Disappointing quality.",
                "The materials used in this {product} are cheap and unreliable.",
                "This {product} is not suitable for serious training. Poor design.",
                "I'm disappointed with this {product}. It's not worth the money.",
                "This {product} is poorly designed. Uncomfortable and ineffective.",
                "The quality control for this {product} is lacking. Defects are visible.",
                "This {product} is not functional for sports. Doesn't work as intended.",
                "I'm not satisfied with this {product}. It's poorly made.",
                "This {product} is not suitable for my training needs. Wrong design.",
                "The durability of this {product} is poor. Breaks easily during use.",
                "This {product} is not reliable for athletic activities. Too fragile.",
                "I'm frustrated with this {product}. It doesn't work properly.",
                "This {product} is not worth the investment. Poor value for money.",
                "The design of this {product} is impractical for sports use.",
                "This {product} is not suitable for athletes. Poor quality materials.",
                "I'm unhappy with this {product}. It's not meeting my expectations.",
                "This {product} is not well-made. Construction is poor and weak.",
                "The functionality of this {product} is limited and disappointing.",
                "This {product} is not suitable for intense training. Too delicate.",
                "I'm disappointed with the overall quality of this {product}.",
                "This {product} is not functional for its intended purpose. Poor design.",
                "The materials of this {product} are not suitable for athletic use.",
                "This {product} is not worth the price. Poor quality and performance.",
                "I'm not impressed with this {product}. It's overpriced and poorly made.",
                "This {product} is not suitable for my sport. Too unreliable.",
                "The construction of this {product} is weak and unreliable.",
                "This {product} is not practical for training. Doesn't work as expected.",
                "I'm dissatisfied with this {product}. It's not worth the money.",
                "This {product} is not durable enough for sports use. Breaks easily.",
                "The design of this {product} is flawed and impractical.",
                "This {product} is not suitable for my athletic needs. Wrong specifications.",
                "I'm frustrated with this {product}. It's not working as advertised.",
                "This {product} is not well-constructed. Poor quality control.",
                "The materials used in this {product} are substandard for sports.",
                "This {product} is not recommended for athletes. Too many issues.",
                "I'm not satisfied with this {product}. It's not meeting my needs.",
                "This {product} is not suitable for serious athletes. Poor quality and design."
            ]
        },
        'Toys': {
            'positive': [
                "This {product} is perfect for my child! Great quality and lots of fun.",
                "Love this {product}! My kids absolutely adore it and it's well-made.",
                "This {product} is fantastic! Great for playtime and excellent quality.",
                "Amazing {product}! Perfect for children and very durable.",
                "This {product} is outstanding! Great quality and kids love it.",
                "Perfect {product}! Excellent for play and very well-made.",
                "This {product} is incredible! Great quality and perfect for kids.",
                "Love this {product}! My children love it and it's very durable.",
                "This {product} is excellent! Great quality and perfect for playtime.",
                "This {product} is fantastic! Well-made and kids absolutely love it.",
                "I'm so happy with this {product}! My child plays with it every day.",
                "This {product} has provided hours of entertainment. Highly recommend!",
                "The quality of this {product} is excellent. Built to last through rough play.",
                "I've been impressed with how durable this {product} is. Still looks new.",
                "This {product} is exactly what my child needed. Perfect for their age.",
                "The design of this {product} is both fun and educational. Love it!",
                "This {product} is well-constructed and safe for children. Great investment.",
                "I'm amazed by how much my child enjoys this {product}. Worth every penny.",
                "This {product} has become my child's favorite toy. They play with it constantly.",
                "The materials used in this {product} are high-quality and child-safe.",
                "This {product} is perfect for my child's development. Educational and fun.",
                "I love how this {product} encourages creativity and imagination.",
                "This {product} is ideal for children. Safe, durable, and entertaining.",
                "The craftsmanship of this {product} is impressive. Very well made.",
                "I've been recommending this {product} to other parents. It's that good!",
                "This {product} has enhanced my child's playtime. Highly effective.",
                "The design of this {product} is both engaging and safe for kids.",
                "I'm thrilled with this {product}. It's exceeded my expectations.",
                "This {product} is perfect for children. Excellent quality and design.",
                "The performance of this {product} is consistent and reliable.",
                "I love everything about this {product}. Quality, safety, and fun.",
                "This {product} has made playtime more enjoyable for my child.",
                "The build quality of this {product} is excellent. Very sturdy.",
                "I'm completely satisfied with this {product}. It's perfect for my child.",
                "This {product} is ideal for my child's interests. Highly functional.",
                "The materials of this {product} are premium quality. Feels great.",
                "I'm impressed with the overall quality and safety of this {product}.",
                "This {product} is perfect for my child. Excellent value for money.",
                "The functionality of this {product} is exactly what I was looking for.",
                "I'm so glad I purchased this {product}. It's perfect for my child.",
                "This {product} is well-designed and practical. Great for kids.",
                "The durability of this {product} is impressive. Built to withstand play.",
                "I'm delighted with this {product}. It's everything I hoped for.",
                "This {product} has improved my child's play experience. Highly effective.",
                "The quality of this {product} is consistent throughout. Excellent workmanship.",
                "I'm thrilled with this {product}. It's perfect for my child's needs.",
                "This {product} is ideal for children's play. Professional-grade quality.",
                "The performance of this {product} is outstanding. Highly recommend!",
                "I'm impressed with how well this {product} holds up during play.",
                "This {product} is perfect for my child's needs. Excellent quality and design.",
                "The materials and construction of this {product} are top-notch.",
                "I'm completely satisfied with this {product}. It's perfect for my child."
            ],
            'negative': [
                "This {product} broke easily and is not safe for children.",
                "Poor quality {product}. Cheap materials and doesn't work properly.",
                "This {product} is not suitable for kids. Poor quality and unsafe.",
                "Very disappointed with this {product}. It's flimsy and overpriced.",
                "This {product} is terrible quality. Broke quickly and poor design.",
                "Not happy with this {product}. Poor quality and doesn't work properly.",
                "This {product} is disappointing. Poor quality and not safe for children.",
                "Terrible {product}. Cheap materials and poor construction.",
                "This {product} is not worth the price. Poor quality and doesn't work.",
                "Regret buying this {product}. It's poorly made and not safe for kids.",
                "This {product} is not suitable for children. Too fragile and dangerous.",
                "The construction of this {product} is weak. Poor workmanship.",
                "This {product} doesn't work as advertised. Disappointing quality.",
                "The materials used in this {product} are cheap and unsafe.",
                "This {product} is not suitable for kids' play. Poor design.",
                "I'm disappointed with this {product}. It's not worth the money.",
                "This {product} is poorly designed. Uncomfortable and unsafe for children.",
                "The quality control for this {product} is lacking. Defects are visible.",
                "This {product} is not functional for children. Doesn't work as intended.",
                "I'm not satisfied with this {product}. It's poorly made.",
                "This {product} is not suitable for my child's needs. Wrong design.",
                "The durability of this {product} is poor. Breaks easily during play.",
                "This {product} is not safe for children. Too many sharp edges.",
                "I'm frustrated with this {product}. It doesn't work properly.",
                "This {product} is not worth the investment. Poor value for money.",
                "The design of this {product} is impractical for children's use.",
                "This {product} is not suitable for kids. Poor quality materials.",
                "I'm unhappy with this {product}. It's not meeting my expectations.",
                "This {product} is not well-made. Construction is poor and weak.",
                "The functionality of this {product} is limited and disappointing.",
                "This {product} is not suitable for children's play. Too delicate.",
                "I'm disappointed with the overall quality of this {product}.",
                "This {product} is not functional for its intended purpose. Poor design.",
                "The materials of this {product} are not suitable for children.",
                "This {product} is not worth the price. Poor quality and safety.",
                "I'm not impressed with this {product}. It's overpriced and poorly made.",
                "This {product} is not suitable for my child. Too unreliable.",
                "The construction of this {product} is weak and unreliable.",
                "This {product} is not practical for children. Doesn't work as expected.",
                "I'm dissatisfied with this {product}. It's not worth the money.",
                "This {product} is not durable enough for children's use. Breaks easily.",
                "The design of this {product} is flawed and unsafe.",
                "This {product} is not suitable for my child's needs. Wrong specifications.",
                "I'm frustrated with this {product}. It's not working as advertised.",
                "This {product} is not well-constructed. Poor quality control.",
                "The materials used in this {product} are substandard for children.",
                "This {product} is not recommended for kids. Too many safety issues.",
                "I'm not satisfied with this {product}. It's not meeting my child's needs.",
                "This {product} is not suitable for children. Poor quality and unsafe design."
            ]
        }
    }
    
    # Determine sentiment based on rating
    if rating >= 4.0:
        sentiment = 'positive'
    else:
        sentiment = 'negative'
    
    # Get templates for the category and sentiment
    templates = review_templates.get(category, review_templates['Electronics'])
    template_list = templates.get(sentiment, templates['positive'])
    
    # Select a random template
    template = random.choice(template_list)
    
    # Replace placeholder with actual product name
    review_text = template.format(product=product_name)
    
    return review_text

def generate_enhanced_realistic_review(rating, category, product_name, product_brand, order_value, days_since_purchase, customer_tier, user_name):
    """Generate a realistic product review with enhanced metadata and natural language."""
    
    # Get review metadata
    metadata = generate_enhanced_review_metadata(rating, category, order_value, days_since_purchase, customer_tier)
    
    # Enhanced review templates with more natural language and specific details
    enhanced_templates = {
        'Electronics': {
            'positive': {
                'short': [
                    "Great {product}! Works perfectly.",
                    "Love this {product}. Highly recommend!",
                    "Excellent {product}. Fast delivery.",
                    "Perfect {product}! Exactly as described.",
                    "Amazing {product}. Worth every penny!",
                    "Outstanding {product}! Great quality.",
                    "This {product} is fantastic!",
                    "Excellent purchase! Works great.",
                    "Love it! This {product} is perfect.",
                    "Great {product}! Very satisfied."
                ],
                'medium': [
                    "I've been using this {product} for about {weeks} weeks now and I'm really impressed. The build quality is solid and it works exactly as advertised. The {feature} feature is particularly useful. Setup was easy and it integrates well with my other devices. Would definitely recommend to anyone looking for a reliable {category}.",
                    "This {product} exceeded my expectations! The performance is outstanding and the design is sleek. I especially love how {specific_feature}. The price point is reasonable for the quality you get. Customer service was also helpful when I had questions. This is now my go-to {category}.",
                    "Excellent {product}! I've tried several similar products but this one stands out. The {feature} works flawlessly and the user interface is intuitive. It's been {time_period} since I bought it and it still works like new. Great value for money and I'd buy it again.",
                    "I'm thoroughly impressed with this {product}. The quality is top-notch and it has all the features I need. The {specific_feature} is exactly what I was looking for. Setup was straightforward and it's been working perfectly for {time_period}. Highly recommend!",
                    "This {product} is a game-changer! The performance is incredible and the build quality is excellent. I love the {feature} and how it {specific_benefit}. It's been {time_period} and I'm still discovering new features. Worth every penny and then some."
                ],
                'long': [
                    "I've been using this {product} for {weeks} weeks now and I can honestly say it's one of the best purchases I've made this year. The build quality is exceptional - it feels solid and well-constructed. The {feature} feature works flawlessly and has made my daily routine so much easier. I particularly appreciate how {specific_feature} because it {specific_benefit}. The user interface is intuitive and I was able to set it up without any issues. The {another_feature} is also impressive and works exactly as described. I've recommended this to several friends who have also been very happy with their purchases. The customer service team was also very helpful when I had a question about compatibility. Overall, this {product} delivers on every promise and I would definitely buy it again. It's worth every penny and I'm confident it will last for years to come.",
                    "After extensive research and reading countless reviews, I decided to go with this {product} and I'm so glad I did. The quality is outstanding and it has exceeded all my expectations. The {feature} is exactly what I needed and works perfectly. I've been using it for {time_period} and it's been incredibly reliable. The {specific_feature} is particularly impressive - it {specific_benefit}. The design is sleek and modern, fitting perfectly with my setup. I also appreciate the attention to detail in the packaging and documentation. The setup process was straightforward and I was up and running in no time. The {another_feature} works seamlessly with my other devices. I've had no issues whatsoever and the performance has been consistent. The value for money is excellent - you get premium quality at a reasonable price. I would definitely recommend this to anyone looking for a high-quality {category}. It's a solid investment that I'm confident will serve me well for years to come.",
                    "This {product} is absolutely fantastic! I've been using it for {weeks} weeks and I'm still impressed every time I use it. The build quality is exceptional - it feels premium and well-made. The {feature} feature is incredible and works exactly as advertised. I particularly love how {specific_feature} because it {specific_benefit}. The user experience is smooth and intuitive, making it a pleasure to use daily. The {another_feature} is also excellent and adds real value. I've compared it to several competitors and this one clearly stands out in terms of both quality and functionality. The customer support team was also very helpful when I had questions about advanced features. The documentation is comprehensive and well-written. I've recommended this to multiple friends and colleagues who have all been very satisfied with their purchases. The price point is fair for the quality and features you get. This is definitely a product I would buy again and I'm confident it will last for many years. Highly recommend to anyone looking for a top-quality {category}."
                ]
            },
            'negative': {
                'short': [
                    "Not impressed with this {product}.",
                    "Poor quality. Would not recommend.",
                    "This {product} stopped working quickly.",
                    "Disappointed with this {product}.",
                    "Not worth the money.",
                    "This {product} has issues.",
                    "Poor build quality.",
                    "Doesn't work as advertised.",
                    "Regret buying this {product}.",
                    "Not reliable at all."
                ],
                'medium': [
                    "I had high hopes for this {product} but unfortunately it didn't meet my expectations. The build quality feels cheap and it stopped working properly after just {weeks} weeks. The {feature} feature that I was most excited about doesn't work as advertised. Customer service was unhelpful when I tried to get support. For the price, I expected much better quality. I would not recommend this {product} to others.",
                    "This {product} is disappointing. While it looks good initially, the performance is subpar. The {feature} feature is buggy and crashes frequently. The user interface is confusing and not intuitive. I've had several issues with connectivity and the overall reliability is poor. The price point is too high for what you actually get. I regret this purchase and would not buy it again.",
                    "I'm not satisfied with this {product}. The quality is not what I expected for the price. The {feature} doesn't work properly and I've had to troubleshoot issues constantly. The build quality feels flimsy and I'm concerned about its durability. Customer support was slow to respond and not very helpful. I would recommend looking at other options before buying this {product}.",
                    "This {product} has been a letdown. The performance is inconsistent and it doesn't deliver on its promises. The {feature} feature is unreliable and I've had multiple problems with it. The overall quality feels cheap and I'm not confident it will last. The price is too high for the quality you receive. I would not recommend this to anyone looking for a reliable {category}."
                ],
                'long': [
                    "I really wanted to love this {product} but unfortunately it has been a major disappointment. After using it for {weeks} weeks, I can say that the quality is not what I expected for the price point. The build quality feels cheap and flimsy - it doesn't have the solid, premium feel I was hoping for. The {feature} feature, which was the main reason I bought this {product}, is buggy and unreliable. It frequently crashes or doesn't work at all, which is incredibly frustrating. The user interface is confusing and not intuitive, making it difficult to use effectively. I've spent hours trying to troubleshoot various issues and the customer support team has been unhelpful and slow to respond. The {specific_feature} that was advertised as a key selling point doesn't work as described. I've had connectivity issues, performance problems, and the overall reliability is poor. For the amount of money I spent, I expected much better quality and functionality. I would not recommend this {product} to anyone and I regret this purchase. I'm currently looking for alternatives that actually deliver on their promises.",
                    "This {product} has been nothing but trouble since I bought it. The initial setup was problematic and I had to contact customer support multiple times just to get it working. The build quality is substandard - it feels cheap and poorly made. The {feature} feature that I was most excited about is completely unreliable and frequently stops working. The user interface is confusing and not user-friendly at all. I've had numerous technical issues including connectivity problems, software crashes, and inconsistent performance. The {specific_feature} doesn't work as advertised and I've been very disappointed with the overall functionality. Customer service has been unresponsive and unhelpful when I've tried to get support. The documentation is poorly written and doesn't provide adequate guidance. For the premium price I paid, I expected much better quality and reliability. I would not recommend this {product} to anyone and I'm currently looking for a replacement. This has been a complete waste of money and I regret the purchase entirely."
                ]
            }
        }
    }
    
    # Determine sentiment and length
    sentiment = 'positive' if rating >= 4.0 else 'negative'
    length = metadata['review_length']
    
    # Get templates for the category and sentiment
    templates = enhanced_templates.get(category, enhanced_templates['Electronics'])
    template_list = templates.get(sentiment, templates['positive'])
    length_templates = template_list.get(length, template_list['medium'])
    
    # Select a random template
    template = random.choice(length_templates)
    
    # Replace placeholders with actual values
    review_text = template.format(
        product=product_name,
        brand=product_brand,
        category=category,
        feature=random.choice(['design', 'quality', 'performance', 'durability', 'functionality']),
        specific_feature=random.choice(['battery life', 'screen quality', 'sound quality', 'build quality', 'user interface']),
        weeks=random.randint(1, 52),
        months=random.randint(1, 12),
        days=random.randint(1, 30)
    )
    
    # Add verified purchase context
    if metadata['verified_purchase']:
        verified_additions = [
            " Verified purchase - arrived exactly as described.",
            " Verified purchase - great packaging and fast shipping.",
            " Verified purchase - would definitely buy again.",
            " Verified purchase - excellent customer service.",
            " Verified purchase - exceeded my expectations.",
            " Verified purchase - highly recommend this seller.",
            " Verified purchase - fast delivery and great quality.",
            " Verified purchase - exactly what I was looking for.",
            " Verified purchase - great value for money.",
            " Verified purchase - will be ordering more soon.",
            " Purchased this item and it arrived in perfect condition.",
            " Bought this item and the packaging was excellent."
        ]
        if random.random() < 0.2:  # 20% chance to add verified context
            review_text += random.choice(verified_additions)
    
    return {
        'review_text': review_text,
        'helpful_votes': metadata['helpful_votes'],
        'verified_purchase': metadata['verified_purchase'],
        'has_images': metadata['has_images'],
        'image_count': metadata['image_count'],
        'experience_level': metadata['experience_level']
    }

def generate_realistic_email(name):
                'short': [
                    "Perfect fit! Love this {product}.",
                    "Great quality {product}. True to size.",
                    "Comfortable and stylish {product}.",
                    "Excellent {product}! Will buy again.",
                    "Love this {product}. Great material.",
                    "Perfect {product}! Exactly as described.",
                    "Amazing {product}. Very comfortable.",
                    "Great {product}! Fits perfectly.",
                    "Love it! This {product} is perfect.",
                    "Excellent quality {product}."
                ],
                'medium': [
                    "I'm really happy with this {product}! The fit is perfect and the material is high quality. I ordered my usual size and it fits exactly as expected. The {feature} is exactly what I was looking for. I've worn it {time_period} and it still looks great. The {specific_feature} is particularly nice. Would definitely recommend to anyone looking for a quality {category}.",
                    "This {product} exceeded my expectations! The fabric is soft and comfortable, and the fit is perfect. I love the {feature} and how it {specific_benefit}. The quality is excellent for the price. I've received several compliments while wearing it. The {specific_feature} is a nice touch. This is now one of my favorite pieces in my wardrobe.",
                    "Excellent {product}! The quality is outstanding and it fits perfectly. I was a bit worried about the sizing but it's true to size. The {feature} works great and the material feels premium. I've been wearing it for {time_period} and it still looks brand new. The {specific_feature} is exactly what I needed. Highly recommend!",
                    "I'm thoroughly impressed with this {product}. The fit is perfect and the material is high quality. The {feature} is exactly what I was looking for. I've worn it several times and it's very comfortable. The {specific_feature} is a nice detail. Great value for money and I'd definitely buy it again."
                ],
                'long': [
                    "I've been wearing this {product} for {weeks} weeks now and I can honestly say it's one of the best clothing purchases I've made. The fit is absolutely perfect - it's true to size and flattering. The material is high quality and feels comfortable against my skin. The {feature} is exactly what I was looking for and works perfectly. I particularly love how {specific_feature} because it {specific_benefit}. The attention to detail in the construction is impressive. I've received multiple compliments while wearing it. The {another_feature} is also excellent and adds real value. The fabric quality is outstanding and it has held up well through multiple washes. I would definitely recommend this to anyone looking for a high-quality {category}. It's worth every penny and I'm confident it will last for years to come.",
                    "After reading many reviews and comparing different options, I decided to go with this {product} and I'm so glad I did. The quality is exceptional and it has exceeded all my expectations. The fit is perfect and the material is comfortable and durable. The {feature} is exactly what I needed and works flawlessly. I've been wearing it for {time_period} and it still looks great. The {specific_feature} is particularly impressive - it {specific_benefit}. The design is stylish and versatile, fitting perfectly with my wardrobe. I also appreciate the attention to detail in the construction and finishing. The {another_feature} works seamlessly and adds real value. I've had no issues whatsoever and the quality has been consistent. The value for money is excellent - you get premium quality at a reasonable price. I would definitely recommend this to anyone looking for a high-quality {category}. It's a solid investment that I'm confident will serve me well for years to come."
                ]
            },
            'negative': {
                'short': [
                    "Poor fit. Not true to size.",
                    "Cheap material. Would not recommend.",
                    "This {product} doesn't fit well.",
                    "Disappointed with the quality.",
                    "Not worth the money.",
                    "Poor construction.",
                    "Doesn't look like the picture.",
                    "Uncomfortable to wear.",
                    "Regret buying this {product}.",
                    "Poor quality material."
                ],
                'medium': [
                    "I was disappointed with this {product}. The fit is not what I expected and the material feels cheap. The {feature} doesn't work as advertised. The sizing is off and it doesn't look like the picture. I've worn it a few times and it's already showing wear. The {specific_feature} is poorly made. I would not recommend this {product} to others.",
                    "This {product} is not what I expected. The quality is poor and the fit is uncomfortable. The {feature} doesn't work properly and the material feels flimsy. The construction is subpar and it doesn't look like the description. I've had issues with the {specific_feature} and it's not holding up well. I regret this purchase and would not buy it again.",
                    "I'm not satisfied with this {product}. The fit is wrong and the material is not what I expected. The {feature} is poorly designed and doesn't work as intended. The quality is not worth the price. I've worn it a few times and it's already falling apart. The {specific_feature} is not well made. I would recommend looking at other options before buying this {product}."
                ],
                'long': [
                    "I really wanted to love this {product} but unfortunately it has been a major disappointment. The fit is completely wrong - it's not true to size and doesn't look flattering at all. The material feels cheap and flimsy, not at all what I expected for the price. The {feature} that was advertised as a key selling point doesn't work as described. The construction is poor and it's already showing wear after just {weeks} weeks. The {specific_feature} is poorly made and doesn't hold up well. The sizing is completely off and it doesn't look anything like the picture. I've tried to make it work but it's just not comfortable to wear. The quality is not worth the money I spent. I would not recommend this {product} to anyone and I regret this purchase. I'm currently looking for alternatives that actually deliver on their promises.",
                    "This {product} has been nothing but trouble since I bought it. The fit is terrible and the material is not what I expected. The {feature} doesn't work properly and the construction is subpar. The sizing is completely wrong and it doesn't look like the description at all. I've had issues with the {specific_feature} and it's not holding up well. The quality is poor and it's already showing wear after minimal use. The material feels cheap and uncomfortable. I've tried to contact customer service but they've been unhelpful. For the amount of money I spent, I expected much better quality and fit. I would not recommend this {product} to anyone and I'm currently looking for a replacement. This has been a complete waste of money and I regret the purchase entirely."
                ]
            }
        },
        'Beauty': {
            'positive': {
                'short': [
                    "Love this {product}! Great quality.",
                    "Perfect {product}. Works great.",
                    "Excellent {product}! Highly recommend.",
                    "Amazing {product}. Worth the money.",
                    "Great {product}! Long lasting.",
                    "Perfect {product}! Easy to apply.",
                    "Love this {product}. Great pigmentation.",
                    "Excellent {product}! Great value.",
                    "Amazing {product}. Perfect shade.",
                    "Great {product}! Very satisfied."
                ],
                'medium': [
                    "I'm really impressed with this {product}! The quality is excellent and it works exactly as advertised. The {feature} is perfect and the application is smooth. I've been using it for {time_period} and it still works great. The {specific_feature} is exactly what I was looking for. The pigmentation is excellent and it lasts all day. Would definitely recommend to anyone looking for a quality {category}.",
                    "This {product} exceeded my expectations! The formula is great and it applies beautifully. I love the {feature} and how it {specific_benefit}. The quality is excellent for the price. I've been using it regularly and it's become a staple in my routine. The {specific_feature} is a nice touch. This is now one of my favorite {category} products.",
                    "Excellent {product}! The quality is outstanding and it works perfectly. The {feature} is exactly what I needed and the application is easy. I've been using it for {time_period} and it still performs great. The {specific_feature} is exactly what I was looking for. The pigmentation is excellent and it's very long-lasting. Highly recommend!",
                    "I'm thoroughly impressed with this {product}. The formula is great and it applies smoothly. The {feature} is exactly what I was looking for. I've been using it regularly and it's very effective. The {specific_feature} is a nice detail. Great value for money and I'd definitely buy it again."
                ],
                'long': [
                    "I've been using this {product} for {weeks} weeks now and I can honestly say it's one of the best beauty purchases I've made. The formula is excellent and it applies beautifully. The {feature} is exactly what I was looking for and works perfectly. I particularly love how {specific_feature} because it {specific_benefit}. The pigmentation is outstanding and it lasts all day without fading. The application is smooth and easy, and it blends perfectly. I've received multiple compliments while wearing it. The {another_feature} is also excellent and adds real value. The quality is outstanding and it has held up well through regular use. I would definitely recommend this to anyone looking for a high-quality {category}. It's worth every penny and I'm confident it will last for months to come.",
                    "After trying many different {category} products, I decided to go with this {product} and I'm so glad I did. The quality is exceptional and it has exceeded all my expectations. The formula is great and it applies beautifully. The {feature} is exactly what I needed and works flawlessly. I've been using it for {time_period} and it still performs great. The {specific_feature} is particularly impressive - it {specific_benefit}. The pigmentation is excellent and it's very long-lasting. The application is smooth and easy, and it blends perfectly with my skin tone. I also appreciate the attention to detail in the packaging and formula. The {another_feature} works seamlessly and adds real value. I've had no issues whatsoever and the quality has been consistent. The value for money is excellent - you get premium quality at a reasonable price. I would definitely recommend this to anyone looking for a high-quality {category}. It's a solid investment that I'm confident will serve me well for months to come."
                ]
            },
            'negative': {
                'short': [
                    "Poor quality. Doesn't work well.",
                    "Not worth the money.",
                    "This {product} doesn't work as advertised.",
                    "Disappointed with the quality.",
                    "Poor pigmentation.",
                    "Doesn't last long.",
                    "Not what I expected.",
                    "Regret buying this {product}.",
                    "Poor formula.",
                    "Not recommended."
                ],
                'medium': [
                    "I was disappointed with this {product}. The quality is not what I expected and it doesn't work as advertised. The {feature} doesn't work properly and the pigmentation is poor. The formula is not good and it doesn't last long. I've tried to make it work but it's just not effective. The {specific_feature} is poorly made. I would not recommend this {product} to others.",
                    "This {product} is not what I expected. The formula is poor and it doesn't apply well. The {feature} doesn't work as intended and the pigmentation is weak. The quality is not worth the price. I've had issues with the {specific_feature} and it's not holding up well. I regret this purchase and would not buy it again.",
                    "I'm not satisfied with this {product}. The formula is not good and it doesn't work as advertised. The {feature} is poorly designed and doesn't work properly. The pigmentation is weak and it doesn't last long. I've tried to make it work but it's just not effective. The {specific_feature} is not well made. I would recommend looking at other options before buying this {product}."
                ],
                'long': [
                    "I really wanted to love this {product} but unfortunately it has been a major disappointment. The formula is not good and it doesn't apply well. The {feature} that was advertised as a key selling point doesn't work as described. The pigmentation is weak and it doesn't last long. The quality is not what I expected for the price. I've tried to make it work but it's just not effective. The {specific_feature} is poorly made and doesn't hold up well. The application is difficult and it doesn't blend well. I've had issues with the formula and it's not performing as advertised. The quality is not worth the money I spent. I would not recommend this {product} to anyone and I regret this purchase. I'm currently looking for alternatives that actually deliver on their promises.",
                    "This {product} has been nothing but trouble since I bought it. The formula is poor and it doesn't work properly. The {feature} doesn't work as intended and the pigmentation is weak. The quality is not what I expected and it's not performing well. I've had issues with the {specific_feature} and it's not holding up well. The application is difficult and it doesn't blend well. The formula is not good and it doesn't last long. I've tried to contact customer service but they've been unhelpful. For the amount of money I spent, I expected much better quality and performance. I would not recommend this {product} to anyone and I'm currently looking for a replacement. This has been a complete waste of money and I regret the purchase entirely."
                ]
        }
    }
    
    # Add more categories with similar structure
    # For now, let's use Electronics as the base and expand later
    
    # Determine sentiment and length
    sentiment = 'positive' if rating >= 4.0 else 'negative'
    length = metadata['review_length']
    
    # Get templates for the category and sentiment
    templates = enhanced_templates.get(category, enhanced_templates['Electronics'])
    template_list = templates.get(sentiment, templates['positive'])
    length_templates = template_list.get(length, template_list['medium'])
    
    # Select a random template
    template = random.choice(length_templates)
    
    # Generate realistic details to fill in template placeholders
    weeks = random.randint(1, 12)
    time_period = random.choice([f"{weeks} weeks", f"{random.randint(1, 3)} months", "several months"])
    
    # Category-specific features
    feature_options = {
        'Electronics': ['battery life', 'connectivity', 'user interface', 'performance', 'speed', 'reliability'],
        'Clothing': ['fit', 'fabric quality', 'comfort', 'style', 'durability', 'washing'],
        'Beauty': ['application', 'longevity', 'pigmentation', 'texture', 'packaging', 'effectiveness'],
        'Home': ['assembly', 'durability', 'functionality', 'design', 'materials', 'ease of use'],
        'Toys': ['safety', 'educational value', 'durability', 'age appropriateness', 'fun factor', 'quality']
    }
    
    features = feature_options.get(category, feature_options['Electronics'])
    feature = random.choice(features)
    specific_feature = random.choice(features)
    another_feature = random.choice([f for f in features if f != feature and f != specific_feature])
    
    # Generate specific benefits
    benefits = [
        "saves me time every day",
        "works exactly as I need it to",
        "has exceeded my expectations",
        "is incredibly user-friendly",
        "provides excellent value",
        "is built to last",
        "makes my life easier",
        "is worth every penny"
    ]
    specific_benefit = random.choice(benefits)
    
    # Fill in the template
    review_text = template.format(
        product=product_name,
        weeks=weeks,
        time_period=time_period,
        feature=feature,
        specific_feature=specific_feature,
        another_feature=another_feature,
        specific_benefit=specific_benefit,
        category=category.lower()
    )
    
    # Add personal touches based on experience level
    if metadata['experience_level'] == 'expert':
        expert_additions = [
            " As someone who has tried many similar products, this one stands out.",
            " I've been in this field for years and this is quality work.",
            " Coming from a technical background, I appreciate the attention to detail.",
            " Having used many {category} products, this is among the best."
        ]
        if random.random() < 0.3:  # 30% chance to add expert context
            review_text += random.choice(expert_additions)
    
    # Add verified purchase context
    if metadata['verified_purchase']:
        verified_additions = [
            " Ordered this directly from the manufacturer and received it quickly.",
            " Fast shipping and arrived exactly as described.",
            " Purchased this item and it arrived in perfect condition.",
            " Bought this item and the packaging was excellent."
        ]
        if random.random() < 0.2:  # 20% chance to add verified context
            review_text += random.choice(verified_additions)
    
    return {
        'review_text': review_text,
        'helpful_votes': metadata['helpful_votes'],
        'verified_purchase': metadata['verified_purchase'],
        'has_images': metadata['has_images'],
        'image_count': metadata['image_count'],
        'experience_level': metadata['experience_level']
    }

def generate_realistic_email(name):
    """Generate a realistic email based on the user's actual name or random patterns."""
    
    # Common email domains
    domains = ['gmail.com', 'yahoo.com', 'hotmail.com', 'outlook.com', 'aol.com', 
               'icloud.com', 'protonmail.com', 'live.com', 'msn.com', 'comcast.net',
               'verizon.net', 'att.net', 'sbcglobal.net', 'bellsouth.net']
    
    # Split the name into parts
    name_parts = name.lower().split()
    first_name = name_parts[0] if name_parts else 'user'
    last_name = name_parts[-1] if len(name_parts) > 1 else ''
    
    # Random creative patterns (60% of emails)
    creative_patterns = [
        # Sports teams and interests
        lambda: f"{random.choice(['cowboys', 'patriots', 'lakers', 'warriors', 'yankees', 'dodgers', 'packers', 'steelers', 'bulls', 'heat'])}fan{random.randint(1, 99)}",
        lambda: f"{random.choice(['football', 'basketball', 'baseball', 'soccer', 'hockey', 'tennis', 'golf', 'boxing', 'mma', 'racing'])}lover{random.randint(10, 99)}",
        lambda: f"{random.choice(['game', 'gamer', 'player', 'pro', 'master', 'king', 'queen', 'legend', 'hero', 'champ'])}{random.randint(1, 999)}",
        
        # Colors and numbers
        lambda: f"{random.choice(['red', 'blue', 'green', 'purple', 'orange', 'yellow', 'pink', 'black', 'white', 'silver'])}{random.randint(1, 999)}",
        lambda: f"{random.choice(['cool', 'hot', 'fire', 'ice', 'storm', 'thunder', 'lightning', 'shadow', 'moon', 'star'])}{random.randint(10, 99)}",
        
        # Hobbies and interests
        lambda: f"{random.choice(['music', 'artist', 'singer', 'dancer', 'writer', 'reader', 'bookworm', 'poet', 'actor', 'director'])}{random.randint(1, 99)}",
        lambda: f"{random.choice(['tech', 'geek', 'nerd', 'hacker', 'coder', 'developer', 'engineer', 'scientist', 'inventor', 'creator'])}{random.randint(10, 99)}",
        lambda: f"{random.choice(['travel', 'adventure', 'explorer', 'wanderer', 'nomad', 'pilot', 'captain', 'sailor', 'driver', 'rider'])}{random.randint(1, 99)}",
        
        # Animals and nature
        lambda: f"{random.choice(['cat', 'dog', 'tiger', 'lion', 'eagle', 'wolf', 'bear', 'fox', 'owl', 'dragon'])}{random.randint(1, 999)}",
        lambda: f"{random.choice(['mountain', 'river', 'ocean', 'forest', 'desert', 'valley', 'canyon', 'peak', 'lake', 'island'])}{random.randint(10, 99)}",
        
        # Food and drinks
        lambda: f"{random.choice(['pizza', 'burger', 'coffee', 'tea', 'beer', 'wine', 'chocolate', 'candy', 'sweet', 'spicy'])}{random.randint(1, 99)}",
        
        # Random combinations
        lambda: f"{random.choice(['playstation', 'xbox', 'nintendo', 'steam', 'epic', 'blizzard', 'riot', 'valve', 'ubisoft', 'ea'])}lover{random.randint(1, 99)}",
        lambda: f"{random.choice(['marvel', 'dc', 'disney', 'pixar', 'netflix', 'hulu', 'amazon', 'google', 'apple', 'microsoft'])}fan{random.randint(10, 99)}",
        lambda: f"{random.choice(['rock', 'metal', 'pop', 'jazz', 'blues', 'country', 'rap', 'hiphop', 'electronic', 'classical'])}{random.randint(1, 99)}",
        
        # Abstract concepts
        lambda: f"{random.choice(['dream', 'hope', 'love', 'peace', 'joy', 'happy', 'smile', 'laugh', 'fun', 'magic'])}{random.randint(1, 999)}",
        lambda: f"{random.choice(['night', 'day', 'sun', 'moon', 'sky', 'cloud', 'rain', 'snow', 'wind', 'fire'])}{random.randint(10, 99)}",
        
        # Random words with numbers
        lambda: f"{random.choice(['alpha', 'beta', 'gamma', 'delta', 'omega', 'sigma', 'theta', 'phi', 'psi', 'lambda'])}{random.randint(1, 99)}",
        lambda: f"{random.choice(['nova', 'cosmos', 'galaxy', 'planet', 'comet', 'asteroid', 'meteor', 'satellite', 'orbit', 'space'])}{random.randint(10, 99)}",
        
        # Gaming and tech terms
        lambda: f"{random.choice(['noob', 'pro', 'elite', 'veteran', 'rookie', 'expert', 'genius', 'wizard', 'ninja', 'samurai'])}{random.randint(1, 999)}",
        lambda: f"{random.choice(['cyber', 'digital', 'virtual', 'online', 'internet', 'web', 'net', 'data', 'code', 'byte'])}{random.randint(10, 99)}",
        
        # Year-based patterns
        lambda: f"{random.choice(['retro', 'vintage', 'classic', 'modern', 'future', 'new', 'old', 'ancient', 'timeless', 'eternal'])}{random.randint(1980, 2025)}",
        
        # Random combinations
        lambda: f"{random.choice(['super', 'mega', 'ultra', 'hyper', 'turbo', 'max', 'extreme', 'ultimate', 'supreme', 'epic'])}{random.choice(['man', 'woman', 'guy', 'girl', 'dude', 'bro', 'sis', 'kid', 'teen', 'adult'])}{random.randint(1, 99)}"
    ]
    
    # Name-based patterns (40% of emails)
    name_patterns = [
        # Pattern 1: firstname.lastname (15%)
        lambda: f"{first_name}.{last_name}",
        # Pattern 2: firstname_lastname (8%)
        lambda: f"{first_name}_{last_name}",
        # Pattern 3: firstname + lastname (7%)
        lambda: f"{first_name}{last_name}",
        # Pattern 4: first initial + lastname (5%)
        lambda: f"{first_name[0]}{last_name}",
        # Pattern 5: firstname + last initial (3%)
        lambda: f"{first_name}{last_name[0] if last_name else ''}",
        # Pattern 6: firstname + numbers (2%)
        lambda: f"{first_name}{random.randint(1, 999)}"
    ]
    
    # Choose between creative (60%) and name-based (40%) patterns
    if random.random() < 0.6:
        # Use creative patterns
        selected_pattern = random.choice(creative_patterns)
        email_prefix = selected_pattern()
    else:
        # Use name-based patterns
        pattern_weights = [15, 8, 7, 5, 3, 2]
        selected_pattern = random.choices(name_patterns, weights=pattern_weights)[0]
        email_prefix = selected_pattern()
    
    # Clean up the email prefix (remove any spaces, special chars)
    email_prefix = ''.join(c for c in email_prefix if c.isalnum() or c in '._-')
    
    # Select a random domain
    domain = random.choice(domains)
    
    return f"{email_prefix}@{domain}"

def generate_realistic_products(num_products):
    """Generate realistic e-commerce products with proper names, brands, and details."""
    
    # Define product categories with realistic subcategories and brands
    product_data = {
        'Electronics': {
            'subcategories': ['Smartphones', 'Laptops', 'Tablets', 'Headphones', 'Cameras', 'Gaming', 'Smart Home', 'Accessories'],
            'brands': ['Apple', 'Samsung', 'Sony', 'Bose', 'Canon', 'Nintendo', 'Google', 'Microsoft', 'Dell', 'HP', 'Lenovo', 'OnePlus', 'Xiaomi', 'Logitech', 'JBL'],
            'price_ranges': [(50, 1500), (200, 3000), (100, 800), (20, 500), (200, 2000), (30, 600), (30, 400), (5, 200)],
            'names': {
                'Smartphones': ['iPhone 15 Pro', 'Samsung Galaxy S24', 'Google Pixel 8', 'OnePlus 12', 'iPhone 14', 'Samsung Galaxy A54'],
                'Laptops': ['MacBook Pro 16"', 'Dell XPS 13', 'HP Spectre x360', 'Lenovo ThinkPad X1', 'MacBook Air M2', 'ASUS ROG Strix'],
                'Tablets': ['iPad Pro 12.9"', 'Samsung Galaxy Tab S9', 'iPad Air', 'Microsoft Surface Pro', 'iPad mini', 'Amazon Fire HD'],
                'Headphones': ['AirPods Pro', 'Sony WH-1000XM5', 'Bose QuietComfort 45', 'Beats Studio3', 'Sennheiser HD 660S', 'JBL Live Pro 2'],
                'Cameras': ['Canon EOS R5', 'Sony A7 IV', 'Nikon Z6 II', 'Canon PowerShot G7X', 'Fujifilm X-T5', 'GoPro Hero 12'],
                'Gaming': ['PlayStation 5', 'Xbox Series X', 'Nintendo Switch OLED', 'Steam Deck', 'Gaming PC RTX 4080', 'Razer Blade 15'],
                'Smart Home': ['Amazon Echo Dot', 'Google Nest Hub', 'Ring Video Doorbell', 'Philips Hue Starter Kit', 'Nest Thermostat', 'Arlo Pro 4'],
                'Accessories': ['Lightning Cable', 'USB-C Hub', 'Wireless Charger', 'Phone Case', 'Screen Protector', 'Bluetooth Speaker']
            }
        },
        'Clothing': {
            'subcategories': ['Tops', 'Bottoms', 'Dresses', 'Outerwear', 'Shoes', 'Accessories', 'Underwear', 'Activewear'],
            'brands': ['Nike', 'Adidas', 'Zara', 'H&M', 'Uniqlo', 'Levi\'s', 'Gap', 'Calvin Klein', 'Tommy Hilfiger', 'Ralph Lauren', 'Champion', 'Puma', 'Under Armour', 'Lululemon', 'Patagonia'],
            'price_ranges': [(15, 80), (25, 120), (30, 150), (50, 300), (40, 200), (10, 50), (8, 40), (20, 100)],
            'names': {
                'Tops': ['Classic T-Shirt', 'Polo Shirt', 'Blouse', 'Tank Top', 'Hoodie', 'Sweater', 'Button-Down Shirt', 'Crop Top'],
                'Bottoms': ['Jeans', 'Chinos', 'Shorts', 'Leggings', 'Trousers', 'Skirt', 'Cargo Pants', 'Joggers'],
                'Dresses': ['Summer Dress', 'Cocktail Dress', 'Maxi Dress', 'Midi Dress', 'Wrap Dress', 'Shift Dress', 'Bodycon Dress', 'A-Line Dress'],
                'Outerwear': ['Denim Jacket', 'Leather Jacket', 'Blazer', 'Coat', 'Cardigan', 'Windbreaker', 'Bomber Jacket', 'Trench Coat'],
                'Shoes': ['Sneakers', 'Boots', 'Sandals', 'Heels', 'Loafers', 'Running Shoes', 'Dress Shoes', 'Flip Flops'],
                'Accessories': ['Handbag', 'Backpack', 'Belt', 'Scarf', 'Hat', 'Sunglasses', 'Watch', 'Jewelry Set'],
                'Underwear': ['Bra Set', 'Underwear Pack', 'Socks', 'Boxers', 'Bikini', 'Lingerie Set', 'Thermal Underwear', 'Shapewear'],
                'Activewear': ['Yoga Pants', 'Sports Bra', 'Running Shorts', 'Gym Tank', 'Athletic Leggings', 'Workout Hoodie', 'Compression Shirt', 'Swimwear']
            }
        },
        'Beauty': {
            'subcategories': ['Skincare', 'Makeup', 'Fragrance', 'Hair Care', 'Body Care', 'Tools', 'Men\'s Grooming', 'Nail Care'],
            'brands': ['L\'Oréal', 'Maybelline', 'Revlon', 'MAC', 'Urban Decay', 'Too Faced', 'Fenty Beauty', 'Glossier', 'The Ordinary', 'CeraVe', 'Olay', 'Neutrogena', 'Clinique', 'Estée Lauder', 'Chanel'],
            'price_ranges': [(8, 50), (5, 80), (20, 200), (10, 60), (5, 40), (3, 30), (5, 50), (3, 25)],
            'names': {
                'Skincare': ['Moisturizer', 'Cleanser', 'Serum', 'Sunscreen', 'Toner', 'Face Mask', 'Eye Cream', 'Exfoliant'],
                'Makeup': ['Foundation', 'Concealer', 'Lipstick', 'Mascara', 'Eyeshadow Palette', 'Blush', 'Highlighter', 'Setting Powder'],
                'Fragrance': ['Eau de Parfum', 'Body Spray', 'Cologne', 'Perfume Gift Set', 'Rollerball', 'Travel Size', 'Solid Perfume', 'Room Spray'],
                'Hair Care': ['Shampoo', 'Conditioner', 'Hair Mask', 'Hair Oil', 'Dry Shampoo', 'Hair Serum', 'Heat Protectant', 'Hair Dye'],
                'Body Care': ['Body Lotion', 'Body Wash', 'Body Scrub', 'Hand Cream', 'Foot Cream', 'Deodorant', 'Body Butter', 'Bath Bombs'],
                'Tools': ['Makeup Brushes', 'Beauty Blender', 'Hair Dryer', 'Curling Iron', 'Tweezers', 'Nail Clippers', 'Mirror', 'Makeup Organizer'],
                'Men\'s Grooming': ['Face Wash', 'Aftershave', 'Beard Oil', 'Razor', 'Shaving Cream', 'Cologne', 'Hair Pomade', 'Face Moisturizer'],
                'Nail Care': ['Nail Polish', 'Base Coat', 'Top Coat', 'Nail Art Kit', 'Nail File', 'Cuticle Oil', 'Nail Strengthener', 'Gel Polish']
            }
        },
        'Home': {
            'subcategories': ['Furniture', 'Decor', 'Kitchen', 'Bedding', 'Bath', 'Storage', 'Lighting', 'Garden'],
            'brands': ['IKEA', 'West Elm', 'Pottery Barn', 'Crate & Barrel', 'Target', 'Wayfair', 'Amazon Basics', 'Dyson', 'KitchenAid', 'Instant Pot', 'Nespresso', 'Philips', 'Honeywell', 'Bissell', 'Shark'],
            'price_ranges': [(50, 800), (20, 200), (30, 500), (25, 300), (15, 150), (20, 200), (25, 300), (30, 400)],
            'names': {
                'Furniture': ['Dining Table', 'Sofa', 'Bed Frame', 'Bookshelf', 'Coffee Table', 'Dresser', 'Office Chair', 'Nightstand'],
                'Decor': ['Wall Art', 'Throw Pillows', 'Vases', 'Candles', 'Mirrors', 'Plants', 'Rugs', 'Picture Frames'],
                'Kitchen': ['Coffee Maker', 'Blender', 'Air Fryer', 'Dinnerware Set', 'Cookware Set', 'Knife Set', 'Cutting Board', 'Food Storage'],
                'Bedding': ['Sheet Set', 'Comforter', 'Pillows', 'Duvet Cover', 'Mattress Topper', 'Throw Blanket', 'Bed Skirt', 'Pillow Cases'],
                'Bath': ['Towel Set', 'Bath Mat', 'Shower Curtain', 'Toothbrush Holder', 'Soap Dispenser', 'Bath Caddy', 'Scale', 'Bath Bombs'],
                'Storage': ['Storage Bins', 'Closet Organizer', 'Shoe Rack', 'Laundry Hamper', 'Jewelry Box', 'File Organizer', 'Under Bed Storage', 'Pantry Organizer'],
                'Lighting': ['Table Lamp', 'Floor Lamp', 'Pendant Light', 'String Lights', 'LED Strip', 'Desk Lamp', 'Chandelier', 'Night Light'],
                'Garden': ['Plant Pots', 'Garden Tools', 'Outdoor Furniture', 'Plant Stand', 'Garden Hose', 'Plant Food', 'Seeds', 'Garden Decor']
            }
        },
        'Sports': {
            'subcategories': ['Fitness', 'Outdoor', 'Team Sports', 'Water Sports', 'Winter Sports', 'Cycling', 'Running', 'Yoga'],
            'brands': ['Nike', 'Adidas', 'Under Armour', 'Puma', 'Reebok', 'New Balance', 'ASICS', 'Brooks', 'Wilson', 'Spalding', 'Coleman', 'Yeti', 'Patagonia', 'North Face', 'Columbia'],
            'price_ranges': [(20, 200), (30, 300), (15, 150), (25, 250), (40, 400), (50, 500), (25, 200), (15, 100)],
            'names': {
                'Fitness': ['Dumbbells', 'Resistance Bands', 'Yoga Mat', 'Jump Rope', 'Kettlebell', 'Foam Roller', 'Pull-Up Bar', 'Weight Bench'],
                'Outdoor': ['Tent', 'Sleeping Bag', 'Backpack', 'Hiking Boots', 'Camping Chair', 'Cooler', 'Headlamp', 'Water Bottle'],
                'Team Sports': ['Basketball', 'Soccer Ball', 'Tennis Racket', 'Baseball Glove', 'Volleyball', 'Hockey Stick', 'Golf Clubs', 'Football'],
                'Water Sports': ['Swim Goggles', 'Swim Cap', 'Water Bottle', 'Pool Noodle', 'Swim Fins', 'Snorkel Set', 'Beach Towel', 'Water Shoes'],
                'Winter Sports': ['Ski Goggles', 'Ski Gloves', 'Thermal Base Layer', 'Ski Socks', 'Hand Warmers', 'Ski Helmet', 'Ski Jacket', 'Ski Pants'],
                'Cycling': ['Bike Helmet', 'Bike Lights', 'Water Bottle Cage', 'Bike Lock', 'Bike Pump', 'Cycling Shorts', 'Bike Computer', 'Bike Rack'],
                'Running': ['Running Shoes', 'Running Shorts', 'Running Watch', 'Hydration Belt', 'Reflective Vest', 'Running Hat', 'Compression Socks', 'GPS Watch'],
                'Yoga': ['Yoga Mat', 'Yoga Blocks', 'Yoga Strap', 'Meditation Cushion', 'Yoga Towel', 'Yoga Bolster', 'Yoga Wheel', 'Yoga Blanket']
            }
        },
        'Toys': {
            'subcategories': ['Action Figures', 'Dolls', 'Building Sets', 'Board Games', 'Puzzles', 'Educational', 'Outdoor', 'Electronic'],
            'brands': ['LEGO', 'Mattel', 'Hasbro', 'Fisher-Price', 'Melissa & Doug', 'VTech', 'Playmobil', 'Hot Wheels', 'Barbie', 'Nerf', 'Monopoly', 'Paw Patrol', 'Disney', 'Marvel', 'Star Wars'],
            'price_ranges': [(10, 100), (15, 80), (20, 200), (25, 150), (8, 50), (15, 120), (20, 150), (30, 300)],
            'names': {
                'Action Figures': ['Superhero Figure', 'Action Figure Set', 'Collectible Figure', 'Transformers', 'Power Rangers', 'Ninja Turtles', 'Avengers Figure', 'Star Wars Figure'],
                'Dolls': ['Fashion Doll', 'Baby Doll', 'Doll House', 'Doll Accessories', 'Princess Doll', 'Barbie Set', 'American Girl Doll', 'Doll Stroller'],
                'Building Sets': ['LEGO Set', 'Building Blocks', 'Magnetic Tiles', 'Construction Set', 'Marble Run', 'K\'NEX Set', 'Mega Bloks', 'Architectural Set'],
                'Board Games': ['Monopoly', 'Scrabble', 'Chess Set', 'Checkers', 'Uno', 'Candy Land', 'Chutes and Ladders', 'Connect 4'],
                'Puzzles': ['Jigsaw Puzzle', '3D Puzzle', 'Wooden Puzzle', 'Educational Puzzle', 'Floor Puzzle', 'Brain Teaser', 'Crossword Puzzle', 'Word Search'],
                'Educational': ['Learning Tablet', 'Science Kit', 'Art Supplies', 'Musical Instrument', 'Language Learning', 'Math Games', 'Coding Robot', 'Microscope'],
                'Outdoor': ['Trampoline', 'Swing Set', 'Sandbox', 'Bike', 'Scooter', 'Skateboard', 'Jump Rope', 'Hula Hoop'],
                'Electronic': ['RC Car', 'Drone', 'Electronic Game', 'Robot Kit', 'Walkie Talkies', 'Electronic Keyboard', 'Gaming Console', 'Virtual Reality Set']
            }
        }
    }
    
    # Colors and sizes for product variations
    colors = ['Black', 'White', 'Red', 'Blue', 'Green', 'Yellow', 'Pink', 'Purple', 'Gray', 'Brown', 'Orange', 'Navy', 'Beige', 'Silver', 'Gold']
    sizes = ['XS', 'S', 'M', 'L', 'XL', 'XXL', 'One Size', 'Small', 'Medium', 'Large', 'Extra Large']
    
    products = []
    
    for i in range(num_products):
        # Select category
        category = random.choice(list(product_data.keys()))
        category_info = product_data[category]
        
        # Select subcategory
        subcategory = random.choice(category_info['subcategories'])
        subcategory_idx = category_info['subcategories'].index(subcategory)
        
        # Select brand
        brand = random.choice(category_info['brands'])
        
        # Generate product name
        if subcategory in category_info['names']:
            base_name = random.choice(category_info['names'][subcategory])
        else:
            base_name = f"{subcategory} Item"
        
        # Add brand to name (sometimes)
        if random.random() < 0.7:  # 70% chance to include brand
            product_name = f"{brand} {base_name}"
        else:
            product_name = base_name
        
        # Add color variation (sometimes)
        if random.random() < 0.4:  # 40% chance to add color
            color = random.choice(colors)
            product_name = f"{product_name} - {color}"
        
        # Add size variation for clothing
        if category == 'Clothing' and random.random() < 0.6:  # 60% chance for clothing
            size = random.choice(sizes)
            product_name = f"{product_name} ({size})"
        
        # Generate SKU
        sku = f"{brand[:3].upper()}{random.randint(1000, 9999)}{random.choice(['A', 'B', 'C', 'D'])}"
        
        # Generate price based on category and brand
        price_range = category_info['price_ranges'][subcategory_idx]
        base_price = random.uniform(price_range[0], price_range[1])
        
        # Add brand premium
        premium_brands = ['Apple', 'Samsung', 'Nike', 'Adidas', 'Dyson', 'KitchenAid', 'LEGO', 'Mattel', 'Hasbro']
        if brand in premium_brands:
            base_price *= random.uniform(1.2, 1.8)
        
        price = round(base_price, 2)
        
        # Generate stock quantity based on product type and popularity
        if category in ['Electronics', 'Clothing'] and random.random() < 0.3:  # 30% chance for high-demand items
            stock = random.randint(200, 1000)
        elif category in ['Beauty', 'Toys'] and random.random() < 0.2:  # 20% chance for popular items
            stock = random.randint(100, 500)
        elif random.random() < 0.1:  # 10% chance for out of stock
            stock = 0
        else:
            stock = random.randint(5, 200)
        
        # Generate rating and review count
        if random.random() < 0.15:  # 15% chance for new products with no reviews
            rating = 0.0
            review_count = 0
        else:
            # Realistic rating distribution
            rating = np.clip(np.random.normal(4.2, 0.6), 1.0, 5.0)
            rating = round(rating, 1)
            
            # Review count based on rating and stock
            if rating >= 4.5:
                review_count = random.randint(50, 500)
            elif rating >= 4.0:
                review_count = random.randint(20, 200)
            elif rating >= 3.0:
                review_count = random.randint(5, 100)
            else:
                review_count = random.randint(1, 50)
        
        # Generate description
        description = generate_product_description(category, subcategory, product_name, brand)
        
        # Generate realistic weight based on category and product type
        if category == 'Electronics':
            if 'Software' in product_name or 'App' in product_name or 'Digital' in product_name:
                weight = 0.0  # Digital products have no weight
            elif 'Smartphone' in product_name or 'Phone' in product_name:
                weight = round(random.uniform(0.15, 0.25), 2)  # 150-250g
            elif 'Laptop' in product_name or 'MacBook' in product_name:
                weight = round(random.uniform(1.2, 2.5), 2)  # 1.2-2.5kg
            elif 'Tablet' in product_name or 'iPad' in product_name:
                weight = round(random.uniform(0.4, 0.8), 2)  # 400-800g
            elif 'Headphones' in product_name or 'AirPods' in product_name:
                weight = round(random.uniform(0.2, 0.4), 2)  # 200-400g
            else:
                weight = round(random.uniform(0.1, 2.0), 2)  # General electronics
        elif category == 'Clothing':
            if 'Dress' in product_name:
                weight = round(random.uniform(0.3, 0.8), 2)  # 300-800g
            elif 'Jacket' in product_name or 'Coat' in product_name:
                weight = round(random.uniform(0.8, 1.5), 2)  # 800g-1.5kg
            elif 'Shoes' in product_name:
                weight = round(random.uniform(0.5, 1.2), 2)  # 500g-1.2kg
            else:
                weight = round(random.uniform(0.1, 0.6), 2)  # General clothing
        elif category == 'Beauty':
            if 'Tweezers' in product_name or 'Tools' in subcategory:
                weight = round(random.uniform(0.01, 0.1), 2)  # Very light tools
            else:
                weight = round(random.uniform(0.1, 0.5), 2)  # General beauty products
        elif category == 'Home':
            if 'Furniture' in subcategory:
                weight = round(random.uniform(5.0, 50.0), 2)  # Heavy furniture
            elif 'Towel' in product_name:
                weight = round(random.uniform(0.3, 0.8), 2)  # Towels
            else:
                weight = round(random.uniform(0.2, 3.0), 2)  # General home items
        elif category == 'Sports':
            if 'Pool' in product_name or 'Noodle' in product_name:
                weight = round(random.uniform(0.2, 0.5), 2)  # Light sports items
            else:
                weight = round(random.uniform(0.5, 5.0), 2)  # General sports equipment
        elif category == 'Toys':
            weight = round(random.uniform(0.2, 2.0), 2)  # General toys
        else:
            weight = round(random.uniform(0.1, 2.0), 2)  # Default
        
        # Generate realistic dimensions based on weight and category
        if weight == 0.0:  # Digital products
            dimensions = "N/A"
        elif weight < 0.5:
            dimensions = f"{random.randint(5, 15)}x{random.randint(5, 15)}x{random.randint(2, 8)} cm"
        elif weight < 2.0:
            dimensions = f"{random.randint(10, 30)}x{random.randint(10, 30)}x{random.randint(5, 15)} cm"
        else:
            dimensions = f"{random.randint(20, 60)}x{random.randint(20, 60)}x{random.randint(10, 30)} cm"
        
        color = random.choice(colors) if random.random() < 0.8 else 'Various'
        size = random.choice(sizes) if category == 'Clothing' and random.random() < 0.7 else 'One Size'
        
        # Determine if product is featured or digital
        is_featured = random.random() < 0.1  # 10% chance
        
        # Only digital products should be marked as digital
        digital_keywords = ['Software', 'App', 'Digital', 'Download', 'E-book', 'Ebook', 'MP3', 'Video', 'Streaming']
        is_digital = any(keyword in product_name for keyword in digital_keywords) or weight == 0.0
        
        # Realistic shipping class based on weight and category
        if is_digital or weight == 0.0:
            shipping_class = 'Digital'
        elif weight > 10 or category in ['Furniture']:
            shipping_class = 'Heavy'
        elif weight > 2 or category in ['Sports', 'Home'] and 'Furniture' in subcategory:
            shipping_class = 'Standard'
        else:
            shipping_class = 'Light'
        
        product = {
            'product_id': i + 1,
            'sku': sku,
            'name': product_name,
            'brand': brand,
            'category': category,
            'subcategory': subcategory,
            'price': price,
            'description': description,
            'weight': weight,
            'dimensions': dimensions,
            'color': color,
            'size': size,
            'stock_quantity': stock,
            'rating': rating,
            'review_count': review_count,
            'is_featured': is_featured,
            'is_digital': is_digital,
            'shipping_class': shipping_class
        }
        
        products.append(product)
    
    return pd.DataFrame(products)

def generate_product_description(category, subcategory, product_name, brand):
    """Generate a realistic product description."""
    
    descriptions = {
        'Electronics': {
            'Smartphones': [
                f"Experience cutting-edge technology with the {product_name}. Features advanced camera system, all-day battery life, and premium design.",
                f"The {product_name} delivers exceptional performance with its powerful processor and stunning display. Perfect for work and play.",
                f"Discover the future of mobile technology with the {product_name}. Sleek design meets powerful functionality."
            ],
            'Laptops': [
                f"Power through your workday with the {product_name}. High-performance processor, stunning display, and all-day battery life.",
                f"The {product_name} combines portability with power. Perfect for professionals and students alike.",
                f"Experience premium computing with the {product_name}. Built for productivity and creativity."
            ],
            'Headphones': [
                f"Immerse yourself in crystal-clear audio with the {product_name}. Superior sound quality and comfortable fit.",
                f"The {product_name} delivers studio-quality sound with active noise cancellation and wireless convenience.",
                f"Enjoy your music like never before with the {product_name}. Premium audio experience for every listener."
            ]
        },
        'Clothing': {
            'Tops': [
                f"Stay comfortable and stylish with the {product_name}. Made from premium materials for lasting quality.",
                f"The {product_name} offers the perfect blend of comfort and style. Versatile design for any occasion.",
                f"Elevate your wardrobe with the {product_name}. Classic design meets modern comfort."
            ],
            'Shoes': [
                f"Step out in style with the {product_name}. Comfortable fit and durable construction for everyday wear.",
                f"The {product_name} combines fashion and function. Perfect for any outfit and occasion.",
                f"Experience comfort and style with the {product_name}. Designed for the modern lifestyle."
            ]
        },
        'Beauty': {
            'Skincare': [
                f"Nourish your skin with the {product_name}. Formulated with premium ingredients for visible results.",
                f"The {product_name} delivers professional-quality skincare at home. Gentle yet effective formula.",
                f"Transform your skincare routine with the {product_name}. Clinically tested and dermatologist recommended."
            ],
            'Makeup': [
                f"Enhance your natural beauty with the {product_name}. Long-lasting formula with stunning color payoff.",
                f"The {product_name} offers professional-quality makeup for everyday wear. Easy to apply and blend.",
                f"Create flawless looks with the {product_name}. High-pigment formula for bold, beautiful results."
            ]
        }
    }
    
    # Get category-specific descriptions
    if category in descriptions and subcategory in descriptions[category]:
        return random.choice(descriptions[category][subcategory])
    
    # Generic descriptions
    generic_descriptions = [
        f"High-quality {subcategory.lower()} from {brand}. Designed for durability and performance.",
        f"The {product_name} delivers exceptional value and quality. Perfect for everyday use.",
        f"Experience the difference with the {product_name}. Premium materials and expert craftsmanship.",
        f"Discover why the {product_name} is a customer favorite. Reliable, stylish, and affordable.",
        f"The {product_name} combines form and function for the perfect addition to your collection."
    ]
    
    return random.choice(generic_descriptions)

def generate_enhanced_orders(num_orders, user_ids, order_times, products_df, users_df):
    """Generate orders with realistic business context."""
    
    orders = []
    
    for i in range(num_orders):
        order_id = i + 1
        user_id = user_ids[i]
        order_time = order_times[i]
        
        # Determine order source based on realistic patterns
        order_sources = ['web', 'mobile_app', 'mobile_web', 'api']
        source_weights = [0.45, 0.30, 0.20, 0.05]  # Web dominant, mobile growing
        order_source = np.random.choice(order_sources, p=source_weights)
        
        # Order value with realistic distribution
        order_value = np.random.lognormal(mean=4.5, sigma=0.8)  # Log-normal distribution
        order_value = max(10, min(2000, order_value))  # Clamp between $10-$2000
        
        # Payment method based on order value and customer behavior
        if order_value > 200:
            payment_methods = ['credit_card', 'paypal', 'apple_pay', 'google_pay']
            payment_weights = [0.60, 0.25, 0.10, 0.05]
        else:
            payment_methods = ['credit_card', 'debit_card', 'paypal', 'apple_pay']
            payment_weights = [0.50, 0.25, 0.15, 0.10]
        
        payment_method = np.random.choice(payment_methods, p=payment_weights)
        
        # Order status with realistic business logic
        status = determine_realistic_order_status(order_time, order_value, user_id)
        
        # Shipping method based on order value and urgency
        shipping_method = determine_shipping_method(order_value, order_time)
        
        # Promotional code usage (15% of orders)
        promo_code = None
        if random.random() < 0.15:
            promo_codes = ['WELCOME10', 'SAVE20', 'FREESHIP', 'HOLIDAY15', 'NEWUSER', 'SUMMER25']
            promo_code = random.choice(promo_codes)
        
        # Geographic patterns
        timezone_weights = {
            'EST': 0.35,    # East Coast (most populous)
            'CST': 0.25,    # Central
            'MST': 0.15,    # Mountain
            'PST': 0.20,    # West Coast
            'Other': 0.05   # International
        }
        timezone = np.random.choice(list(timezone_weights.keys()), p=list(timezone_weights.values()))
        
        # Customer notes (5% of orders)
        customer_notes = None
        if random.random() < 0.05:
            customer_notes = generate_customer_notes()
        
        # Order priority
        order_priority = determine_order_priority(order_value, user_id)
        
        # Shipping and billing addresses (simplified)
        shipping_address_id = random.randint(1, 1000)
        billing_address_id = shipping_address_id if random.random() < 0.8 else random.randint(1, 1000)
        
        orders.append({
            'order_id': order_id,
            'user_id': user_id,
            'order_date': order_time.date().strftime('%Y-%m-%d'),
            'status': status,
            'total_amount': round(order_value, 2),
            'order_source': order_source,
            'payment_method': payment_method,
            'shipping_method': shipping_method,
            'promo_code': promo_code,
            'shipping_address_id': shipping_address_id,
            'billing_address_id': billing_address_id,
            'customer_notes': customer_notes,
            'order_priority': order_priority,
            'timezone': timezone,
            'shipping_region': timezone
        })
    
    df_orders = pd.DataFrame(orders)
    # Ensure order_date is properly formatted as date-only string
    df_orders['order_date'] = pd.to_datetime(df_orders['order_date']).dt.strftime('%Y-%m-%d')
    return df_orders

def apply_seasonal_patterns(orders_df):
    """Apply realistic seasonal and event-based ordering patterns."""
    
    # Convert to datetime for easier manipulation
    orders_df['order_date'] = pd.to_datetime(orders_df['order_date'])
    
    # Holiday season boost (November-December)
    holiday_mask = (orders_df['order_date'].dt.month.isin([11, 12]))
    orders_df.loc[holiday_mask, 'total_amount'] *= np.random.uniform(1.2, 1.8, size=holiday_mask.sum())
    
    # Black Friday spike (last Friday of November)
    black_friday_mask = (
        (orders_df['order_date'].dt.month == 11) & 
        (orders_df['order_date'].dt.day >= 24) & 
        (orders_df['order_date'].dt.day <= 30) &
        (orders_df['order_date'].dt.weekday == 4)  # Friday
    )
    orders_df.loc[black_friday_mask, 'total_amount'] *= np.random.uniform(1.5, 2.5, size=black_friday_mask.sum())
    
    # Weekend vs weekday patterns
    weekend_mask = orders_df['order_date'].dt.weekday >= 5
    orders_df.loc[weekend_mask, 'total_amount'] *= np.random.uniform(0.9, 1.1, size=weekend_mask.sum())
    
    # Summer season boost for certain categories (would need product data)
    summer_mask = orders_df['order_date'].dt.month.isin([6, 7, 8])
    orders_df.loc[summer_mask, 'total_amount'] *= np.random.uniform(1.05, 1.15, size=summer_mask.sum())
    
    # Convert back to date-only string format
    orders_df['order_date'] = orders_df['order_date'].dt.strftime('%Y-%m-%d')
    
    return orders_df

def generate_customer_behavior_patterns(orders_df, users_df):
    """Add realistic customer behavior patterns."""
    
    # High-value customers order more frequently
    high_value_customers = users_df[users_df['loyalty_points'] > 10000]['user_id'].tolist()
    
    # Add repeat orders for high-value customers
    repeat_orders = []
    for customer_id in high_value_customers[:min(100, len(high_value_customers))]:  # Top 100 customers
        num_repeat_orders = random.randint(2, 8)
        customer_orders = orders_df[orders_df['user_id'] == customer_id]
        
        if len(customer_orders) > 0:
            base_order = customer_orders.iloc[0]
            for _ in range(num_repeat_orders):
                # Generate follow-up order 1-30 days later
                follow_up_date = pd.to_datetime(base_order['order_date']) + timedelta(days=random.randint(1, 30))
                
                repeat_orders.append({
                    'order_id': len(orders_df) + len(repeat_orders) + 1,
                    'user_id': customer_id,
                    'order_date': follow_up_date.strftime('%Y-%m-%d'),
                    'status': 'delivered',
                    'total_amount': round(base_order['total_amount'] * random.uniform(0.8, 1.2), 2),
                    'order_source': base_order['order_source'],
                    'payment_method': base_order['payment_method'],
                    'shipping_method': base_order['shipping_method'],
                    'promo_code': base_order['promo_code'],
                    'shipping_address_id': base_order['shipping_address_id'],
                    'billing_address_id': base_order['billing_address_id'],
                    'customer_notes': base_order['customer_notes'],
                    'order_priority': base_order['order_priority'],
                    'timezone': base_order['timezone'],
                    'shipping_region': base_order['shipping_region']
                })
    
    if repeat_orders:
        return pd.concat([orders_df, pd.DataFrame(repeat_orders)], ignore_index=True)
    return orders_df

def generate_realistic_order_items(orders_df, products_df, users_df):
    """Generate realistic order items with multiple items per order, cross-selling, and business logic."""
    
    order_items = []
    
    # Define product relationships for cross-selling
    product_relationships = {
        'Electronics': {
            'Smartphones': ['Accessories', 'Accessories', 'Accessories'],  # Phone cases, chargers, etc.
            'Laptops': ['Accessories', 'Accessories'],  # Mouse, keyboard, bag
            'Headphones': ['Accessories'],  # Carrying case
            'Cameras': ['Accessories', 'Accessories'],  # Memory cards, cases
            'Gaming': ['Accessories', 'Accessories'],  # Controllers, games
        },
        'Clothing': {
            'Tops': ['Bottoms', 'Accessories'],  # Pants, belts
            'Dresses': ['Shoes', 'Accessories'],  # Shoes, jewelry
            'Shoes': ['Accessories'],  # Socks, shoe care
            'Outerwear': ['Tops', 'Bottoms'],  # Shirts, pants
        },
        'Beauty': {
            'Skincare': ['Skincare', 'Tools'],  # Multiple skincare items
            'Makeup': ['Makeup', 'Tools'],  # Multiple makeup items
            'Hair Care': ['Hair Care', 'Tools'],  # Shampoo + conditioner
        },
        'Home': {
            'Furniture': ['Decor', 'Lighting'],  # Furniture + decor
            'Kitchen': ['Kitchen', 'Kitchen'],  # Multiple kitchen items
            'Bedding': ['Bedding', 'Bath'],  # Sheets + towels
        },
        'Sports': {
            'Fitness': ['Fitness', 'Activewear'],  # Equipment + clothing
            'Outdoor': ['Outdoor', 'Outdoor'],  # Multiple outdoor items
            'Running': ['Running', 'Running'],  # Shoes + clothing
        },
        'Toys': {
            'Building Sets': ['Building Sets', 'Puzzles'],  # Multiple building items
            'Board Games': ['Board Games', 'Puzzles'],  # Multiple games
            'Educational': ['Educational', 'Educational'],  # Multiple educational items
        }
    }
    
    # Define quantity patterns by product type
    quantity_patterns = {
        'Electronics': {'single': 0.8, 'multiple': 0.2, 'max_qty': 3},
        'Clothing': {'single': 0.7, 'multiple': 0.3, 'max_qty': 5},
        'Beauty': {'single': 0.4, 'multiple': 0.6, 'max_qty': 8},
        'Home': {'single': 0.6, 'multiple': 0.4, 'max_qty': 4},
        'Sports': {'single': 0.7, 'multiple': 0.3, 'max_qty': 6},
        'Toys': {'single': 0.5, 'multiple': 0.5, 'max_qty': 10}
    }
    
    # Define bulk order patterns
    bulk_patterns = {
        'office_supplies': {'probability': 0.05, 'min_qty': 10, 'max_qty': 50},
        'party_supplies': {'probability': 0.03, 'min_qty': 15, 'max_qty': 100},
        'beauty_bulk': {'probability': 0.08, 'min_qty': 5, 'max_qty': 20},
        'clothing_bulk': {'probability': 0.02, 'min_qty': 8, 'max_qty': 30}
    }
    
    for _, order in orders_df.iterrows():
        order_id = order['order_id']
        user_id = order['user_id']
        order_date = pd.to_datetime(order['order_date'])
        
        # Get user information for behavior patterns
        user_matches = users_df[users_df['user_id'] == user_id]
        if len(user_matches) == 0:
            # Fallback to random user if not found
            user_info = users_df.sample(1).iloc[0]
        else:
            user_info = user_matches.iloc[0]
        
        membership_status = user_info['membership_status']
        loyalty_points = user_info['loyalty_points']
        
        # Determine number of items in this order
        num_items = determine_order_size(user_id, membership_status, loyalty_points)
        
        # Select products for this order
        selected_products = select_products_for_order(
            products_df, num_items, order_date, membership_status, 
            product_relationships, quantity_patterns, bulk_patterns
        )
        
        # Generate order items
        for product_info in selected_products:
            product_id = product_info['product_id']
            quantity = product_info['quantity']
            unit_price = product_info['unit_price']
            discount_rate = product_info['discount_rate']
            
            # Calculate pricing
            subtotal = unit_price * quantity
            discount_amount = subtotal * discount_rate
            discounted_subtotal = subtotal - discount_amount
            
            # Calculate tax (8% average)
            tax_rate = 0.08
            tax_amount = discounted_subtotal * tax_rate
            
            # Get product details for shipping calculation
            product_details = products_df[products_df['product_id'] == product_id].iloc[0]
            
            # Calculate shipping based on product weight and category
            shipping_cost = calculate_shipping_cost(product_details, quantity)
            
            # Total for this line item
            total_price = discounted_subtotal + tax_amount + shipping_cost
            
            # Determine if gift wrapped (5% chance)
            is_gift_wrapped = random.random() < 0.05
            
            order_item = {
                'order_id': order_id,
                'product_id': product_id,
                'quantity': quantity,
                'unit_price': round(unit_price, 2),
                'total_price': round(total_price, 2),
                'discount_amount': round(discount_amount, 2),
                'discount_rate': round(discount_rate, 3),
                'tax_amount': round(tax_amount, 2),
                'tax_rate': tax_rate,
                'shipping_cost': round(shipping_cost, 2),
                'product_variant': product_info.get('variant', 'Standard'),
                'is_gift_wrapped': is_gift_wrapped,
                'is_bulk_order': quantity >= 10,
                'cross_sell_item': product_info.get('is_cross_sell', False)
            }
            
            order_items.append(order_item)
    
    return pd.DataFrame(order_items)

def determine_order_size(user_id, membership_status, loyalty_points):
    """Determine realistic number of items per order based on customer profile."""
    
    # Base probabilities for number of items
    if membership_status == 'Platinum' or loyalty_points > 15000:
        # VIP customers - larger orders
        probabilities = [0.15, 0.25, 0.25, 0.20, 0.10, 0.05]
        item_counts = [1, 2, 3, 4, 5, 6]
    elif membership_status == 'Gold' or loyalty_points > 8000:
        # Gold customers - medium orders
        probabilities = [0.25, 0.30, 0.25, 0.15, 0.05]
        item_counts = [1, 2, 3, 4, 5]
    elif membership_status == 'Silver' or loyalty_points > 3000:
        # Silver customers - small-medium orders
        probabilities = [0.40, 0.30, 0.20, 0.10]
        item_counts = [1, 2, 3, 4]
    else:
        # Bronze/new customers - small orders
        probabilities = [0.60, 0.25, 0.15]
        item_counts = [1, 2, 3]
    
    return np.random.choice(item_counts, p=probabilities)

def select_products_for_order(products_df, num_items, order_date, membership_status, 
                            product_relationships, quantity_patterns, bulk_patterns):
    """Select products for an order with realistic cross-selling and business logic."""
    
    selected_products = []
    used_products = set()
    
    # First item - main product (no cross-selling)
    main_product = select_main_product(products_df, order_date, membership_status, used_products)
    if main_product:
        selected_products.append(main_product)
        used_products.add(main_product['product_id'])
    
    # Additional items - mix of cross-sells and independent products
    remaining_items = num_items - 1
    cross_sell_attempts = 0
    max_cross_sell_attempts = min(remaining_items, 3)
    
    while remaining_items > 0 and len(selected_products) < num_items:
        # 60% chance for cross-sell if we have a main product and haven't exceeded attempts
        if (main_product and cross_sell_attempts < max_cross_sell_attempts and 
            random.random() < 0.6):
            
            cross_sell_product = select_cross_sell_product(
                main_product, products_df, product_relationships, used_products
            )
            if cross_sell_product:
                selected_products.append(cross_sell_product)
                used_products.add(cross_sell_product['product_id'])
                cross_sell_attempts += 1
                remaining_items -= 1
                continue
        
        # Independent product selection
        independent_product = select_independent_product(
            products_df, order_date, membership_status, used_products
        )
        if independent_product:
            selected_products.append(independent_product)
            used_products.add(independent_product['product_id'])
            remaining_items -= 1
    
    return selected_products

def select_main_product(products_df, order_date, membership_status, used_products):
    """Select the main product for an order."""
    
    # Filter available products (not used, in stock)
    available_products = products_df[
        (~products_df['product_id'].isin(used_products)) & 
        (products_df['stock_quantity'] > 0)
    ].copy()
    
    if len(available_products) == 0:
        return None
    
    # Weight products by membership status and seasonality
    weights = calculate_product_weights(available_products, order_date, membership_status)
    
    # Select product
    selected_idx = np.random.choice(len(available_products), p=weights)
    product = available_products.iloc[selected_idx]
    
    # Define quantity patterns and bulk patterns
    quantity_patterns = {
        'Electronics': {'single': 0.8, 'multiple': 0.2, 'max_qty': 3},
        'Clothing': {'single': 0.7, 'multiple': 0.3, 'max_qty': 5},
        'Beauty': {'single': 0.4, 'multiple': 0.6, 'max_qty': 8},
        'Home': {'single': 0.6, 'multiple': 0.4, 'max_qty': 4},
        'Sports': {'single': 0.7, 'multiple': 0.3, 'max_qty': 6},
        'Toys': {'single': 0.5, 'multiple': 0.5, 'max_qty': 10}
    }
    
    bulk_patterns = {
        'office_supplies': {'probability': 0.05, 'min_qty': 10, 'max_qty': 50},
        'party_supplies': {'probability': 0.03, 'min_qty': 15, 'max_qty': 100},
        'beauty_bulk': {'probability': 0.08, 'min_qty': 5, 'max_qty': 20},
        'clothing_bulk': {'probability': 0.02, 'min_qty': 8, 'max_qty': 30}
    }
    
    # Determine quantity
    quantity = determine_product_quantity(product, quantity_patterns, bulk_patterns)
    
    # Calculate pricing
    unit_price, discount_rate = calculate_product_pricing(product, membership_status, quantity)
    
    return {
        'product_id': product['product_id'],
        'quantity': quantity,
        'unit_price': unit_price,
        'discount_rate': discount_rate,
        'variant': 'Standard',
        'is_cross_sell': False
    }

def select_cross_sell_product(main_product, products_df, product_relationships, used_products):
    """Select a cross-sell product based on the main product."""
    
    # Get the main product details from products_df
    main_product_id = main_product['product_id']
    main_product_details = products_df[products_df['product_id'] == main_product_id].iloc[0]
    
    main_category = main_product_details['category']
    main_subcategory = main_product_details['subcategory']
    
    # Get related subcategories
    if main_category in product_relationships and main_subcategory in product_relationships[main_category]:
        related_subcategories = product_relationships[main_category][main_subcategory]
        target_subcategory = random.choice(related_subcategories)
    else:
        return None
    
    # Find products in related subcategory
    related_products = products_df[
        (products_df['category'] == main_category) &
        (products_df['subcategory'] == target_subcategory) &
        (~products_df['product_id'].isin(used_products)) &
        (products_df['stock_quantity'] > 0)
    ]
    
    if len(related_products) == 0:
        return None
    
    # Select product
    product = related_products.sample(1).iloc[0]
    
    # Cross-sell items usually have smaller quantities
    quantity = random.randint(1, 3)
    
    # Cross-sell discount (10-20% off)
    discount_rate = random.uniform(0.10, 0.20)
    unit_price = product['price'] * (1 - discount_rate)
    
    return {
        'product_id': product['product_id'],
        'quantity': quantity,
        'unit_price': unit_price,
        'discount_rate': discount_rate,
        'variant': 'Standard',
        'is_cross_sell': True
    }

def select_independent_product(products_df, order_date, membership_status, used_products):
    """Select an independent product for the order."""
    
    # Filter available products
    available_products = products_df[
        (~products_df['product_id'].isin(used_products)) & 
        (products_df['stock_quantity'] > 0)
    ].copy()
    
    if len(available_products) == 0:
        return None
    
    # Weight products
    weights = calculate_product_weights(available_products, order_date, membership_status)
    
    # Select product
    selected_idx = np.random.choice(len(available_products), p=weights)
    product = available_products.iloc[selected_idx]
    
    # Define quantity patterns and bulk patterns
    quantity_patterns = {
        'Electronics': {'single': 0.8, 'multiple': 0.2, 'max_qty': 3},
        'Clothing': {'single': 0.7, 'multiple': 0.3, 'max_qty': 5},
        'Beauty': {'single': 0.4, 'multiple': 0.6, 'max_qty': 8},
        'Home': {'single': 0.6, 'multiple': 0.4, 'max_qty': 4},
        'Sports': {'single': 0.7, 'multiple': 0.3, 'max_qty': 6},
        'Toys': {'single': 0.5, 'multiple': 0.5, 'max_qty': 10}
    }
    
    bulk_patterns = {
        'office_supplies': {'probability': 0.05, 'min_qty': 10, 'max_qty': 50},
        'party_supplies': {'probability': 0.03, 'min_qty': 15, 'max_qty': 100},
        'beauty_bulk': {'probability': 0.08, 'min_qty': 5, 'max_qty': 20},
        'clothing_bulk': {'probability': 0.02, 'min_qty': 8, 'max_qty': 30}
    }
    
    # Determine quantity
    quantity = determine_product_quantity(product, quantity_patterns, bulk_patterns)
    
    # Calculate pricing
    unit_price, discount_rate = calculate_product_pricing(product, membership_status, quantity)
    
    return {
        'product_id': product['product_id'],
        'quantity': quantity,
        'unit_price': unit_price,
        'discount_rate': discount_rate,
        'variant': 'Standard',
        'is_cross_sell': False
    }

def calculate_product_weights(products_df, order_date, membership_status):
    """Calculate selection weights for products based on various factors."""
    
    weights = np.ones(len(products_df))
    
    # Featured products get higher weight
    weights[products_df['is_featured']] *= 2.0
    
    # High-rated products get higher weight
    weights[products_df['rating'] >= 4.5] *= 1.5
    weights[products_df['rating'] >= 4.0] *= 1.2
    
    # Premium brands for higher-tier customers
    if membership_status in ['Gold', 'Platinum']:
        premium_brands = ['Apple', 'Samsung', 'Nike', 'Adidas', 'Dyson', 'KitchenAid']
        weights[products_df['brand'].isin(premium_brands)] *= 1.3
    
    # Seasonal weighting (simplified)
    month = order_date.month
    if month in [11, 12]:  # Holiday season
        weights[products_df['category'].isin(['Toys', 'Electronics', 'Home'])] *= 1.4
    elif month in [6, 7, 8]:  # Summer
        weights[products_df['category'].isin(['Sports', 'Clothing'])] *= 1.3
    
    # Normalize weights
    return weights / weights.sum()

def determine_product_quantity(product, quantity_patterns, bulk_patterns):
    """Determine realistic quantity for a product."""
    
    category = product['category']
    subcategory = product['subcategory']
    
    # Check for bulk order patterns
    for pattern_name, pattern_info in bulk_patterns.items():
        if (random.random() < pattern_info['probability'] and 
            category in ['Beauty', 'Home', 'Sports', 'Toys']):
            return random.randint(pattern_info['min_qty'], pattern_info['max_qty'])
    
    # Regular quantity patterns
    if category in quantity_patterns:
        pattern = quantity_patterns[category]
        if random.random() < pattern['single']:
            return 1
        else:
            return random.randint(2, pattern['max_qty'])
    
    # Default pattern
    if random.random() < 0.7:
        return 1
    else:
        return random.randint(2, 5)

def calculate_product_pricing(product, membership_status, quantity):
    """Calculate unit price and discount rate for a product."""
    
    base_price = product['price']
    
    # Membership discounts
    if membership_status == 'Platinum':
        base_discount = 0.15
    elif membership_status == 'Gold':
        base_discount = 0.10
    elif membership_status == 'Silver':
        base_discount = 0.05
    else:
        base_discount = 0.0
    
    # Bulk discounts
    bulk_discount = 0.0
    if quantity >= 10:
        bulk_discount = 0.20
    elif quantity >= 5:
        bulk_discount = 0.10
    elif quantity >= 3:
        bulk_discount = 0.05
    
    # Bundle discount (for cross-sell items)
    bundle_discount = 0.0
    if random.random() < 0.3:  # 30% chance of bundle discount
        bundle_discount = 0.15
    
    # Total discount (capped at 50%)
    total_discount = min(base_discount + bulk_discount + bundle_discount, 0.50)
    
    # Apply discount
    unit_price = base_price * (1 - total_discount)
    
    return unit_price, total_discount

def calculate_shipping_cost(product_info, quantity):
    """Calculate shipping cost based on product characteristics."""
    
    # Base shipping costs
    if product_info.get('is_digital', False):
        return 0.0  # Digital products have no shipping
    
    weight = product_info.get('weight', 1.0)
    category = product_info.get('category', 'Electronics')
    
    # Weight-based shipping
    if weight <= 0.5:
        base_cost = 5.99
    elif weight <= 2.0:
        base_cost = 7.99
    elif weight <= 10.0:
        base_cost = 12.99
    else:
        base_cost = 19.99
    
    # Category adjustments
    if category in ['Furniture', 'Sports']:
        base_cost *= 1.5  # Heavy/bulky items
    elif category == 'Electronics':
        base_cost *= 1.2  # Fragile items
    
    # Quantity adjustments
    if quantity >= 10:
        base_cost *= 1.3  # Bulk shipping
    elif quantity >= 5:
        base_cost *= 1.1
    
    return round(base_cost, 2)

def generate_simple_dataset(num_users=100000, num_products=1000, num_orders=1000, num_reviews=1000, output_dir=None):
    """Generate a simple synthetic e-commerce dataset."""
    
    # Auto-generate output directory if not provided
    if output_dir is None:
        size_category = get_size_category(num_users, num_products, num_orders, num_reviews)
        output_dir = create_timestamped_folder(size_category)
    
    print(f"Generating dataset with {num_users} users, {num_products} products, {num_orders} orders, {num_reviews} reviews")
    print(f"Size category: {get_size_category(num_users, num_products, num_orders, num_reviews)}")
    print(f"Output directory: {output_dir}")
    
    # Generate Enhanced Users
    print("Generating enhanced users...")
    df_users = generate_enhanced_users(num_users)
    
    # Generate Products
    print("Generating products...")
    df_products = generate_realistic_products(num_products)
    
    # Generate Orders with enhanced realism
    print("Generating orders...")
    
    # Generate realistic user IDs that actually exist
    realistic_user_ids = generate_realistic_user_ids(num_orders, num_users)
    
    # Generate realistic order times with business patterns
    order_times = generate_realistic_order_times(num_orders, '-1y', 'today')
    
    # Generate enhanced orders with business context
    df_orders = generate_enhanced_orders(num_orders, realistic_user_ids, order_times, df_products, df_users)
    
    # Apply seasonal patterns
    print("Applying seasonal patterns...")
    df_orders = apply_seasonal_patterns(df_orders)
    
    # Add customer behavior patterns (repeat orders for high-value customers)
    print("Adding customer behavior patterns...")
    df_orders = generate_customer_behavior_patterns(df_orders, df_users)
    
    # Generate Order Items
    print("Generating order items...")
    df_order_items = generate_realistic_order_items(df_orders, df_products, df_users)
    
    # Update order totals based on actual order items
    print("Updating order totals...")
    order_totals = df_order_items.groupby('order_id')['total_price'].sum().reset_index()
    order_totals.columns = ['order_id', 'calculated_total']
    df_orders = df_orders.merge(order_totals, on='order_id', how='left')
    df_orders['total_amount'] = df_orders['calculated_total'].fillna(df_orders['total_amount']).round(2)
    df_orders = df_orders.drop('calculated_total', axis=1)
    
    # Generate Reviews with realistic relationships to orders
    print("Generating reviews...")
    
    # Create a mapping of users to their orders for verified purchases
    user_orders = df_orders.groupby('user_id').apply(lambda x: x.to_dict('records')).to_dict()
    
    # Generate reviews with realistic relationships
    reviews = []
    review_id = 1
    
    # First, generate reviews from actual purchasers (verified purchases)
    for user_id, orders in user_orders.items():
        if len(orders) == 0:
            continue
            
        # Each user reviews 20-60% of their purchases
        num_reviews_for_user = max(1, int(len(orders) * random.uniform(0.2, 0.6)))
        orders_to_review = random.sample(orders, min(num_reviews_for_user, len(orders)))
        
        for order in orders_to_review:
            # Get order items for this order
            order_items = df_order_items[df_order_items['order_id'] == order['order_id']]
            
            # Review 1-3 items from this order
            items_to_review = order_items.sample(n=min(random.randint(1, 3), len(order_items)))
            
            for _, item in items_to_review.iterrows():
                product_id = item['product_id']
                product_info = df_products[df_products['product_id'] == product_id].iloc[0]
                user_info = df_users[df_users['user_id'] == user_id].iloc[0]
                
                # Generate realistic rating based on product quality and price
                base_rating = product_info['rating']
                if base_rating > 0:
                    # Add some variation based on individual experience
                    rating_variation = random.uniform(-0.5, 0.5)
                    rating = max(1.0, min(5.0, base_rating + rating_variation))
                else:
                    # New product, generate rating based on price and category
                    if product_info['price'] > 200:
                        rating = random.uniform(3.5, 4.8)
                    elif product_info['price'] > 100:
                        rating = random.uniform(3.2, 4.6)
                    else:
                        rating = random.uniform(3.0, 4.4)
                
                rating = round(rating, 1)
                
                # Calculate days since purchase
                order_date = pd.to_datetime(order['order_date'])
                days_since_purchase = (pd.Timestamp.now() - order_date).days
                
                # Generate enhanced review
                review_data = generate_enhanced_realistic_review(
                    rating=rating,
                    category=product_info['category'],
                    product_name=product_info['name'],
                    product_brand=product_info['brand'],
                    order_value=item['total_price'],
                    days_since_purchase=days_since_purchase,
                    customer_tier=user_info['membership_status'],
                    user_name=user_info['name']
                )
                
                # Generate review date (1-30 days after order)
                review_date = order_date + pd.Timedelta(days=random.randint(1, 30))
                
                reviews.append({
                    'review_id': review_id,
                    'user_id': user_id,
                    'product_id': product_id,
                    'rating': rating,
                    'review_text': review_data['review_text'],
                    'review_date': review_date.strftime('%Y-%m-%d'),
                    'helpful_votes': review_data['helpful_votes'],
                    'verified_purchase': True,  # All these are verified
                    'has_images': review_data['has_images'],
                    'image_count': review_data['image_count'],
                    'experience_level': review_data['experience_level']
                })
                review_id += 1
                
                if review_id > num_reviews:
                    break
        
        if review_id > num_reviews:
            break
    
    # Fill remaining reviews with non-verified purchases if needed
    while review_id <= num_reviews:
        user_id = random.choice(df_users['user_id'])
        product_id = random.choice(df_products['product_id'])
        
        product_info = df_products[df_products['product_id'] == product_id].iloc[0]
        user_info = df_users[df_users['user_id'] == user_id].iloc[0]
        
        # Generate rating
        if product_info['rating'] > 0:
            rating = max(1.0, min(5.0, product_info['rating'] + random.uniform(-0.8, 0.8)))
        else:
            rating = random.uniform(2.0, 4.5)
        rating = round(rating, 1)
        
        # Generate enhanced review
        review_data = generate_enhanced_realistic_review(
            rating=rating,
            category=product_info['category'],
            product_name=product_info['name'],
            product_brand=product_info['brand'],
            order_value=random.uniform(20, 300),  # Random order value
            days_since_purchase=random.randint(1, 365),
            customer_tier=user_info['membership_status'],
            user_name=user_info['name']
        )
        
        # Generate review date
        review_date = fake.date_between(start_date='-1y', end_date='today')
        
        reviews.append({
            'review_id': review_id,
            'user_id': user_id,
            'product_id': product_id,
            'rating': rating,
            'review_text': review_data['review_text'],
            'review_date': review_date.strftime('%Y-%m-%d'),
            'helpful_votes': review_data['helpful_votes'],
            'verified_purchase': review_data['verified_purchase'],
            'has_images': review_data['has_images'],
            'image_count': review_data['image_count'],
            'experience_level': review_data['experience_level']
        })
        review_id += 1
    
    df_reviews = pd.DataFrame(reviews)
    
    # Save datasets
    os.makedirs(output_dir, exist_ok=True)
    print(f"Saving datasets to {output_dir}/...")
    
    df_users.to_csv(f'{output_dir}/users.csv', index=False)
    df_products.to_csv(f'{output_dir}/products.csv', index=False)
    df_orders.to_csv(f'{output_dir}/orders.csv', index=False)
    df_order_items.to_csv(f'{output_dir}/order_items.csv', index=False)
    df_reviews.to_csv(f'{output_dir}/reviews.csv', index=False)
    
    # Create a metadata file
    metadata = {
        'generation_time': datetime.now().isoformat(),
        'size_category': get_size_category(num_users, num_products, num_orders, num_reviews),
        'parameters': {
            'num_users': num_users,
            'num_products': num_products,
            'num_orders': num_orders,
            'num_reviews': num_reviews
        },
        'file_sizes': {
            'users.csv': os.path.getsize(f'{output_dir}/users.csv'),
            'products.csv': os.path.getsize(f'{output_dir}/products.csv'),
            'orders.csv': os.path.getsize(f'{output_dir}/orders.csv'),
            'order_items.csv': os.path.getsize(f'{output_dir}/order_items.csv'),
            'reviews.csv': os.path.getsize(f'{output_dir}/reviews.csv')
        }
    }
    
    with open(f'{output_dir}/metadata.txt', 'w') as f:
        f.write(f"Dataset Generation Metadata\n")
        f.write(f"==========================\n")
        f.write(f"Generated: {metadata['generation_time']}\n")
        f.write(f"Size Category: {metadata['size_category']}\n")
        f.write(f"\nParameters:\n")
        f.write(f"  Users: {metadata['parameters']['num_users']:,}\n")
        f.write(f"  Products: {metadata['parameters']['num_products']:,}\n")
        f.write(f"  Orders: {metadata['parameters']['num_orders']:,}\n")
        f.write(f"  Reviews: {metadata['parameters']['num_reviews']:,}\n")
        f.write(f"\nFile Sizes:\n")
        for file, size in metadata['file_sizes'].items():
            f.write(f"  {file}: {size:,} bytes\n")
    
    print("✅ Dataset generation completed!")
    print(f"Files created in '{output_dir}/' directory:")
    print("  - users.csv")
    print("  - products.csv")
    print("  - orders.csv")
    print("  - order_items.csv")
    print("  - reviews.csv")
    print("  - metadata.txt")
    
    return output_dir

def list_existing_datasets(base_dir="datasets"):
    """List all existing datasets organized by size and timestamp."""
    if not os.path.exists(base_dir):
        print(f"No datasets found in {base_dir}")
        return
    
    print(f"\nExisting datasets in {base_dir}:")
    print("=" * 50)
    
    for size_category in ['small', 'medium', 'large', 'xlarge']:
        size_dir = os.path.join(base_dir, f"{size_category}_*")
        import glob
        folders = glob.glob(size_dir)
        if folders:
            print(f"\n{size_category.upper()} datasets:")
            for folder in sorted(folders):
                folder_name = os.path.basename(folder)
                timestamp = folder_name.split('_', 1)[1] if '_' in folder_name else 'unknown'
                print(f"  📁 {folder_name}")
                print(f"     Generated: {timestamp}")
                
                # Show file sizes if metadata exists
                metadata_file = os.path.join(folder, 'metadata.txt')
                if os.path.exists(metadata_file):
                    with open(metadata_file, 'r') as f:
                        lines = f.readlines()
                        for line in lines:
                            if 'Users:' in line or 'Products:' in line or 'Orders:' in line or 'Reviews:' in line:
                                print(f"     {line.strip()}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Generate synthetic e-commerce dataset with organized folders')
    parser.add_argument('--users', type=int, default=100000, help='Number of users')
    parser.add_argument('--products', type=int, default=1000, help='Number of products')
    parser.add_argument('--orders', type=int, default=1000, help='Number of orders')
    parser.add_argument('--reviews', type=int, default=1000, help='Number of reviews')
    parser.add_argument('--output-dir', type=str, default=None, help='Custom output directory (auto-generated if not provided)')
    parser.add_argument('--list', action='store_true', help='List existing datasets')
    
    args = parser.parse_args()
    
    if args.list:
        list_existing_datasets()
    else:
        output_dir = generate_simple_dataset(
            num_users=args.users,
            num_products=args.products,
            num_orders=args.orders,
            num_reviews=args.reviews,
            output_dir=args.output_dir
        )
        print(f"\n🎉 Dataset saved to: {output_dir}")
