"""
Sample Data Generator for Product Recommendation System
Generates realistic Indian e-commerce product data
"""

import random
import sys
import os
from datetime import datetime, timedelta

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from sqlalchemy.orm import Session
from src.database.models import Product, Review, PriceHistory, CardOffer
from src.database.connection import SessionLocal
import json

# Comprehensive product categories with realistic Indian e-commerce data (like Amazon/Flipkart)
CATEGORIES_DATA = {
    'Electronics': {
        'Headphones': {
            'brands': ['boAt', 'JBL', 'Sony', 'OnePlus', 'Realme', 'Noise', 'ptron', 'Sennheiser', 'Audio-Technica', 'Bose', 'Skullcandy'],
            'features': ['Active Noise Cancellation', 'Wireless', 'Fast Charging', 'Water Resistant', 'Extra Bass', 'Long Battery Life', 'Gaming Mode', 'Touch Controls', 'Voice Assistant'],
            'price_range': (799, 29999),  # Updated 2026 prices
            'models': ['Airdopes', 'Rockerz', 'ProBuds', 'Pods', 'Buds', 'Elite', 'Tune', 'Wave', 'Storm']
        },
        'Smartphones': {
            'brands': ['Samsung', 'Xiaomi', 'Realme', 'OnePlus', 'Vivo', 'Oppo', 'Apple', 'Google', 'Motorola', 'Nothing', 'iQOO', 'Poco'],
            'features': ['5G', '120Hz Display', 'Fast Charging', '64MP Camera', 'AMOLED Display', 'Gorilla Glass', 'Wireless Charging', 'IP Rating', 'OIS', 'Dual SIM'],
            'price_range': (7999, 149999),  # Updated 2026 prices (₹7,999 to ₹1,49,999)
            'models': ['Galaxy', 'Redmi', 'Note', 'Pro', 'Nord', 'iPhone', 'Pixel', 'Edge', 'Phone', 'GT']
        },
        'Laptops': {
            'brands': ['HP', 'Dell', 'Lenovo', 'ASUS', 'Acer', 'MSI', 'Apple', 'Avita', 'Infinix', 'Samsung'],
            'features': ['16GB RAM', 'SSD Storage', 'Backlit Keyboard', 'Dedicated Graphics', 'Windows 11', 'Full HD Display', 'Fingerprint Reader', 'Type-C Port', 'Thunderbolt', 'WiFi 6'],
            'price_range': (27999, 199999),  # Updated 2026 prices (₹27,999 to ₹1,99,999)
            'models': ['Pavilion', 'Inspiron', 'IdeaPad', 'VivoBook', 'Aspire', 'Prestige', 'MacBook', 'TUF', 'ROG']
        },
        'Smart Watches': {
            'brands': ['Apple', 'Samsung', 'Noise', 'boAt', 'Fire-Boltt', 'Amazfit', 'Realme', 'OnePlus', 'Fastrack', 'Titan'],
            'features': ['Heart Rate Monitor', 'SpO2 Tracking', 'GPS', 'Water Resistant', 'Long Battery', 'AMOLED Display', 'Fitness Tracking', 'Sleep Monitor', 'Bluetooth Calling'],
            'price_range': (1199, 52999),
            'models': ['Watch', 'Pulse', 'Active', 'Storm', 'Ninja', 'GTR', 'Fit', 'Ultra']
        },
        'Tablets': {
            'brands': ['Apple', 'Samsung', 'Lenovo', 'Xiaomi', 'Realme', 'OnePlus', 'Amazon', 'Nokia'],
            'features': ['WiFi + 5G', 'Stylus Support', 'Quad Speakers', 'High Resolution', 'Long Battery', 'Fast Charging', 'Dual Camera'],
            'price_range': (8999, 94999),
            'models': ['iPad', 'Tab', 'Pad', 'Fire', 'MatePad']
        },
        'Power Banks': {
            'brands': ['Mi', 'Ambrane', 'Syska', 'OnePlus', 'Realme', 'Samsung', 'boAt', 'Anker', 'Portronics'],
            'features': ['Fast Charging', 'Type-C', 'Multiple Ports', 'LED Indicator', 'Compact Design', 'High Capacity', 'Quick Charge', 'Power Delivery'],
            'price_range': (499, 4999),
            'models': ['Power', 'Energy', 'Charge', 'Boost', 'Pocket']
        },
        'Cameras': {
            'brands': ['Canon', 'Nikon', 'Sony', 'Fujifilm', 'Panasonic', 'GoPro', 'DJI', 'Olympus'],
            'features': ['4K Video', 'WiFi', 'Touchscreen', 'Image Stabilization', 'Weather Sealed', 'High ISO', 'Dual Card Slots', 'RAW Support'],
            'price_range': (22999, 289999),
            'models': ['EOS', 'Alpha', 'Z', 'X', 'Lumix', 'Hero', 'Action']
        },
        'Televisions': {
            'brands': ['Samsung', 'LG', 'Sony', 'Mi', 'OnePlus', 'TCL', 'VU', 'Hisense', 'Panasonic'],
            'features': ['4K', 'Smart TV', 'HDR', 'Dolby Atmos', 'Google TV', 'Voice Control', 'Gaming Mode', 'HDMI 2.1'],
            'price_range': (12999, 189999),
            'models': ['Crystal', 'OLED', 'QLED', 'NanoCell', 'Bravia']
        }
    },
    'Fashion': {
        'Mens Clothing': {
            'brands': ['Van Heusen', 'Allen Solly', 'Peter England', 'Louis Philippe', 'Raymond', 'Arrow', 'Blackberrys', 'Park Avenue', 'US Polo', 'Lee', "Levi's"],
            'features': ['Cotton', 'Slim Fit', 'Wrinkle Free', 'Formal', 'Casual', 'Regular Fit', 'Stretchable', 'Breathable', 'Machine Washable'],
            'price_range': (349, 6999),
            'models': ['Shirt', 'T-Shirt', 'Trouser', 'Jeans', 'Blazer', 'Jacket']
        },
        'Womens Clothing': {
            'brands': ['W', 'Biba', 'Aurelia', 'AND', 'Global Desi', 'FabIndia', 'Manyavar', 'Libas', 'Janasya', 'Khushal K'],
            'features': ['Cotton', 'Ethnic Wear', 'Western Wear', 'Comfortable', 'Trendy', 'Party Wear', 'Casual', 'Hand Block Print'],
            'price_range': (449, 8999),
            'models': ['Kurti', 'Dress', 'Saree', 'Top', 'Jeans', 'Leggings', 'Palazzo']
        },
        'Footwear': {
            'brands': ['Nike', 'Adidas', 'Puma', 'Red Tape', 'Woodland', 'Bata', 'Reebok', 'Skechers', 'Sparx', 'Asian', 'Campus', 'Liberty'],
            'features': ['Comfortable', 'Durable', 'Lightweight', 'Sports', 'Casual', 'Memory Foam', 'Breathable', 'Anti-Slip', 'Cushioned'],
            'price_range': (499, 14999),
            'models': ['Running', 'Casual', 'Formal', 'Sneakers', 'Sports', 'Walking', 'Loafers']
        },
        'Watches': {
            'brands': ['Titan', 'Fastrack', 'Timex', 'Casio', 'Fossil', 'Daniel Wellington', 'Seiko', 'Citizen', 'Sonata'],
            'features': ['Water Resistant', 'Analog', 'Digital', 'Chronograph', 'Leather Strap', 'Metal Strap', 'Warranty', 'Scratch Resistant'],
            'price_range': (699, 32999),
            'models': ['Classic', 'Sport', 'Casual', 'Formal', 'Automatic']
        },
        'Bags': {
            'brands': ['Wildcraft', 'American Tourister', 'Skybags', 'Safari', 'Tommy Hilfiger', 'Lavie', 'Caprese', 'Puma', 'Nike'],
            'features': ['Durable', 'Water Resistant', 'Multiple Compartments', 'Laptop Compatible', 'Lightweight', 'Warranty', 'Ergonomic'],
            'price_range': (599, 9999),
            'models': ['Backpack', 'Laptop Bag', 'Travel Bag', 'Handbag', 'Sling Bag', 'Duffle']
        },
        'Sunglasses': {
            'brands': ['Ray-Ban', 'Oakley', 'Fastrack', 'IDEE', 'Vincent Chase', 'Polaroid', 'Carrera'],
            'features': ['UV Protection', 'Polarized', 'Lightweight', 'Stylish', 'Durable Frame', 'Anti-Glare'],
            'price_range': (599, 18999),
            'models': ['Aviator', 'Wayfarer', 'Round', 'Clubmaster', 'Sport']
        }
    },
    'Home & Kitchen': {
        'Kitchen Appliances': {
            'brands': ['Philips', 'Prestige', 'Pigeon', 'Bajaj', 'Havells', 'Butterfly', 'Morphy Richards', 'Inalsa', 'Kent', 'Usha'],
            'features': ['Energy Efficient', 'Easy to Clean', 'Durable', 'Compact', 'Multi-functional', 'Auto Shut-off', 'Warranty', 'BEE Certified'],
            'price_range': (799, 35000),
            'models': ['Mixer', 'Grinder', 'Air Fryer', 'Toaster', 'Kettle', 'Cooker', 'Blender', 'Juicer']
        },
        'Home Decor': {
            'brands': ['Philips', 'Syska', 'Wipro', 'Home Centre', 'Urban Ladder', 'Pepperfry', 'Halonix'],
            'features': ['Modern Design', 'Easy Installation', 'Durable', 'Energy Efficient', 'Warranty', 'Aesthetic', 'Eco-Friendly'],
            'price_range': (249, 16999),
            'models': ['LED Light', 'Wall Art', 'Curtain', 'Cushion', 'Lamp', 'Mirror', 'Show Piece']
        },
        'Furniture': {
            'brands': ['Nilkamal', 'Supreme', 'Godrej', 'Durian', 'Urban Ladder', 'Pepperfry', 'IKEA', 'Hometown'],
            'features': ['Solid Wood', 'Engineered Wood', 'Easy Assembly', 'Warranty', 'Modern Design', 'Space Saving', 'Durable'],
            'price_range': (1899, 65000),
            'models': ['Chair', 'Table', 'Bed', 'Sofa', 'Wardrobe', 'Shelf', 'Cabinet']
        },
        'Bedding': {
            'brands': ['Bombay Dyeing', 'Raymond Home', 'Spaces', 'Story@Home', 'Solimo', 'Amazon Brand', 'Portico'],
            'features': ['Cotton', 'Soft', 'Durable', 'Wrinkle Free', 'Colorfast', 'Easy Care', 'Thread Count 200+'],
            'price_range': (349, 6999),
            'models': ['Bedsheet', 'Comforter', 'Pillow', 'Mattress Protector', 'Blanket', 'Quilt']
        },
        'Cookware': {
            'brands': ['Prestige', 'Hawkins', 'Pigeon', 'Butterfly', 'Wonderchef', 'Meyer', 'Vinod'],
            'features': ['Non-Stick', 'Induction Compatible', 'Durable', 'Easy to Clean', 'PFOA Free', 'Warranty'],
            'price_range': (399, 8999),
            'models': ['Pressure Cooker', 'Fry Pan', 'Kadai', 'Tawa', 'Cookware Set']
        }
    },
    'Books': {
        'Fiction': {
            'brands': ['Penguin', 'HarperCollins', 'Scholastic', 'Bloomsbury', 'Rupa', 'Hachette', 'Simon & Schuster'],
            'features': ['Bestseller', 'Award Winner', 'Popular Author', 'Page Turner', 'New Release', 'Classic', 'Paperback', 'Hardcover'],
            'price_range': (89, 1499),
            'models': ['Novel', 'Thriller', 'Romance', 'Mystery', 'Fantasy', 'Sci-Fi']
        },
        'Non-Fiction': {
            'brands': ['Penguin', 'HarperCollins', 'Simon & Schuster', 'Random House', 'Oxford', 'Westland'],
            'features': ['Bestseller', 'Award Winner', 'Educational', 'Inspiring', 'Research Based', 'Informative'],
            'price_range': (149, 1899),
            'models': ['Biography', 'Self-Help', 'Business', 'History', 'Science', 'Philosophy']
        },
        'Children Books': {
            'brands': ['Scholastic', 'Penguin', 'Disney', 'Wonder House', 'Om Books', 'Usborne'],
            'features': ['Illustrated', 'Age Appropriate', 'Educational', 'Fun Learning', 'Colorful', 'Interactive'],
            'price_range': (69, 999),
            'models': ['Story Book', 'Activity Book', 'Picture Book', 'Learning Book', 'Board Book']
        },
        'Academic': {
            'brands': ['NCERT', 'RS Aggarwal', 'RD Sharma', 'Arihant', 'Oswaal', 'MTG'],
            'features': ['Latest Edition', 'Solved Examples', 'Practice Questions', 'Previous Year Papers', 'Board Exam Prep'],
            'price_range': (99, 1299),
            'models': ['Textbook', 'Reference Book', 'Question Bank', 'Sample Papers']
        }
    },
    'Sports & Fitness': {
        'Fitness Equipment': {
            'brands': ['Decathlon', 'Nivia', 'Cosco', 'Kore', 'Strauss', 'Cockatoo', 'Fitkit', 'Lifelong', 'Protoner'],
            'features': ['Durable', 'Professional Grade', 'Home Use', 'Portable', 'Easy Assembly', 'Multi-functional', 'Warranty', 'Adjustable'],
            'price_range': (349, 32999),
            'models': ['Dumbbell', 'Treadmill', 'Yoga Mat', 'Resistance Band', 'Cycle', 'Bench', 'Pull-up Bar']
        },
        'Sports Gear': {
            'brands': ['Nike', 'Adidas', 'Puma', 'Nivia', 'Cosco', 'Yonex', 'Li-Ning', 'SG', 'Kookaburra'],
            'features': ['Professional Quality', 'Durable', 'Lightweight', 'Comfortable', 'Weather Resistant', 'Certified'],
            'price_range': (249, 12999),
            'models': ['Football', 'Cricket Bat', 'Badminton Racket', 'Tennis Ball', 'Sportswear', 'Gloves']
        },
        'Cycling': {
            'brands': ['Firefox', 'Hero', 'Hercules', 'Roadeo', 'Montra', 'Btwin', 'Ninety One', 'Cosmic'],
            'features': ['Lightweight', 'Durable Frame', 'Multi-speed', 'Suspension', 'Warranty', 'Disc Brakes', 'Alloy Frame'],
            'price_range': (4499, 68999),
            'models': ['Mountain Bike', 'Road Bike', 'Hybrid Bike', 'Kids Bike', 'Gear Cycle']
        },
        'Swimming': {
            'brands': ['Speedo', 'Arena', 'Nivia', 'Strauss', 'Vector X', 'Cosco'],
            'features': ['Chlorine Resistant', 'UV Protection', 'Quick Dry', 'Comfortable', 'Durable'],
            'price_range': (299, 5999),
            'models': ['Swimsuit', 'Goggles', 'Cap', 'Fins', 'Kickboard']
        }
    },
    'Beauty & Personal Care': {
        'Skincare': {
            'brands': ['Mamaearth', 'Plum', 'WOW', 'Dot & Key', 'The Derma Co', 'Minimalist', 'Cetaphil', 'Neutrogena', 'Lakme', 'Ponds'],
            'features': ['Natural', 'Dermatologically Tested', 'Paraben Free', 'SLS Free', 'Cruelty Free', 'Organic', 'Vegan'],
            'price_range': (179, 3999),
            'models': ['Face Wash', 'Moisturizer', 'Serum', 'Sunscreen', 'Face Mask', 'Toner', 'Cleanser']
        },
        'Haircare': {
            'brands': ['Mamaearth', 'WOW', 'Pantene', 'Dove', 'Loreal', 'Tresemme', 'Biotique', 'Indulekha', 'Kesh King'],
            'features': ['Natural', 'Sulfate Free', 'Paraben Free', 'For All Hair Types', 'Anti-dandruff', 'Hair Growth', 'Nourishing'],
            'price_range': (129, 2999),
            'models': ['Shampoo', 'Conditioner', 'Hair Oil', 'Hair Serum', 'Hair Mask', 'Hair Color']
        },
        'Fragrances': {
            'brands': ['Wild Stone', 'Engage', 'Fogg', 'Skinn', 'Denver', 'Park Avenue', 'Axe', 'Set Wet', 'Beardo'],
            'features': ['Long Lasting', 'Premium Fragrance', 'No Gas Deodorant', 'Travel Size', 'Gift Pack', 'Alcohol Free'],
            'price_range': (169, 6999),
            'models': ['Perfume', 'Deodorant', 'Body Spray', 'Cologne', 'Attar']
        },
        'Makeup': {
            'brands': ['Maybelline', 'Lakme', 'LOreal', 'Colorbar', 'Swiss Beauty', 'Nykaa', 'MAC', 'Sugar'],
            'features': ['Long Lasting', 'Waterproof', 'Smudge Proof', 'Cruelty Free', 'Matte Finish', 'Natural Look'],
            'price_range': (149, 4999),
            'models': ['Lipstick', 'Kajal', 'Eyeliner', 'Foundation', 'Compact', 'Mascara']
        }
    },
    'Toys & Games': {
        'Toys': {
            'brands': ['Funskool', 'Mattel', 'Hasbro', 'LEGO', 'Hot Wheels', 'Disney', 'Fisher-Price', 'Nerf'],
            'features': ['Safe Materials', 'Age Appropriate', 'Educational', 'Interactive', 'Durable', 'BIS Certified', 'Battery Operated'],
            'price_range': (179, 9999),
            'models': ['Action Figure', 'Doll', 'Building Blocks', 'Car', 'Puzzle', 'Board Game', 'Soft Toy']
        },
        'Video Games': {
            'brands': ['Sony', 'Microsoft', 'Nintendo', 'Logitech', 'Razer', 'Cosmic Byte', 'Redgear'],
            'features': ['Wireless', 'Ergonomic', 'RGB Lighting', 'Programmable', 'High Precision', 'Long Battery', 'Quick Response'],
            'price_range': (449, 64999),
            'models': ['Console', 'Controller', 'Gaming Mouse', 'Gaming Keyboard', 'Headset', 'Mouse Pad']
        },
        'Outdoor Games': {
            'brands': ['Funskool', 'Nerf', 'Hasbro', 'Cosco', 'Nivia', 'Disney'],
            'features': ['Durable', 'Safe', 'Outdoor Play', 'Team Game', 'Active Play', 'Weather Resistant'],
            'price_range': (199, 3999),
            'models': ['Frisbee', 'Kite', 'Ball', 'Bat', 'Ring Toss', 'Water Gun']
        }
    },
    'Automotive': {
        'Car Accessories': {
            'brands': ['Bosch', '3M', 'Amaron', 'Michelin', 'Ceat', 'MRF', 'Philips', 'Wrangler'],
            'features': ['Durable', 'Easy Installation', 'Warranty', 'Weather Resistant', 'Premium Quality', 'Universal Fit'],
            'price_range': (249, 18999),
            'models': ['Car Cover', 'Seat Cover', 'Floor Mat', 'Air Freshener', 'Phone Holder', 'Vacuum Cleaner', 'Dash Cam']
        },
        'Bike Accessories': {
            'brands': ['Steelbird', 'SMK', 'Vega', 'LS2', 'Studds', 'Axor', 'MT', 'Royal Enfield'],
            'features': ['ISI Certified', 'Lightweight', 'Durable', 'Comfortable', 'Aerodynamic', 'Warranty', 'Ventilated'],
            'price_range': (449, 12999),
            'models': ['Helmet', 'Gloves', 'Jacket', 'Lock', 'Phone Holder', 'Riding Gear']
        },
        'Bike Care': {
            'brands': ['3M', 'Motul', 'Shell', 'Castrol', 'Waxpol', 'Liqui Moly'],
            'features': ['Premium Quality', 'Long Lasting', 'Easy Application', 'Weather Protection', 'Shine Enhancer'],
            'price_range': (199, 3999),
            'models': ['Wax', 'Polish', 'Cleaner', 'Engine Oil', 'Chain Lubricant']
        }
    },
    'Health & Wellness': {
        'Supplements': {
            'brands': ['Optimum Nutrition', 'MuscleBlaze', 'MyProtein', 'HealthKart', 'Oziva', 'Wellbeing Nutrition', 'GNC', 'Nutrabay'],
            'features': ['Lab Tested', 'No Harmful Additives', 'Vegetarian', 'GMP Certified', 'Third Party Tested', 'Clinically Proven'],
            'price_range': (349, 8999),
            'models': ['Whey Protein', 'Multivitamin', 'Omega 3', 'Vitamin D', 'Creatine', 'Pre-Workout', 'BCAA']
        },
        'Medical Devices': {
            'brands': ['Omron', 'Dr Morepen', 'AccuSure', 'BPL', 'Beurer', 'Healthgenie', 'Control D'],
            'features': ['Accurate', 'Easy to Use', 'Digital Display', 'Warranty', 'Certified', 'Portable', 'Memory Function'],
            'price_range': (549, 6999),
            'models': ['BP Monitor', 'Glucometer', 'Thermometer', 'Oximeter', 'Weighing Scale', 'Nebulizer']
        },
        'Ayurvedic': {
            'brands': ['Patanjali', 'Himalaya', 'Dabur', 'Baidyanath', 'Zandu', 'Organic India'],
            'features': ['Natural', 'Ayurvedic', 'No Side Effects', 'Certified', 'Traditional Formula', 'GMP Certified'],
            'price_range': (99, 1999),
            'models': ['Chyawanprash', 'Health Tonic', 'Immunity Booster', 'Digestive', 'Pain Relief']
        }
    },
    'Office Supplies': {
        'Stationery': {
            'brands': ['Classmate', 'Camlin', 'Cello', 'Reynolds', 'Faber-Castell', 'Apsara', 'Nataraj'],
            'features': ['High Quality', 'Smooth Writing', 'Durable', 'Value Pack', 'Eco-Friendly', 'Long Lasting'],
            'price_range': (39, 1999),
            'models': ['Notebook', 'Pen', 'Pencil', 'Eraser', 'Sharpener', 'Geometry Box', 'Marker']
        },
        'Office Equipment': {
            'brands': ['HP', 'Canon', 'Epson', 'Brother', 'iBall', 'Logitech', 'Dell', 'Zebronics'],
            'features': ['Wireless', 'Multi-functional', 'Energy Efficient', 'Compact', 'Warranty', 'Easy Setup', 'High Speed'],
            'price_range': (699, 42999),
            'models': ['Printer', 'Scanner', 'Keyboard', 'Mouse', 'Webcam', 'Laminator', 'Shredder']
        },
        'Desk Organizers': {
            'brands': ['Nilkamal', 'Cello', 'Solo', 'Deli', 'Arvind'],
            'features': ['Durable', 'Space Saving', 'Multi-compartment', 'Modern Design', 'Easy to Clean'],
            'price_range': (149, 2999),
            'models': ['Pen Stand', 'File Holder', 'Desk Mat', 'Cable Organizer', 'Storage Box']
        }
    },
    'Baby Products': {
        'Baby Care': {
            'brands': ['Pampers', 'Huggies', 'Mee Mee', 'Himalaya', 'Mamaearth', 'Johnson & Johnson', 'Chicco'],
            'features': ['Gentle', 'Dermatologically Tested', 'Hypoallergenic', 'Natural', 'Baby Safe', 'Soft'],
            'price_range': (99, 3999),
            'models': ['Diapers', 'Baby Wipes', 'Baby Lotion', 'Baby Oil', 'Baby Powder', 'Baby Shampoo']
        },
        'Baby Gear': {
            'brands': ['Chicco', 'Graco', 'LuvLap', 'R for Rabbit', 'BabyHug', 'Peg Perego'],
            'features': ['Safe', 'Durable', 'Easy to Use', 'Certified', 'Comfortable', 'Portable'],
            'price_range': (899, 24999),
            'models': ['Stroller', 'Car Seat', 'High Chair', 'Baby Walker', 'Baby Carrier']
        },
        'Toys & Learning': {
            'brands': ['Fisher-Price', 'Funskool', 'Playskool', 'VTech', 'Leap Frog'],
            'features': ['Educational', 'Safe Materials', 'Age Appropriate', 'Interactive', 'BIS Certified'],
            'price_range': (249, 5999),
            'models': ['Musical Toy', 'Learning Toy', 'Soft Toy', 'Rattle', 'Activity Gym']
        }
    },
    'Pet Supplies': {
        'Pet Food': {
            'brands': ['Pedigree', 'Whiskas', 'Drools', 'Royal Canin', 'Purepet', 'Meat Up'],
            'features': ['Nutritious', 'Vet Recommended', 'No Artificial Colors', 'High Protein', 'Digestive Health'],
            'price_range': (149, 5999),
            'models': ['Dog Food', 'Cat Food', 'Treats', 'Puppy Food', 'Kitten Food']
        },
        'Pet Accessories': {
            'brands': ['Petshop', 'Emily Pets', 'Trixie', 'Choostix', 'Pawzone'],
            'features': ['Durable', 'Safe', 'Comfortable', 'Easy to Clean', 'Attractive Design'],
            'price_range': (99, 3999),
            'models': ['Collar', 'Leash', 'Bowl', 'Toy', 'Bed', 'Grooming Kit']
        }
    }
}

