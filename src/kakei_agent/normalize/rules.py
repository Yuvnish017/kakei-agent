from dataclasses import dataclass

from kakei_agent.models.category import Category


@dataclass(frozen=True)
class MerchantRule:
    pattern: str
    merchant_name: str
    category: Category


CATEGORIES = {

    # ---------------------------------------------------------
    # Food & Dining
    # ---------------------------------------------------------
    "food_restaurant": Category(
        name="Food & Dining",
        subcategory="Restaurant",
    ),

    "food_fast_food": Category(
        name="Food & Dining",
        subcategory="Fast Food",
    ),

    "food_cafe": Category(
        name="Food & Dining",
        subcategory="Cafe",
    ),

    "food_desserts": Category(
        name="Food & Dining",
        subcategory="Desserts",
    ),

    "food_delivery": Category(
        name="Food & Dining",
        subcategory="Food Delivery",
    ),

    "food_drinks": Category(
        name="Food & Dining",
        subcategory="Drinks",
    ),

    # ---------------------------------------------------------
    # Groceries
    # ---------------------------------------------------------
    "groceries_supermarket": Category(
        name="Groceries",
        subcategory="Supermarket",
    ),

    "groceries_convenience": Category(
        name="Groceries",
        subcategory="Convenience Store",
    ),

    # ---------------------------------------------------------
    # Transport
    # ---------------------------------------------------------
    "transport_transit_topup": Category(
        name="Transport",
        subcategory="Transit Top-up",
    ),

    "transport_public": Category(
        name="Transport",
        subcategory="Public Transport",
    ),

    # ---------------------------------------------------------
    # Shopping
    # ---------------------------------------------------------
    "shopping_general": Category(
        name="Shopping",
        subcategory="General Shopping",
    ),

    "shopping_online": Category(
        name="Shopping",
        subcategory="Online Shopping",
    ),

    # ---------------------------------------------------------
    # Personal Care
    # ---------------------------------------------------------
    "personal_care_haircare": Category(
        name="Personal Care",
        subcategory="Haircare",
    ),

    # ---------------------------------------------------------
    # Education
    # ---------------------------------------------------------
    "education_music": Category(
        name="Education",
        subcategory="Music Lessons",
    ),

    # ---------------------------------------------------------
    # Entertainment
    # ---------------------------------------------------------
    "entertainment_recreation": Category(
        name="Entertainment",
        subcategory="Recreation",
    ),

    "entertainment_games": Category(
        name="Entertainment",
        subcategory="Games",
    ),

    # ---------------------------------------------------------
    # Subscriptions
    # ---------------------------------------------------------
    "subscriptions_digital": Category(
        name="Subscriptions",
        subcategory="Digital Services",
    ),

    "subscriptions_professional": Category(
        name="Subscriptions",
        subcategory="Professional Services",
    ),

    # ---------------------------------------------------------
    # Communication
    # ---------------------------------------------------------
    "communication_internet": Category(
        name="Communication",
        subcategory="Internet / Mobile",
    ),

    # ---------------------------------------------------------
    # Health
    # ---------------------------------------------------------
    "health": Category(
        name="Health",
        subcategory="Health & Supplements",
    ),

    # ---------------------------------------------------------
    # Financial
    # ---------------------------------------------------------
    "financial": Category(
        name="Financial",
        subcategory="Fees / Interest",
    ),

    # ---------------------------------------------------------
    # Other
    # ---------------------------------------------------------
    "other": Category(
        name="Other",
        subcategory="Uncategorized",
    ),
}


