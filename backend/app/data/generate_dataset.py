"""
Generate the skincare products CSV for SkinIntel.
Concern tags match the 4 skin types from the trained CNN model:
  oily_skin, dry_skin, normal_skin, combination_skin, general_skincare

Run: python3 -m app.data.generate_dataset
Outputs: data/products.csv
"""
import csv
import os
import random

COUNTRIES = ["IN", "US", "UK", "CA", "AU", "DE", "FR", "JP"]

PRODUCTS_BY_CONCERN = {
    "oily_skin": [
        ("Mattifying Oil-Control Gel Cleanser", "ClearSkin Labs", 449, "INR",
         "Removes excess oil without stripping the skin barrier.",
         "https://images.unsplash.com/photo-1556228453-efd6c1ff04f6?w=400"),
        ("Niacinamide 10% + Zinc Serum", "DermaGlow", 699, "INR",
         "Regulates sebum production and minimizes pore appearance.",
         "https://images.unsplash.com/photo-1571781926291-c477ebfd024b?w=400"),
        ("Oil-Free Lightweight Moisturizer", "AquaLux", 599, "INR",
         "Hydrates oily skin without adding greasiness.",
         "https://images.unsplash.com/photo-1598440947619-2c35fc9aa908?w=400"),
        ("BHA 2% Exfoliating Toner", "SkinRevive", 849, "INR",
         "Unclogs pores and dissolves blackheads with salicylic acid.",
         "https://images.unsplash.com/photo-1556228724-4f1836f8f7fd?w=400"),
        ("Mattifying SPF 50 Sunscreen", "SunGuard", 999, "INR",
         "Controls shine all day while protecting from UV rays.",
         "https://images.unsplash.com/photo-1526758097130-bab247274f58?w=400"),
        ("Clay Detox Pore Mask", "PureClay", 699, "INR",
         "Draws out impurities and minimizes pore appearance.",
         "https://images.unsplash.com/photo-1629198735660-e39ea93f5c18?w=400"),
    ],
    "dry_skin": [
        ("Ceramide Barrier Repair Moisturizer", "AquaLux", 799, "INR",
         "Locks in hydration and restores the skin barrier with ceramides.",
         "https://images.unsplash.com/photo-1556228578-8c89e6adf883?w=400"),
        ("Hyaluronic Acid Deep Hydration Serum", "GlowLeaf", 649, "INR",
         "Multi-weight HA for deep and surface hydration.",
         "https://images.unsplash.com/photo-1617897903246-719242758050?w=400"),
        ("Rich Shea Butter Night Cream", "NightGlow", 1199, "INR",
         "Intensely nourishes dry skin overnight.",
         "https://images.unsplash.com/photo-1570194065650-d99fb4bedf0a?w=400"),
        ("Squalane Facial Oil", "SkinRevive", 999, "INR",
         "Lightweight oil that mimics skin's natural sebum.",
         "https://images.unsplash.com/photo-1556228720-195a672e8a03?w=400"),
        ("Oat Milk Gentle Cream Cleanser", "CalmSkin", 499, "INR",
         "Creamy cleanser that soothes and hydrates dry skin.",
         "https://images.unsplash.com/photo-1608248597279-f99d160bfcbc?w=400"),
        ("Glycerin + Aloe Hydrating Toner", "HerbaClear", 349, "INR",
         "Alcohol-free toner that preps dry skin for moisturizer.",
         "https://images.unsplash.com/photo-1731657979854-30bb7001cc8a?w=400"),
    ],
    "normal_skin": [
        ("Gentle pH-Balanced Cleanser", "CalmSkin", 399, "INR",
         "Daily cleanser suitable for all skin types.",
         "https://images.unsplash.com/photo-1556228724-4f1836f8f7fd?w=400"),
        ("Broad Spectrum SPF 50 Gel", "SunGuard", 1099, "INR",
         "Lightweight sunscreen for daily UV protection.",
         "https://images.unsplash.com/photo-1526758097130-bab247274f58?w=400"),
        ("Vitamin C Brightening Serum", "SkinRevive", 1299, "INR",
         "Antioxidant serum for radiance and even skin tone.",
         "https://images.unsplash.com/photo-1556228578-8c89e6adf883?w=400"),
        ("Daily Hydration Moisturizer", "AquaLux", 699, "INR",
         "Balanced moisturizer for normal skin maintenance.",
         "https://images.unsplash.com/photo-1571781926291-c477ebfd024b?w=400"),
        ("Antioxidant Facial Mist", "GlowLeaf", 449, "INR",
         "Refreshing mist with green tea and vitamin E.",
         "https://images.unsplash.com/photo-1598440947619-2c35fc9aa908?w=400"),
    ],
    "combination_skin": [
        ("Balancing Gel Cleanser", "ClearSkin Labs", 449, "INR",
         "Cleanses oily zones without drying out normal or dry areas.",
         "https://images.unsplash.com/photo-1556228453-efd6c1ff04f6?w=400"),
        ("Dual-Zone Hydrating Serum", "AquaLux", 899, "INR",
         "Lightweight serum that hydrates dry areas without adding shine.",
         "https://images.unsplash.com/photo-1617897903246-719242758050?w=400"),
        ("T-Zone Control Mattifying Lotion", "DermaGlow", 749, "INR",
         "Targets oily T-zone while keeping cheeks comfortable.",
         "https://images.unsplash.com/photo-1571781926291-c477ebfd024b?w=400"),
        ("Niacinamide 5% Balance Serum", "SkinRevive", 799, "INR",
         "Balances oil production across combination skin zones.",
         "https://images.unsplash.com/photo-1556228578-8c89e6adf883?w=400"),
        ("Lightweight SPF 50 Fluid", "SunGuard", 1099, "INR",
         "Non-greasy sunscreen suitable for combination skin.",
         "https://images.unsplash.com/photo-1526758097130-bab247274f58?w=400"),
        ("Multi-Zone Clay Mask", "PureClay", 799, "INR",
         "Apply to T-zone only to absorb oil without over-drying cheeks.",
         "https://images.unsplash.com/photo-1629198735660-e39ea93f5c18?w=400"),
    ],
    "acne": [
        ("2% Salicylic Acid Foaming Cleanser", "ClearSkin Labs", 349, "INR",
         "Deep-cleans pores and removes excess oil with BHA.",
         "https://images.unsplash.com/photo-1556228453-efd6c1ff04f6?w=400"),
        ("Niacinamide + Zinc Control Serum", "DermaGlow", 899, "INR",
         "Reduces redness, regulates sebum, and minimizes breakouts.",
         "https://images.unsplash.com/photo-1571781926291-c477ebfd024b?w=400"),
        ("Oil-Free Barrier Gel Moisturizer", "AquaLux", 599, "INR",
         "Hydrates acne-prone skin without clogging pores.",
         "https://images.unsplash.com/photo-1598440947619-2c35fc9aa908?w=400"),
        ("Benzoyl Peroxide Spot Gel 2.5%", "ToneFix", 1199, "INR",
         "Targeted treatment for active acne lesions.",
         "https://images.unsplash.com/photo-1629198735660-e39ea93f5c18?w=400"),
        ("Azelaic Acid 10% Brightening Cream", "SkinRevive", 1299, "INR",
         "Reduces acne marks and evens skin tone post-breakout.",
         "https://images.unsplash.com/photo-1631214524020-6f3f80c5ea1d?w=400"),
        ("Retinoid Night Repair Gel", "NightGlow", 1899, "INR",
         "Supports smoother skin and fewer recurring breakouts.",
         "https://images.unsplash.com/photo-1556228578-8c89e6adf883?w=400"),
    ],
    "dark_circles": [
        ("Cooling Caffeine Under-Eye Roll-On", "FreshMint", 299, "INR",
         "Depuffs tired eyes with caffeine and a cooling metal roller.",
         "https://images.unsplash.com/photo-1556228720-195a672e8a03?w=400"),
        ("Hydra Bright Eye Gel", "GlowLeaf", 499, "INR",
         "Lightweight gel with aloe and niacinamide for daily hydration.",
         "https://images.unsplash.com/photo-1617897903246-719242758050?w=400"),
        ("Peptide Lift Eye Cream", "DermaGlow", 1099, "INR",
         "Peptide-rich formula that improves elasticity and firmness.",
         "https://images.unsplash.com/photo-1570194065650-d99fb4bedf0a?w=400"),
        ("Dark Circle Corrector Cream", "ToneFix", 1999, "INR",
         "Targets pigmentation with tranexamic acid and vitamin C.",
         "https://images.unsplash.com/photo-1608248597279-f99d160bfcbc?w=400"),
        ("Vitamin K Eye Serum", "EyeRevive", 799, "INR",
         "Strengthens capillaries and reduces dark discoloration.",
         "https://images.unsplash.com/photo-1731657979854-30bb7001cc8a?w=400"),
        ("Retinol Eye Renewal Cream", "NightGlow", 2499, "INR",
         "Stimulates collagen to reduce fine lines and dark circles.",
         "https://images.unsplash.com/photo-1556228578-8c89e6adf883?w=400"),
    ],
    "hyperpigmentation": [
        ("Niacinamide Tone Correct Serum", "DermaBright", 449, "INR",
         "Reduces uneven tone and supports barrier repair.",
         "https://images.unsplash.com/photo-1739987301957-fc2e1179db0a?w=400"),
        ("Alpha Arbutin Spot Fade Essence", "ToneFix", 699, "INR",
         "Targets dark spots and post-acne marks.",
         "https://images.unsplash.com/photo-1556228841-a3fdb1d8f7b3?w=400"),
        ("Vitamin C Brightening Fluid", "SkinRevive", 999, "INR",
         "Antioxidant-rich formula for dullness and pigmentation.",
         "https://images.unsplash.com/photo-1556228578-8c89e6adf883?w=400"),
        ("Tranexamic Acid Pigment Corrector", "EvenAura", 1799, "INR",
         "Focused treatment for stubborn dark patches and melasma.",
         "https://images.unsplash.com/photo-1526758097130-bab247274f58?w=400"),
        ("Kojic Acid Brightening Soap", "DermaBright", 299, "INR",
         "Daily brightening soap that fades dark spots gradually.",
         "https://images.unsplash.com/photo-1629198735660-e39ea93f5c18?w=400"),
        ("Mandelic Acid Resurfacing Serum", "SkinRevive", 1499, "INR",
         "Gentle AHA for hyperpigmentation and texture improvement.",
         "https://images.unsplash.com/photo-1571781926291-c477ebfd024b?w=400"),
    ],
    "blackheads": [
        ("BHA 2% Exfoliating Toner", "ClearSkin Labs", 549, "INR",
         "Unclogs pores and dissolves blackheads with beta hydroxy acid.",
         "https://images.unsplash.com/photo-1556228453-efd6c1ff04f6?w=400"),
        ("Charcoal Deep Cleanse Scrub", "DarkDetox", 399, "INR",
         "Activated charcoal scrub for deep pore cleansing.",
         "https://images.unsplash.com/photo-1598440947619-2c35fc9aa908?w=400"),
        ("Clay Detox Pore Mask", "PureClay", 699, "INR",
         "Draws out impurities and minimizes the appearance of pores.",
         "https://images.unsplash.com/photo-1629198735660-e39ea93f5c18?w=400"),
        ("Pore Minimizing Serum", "DermaGlow", 1199, "INR",
         "Tightens pores and controls excess sebum production.",
         "https://images.unsplash.com/photo-1571781926291-c477ebfd024b?w=400"),
        ("Retinol Pore Refining Cream", "NightGlow", 1799, "INR",
         "Refines skin texture and reduces blackhead formation.",
         "https://images.unsplash.com/photo-1556228578-8c89e6adf883?w=400"),
    ],
    "wrinkles": [
        ("Retinol 0.3% Anti-Age Serum", "NightGlow", 1599, "INR",
         "Stimulates collagen production to reduce fine lines.",
         "https://images.unsplash.com/photo-1617897903246-719242758050?w=400"),
        ("Peptide Complex Firming Cream", "DermaGlow", 2199, "INR",
         "Multi-peptide formula for firmer, plumper skin.",
         "https://images.unsplash.com/photo-1570194065650-d99fb4bedf0a?w=400"),
        ("Hyaluronic Plumping Serum", "GlowLeaf", 899, "INR",
         "Instantly plumps fine lines with deep hydration.",
         "https://images.unsplash.com/photo-1556228578-8c89e6adf883?w=400"),
        ("Vitamin C + E Antioxidant Cream", "SkinRevive", 1399, "INR",
         "Protects against free radical damage that ages skin.",
         "https://images.unsplash.com/photo-1526758097130-bab247274f58?w=400"),
        ("Bakuchiol Natural Retinol Alternative", "HerbaClear", 1799, "INR",
         "Plant-based retinol alternative for sensitive skin.",
         "https://images.unsplash.com/photo-1629198735660-e39ea93f5c18?w=400"),
        ("Collagen Boost Night Mask", "NightGlow", 2499, "INR",
         "Overnight mask that supports collagen synthesis.",
         "https://images.unsplash.com/photo-1631214524020-6f3f80c5ea1d?w=400"),
    ],
    "general_skincare": [
        ("Gentle pH-Balanced Cleanser", "CalmSkin", 399, "INR",
         "Daily cleanser suitable for all skin types.",
         "https://images.unsplash.com/photo-1556228724-4f1836f8f7fd?w=400"),
        ("Ceramide Barrier Moisturizer", "AquaLux", 799, "INR",
         "Locks hydration and supports barrier strength.",
         "https://images.unsplash.com/photo-1556228578-8c89e6adf883?w=400"),
        ("Broad Spectrum SPF 50 Gel", "SunGuard", 1099, "INR",
         "Lightweight sunscreen for daily UV protection.",
         "https://images.unsplash.com/photo-1526758097130-bab247274f58?w=400"),
        ("Vitamin C Brightening Serum", "SkinRevive", 1299, "INR",
         "Antioxidant serum for radiance and even tone.",
         "https://images.unsplash.com/photo-1571781926291-c477ebfd024b?w=400"),
        ("Hyaluronic Acid Hydrating Serum", "GlowLeaf", 649, "INR",
         "Multi-weight HA for deep and surface hydration.",
         "https://images.unsplash.com/photo-1617897903246-719242758050?w=400"),
    ],
}