# Comprehensive review templates for Review Analyzer Agent testing
REVIEW_TEMPLATES = {
    5: [
        "Excellent product! {feature} works perfectly. Highly recommend for {use_case}.",
        "Best purchase ever! {feature} is amazing. Worth every rupee!",
        "Outstanding quality! {feature} exceeded expectations. Must buy!",
        "Perfect for {use_case}! {feature} is top-notch. Very satisfied!",
        "Amazing product! {feature} is fantastic. Will buy again!",
        "Absolutely love it! {feature} is superb. Best in this price range.",
        "Exceeded all my expectations! {feature} works flawlessly. Genuine product!",
        "Premium quality! {feature} is outstanding. Better than branded ones.",
        "Highly satisfied with my purchase! {feature} is perfect. Fast delivery too!",
        "Worth every penny! {feature} works great. Family loved it!",
        "Best choice for {use_case}! {feature} is excellent. Recommend to everyone!",
        "Five stars well deserved! {feature} is top quality. No regrets!",
        "Superb product! {feature} exceeded expectations. Will order more!",
        "Fantastic! {feature} works like a charm. Best purchase this year!",
        "Amazing value! {feature} is brilliant. Can't believe the price!"
    ],
    4: [
        "Good product overall. {feature} works well. Minor improvements needed in {area}.",
        "Pretty satisfied! {feature} is good but {area} could be better.",
        "Nice purchase. {feature} is decent. Good value for money.",
        "Recommended! {feature} works fine. Small issue with {area}.",
        "Happy with purchase. {feature} is good quality. Worth buying.",
        "Solid product! {feature} performs well. Just the {area} needs work.",
        "Great buy! {feature} is reliable. Would give 5 stars if {area} was better.",
        "Very good! {feature} works smoothly. Only concern is {area}.",
        "Satisfied customer! {feature} is impressive. {area} is average though.",
        "Nice quality! {feature} is effective. {area} could be improved.",
        "Good for {use_case}! {feature} is fine. {area} is okay-ish.",
        "Pleased with it! {feature} meets expectations. {area} is manageable.",
        "Worth it! {feature} is solid. Just wish {area} was better.",
        "Recommended product! {feature} works nicely. {area} is acceptable.",
        "Good purchase! {feature} is quality stuff. {area} needs attention."
    ],
    3: [
        "Average product. {feature} is okay but {area} needs improvement.",
        "It's fine for the price. {feature} works but not great in {area}.",
        "Decent product. {feature} is acceptable. Expected more from {area}.",
        "Satisfactory. {feature} does the job but {area} disappointing.",
        "Okay-ish. {feature} works sometimes. Issues with {area}.",
        "Mixed feelings. {feature} is passable. {area} is below par.",
        "Could be better. {feature} is basic. {area} needs serious work.",
        "Just average. {feature} functions but {area} is problematic.",
        "Not impressed. {feature} is mediocre. {area} is quite poor.",
        "Fair enough. {feature} works occasionally. {area} is concerning.",
        "Neutral review. {feature} is so-so. {area} disappoints.",
        "It's alright. {feature} is functional. {area} could be much better.",
        "Medium quality. {feature} performs okay. {area} is weak point.",
        "Standard product. {feature} is reasonable. {area} needs upgrade.",
        "Nothing special. {feature} is ordinary. {area} is letdown."
    ],
    2: [
        "Not satisfied. {feature} doesn't work well. Problem with {area}.",
        "Below expectations. {feature} is poor. Major issue in {area}.",
        "Disappointed! {feature} not as advertised. {area} is terrible.",
        "Not good. {feature} barely works. {area} completely failed.",
        "Poor quality. {feature} stopped working. {area} is worst.",
        "Regret buying this! {feature} is substandard. {area} broke fast.",
        "Not recommended! {feature} malfunctions often. {area} is horrible.",
        "Waste of hard-earned money! {feature} is unreliable. {area} failed.",
        "Very disappointed! {feature} doesn't last. {area} is defective.",
        "Poor build! {feature} stopped after few days. {area} is pathetic.",
        "Bad purchase! {feature} never worked properly. {area} is useless.",
        "Not worth it! {feature} is cheap quality. {area} damaged soon.",
        "Unsatisfied customer! {feature} is faulty. {area} is disaster.",
        "Don't waste money! {feature} is inferior. {area} broke immediately.",
        "Terrible quality! {feature} fails constantly. {area} is junk."
    ],
    1: [
        "Worst purchase! {feature} completely failed. {area} is useless. Don't buy!",
        "Terrible product! {feature} doesn't work at all. {area} broke immediately.",
        "Waste of money! {feature} is fake. {area} totally defective.",
        "Horrible! {feature} stopped in 2 days. {area} is garbage.",
        "Don't buy this! {feature} is a lie. {area} completely useless.",
        "Fraud product! {feature} never worked. {area} is completely broken. Money wasted!",
        "Absolute garbage! {feature} is non-functional. {area} is pathetic. Worst purchase ever!",
        "Total scam! {feature} is false advertising. {area} stopped day one. Return it!",
        "Pathetic quality! {feature} is absolutely useless. {area} is damaged. Don't trust this!",
        "Extremely dissatisfied! {feature} failed instantly. {area} is totally defective. Avoid!",
        "Horrible experience! {feature} doesn't exist. {area} broke on arrival. Refund needed!",
        "Zero stars if possible! {feature} is complete lie. {area} is trash. Warning to all!",
        "Biggest regret! {feature} stopped working. {area} is manufactured poorly. Save your money!",
        "Awful product! {feature} is damaged. {area} is worst I've seen. Customer service zero!",
        "Complete disaster! {feature} malfunctioned immediately. {area} is junk. Returning ASAP!"
    ]
}