MERCHANT_RULES = [
    # ---------------------------------------------------------
    # Transport
    # ---------------------------------------------------------
    MerchantRule(
        pattern="GPﾓﾊﾞｲﾙﾊﾟｽﾓﾁﾔ-ｼﾞ",
        merchant_name="Mobile PASMO",
        category=CATEGORIES["transport_transit_topup"],
    ),

    # ---------------------------------------------------------
    # Groceries
    # ---------------------------------------------------------
    MerchantRule(
        pattern="ﾏｲﾊﾞｽｹﾂﾄ",
        merchant_name="My Basket",
        category=CATEGORIES["groceries_supermarket"],
    ),

    MerchantRule(
        pattern="ﾛｰｿﾝ",
        merchant_name="Lawson",
        category=CATEGORIES["groceries_convenience"],
    ),

    MerchantRule(
        pattern="ローソン",
        merchant_name="Lawson",
        category=CATEGORIES["groceries_convenience"],
    ),

    MerchantRule(
        pattern="ポプラ",
        merchant_name="Poplar",
        category=CATEGORIES["groceries_convenience"],
    ),

    MerchantRule(
        pattern="ミニストップ",
        merchant_name="Ministop",
        category=CATEGORIES["groceries_convenience"],
    ),

    MerchantRule(
        pattern="オーケー",
        merchant_name="OK Store",
        category=CATEGORIES["groceries_supermarket"],
    ),

    MerchantRule(
        pattern="二子玉川東急フードシ",
        merchant_name="Tokyu Food Show",
        category=CATEGORIES["groceries_supermarket"],
    ),

    MerchantRule(
        pattern="東急ストア",
        merchant_name="Tokyu Store",
        category=CATEGORIES["groceries_supermarket"],
    ),

    # ---------------------------------------------------------
    # Food & Dining
    # ---------------------------------------------------------
    MerchantRule(
        pattern="ﾛｹﾂﾄﾅｳ",
        merchant_name="Rocket Now",
        category=CATEGORIES["food_delivery"],
    ),

    MerchantRule(
        pattern="マクドナルド",
        merchant_name="McDonald's",
        category=CATEGORIES["food_fast_food"],
    ),

    MerchantRule(
        pattern="楽天カフェ",
        merchant_name="Rakuten Cafe",
        category=CATEGORIES["food_cafe"],
    ),

    MerchantRule(
        pattern="自販機サントリービバ",
        merchant_name="Suntory Vending Machine",
        category=CATEGORIES["food_drinks"],
    ),

    MerchantRule(
        pattern="ﾀｺｽﾊﾞ-",
        merchant_name="Tacos Bar",
        category=CATEGORIES["food_restaurant"],
    ),

    MerchantRule(
        pattern="テクス メクス",
        merchant_name="Tex-Mex Factory",
        category=CATEGORIES["food_restaurant"],
    ),

    MerchantRule(
        pattern="ミスタードーナツ",
        merchant_name="Mister Donut",
        category=CATEGORIES["food_desserts"],
    ),

    MerchantRule(
        pattern="インドリヨウリ",
        merchant_name="Indian Restaurant",
        category=CATEGORIES["food_restaurant"],
    ),

    MerchantRule(
        pattern="シェイクシャック",
        merchant_name="Shake Shack",
        category=CATEGORIES["food_fast_food"],
    ),

    # ---------------------------------------------------------
    # Education
    # ---------------------------------------------------------
    MerchantRule(
        pattern="ｱﾒﾘｶﾝｷﾞﾀ-ｱｶﾃﾞﾐ-",
        merchant_name="American Guitar Academy",
        category=CATEGORIES["education_music"],
    ),

    # ---------------------------------------------------------
    # Subscriptions / Digital
    # ---------------------------------------------------------
    MerchantRule(
        pattern="ﾈｯﾄﾌﾘｯｸｽ",
        merchant_name="Netflix",
        category=CATEGORIES["subscriptions_digital"],
    ),

    MerchantRule(
        pattern="LINKEDIN",
        merchant_name="LinkedIn",
        category=CATEGORIES["subscriptions_professional"],
    ),

    MerchantRule(
        pattern="GOOGLE PLAY",
        merchant_name="Google Play",
        category=CATEGORIES["subscriptions_digital"],
    ),

    # ---------------------------------------------------------
    # Personal Care
    # ---------------------------------------------------------
    MerchantRule(
        pattern="楽天ヘアサロン",
        merchant_name="Hair Salon",
        category=CATEGORIES["personal_care_haircare"],
    ),

    # ---------------------------------------------------------
    # Shopping / Health
    # ---------------------------------------------------------
    MerchantRule(
        pattern="ｱｲﾊｰﾌﾞｼﾞｬﾊﾟﾝｺﾞｳﾄﾞ",
        merchant_name="iHerb Japan",
        category=CATEGORIES["shopping_general"],
    ),

    # ---------------------------------------------------------
    # Entertainment
    # ---------------------------------------------------------
    MerchantRule(
        pattern="ムサシボウル",
        merchant_name="Musashi Bowl",
        category=CATEGORIES["entertainment_recreation"],
    ),

    MerchantRule(
        pattern="精算機タイトー",
        merchant_name="Taito",
        category=CATEGORIES["entertainment_recreation"],
    ),

    # ---------------------------------------------------------
    # Communication
    # ---------------------------------------------------------
    MerchantRule(
        pattern="ＩＩＪ",
        merchant_name="IIJ",
        category=CATEGORIES["communication_internet"],
    ),
]