STORE_URLS = {
    "amazon":   "https://www.amazon.in/s?k=",
    "nykaa":    "https://www.nykaa.com/search/result/?q=",
    "flipkart": "https://www.flipkart.com/search?q=",
}


def generate():
    os.makedirs("data", exist_ok=True)
    rows = []
    product_id = 1

    for concern, products in PRODUCTS_BY_CONCERN.items():
        for name, brand, base_price, currency, description, image_url in products:
            num_countries = random.randint(3, 6)
            countries = random.sample(COUNTRIES, num_countries)
            if "IN" not in countries:
                countries[0] = "IN"

            price = base_price + random.randint(-50, 100)
            rating = round(random.uniform(3.8, 5.0), 1)
            slug = name.lower().replace(" ", "+")

            rows.append({
                "product_id":        f"SKU{product_id:04d}",
                "name":              name,
                "brand":             brand,
                "price":             price,
                "currency":          currency,
                "rating":            rating,
                "description":       description,
                "concern_tags":      concern,
                "available_countries": ",".join(countries),
                "links_amazon":      STORE_URLS["amazon"] + slug,
                "links_nykaa":       STORE_URLS["nykaa"] + slug,
                "links_flipkart":    STORE_URLS["flipkart"] + slug,
                "image_url":         image_url,
            })
            product_id += 1

    output_path = "data/products.csv"
    fieldnames = [
        "product_id", "name", "brand", "price", "currency", "rating",
        "description", "concern_tags", "available_countries",
        "links_amazon", "links_nykaa", "links_flipkart", "image_url",
    ]

    with open(output_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    print(f"Generated {len(rows)} products → {output_path}")


if __name__ == "__main__":
    generate()