USE_CASES = {
    'Headphones': ['gym', 'gaming', 'commute', 'work from home', 'music production'],
    'Smartphones': ['photography', 'gaming', 'daily use', 'business', 'content creation'],
    'Laptops': ['programming', 'gaming', 'office work', 'video editing', 'student use'],
    'Mens Clothing': ['office', 'casual wear', 'party', 'gym', 'outdoor activities'],
    'Footwear': ['running', 'walking', 'gym', 'casual wear', 'sports'],
    'Kitchen Appliances': ['daily cooking', 'quick meals', 'family use', 'bachelors', 'party'],
    'Fiction': ['leisure reading', 'book club', 'gift', 'collection', 'bedtime'],
    'Fitness Equipment': ['home workout', 'weight loss', 'muscle building', 'cardio', 'yoga']
}

PROBLEM_AREAS = ['battery', 'build quality', 'connectivity', 'packaging', 'customer service',
                'durability', 'size', 'color', 'delivery', 'instructions']


def generate_product_name(category, subcategory, brand):
    """Generate highly realistic product names matching Amazon/Flipkart style"""
    
    # Realistic model names by brand and subcategory
    brand_models = {
        'Headphones': {
            'boAt': ['Airdopes', 'Rockerz', 'Bassheads'],
            'JBL': ['Tune', 'Live', 'Endurance', 'Reflect'],
            'Sony': ['WH-', 'WF-', 'WI-'],
            'OnePlus': ['Buds', 'Bullets'],
            'Realme': ['Buds Air', 'Buds'],
            'Noise': ['Buds', 'Shots'],
            'Sennheiser': ['HD', 'Momentum', 'CX'],
            'Bose': ['QuietComfort', 'SoundSport']
        },
        'Smartphones': {
            'Samsung': ['Galaxy S', 'Galaxy M', 'Galaxy A', 'Galaxy F'],
            'Xiaomi': ['Redmi Note', 'Redmi', 'Mi'],
            'Realme': ['Narzo', 'C', 'GT'],
            'OnePlus': ['Nord', 'CE'],
            'Vivo': ['Y', 'V', 'T'],
            'Oppo': ['A', 'F', 'Reno'],
            'Apple': ['iPhone'],
            'Google': ['Pixel'],
            'Motorola': ['Edge', 'G'],
            'Nothing': ['Phone'],
            'iQOO': ['Z', 'Neo'],
            'Poco': ['X', 'M', 'F', 'C']
        },
        'Laptops': {
            'HP': ['Pavilion', '14s', '15s', 'Victus'],
            'Dell': ['Inspiron', 'Vostro', 'XPS'],
            'Lenovo': ['IdeaPad', 'ThinkPad', 'ThinkBook', 'LOQ'],
            'ASUS': ['VivoBook', 'TUF Gaming', 'ROG', 'Zenbook'],
            'Acer': ['Aspire', 'Swift', 'Nitro'],
            'MSI': ['Modern', 'Prestige', 'GF'],
            'Apple': ['MacBook Air', 'MacBook Pro']
        }
    }
    
    # Get brand-specific models or use generic
    models = brand_models.get(subcategory, {}).get(brand, [brand])
    base_model = random.choice(models) if models else brand
    
    # Generate realistic product names by subcategory
    if subcategory == 'Headphones':
        number = random.randint(121, 989)
        if brand == 'Sony':
            return f"{brand} {base_model}{number}XM{random.randint(3,5)}"
        return f"{brand} {base_model} {number}"
    
    elif subcategory == 'Smartphones':
        if brand == 'Apple':
            version = random.choice([13, 14, 15, 16])
            variant = random.choice(['', 'Plus', 'Pro', 'Pro Max'])
            return f"Apple iPhone {version} {variant}".strip()
        elif brand == 'Samsung':
            number = random.choice([12, 13, 14, 23, 24, 33, 34, 51, 52, 53])
            variant = random.choice(['', '5G'])
            return f"Samsung {base_model}{number} {variant}".strip()
        else:
            number = random.randint(10, 99)
            variant = random.choice(['', '5G', 'Pro'])
            return f"{brand} {base_model} {number} {variant}".strip()
    
    elif subcategory == 'Laptops':
        if brand == 'Apple':
            chip = random.choice(['M1', 'M2', 'M3'])
            size = random.choice(['13-inch', '15-inch'])
            return f"Apple {base_model} {chip} {size}"
        else:
            gen = random.choice(['11th Gen', '12th Gen', '13th Gen', 'Ryzen 5', 'Ryzen 7'])
            ram = random.choice(['8GB', '16GB'])
            return f"{brand} {base_model} {gen} Intel Core i5 {ram} RAM"
    
    elif subcategory == 'Smart Watches':
        if brand == 'Apple':
            series = random.choice([7, 8, 9, 'SE', 'Ultra'])
            return f"Apple Watch Series {series}"
        number = random.randint(1, 9)
        variant = random.choice(['Pro', 'Plus', 'Ultra', ''])
        return f"{brand} {base_model} {number} {variant}".strip()
    
    elif subcategory in ['Mens Clothing', 'Womens Clothing']:
        style = random.choice(['Slim Fit', 'Regular Fit', 'Casual', 'Formal', 'Printed', 'Solid'])
        item = random.choice(['Shirt', 'T-Shirt', 'Polo', 'Jeans', 'Trousers'])
        return f"{brand} {style} {item}"
    
    elif subcategory == 'Footwear':
        line = random.choice(['Running', 'Walking', 'Casual', 'Sports', 'Sneakers'])
        return f"{brand} {line} Shoes"
    
    elif subcategory == 'Fiction':
        titles = [
            'The Silent Patient', 'The Midnight Library', 'Atomic Habits',
            'The Psychology of Money', 'Rich Dad Poor Dad', 'Think Like a Monk',
            'The Alchemist', 'Life of Pi', 'The White Tiger'
        ]
        return random.choice(titles)
    
    else:
        # Generic naming for other categories
        number = random.randint(100, 999)
        return f"{brand} {subcategory} {number}"


def generate_product_description(subcategory, features):
    """Generate product description"""
    return f"Premium {subcategory.lower()} with {', '.join(features[:3])}. Perfect for daily use."


def generate_specifications(subcategory, features):
    """Generate realistic product specifications based on subcategory"""
    specs = {}
    
    if subcategory == 'Headphones':
        specs = {
            'battery_life': f"{random.choice([6, 8, 10, 12, 16, 20, 24, 32, 40, 48, 60, 72])}h",
            'connectivity': random.choice(['Bluetooth 5.0', 'Bluetooth 5.1', 'Bluetooth 5.2', 'Bluetooth 5.3']),
            'driver_size': f"{random.choice([6, 8, 10, 13, 40, 50])}mm",
            'weight': f"{random.randint(30, 280)}g",
            'charging_time': f"{random.choice([1, 1.5, 2, 2.5, 3])}h",
            'impedance': f"{random.choice([16, 32, 64])}Ω"
        }
    elif subcategory == 'Smartphones':
        specs = {
            'ram': random.choice(['4GB', '6GB', '8GB', '12GB', '16GB']),
            'storage': random.choice(['64GB', '128GB', '256GB', '512GB', '1TB']),
            'battery': f"{random.randint(3000, 6000)}mAh",
            'display': random.choice(['6.1"', '6.3"', '6.4"', '6.5"', '6.67"', '6.7"', '6.8"']),
            'rear_camera': random.choice(['12MP', '48MP', '50MP', '64MP', '108MP', '200MP']),
            'front_camera': random.choice(['8MP', '12MP', '16MP', '20MP', '32MP']),
            'processor': random.choice(['Snapdragon 695', 'Snapdragon 778G', 'Snapdragon 8+ Gen 1', 'Dimensity 8100', 'Dimensity 9000', 'A15 Bionic', 'A16 Bionic']),
            'refresh_rate': random.choice(['60Hz', '90Hz', '120Hz', '144Hz'])
        }
    elif subcategory == 'Laptops':
        specs = {
            'processor': random.choice(['Intel Core i3 11th Gen', 'Intel Core i5 12th Gen', 'Intel Core i5 13th Gen', 'Intel Core i7 12th Gen', 'Intel Core i7 13th Gen', 'AMD Ryzen 5 5500U', 'AMD Ryzen 5 7530U', 'AMD Ryzen 7 5800H', 'AMD Ryzen 7 6800H', 'Apple M1', 'Apple M2', 'Apple M3']),
            'ram': random.choice(['8GB DDR4', '16GB DDR4', '16GB DDR5', '32GB DDR4', '32GB DDR5']),
            'storage': random.choice(['256GB SSD', '512GB SSD', '1TB SSD', '1TB SSD + 1TB HDD', '2TB SSD']),
            'display': random.choice(['14" FHD', '15.6" FHD', '15.6" 2K', '16" FHD', '17" FHD']),
            'graphics': random.choice(['Integrated', 'Intel Iris Xe', 'NVIDIA GTX 1650', 'NVIDIA RTX 3050', 'NVIDIA RTX 4050', 'AMD Radeon']),
            'weight': f"{random.uniform(1.2, 2.8):.1f}kg",
            'battery': f"{random.choice([45, 56, 65, 75, 80, 90, 100])}Wh"
        }
    elif subcategory == 'Smart Watches':
        specs = {
            'display_size': random.choice(['1.32"', '1.43"', '1.52"', '1.69"', '1.75"', '1.83"']),
            'battery_life': f"{random.choice([3, 5, 7, 10, 14, 21, 30])} days",
            'water_resistance': random.choice(['IP67', 'IP68', '5ATM', '10ATM']),
            'sensors': f"{random.randint(8, 24)} sensors",
            'strap_material': random.choice(['Silicone', 'Leather', 'Metal', 'Fabric']),
            'compatible_os': random.choice(['Android & iOS', 'Android Only', 'iOS Only'])
        }
    elif subcategory == 'Tablets':
        specs = {
            'display': random.choice(['8"', '10.1"', '10.4"', '10.9"', '11"', '12.9"']),
            'ram': random.choice(['3GB', '4GB', '6GB', '8GB', '12GB']),
            'storage': random.choice(['32GB', '64GB', '128GB', '256GB', '512GB']),
            'battery': f"{random.randint(6000, 11000)}mAh",
            'processor': random.choice(['Snapdragon 680', 'Snapdragon 870', 'MediaTek Helio G99', 'Apple A14', 'Apple M1']),
            'rear_camera': random.choice(['8MP', '12MP', '13MP']),
            'front_camera': random.choice(['5MP', '8MP', '12MP'])
        }
    elif subcategory == 'Power Banks':
        specs = {
            'capacity': random.choice(['10000mAh', '20000mAh', '30000mAh', '40000mAh', '50000mAh']),
            'input': random.choice(['5V/2A', '5V/2.4A', '9V/2A', '12V/1.5A']),
            'output': random.choice(['5V/2.1A', '5V/2.4A', '5V/3A', '9V/2A', '12V/1.5A']),
            'ports': random.choice(['1 USB', '2 USB', '3 USB', '2 USB + 1 Type-C', '3 USB + 1 Type-C']),
            'weight': f"{random.randint(180, 500)}g",
            'charging_time': f"{random.choice([4, 5, 6, 7, 8, 10])} hours"
        }
    elif subcategory == 'Cameras':
        specs = {
            'megapixels': random.choice(['16MP', '20MP', '24MP', '26MP', '32MP', '45MP', '50MP']),
            'sensor_type': random.choice(['APS-C', 'Full Frame', 'Micro Four Thirds']),
            'iso_range': random.choice(['100-12800', '100-25600', '100-51200', '100-102400']),
            'video_recording': random.choice(['Full HD 60fps', '4K 30fps', '4K 60fps', '6K 30fps']),
            'lens_mount': random.choice(['EF', 'RF', 'Z', 'E', 'FE', 'MFT']),
            'screen_size': random.choice(['3.0"', '3.2"', '3.5"'])
        }
    elif subcategory == 'Televisions':
        specs = {
            'screen_size': random.choice(['32"', '40"', '43"', '50"', '55"', '65"', '75"', '85"']),
            'resolution': random.choice(['Full HD', '4K UHD', '8K UHD']),
            'display_type': random.choice(['LED', 'QLED', 'OLED', 'NanoCell']),
            'refresh_rate': random.choice(['60Hz', '120Hz']),
            'smart_tv': random.choice(['Android TV', 'Google TV', 'WebOS', 'Tizen']),
            'hdmi_ports': random.choice([2, 3, 4]),
            'sound_output': random.choice(['20W', '30W', '40W', '60W'])
        }
    elif subcategory in ['Mens Clothing', 'Womens Clothing']:
        specs = {
            'material': random.choice(['100% Cotton', 'Cotton Blend', 'Polyester', 'Silk', 'Linen', 'Rayon']),
            'fit': random.choice(['Slim Fit', 'Regular Fit', 'Relaxed Fit', 'Tailored Fit']),
            'pattern': random.choice(['Solid', 'Striped', 'Checked', 'Printed', 'Floral']),
            'care': random.choice(['Machine Wash', 'Hand Wash', 'Dry Clean Only']),
            'sizes': 'S, M, L, XL, XXL'
        }
    elif subcategory == 'Footwear':
        specs = {
            'outer_material': random.choice(['Mesh', 'Synthetic', 'Leather', 'Canvas']),
            'sole_material': random.choice(['Rubber', 'EVA', 'PU', 'Phylon']),
            'closure': random.choice(['Lace-Up', 'Velcro', 'Slip-On', 'Zip']),
            'sizes': f"{random.choice(['6-11', '7-12', '8-13'])} UK",
            'heel_type': random.choice(['Flat', 'Low', 'High']),
            'water_resistant': random.choice(['Yes', 'No'])
        }
    elif subcategory == 'Watches':
        specs = {
            'dial_shape': random.choice(['Round', 'Square', 'Rectangular']),
            'strap_material': random.choice(['Leather', 'Metal', 'Silicone', 'Fabric']),
            'movement': random.choice(['Analog', 'Digital', 'Analog-Digital']),
            'water_resistance': random.choice(['30m', '50m', '100m', '200m']),
            'glass': random.choice(['Mineral', 'Sapphire', 'Acrylic']),
            'warranty': random.choice(['1 Year', '2 Years', '3 Years'])
        }
    elif subcategory == 'Bags':
        specs = {
            'material': random.choice(['Polyester', 'Nylon', 'Canvas', 'Leather']),
            'capacity': random.choice(['15L', '20L', '25L', '30L', '35L', '40L']),
            'compartments': random.choice([1, 2, 3, 4, 5]),
            'laptop_size': random.choice(['None', 'Up to 14"', 'Up to 15.6"', 'Up to 17"']),
            'weight': f"{random.randint(300, 1500)}g",
            'warranty': random.choice(['6 Months', '1 Year', '2 Years', '3 Years'])
        }
    elif subcategory == 'Sunglasses':
        specs = {
            'frame_material': random.choice(['Plastic', 'Metal', 'Acetate', 'TR90']),
            'lens_material': random.choice(['Polycarbonate', 'CR-39', 'Glass']),
            'uv_protection': random.choice(['UV400', 'UV380', '100% UV Protection']),
            'polarized': random.choice(['Yes', 'No']),
            'frame_color': random.choice(['Black', 'Brown', 'Blue', 'Silver', 'Gold']),
            'warranty': random.choice(['6 Months', '1 Year', '2 Years'])
        }
    elif subcategory == 'Kitchen Appliances':
        specs = {
            'power': random.choice(['300W', '500W', '750W', '1000W', '1200W', '1500W', '1800W']),
            'capacity': random.choice(['0.5L', '1L', '1.5L', '2L', '3L', '5L']),
            'material': random.choice(['Stainless Steel', 'Plastic', 'Glass', 'Aluminium']),
            'warranty': random.choice(['1 Year', '2 Years', '5 Years']),
            'voltage': '220-240V',
            'certifications': random.choice(['ISI Certified', 'BEE 5 Star', 'BEE 4 Star', 'BEE 3 Star'])
        }
    elif subcategory == 'Home Decor':
        specs = {
            'material': random.choice(['Metal', 'Wood', 'Plastic', 'Glass', 'Ceramic']),
            'color': random.choice(['White', 'Black', 'Gold', 'Silver', 'Multi-color']),
            'dimensions': f"{random.randint(10, 100)}cm x {random.randint(10, 100)}cm",
            'weight': f"{random.randint(100, 5000)}g",
            'warranty': random.choice(['6 Months', '1 Year', '2 Years'])
        }
    elif subcategory == 'Furniture':
        specs = {
            'material': random.choice(['Solid Wood', 'Engineered Wood', 'Metal', 'Plastic', 'Particleboard']),
            'finish': random.choice(['Matte', 'Glossy', 'Natural Wood', 'Lacquered']),
            'color': random.choice(['Brown', 'Black', 'White', 'Natural', 'Walnut']),
            'assembly': random.choice(['Pre-assembled', 'DIY - Easy Assembly', 'DIY - Moderate Assembly']),
            'warranty': random.choice(['1 Year', '2 Years', '3 Years', '5 Years']),
            'weight_capacity': f"{random.choice([50, 75, 100, 150, 200])}kg"
        }
    elif subcategory == 'Bedding':
        specs = {
            'material': random.choice(['Cotton', '100% Cotton', 'Microfiber', 'Silk', 'Polyester']),
            'thread_count': random.choice([144, 180, 200, 250, 300, 400]),
            'size': random.choice(['Single', 'Double', 'Queen', 'King']),
            'care': random.choice(['Machine Wash', 'Hand Wash']),
            'color': random.choice(['White', 'Beige', 'Blue', 'Grey', 'Multi-color']),
            'warranty': random.choice(['3 Months', '6 Months', '1 Year'])
        }
    elif subcategory == 'Cookware':
        specs = {
            'material': random.choice(['Aluminium', 'Stainless Steel', 'Hard Anodized', 'Cast Iron']),
            'coating': random.choice(['Non-Stick', 'PFOA Free Non-Stick', 'Ceramic', 'None']),
            'compatible_with': random.choice(['Gas Only', 'Induction Only', 'Gas & Induction']),
            'capacity': random.choice(['1.5L', '2L', '3L', '5L', '7L']),
            'warranty': random.choice(['1 Year', '2 Years', '5 Years']),
            'dishwasher_safe': random.choice(['Yes', 'No'])
        }
    elif subcategory in ['Fiction', 'Non-Fiction', 'Children Books', 'Academic']:
        specs = {
            'binding': random.choice(['Paperback', 'Hardcover']),
            'pages': random.randint(100, 800),
            'language': random.choice(['English', 'Hindi', 'English & Hindi']),
            'publisher': random.choice(['Penguin', 'HarperCollins', 'Scholastic', 'Bloomsbury', 'Rupa']),
            'isbn': f"978-{random.randint(1000000000, 9999999999)}",
            'dimensions': f"{random.randint(12, 25)}cm x {random.randint(15, 30)}cm"
        }
    elif subcategory == 'Fitness Equipment':
        specs = {
            'material': random.choice(['Steel', 'Plastic', 'Rubber', 'Foam', 'PVC']),
            'weight': f"{random.choice([1, 2, 5, 10, 15, 20, 25])}kg" if random.random() > 0.5 else 'Lightweight',
            'dimensions': f"{random.randint(20, 200)}cm x {random.randint(20, 150)}cm",
            'max_weight_capacity': f"{random.choice([80, 100, 120, 150, 200])}kg",
            'warranty': random.choice(['6 Months', '1 Year', '2 Years']),
            'assembly': random.choice(['Pre-assembled', 'Easy DIY', 'Professional Installation'])
        }
    elif subcategory == 'Sports Gear':
        specs = {
            'material': random.choice(['Synthetic', 'Leather', 'Rubber', 'Composite']),
            'size': random.choice(['Size 5', 'Size 6', 'Standard', 'Junior', 'Senior']),
            'weight': f"{random.randint(100, 500)}g",
            'color': random.choice(['Red', 'Blue', 'Yellow', 'Green', 'Multi-color']),
            'warranty': random.choice(['3 Months', '6 Months', '1 Year']),
            'certification': random.choice(['ISI Certified', 'BCCI Approved', 'FIFA Approved', 'BWF Approved'])
        }
    elif subcategory == 'Cycling':
        specs = {
            'frame_material': random.choice(['Alloy', 'Steel', 'Carbon Fiber', 'Aluminium']),
            'wheel_size': random.choice(['20"', '24"', '26"', '27.5"', '29"']),
            'gears': random.choice(['Single Speed', '7 Speed', '14 Speed', '21 Speed', '27 Speed']),
            'brake_type': random.choice(['Disc Brake', 'V-Brake', 'Caliper Brake']),
            'weight': f"{random.randint(10, 18)}kg",
            'ideal_for': random.choice(['Adults', 'Kids 5-8 yrs', 'Kids 8-12 yrs', 'Teens 12+ yrs'])
        }
    elif subcategory == 'Swimming':
        specs = {
            'material': random.choice(['Polyester', 'Nylon', 'Silicone', 'Rubber']),
            'size': random.choice(['XS', 'S', 'M', 'L', 'XL', 'Free Size']),
            'color': random.choice(['Black', 'Blue', 'Red', 'Green', 'Multi-color']),
            'ideal_for': random.choice(['Men', 'Women', 'Kids', 'Unisex']),
            'care': 'Rinse after use, Dry in shade',
            'warranty': random.choice(['No Warranty', '3 Months', '6 Months'])
        }
    elif subcategory == 'Skincare':
        specs = {
            'skin_type': random.choice(['All Skin Types', 'Oily', 'Dry', 'Combination', 'Sensitive']),
            'quantity': random.choice(['50ml', '100ml', '150ml', '200ml', '250ml']),
            'key_ingredients': random.choice(['Vitamin C', 'Niacinamide', 'Hyaluronic Acid', 'Retinol', 'Natural Extracts']),
            'spf': random.choice(['No SPF', 'SPF 15', 'SPF 30', 'SPF 50', 'SPF 50+']),
            'expiry': f"{random.choice([12, 18, 24, 36])} months from manufacturing",
            'cruelty_free': random.choice(['Yes', 'No'])
        }
    elif subcategory == 'Haircare':
        specs = {
            'hair_type': random.choice(['All Hair Types', 'Oily', 'Dry', 'Damaged', 'Color Treated']),
            'quantity': random.choice(['100ml', '200ml', '300ml', '500ml', '650ml']),
            'fragrance': random.choice(['Floral', 'Citrus', 'Fresh', 'Herbal', 'Mild']),
            'key_benefit': random.choice(['Anti-Dandruff', 'Hair Fall Control', 'Volume', 'Smoothing', 'Repair']),
            'paraben_free': random.choice(['Yes', 'No']),
            'sulfate_free': random.choice(['Yes', 'No'])
        }
    elif subcategory == 'Fragrances':
        specs = {
            'quantity': random.choice(['100ml', '120ml', '150ml', '200ml', '250ml']),
            'fragrance_type': random.choice(['Woody', 'Floral', 'Citrus', 'Oriental', 'Fresh']),
            'ideal_for': random.choice(['Men', 'Women', 'Unisex']),
            'longevity': random.choice(['4-6 hours', '6-8 hours', '8-10 hours', '10+ hours']),
            'type': random.choice(['Perfume', 'Eau de Parfum', 'Eau de Toilette', 'Deodorant', 'Body Spray']),
            'alcohol_content': random.choice(['High', 'Medium', 'Low', 'Alcohol Free'])
        }
    elif subcategory == 'Makeup':
        specs = {
            'shade_count': random.choice(['Single Shade', '3 Shades', '5 Shades', '10 Shades', '20 Shades']),
            'finish': random.choice(['Matte', 'Glossy', 'Satin', 'Shimmer', 'Natural']),
            'quantity': random.choice(['1g', '3g', '5g', '10g', '15g', '30ml']),
            'spf': random.choice(['No SPF', 'SPF 15', 'SPF 20', 'SPF 30']),
            'cruelty_free': random.choice(['Yes', 'No']),
            'waterproof': random.choice(['Yes', 'No'])
        }
    elif subcategory == 'Toys':
        specs = {
            'material': random.choice(['Plastic', 'Wood', 'Metal', 'Fabric', 'Mixed']),
            'age_group': random.choice(['0-1 years', '1-3 years', '3-5 years', '5-8 years', '8+ years']),
            'battery_required': random.choice(['Yes (not included)', 'Yes (included)', 'No']),
            'weight': f"{random.randint(100, 2000)}g",
            'safety_certified': random.choice(['BIS Certified', 'CE Certified', 'EN71 Certified']),
            'assembly': random.choice(['No Assembly', 'Easy Assembly', 'Adult Assembly Required'])
        }
    elif subcategory == 'Video Games':
        specs = {
            'connectivity': random.choice(['Wired', 'Wireless', 'Bluetooth', '2.4GHz Wireless']),
            'compatibility': random.choice(['PC Only', 'Console Only', 'PC & Console', 'Universal']),
            'dpi': random.choice(['800', '1200', '1600', '3200', '6400', '12000', '16000']),
            'buttons': random.choice([4, 6, 8, 12, 16]),
            'battery_life': random.choice(['N/A (Wired)', '20 hours', '30 hours', '40 hours', '50+ hours']),
            'warranty': random.choice(['6 Months', '1 Year', '2 Years'])
        }
    elif subcategory == 'Outdoor Games':
        specs = {
            'material': random.choice(['Plastic', 'Nylon', 'Rubber', 'Foam', 'Fabric']),
            'age_group': random.choice(['3+ years', '5+ years', '8+ years', '12+ years', 'All Ages']),
            'players': random.choice(['1+', '2+', '2-4', '4+', '6+']),
            'weight': f"{random.randint(50, 800)}g",
            'weather_resistant': random.choice(['Yes', 'No']),
            'warranty': random.choice(['No Warranty', '3 Months', '6 Months'])
        }
    elif subcategory == 'Car Accessories':
        specs = {
            'material': random.choice(['Plastic', 'Leather', 'Fabric', 'Metal', 'Silicone']),
            'compatible_with': random.choice(['Universal', 'Sedan', 'SUV', 'Hatchback', 'Specific Models']),
            'color': random.choice(['Black', 'Grey', 'Beige', 'Brown']),
            'warranty': random.choice(['6 Months', '1 Year', '2 Years']),
            'installation': random.choice(['Easy DIY', 'Professional Required']),
            'weather_resistant': random.choice(['Yes', 'No'])
        }
    elif subcategory == 'Bike Accessories':
        specs = {
            'material': random.choice(['ABS', 'Polycarbonate', 'Carbon Fiber', 'Leather']),
            'size': random.choice(['S', 'M', 'L', 'XL', 'XXL', 'Universal']),
            'color': random.choice(['Black', 'Red', 'Blue', 'White', 'Multi-color']),
            'certification': random.choice(['ISI Certified', 'DOT Certified', 'ECE Certified']),
            'warranty': random.choice(['6 Months', '1 Year', '2 Years']),
            'weight': f"{random.randint(200, 1500)}g"
        }
    elif subcategory == 'Bike Care':
        specs = {
            'quantity': random.choice(['100ml', '200ml', '500ml', '1L']),
            'type': random.choice(['Liquid', 'Spray', 'Gel', 'Cream']),
            'application': random.choice(['Direct Apply', 'Spray & Wipe', 'Apply with Cloth']),
            'finish': random.choice(['Glossy', 'Matte', 'Natural']),
            'protection_duration': random.choice(['1 Month', '3 Months', '6 Months']),
            'eco_friendly': random.choice(['Yes', 'No'])
        }
    elif subcategory == 'Supplements':
        specs = {
            'quantity': random.choice(['250g', '500g', '1kg', '2kg', '30 Tablets', '60 Tablets', '90 Capsules']),
            'flavor': random.choice(['Chocolate', 'Vanilla', 'Strawberry', 'Unflavored', 'Mango', 'Mixed Fruit']),
            'protein_per_serving': random.choice(['20g', '24g', '25g', '30g']),
            'servings': random.choice([30, 60, 75, 100]),
            'vegetarian': random.choice(['Yes', 'No']),
            'certification': random.choice(['FSSAI Approved', 'GMP Certified', 'ISO Certified'])
        }
    elif subcategory == 'Medical Devices':
        specs = {
            'type': random.choice(['Digital', 'Automatic', 'Manual']),
            'accuracy': random.choice(['±2%', '±3%', '±5%']),
            'display': random.choice(['LCD', 'LED', 'Digital']),
            'memory': random.choice(['No Memory', '20 Readings', '50 Readings', '100 Readings']),
            'power_source': random.choice(['Battery', 'Rechargeable Battery', 'AC Adapter']),
            'warranty': random.choice(['1 Year', '2 Years', '3 Years', '5 Years'])
        }
    elif subcategory == 'Ayurvedic':
        specs = {
            'quantity': random.choice(['100g', '250g', '500g', '1kg', '200ml', '500ml']),
            'type': random.choice(['Powder', 'Liquid', 'Tablet', 'Capsule', 'Paste']),
            'key_ingredients': random.choice(['Amla', 'Giloy', 'Ashwagandha', 'Tulsi', 'Triphala', 'Mixed Herbs']),
            'ideal_for': random.choice(['Men', 'Women', 'Kids', 'All']),
            'ayush_approved': 'Yes',
            'expiry': f"{random.choice([12, 18, 24, 36])} months"
        }
    elif subcategory == 'Stationery':
        specs = {
            'pack_size': random.choice(['1 Piece', 'Pack of 5', 'Pack of 10', 'Pack of 20', 'Pack of 50']),
            'color': random.choice(['Blue', 'Black', 'Red', 'Multi-color', 'Assorted']),
            'pages': random.choice([60, 100, 120, 160, 200, 240]) if 'Notebook' in subcategory else None,
            'size': random.choice(['A4', 'A5', 'Regular', 'Long']),
            'material': random.choice(['Paper', 'Plastic', 'Wood', 'Metal']),
            'warranty': random.choice(['No Warranty', '3 Months', '6 Months'])
        }
    elif subcategory == 'Office Equipment':
        specs = {
            'connectivity': random.choice(['USB', 'WiFi', 'Bluetooth', 'WiFi + USB']),
            'print_speed': random.choice(['15 ppm', '20 ppm', '25 ppm', '30 ppm', '40 ppm']) if 'Printer' in subcategory else None,
            'resolution': random.choice(['600 dpi', '1200 dpi', '2400 dpi', '4800 dpi', '1080p', '4K']),
            'compatibility': random.choice(['Windows Only', 'Mac Only', 'Windows & Mac', 'Universal']),
            'warranty': random.choice(['1 Year', '2 Years', '3 Years']),
            'power_consumption': random.choice(['5W', '10W', '20W', '50W', '100W'])
        }
    elif subcategory == 'Desk Organizers':
        specs = {
            'material': random.choice(['Plastic', 'Wood', 'Metal', 'Acrylic']),
            'compartments': random.choice([1, 2, 3, 4, 5, 6]),
            'color': random.choice(['Black', 'White', 'Brown', 'Grey', 'Multi-color']),
            'dimensions': f"{random.randint(10, 30)}cm x {random.randint(10, 30)}cm x {random.randint(5, 15)}cm",
            'weight': f"{random.randint(100, 1000)}g",
            'warranty': random.choice(['No Warranty', '3 Months', '6 Months'])
        }
    elif subcategory == 'Baby Care':
        specs = {
            'quantity': random.choice(['1 Pack', '2 Packs', '3 Packs', '50ml', '100ml', '200ml']),
            'age_group': random.choice(['0-6 months', '6-12 months', '1-2 years', 'All Ages']),
            'fragrance': random.choice(['No Fragrance', 'Mild', 'Fresh']),
            'hypoallergenic': random.choice(['Yes', 'No']),
            'paraben_free': 'Yes',
            'dermatologically_tested': 'Yes'
        }
    elif subcategory == 'Baby Gear':
        specs = {
            'age_group': random.choice(['0-6 months', '6-12 months', '1-3 years', '0-3 years']),
            'weight_capacity': f"{random.choice([10, 15, 20, 25])}kg",
            'material': random.choice(['Plastic', 'Metal', 'Fabric', 'Foam']),
            'safety_certified': 'Yes',
            'foldable': random.choice(['Yes', 'No']),
            'warranty': random.choice(['6 Months', '1 Year', '2 Years'])
        }
    elif subcategory == 'Toys & Learning':
        specs = {
            'age_group': random.choice(['0-1 years', '1-2 years', '2-3 years', '3-5 years']),
            'material': random.choice(['Plastic', 'Fabric', 'Wood', 'Foam']),
            'battery_required': random.choice(['Yes', 'No']),
            'educational_benefit': random.choice(['Motor Skills', 'Cognitive', 'Sensory', 'Language']),
            'safety_certified': 'BIS Certified',
            'washable': random.choice(['Yes', 'No'])
        }
    elif subcategory == 'Pet Food':
        specs = {
            'pet_type': random.choice(['Dog', 'Cat']),
            'age_group': random.choice(['Puppy', 'Kitten', 'Adult', 'Senior', 'All Life Stages']),
            'quantity': random.choice(['400g', '1kg', '3kg', '10kg', '15kg']),
            'flavor': random.choice(['Chicken', 'Mutton', 'Fish', 'Vegetarian', 'Mixed']),
            'protein_content': f"{random.choice([18, 22, 26, 30])}%",
            'grain_free': random.choice(['Yes', 'No'])
        }
    elif subcategory == 'Pet Accessories':
        specs = {
            'pet_type': random.choice(['Dog', 'Cat', 'Both']),
            'size': random.choice(['Small', 'Medium', 'Large', 'Universal']),
            'material': random.choice(['Nylon', 'Leather', 'Plastic', 'Rubber', 'Stainless Steel']),
            'color': random.choice(['Black', 'Red', 'Blue', 'Brown', 'Multi-color']),
            'adjustable': random.choice(['Yes', 'No']),
            'warranty': random.choice(['No Warranty', '3 Months', '6 Months'])
        }
    else:
        specs = {
            'material': random.choice(['Plastic', 'Metal', 'Wood', 'Fabric']),
            'color': random.choice(['Black', 'White', 'Silver', 'Multi-color']),
            'warranty': random.choice(['6 Months', '1 Year', '2 Years'])
        }
    
    return specs


def generate_price_history(base_price, days=90):
    """Generate realistic price history with trends and fluctuations for Price Tracker Agent"""
    history = []
    current_date = datetime.now() - timedelta(days=days)
    current_price = base_price
    
    # Random price trend pattern
    trend_type = random.choice([
        'stable',           # 40% - Mostly stable with minor fluctuations
        'stable',           # (doubled for higher probability)
        'gradual_decrease', # 20% - Gradual price decrease (sale/clearance)
        'fluctuating',      # 20% - Regular ups and downs
        'flash_sale',       # 10% - Sudden drops and recovery
        'gradual_increase'  # 10% - Gradual price increase (demand/inflation)
    ])
    
    for day in range(days + 1):
        current_day_date = current_date + timedelta(days=day)
        
        # Apply trend-based price changes
        if trend_type == 'stable':
            # Minor random fluctuations (±3%)
            if random.random() < 0.08:  # 8% chance of small change
                change = random.uniform(-0.03, 0.03)
                current_price = max(base_price * 0.95, min(base_price * 1.05, 
                                   current_price * (1 + change)))
        
        elif trend_type == 'gradual_decrease':
            # Gradual decrease over time (simulating clearance/end of season)
            if random.random() < 0.15:  # 15% chance of decrease
                change = random.uniform(-0.08, -0.02)  # 2-8% decrease
                current_price = max(base_price * 0.65, current_price * (1 + change))
            # Occasional small increase
            elif random.random() < 0.03:
                current_price = min(base_price * 0.95, current_price * 1.02)
        
        elif trend_type == 'fluctuating':
            # Regular price fluctuations (simulating dynamic pricing)
            if random.random() < 0.20:  # 20% chance of change
                change = random.uniform(-0.12, 0.08)  # -12% to +8%
                current_price = max(base_price * 0.75, min(base_price * 1.15, 
                                   current_price * (1 + change)))
        
        elif trend_type == 'flash_sale':
            # Flash sale pattern - sudden drops on specific days
            if day in [15, 16, 45, 46, 75, 76]:  # Sale days
                current_price = base_price * random.uniform(0.60, 0.75)  # 25-40% off
            elif day in [17, 47, 77]:  # Post-sale recovery
                current_price = base_price * random.uniform(0.85, 0.95)
            elif random.random() < 0.05:  # Random minor changes
                current_price = base_price * random.uniform(0.95, 1.05)
        
        elif trend_type == 'gradual_increase':
            # Gradual price increase (simulating high demand/inflation)
            if random.random() < 0.12:  # 12% chance of increase
                change = random.uniform(0.01, 0.05)  # 1-5% increase
                current_price = min(base_price * 1.25, current_price * (1 + change))
        
        # Special event-based pricing (festive sales simulation)
        # Diwali/Festival sales (around day 30-35)
        if 30 <= day <= 35:
            current_price = current_price * random.uniform(0.80, 0.90)  # 10-20% off
        
        history.append({
            'date': current_day_date,
            'price': round(current_price, 2)
        })
    
    return history


def generate_reviews(product_name, features, subcategory, num_reviews=5):
    """Generate realistic reviews"""
    reviews = []
    
    # Rating distribution (more 4-5 stars, fewer 1-2 stars)
    rating_weights = [5, 15, 20, 30, 30]  # 1-star to 5-star
    
    for _ in range(num_reviews):
        rating = random.choices([1, 2, 3, 4, 5], weights=rating_weights)[0]
        template = random.choice(REVIEW_TEMPLATES[rating])
        
        feature = random.choice(features)
        use_case = random.choice(USE_CASES.get(subcategory, ['daily use']))
        area = random.choice(PROBLEM_AREAS)
        
        review_text = template.format(
            feature=feature,
            use_case=use_case,
            area=area
        )
        
        reviews.append({
            'rating': rating,
            'text': review_text,
            'helpful_count': random.randint(0, 50),
            'verified_purchase': random.choice([True, True, True, False]),  # 75% verified
            'created_at': datetime.now() - timedelta(days=random.randint(1, 180))
        })
    
    return reviews


def generate_card_offers(product_id, product_price, product_category):
    """Generate realistic card offers, EMI, and cashback for Buy Plan Optimizer Agent"""
    offers = []
    
    # Indian bank names
    banks = ['HDFC Bank', 'ICICI Bank', 'SBI Card', 'Axis Bank', 'Kotak Mahindra', 
             'IndusInd Bank', 'Yes Bank', 'RBL Bank', 'American Express', 'Citibank']
    
    card_types = ['Credit Card', 'Debit Card', 'EMI Card']
    
    # Number of offers based on price (higher price = more offers)
    num_offers = 0
    if product_price > 50000:
        num_offers = random.randint(4, 6)  # Premium products get more offers
    elif product_price > 20000:
        num_offers = random.randint(3, 5)
    elif product_price > 5000:
        num_offers = random.randint(2, 4)
    elif product_price > 1000:
        num_offers = random.randint(1, 3)
    else:
        num_offers = random.randint(0, 2)  # Low-price items fewer offers
    
    selected_banks = random.sample(banks, min(num_offers, len(banks)))
    
    for bank in selected_banks:
        offer_type = random.choice(['instant_discount', 'cashback', 'emi', 'combo'])
        
        # Base offer structure
        offer = {
            'product_id': product_id,
            'bank_name': bank,
            'card_type': random.choice(card_types),
            'is_active': random.choice([True, True, True, False]),  # 75% active
            'valid_from': datetime.now() - timedelta(days=random.randint(1, 30)),
            'valid_till': datetime.now() + timedelta(days=random.randint(15, 90))
        }
        
        if offer_type == 'instant_discount':
            # Instant discount offers
            discount_pct = random.choice([5, 10, 15, 20]) if product_price > 5000 else random.choice([5, 10])
            offer.update({
                'offer_type': 'Instant Discount',
                'discount_percentage': discount_pct,
                'discount_amount': round(product_price * discount_pct / 100, 2),
                'min_transaction_amount': product_price * 0.8 if product_price > 10000 else None,
                'offer_description': f"Get {discount_pct}% instant discount up to ₹{int(product_price * discount_pct / 100)} on {bank} {offer['card_type']}"
            })
        
        elif offer_type == 'cashback':
            # Cashback offers
            cashback_pct = random.choice([2, 5, 10, 15])
            max_cashback = random.choice([500, 1000, 2000, 3000, 5000])
            actual_cashback = min(round(product_price * cashback_pct / 100, 2), max_cashback)
            offer.update({
                'offer_type': 'Cashback',
                'cashback_amount': actual_cashback,
                'discount_percentage': cashback_pct,
                'min_transaction_amount': 1000 if product_price > 5000 else 500,
                'offer_description': f"Get {cashback_pct}% cashback up to ₹{max_cashback} on {bank} {offer['card_type']}"
            })
        
        elif offer_type == 'emi':
            # EMI offers (only for products above ₹5000)
            if product_price >= 5000:
                # EMI tenures available
                available_tenures = []
                if product_price >= 5000:
                    available_tenures.extend(['3 months', '6 months'])
                if product_price >= 10000:
                    available_tenures.extend(['9 months', '12 months'])
                if product_price >= 25000:
                    available_tenures.extend(['18 months', '24 months'])
                
                selected_tenure = random.choice(available_tenures)
                is_no_cost = random.choice([True, False])  # 50% chance of no-cost EMI
                
                offer.update({
                    'offer_type': 'EMI',
                    'emi_tenure': selected_tenure,
                    'is_no_cost_emi': is_no_cost,
                    'min_transaction_amount': 5000,
                    'offer_description': f"{'No Cost EMI' if is_no_cost else 'EMI'} for {selected_tenure} on {bank} {offer['card_type']}"
                })
            else:
                continue  # Skip EMI for low-price products
        
        elif offer_type == 'combo':
            # Combo offers (discount + EMI or cashback + EMI)
            if product_price >= 10000:
                discount_pct = random.choice([5, 10])
                available_tenures = ['6 months', '9 months', '12 months'] if product_price >= 10000 else ['3 months', '6 months']
                
                offer.update({
                    'offer_type': 'Combo Offer',
                    'discount_percentage': discount_pct,
                    'discount_amount': round(product_price * discount_pct / 100, 2),
                    'emi_tenure': random.choice(available_tenures),
                    'is_no_cost_emi': random.choice([True, False]),
                    'min_transaction_amount': 10000,
                    'offer_description': f"{discount_pct}% discount + No Cost EMI on {bank} {offer['card_type']}"
                })
            else:
                continue
        
        offers.append(offer)
    
    # Add special platform offers
    if product_price > 2000 and random.random() < 0.3:  # 30% chance
        offers.append({
            'product_id': product_id,
            'bank_name': 'Platform Offer',
            'card_type': 'All Cards',
            'offer_type': 'Exchange Offer',
            'discount_amount': round(product_price * random.choice([0.10, 0.15, 0.20]), 2),
            'is_active': True,
            'valid_from': datetime.now() - timedelta(days=7),
            'valid_till': datetime.now() + timedelta(days=30),
            'offer_description': 'Exchange your old product and get extra discount'
        })
    
    return offers


def populate_database():
    """Populate database with comprehensive data for all 6 agents"""
    db = SessionLocal()
    
    try:
        print("\n🎯 Starting comprehensive data generation...")
        print("=" * 70)
        
        product_count = 0
        review_count = 0
        price_history_count = 0
        card_offer_count = 0
        
        for category_name, subcategories in CATEGORIES_DATA.items():
            print(f"\n📦 Category: {category_name}")
            
            for subcategory_name, data in subcategories.items():
                print(f"  └─ Subcategory: {subcategory_name}")
                
                brands = data['brands']
                features_pool = data['features']
                price_min, price_max = data['price_range']
                
                # Generate 8-12 products per subcategory for comprehensive testing
                for _ in range(random.randint(8, 12)):
                    brand = random.choice(brands)
                    features = random.sample(features_pool, min(4, len(features_pool)))
                    
                    product_name = generate_product_name(category_name, subcategory_name, brand)
                    base_price = round(random.uniform(price_min, price_max), 2)
                    
                    # Calculate MRP (5-30% higher than selling price)
                    mrp_price = round(base_price * random.uniform(1.05, 1.30), 2)
                    
                    # Generate model number
                    model_number = f"{brand[:3].upper()}-{random.randint(1000, 9999)}"
                    
                    # Create product with complete realistic data (NO NULL VALUES)
                    product = Product(
                        name=product_name,
                        brand=brand,
                        model=model_number,
                        category=category_name,
                        subcategory=subcategory_name,
                        price=base_price,
                        mrp=mrp_price,
                        description=generate_product_description(subcategory_name, features),
                        features=json.dumps(features),
                        specifications=json.dumps(generate_specifications(subcategory_name, features)),
                        rating=round(random.uniform(3.5, 4.9), 1),
                        review_count=random.randint(10, 500),
                        in_stock=random.choice([True, True, True, False]),  # 75% in stock
                        stock_quantity=random.randint(0, 100) if random.choice([True, True, True, False]) else 0,
                        image_url=f"https://example.com/images/{product_name.replace(' ', '-').lower()}.jpg"
                    )
                    
                    db.add(product)
                    db.flush()  # Get product ID
                    
                    product_count += 1
                    
                    # Generate 8-20 reviews per product for realistic distribution
                    reviews = generate_reviews(product_name, features, subcategory_name, 
                                              random.randint(8, 20))
                    
                    for review_data in reviews:
                        review = Review(
                            product_id=product.id,
                            user_id=random.randint(1, 100),  # Assume 100 users
                            rating=review_data['rating'],
                            review_text=review_data['text'],
                            helpful_count=review_data['helpful_count'],
                            verified_purchase=review_data['verified_purchase'],
                            created_at=review_data['created_at']
                        )
                        db.add(review)
                        review_count += 1
                    
                    # Generate price history (90 days) with realistic trends
                    price_history = generate_price_history(base_price)
                    
                    for price_point in price_history:
                        history = PriceHistory(
                            product_id=product.id,
                            price=price_point['price'],
                            recorded_at=price_point['date']
                        )
                        db.add(history)
                        price_history_count += 1
                    
                    # Generate card offers, EMI, and cashback (for Buy Plan Optimizer Agent)
                    card_offers = generate_card_offers(product.id, base_price, category_name)
                    
                    for offer_data in card_offers:
                        card_offer = CardOffer(**offer_data)
                        db.add(card_offer)
                        card_offer_count += 1
                
                db.commit()
        
        print("\n" + "=" * 70)
        print("✅ COMPREHENSIVE DATA GENERATION COMPLETE!")
        print("=" * 70)
        print(f"📊 Total Products:         {product_count}")
        print(f"⭐ Total Reviews:          {review_count}")
        print(f"💰 Price History Records:  {price_history_count}")
        print(f"💳 Card Offers/EMI/Cashback: {card_offer_count}")
        print(f"📈 Avg Reviews/Product:    {review_count / product_count:.1f}")
        print(f"📈 Avg Price Records/Product: {price_history_count / product_count:.1f}")
        print(f"📈 Avg Offers/Product:     {card_offer_count / product_count:.1f}")
        print(f"📂 Total Categories:       {len(CATEGORIES_DATA)}")
        print(f"📁 Total Subcategories:    {sum(len(s) for s in CATEGORIES_DATA.values())}")
        print("=" * 70)
        print("\n🎉 PRODUCTION-READY DATA - NO NULL VALUES!")
        print("\n✅ Data Completeness:")
        print(f"   ✅ Every product has: Name, Brand, Model, Category, Subcategory, Price, MRP")
        print(f"   ✅ Every product has: Features, Specifications, Rating, Review Count")
        print(f"   ✅ Every product has: {review_count / product_count:.0f} reviews (100% coverage)")
        print(f"   ✅ Every product has: {price_history_count / product_count:.0f} price records (90-day history)")
        print(f"   ✅ Most products have: {card_offer_count / product_count:.0f} bank offers")
        print("\n🤖 Agent-Specific Data:")
        print("   ✅ Product Search Agent: 600-720 products across 60+ subcategories")
        print("   ✅ Review Analyzer Agent: 7,200-14,400 diverse reviews for sentiment analysis")
        print("   ✅ Price Tracker Agent: 54,000+ price records with realistic trends & patterns")
        print("   ✅ Comparison Agent: Multiple products per category for comparison")
        print("   ✅ Buy Plan Optimizer Agent: Card offers, EMI plans, and cashback deals")
        print("   ✅ Orchestrator Agent: Complete ecosystem for multi-agent coordination")
        print("\n💡 Data Quality:")
        print("   ✅ NO NULL VALUES in critical fields")
        print("   ✅ Realistic price fluctuations (stable, trending, flash sales)")
        print("   ✅ Comprehensive review variety (positive, negative, neutral sentiments)")
        print("   ✅ Authentic specifications (real processors, features, specs)")
        print("   ✅ Banking offers from 10+ Indian banks (HDFC, ICICI, SBI, Axis, etc.)")
        print("   ✅ EMI options (3-24 months with no-cost EMI availability)")
        print("   ✅ Cashback & instant discount offers")
        print("\n👉 Next: Run 'python scripts/verify_data.py' to check data quality")
        print("=" * 70)
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        db.rollback()
    finally:
        db.close()


if __name__ == "__main__":
    populate_database()
