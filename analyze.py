#%%
import pandas as pd
df = pd.read_csv('data/fbi_article_links_combined_20260102_170044.csv')
# %%
import pandas as pd
import re
import numpy as np

# Load the dataframe (adjust path if needed)
df = pd.read_csv('data/fbi_article_links_combined_20260102_170044.csv')  # First column is unnamed index

# Comprehensive list of apps/platforms
app_list = [
    "Ask.fm", "Among Us", "Badoo","Seeking Arrangements", "Bigo Live", "Bumble", "Calculator%", "Caffeine",
    "Chat Avenue", "Chatroulette", "Clash of Clans", "Clubhouse", "Discord", "Dropbox",
    "Facebook", "Facebook Messenger", "Fortnite", "Google Hangouts", "Grindr", "Holla",
    "Hoop", "Houseparty", "IMVU","FetLife", "Instagram", "Kik", "KiK Messenger", "Live.me",
    "Marco Polo", "MeetMe", "Minecraft", "Monkey", "Omegle", "Paltalk", "Periscope",
    "PlayStation Network", "Plenty of Fish", "Reddit", "Roblox", "Sarahah", "Signal",
    "Skout", "Skype", "Slack", "Snapchat", "Steam", "Telegram", "TikTok", "Tinder",
    "Tor", "Tumblr", "Twitch", "Twitter", "Viber", "WeChat", "WhatsApp", "Whisper",
    "Wickr", "Xbox Live", "Yubo", "Zoom", "After School", "Amino", "Azar", "Blendr",
    "Boo", "Burner", "Calculator Vault", "Call of Duty", "Cash App", "Depop", "Duo",
    "Evernote", "FaceTime", "Flickr", "Gmail", "GroupMe", "Hinge", "iMessage", "Jodel",
    "Lipsi", "Messenger", "Musical.ly", "Nextdoor", "Oovoo", "Pinterest", "QQ",
    "Rec Room", "SayHi", "Yahoo", "Sessions", "Smule", "SoundCloud", "Spotafriend", "Tango",
    "Tellonym", "TextNow", "TextPlus", "Threema", "VRChat", "Wattpad", "Wishbone",
    "Yellow", "Zello", "Zepeto", "X.com"
]
def get_app_columns(df):
    """
    Get all column names that start with 'app_' from a DataFrame.
    
    Parameters:
    -----------
    df : pd.DataFrame
        Input DataFrame
    
    Returns:
    --------
    list
        List of column names that start with 'app_'
    """
    app_columns = [col for col in df.columns if col.startswith('app_')]
    return app_columns
# Usage example:
# app_column_list = get_app_columns(df)
# print(f"Found {len(app_column_list)} app columns: {app_column_list}")
def extract_apps(text):
    if pd.isna(text):
        return []
    text = str(text)
    found = set()
    for app in app_list:
        if re.search(r'\b' + re.escape(app) + r'\b', text, re.IGNORECASE):
            found.add(app)
    if re.search(r'\b(Twitter|X\.com)\b', text, re.IGNORECASE):
        found.add("Twitter/X")
    return list(found)

df['extracted_apps'] = df['text'].apply(extract_apps)

# Create individual boolean columns for each app
def check_app_in_text(text, app_name):
    if pd.isna(text):
        return False
    text = str(text)
    return bool(re.search(r'\b' + re.escape(app_name) + r'\b', text, re.IGNORECASE))

# Create boolean columns for each app
for app in app_list:
    # Clean app name for column name (remove special characters)
    col_name = f"app_{re.sub(r'[^a-zA-Z0-9]', '_', app)}"
    df[col_name] = df['text'].apply(lambda x: check_app_in_text(x, app))

# Create list of all app column names
app_column_names = [f"app_{re.sub(r'[^a-zA-Z0-9]', '_', app)}" for app in app_list]

def extract_victim_ages(text):
    if pd.isna(text):
        return []
    text = str(text)
    ages = set()
    
    # Match patterns like "5-year-old", "12-year-old"
    matches = re.findall(r'(\d+)-year-old', text, re.IGNORECASE)
    ages.update(matches)
    
    # Match "children ages 5 and 8", "child age 12", etc. - more specific context
    matches = re.findall(r'(?:child(?:ren)?\s+age[sd]?\s+|ages?\s+)(\d{1,2})', text, re.IGNORECASE)
    ages.update(matches)
    
    # Match "under the age of X", "child under X"
    matches = re.findall(r'(?:under\s+(?:the\s+)?age\s+of|child\s+under)\s+(\d{1,2})', text, re.IGNORECASE)
    ages.update(matches)
    
    # Match age ranges like "between 5 and 8"
    matches = re.findall(r'between\s+(\d{1,2})\s+and\s+(\d{1,2})', text, re.IGNORECASE)
    for low, high in matches:
        ages.add(f"{low}-{high}")
    
    # Match specific victim age contexts
    matches = re.findall(r'(?:victims?\s+age[sd]?\s+|minors?\s+age[sd]?\s+)(\d{1,2})', text, re.IGNORECASE)
    ages.update(matches)
    
    if re.search(r'\btoddler|infant|prepubescent\b', text, re.IGNORECASE):
        ages.add("toddler/infant/prepubescent")
    return list(ages)

df['extracted_victim_ages'] = df['text'].apply(extract_victim_ages)

def extract_offender_age(text):
    if pd.isna(text):
        return None
    text = str(text)
    match = re.search(r'\((\d{1,2}),', text)
    if match:
        return match.group(1)
    match = re.search(r'\bage\s+(\d{1,2})\b', text, re.IGNORECASE)
    if match:
        return match.group(1)
    return None

df['extracted_offender_age'] = df['text'].apply(extract_offender_age)

def extract_sentence(text):
    if pd.isna(text):
        return None
    text = str(text)
    match = re.search(r'sentenced.*?(\d+)\s+(?:years?|months?)\b', text, re.IGNORECASE)
    if match:
        num = match.group(1)
        unit = "years" if "year" in text[match.end():match.end()+20].lower() else "months"
        return f"{num} {unit}"
    match = re.search(r'(\d+)\s+months?.*?prison', text, re.IGNORECASE)
    if match:
        return f"{match.group(1)} months"
    return None

df['extracted_sentence'] = df['text'].apply(extract_sentence)

# Crime types (unchanged)
crime_patterns = {
    "Production of CSAM": r'production|producing.*child.*material|sexually exploiting',
    "Possession of CSAM": r'possession|possessing.*child.*material',
    "Distribution/Receipt of CSAM": r'distribution|receipt|receiving|distributing',
    "Coercion/Enticement": r'coercion.*enticement|enticement.*minor',
    "Sextortion": r'sextortion',
    "Sexual Abuse/Contact": r'sexual abuse|abusive sexual contact|aggravated sexual abuse',
    "Travel for Illicit Conduct": r'travel.*illicit sexual conduct|transport.*minor',
    "Failure to Register": r'failure.*register.*sex offender'
}

def extract_crimes(text):
    if pd.isna(text):
        return []
    text = str(text)
    return [crime for crime, pattern in crime_patterns.items() if re.search(pattern, text, re.IGNORECASE)]

df['extracted_crimes'] = df['text'].apply(extract_crimes)

# Tactics (unchanged)
tactic_patterns = {
    "Sextortion Tactics": r'threaten.*release|extort.*images|demand.*more',
    "Online Grooming": r'communicat.*online|met.*internet|online.*conversation',
    "Group/Chat Room": r'group.*Facebook|chat room|joined.*group',
    "Moved Platforms": r'moved.*platform|communicated.*via',
    "In-Person Meeting": r'arrived.*meet|traveled.*meet|meet.*person',
    "File Sharing/Requests": r'send.*images|received.*CSAM|produced.*video'
}

def extract_tactics(text):
    if pd.isna(text):
        return []
    text = str(text)
    return [tactic for tactic, pattern in tactic_patterns.items() if re.search(pattern, text, re.IGNORECASE)]

df['extracted_tactics'] = df['text'].apply(extract_tactics)

def extract_dates(text):
    if pd.isna(text):
        return []
    text = str(text)
    dates = set()
    
    # Pattern for Month DD, YYYY (e.g., "January 15, 2025")
    month_day_year = re.findall(r'\b(?:January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{1,2},\s+\d{4}\b', text, re.IGNORECASE)
    dates.update(month_day_year)
    
    # Pattern for MM/DD/YYYY or MM-DD-YYYY
    numeric_dates = re.findall(r'\b\d{1,2}[/-]\d{1,2}[/-]\d{4}\b', text)
    dates.update(numeric_dates)
    
    # Pattern for YYYY-MM-DD (ISO format)
    iso_dates = re.findall(r'\b\d{4}-\d{1,2}-\d{1,2}\b', text)
    dates.update(iso_dates)
    
    # Pattern for Month YYYY (e.g., "January 2025")
    month_year = re.findall(r'\b(?:January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{4}\b', text, re.IGNORECASE)
    dates.update(month_year)
    
    return list(dates)

df['extracted_dates'] = df['text'].apply(extract_dates)

def extract_victim_gender(df: pd.DataFrame, text_column: str = 'text') -> pd.DataFrame:
    """
    Extracts victim gender from the specified text column in a DataFrame.
    
    Adds a new column 'victim_gender' with values:
    - 'female' if indicators like 'girl', 'girls', 'female', 'females', 'daughter' are found
    - 'male' if indicators like 'boy', 'boys', 'male', 'males', 'son' are found
    - 'unknown' if no clear gender indicator is present
    
    Parameters:
    -----------
    df : pd.DataFrame
        Input DataFrame containing the text data
    text_column : str, default 'text'
        Name of the column containing the case description text
    
    Returns:
    --------
    pd.DataFrame
        Original DataFrame with added 'victim_gender' column
    """
    # Regex pattern to capture gender indicators (singular/plural + daughter/son)
    pattern = r"\b(girls?|boys?|females?|males?|daughters?|sons?)\b"
    
    # Extract the first matching gender indicator (case-insensitive)
    indicator_series = df[text_column].str.extract(pattern, flags=re.IGNORECASE)[0]
    
    # Mapping dictionary to standardize to 'female' / 'male'
    mapping = {
        'girl': 'female',
        'girls': 'female',
        'female': 'female',
        'females': 'female',
        'daughter': 'female',
        'daughters': 'female',
        'boy': 'male',
        'boys': 'male',
        'male': 'male',
        'males': 'male',
        'son': 'male',
        'sons': 'male'
    }
    
    # Apply mapping and fill NaN with 'unknown'
    df['victim_gender'] = indicator_series.str.lower().map(mapping).fillna('unknown')
    
    return df

# Apply victim gender extraction
df = extract_victim_gender(df)

# UPDATED: extract_cities now uses the URL column to pull the FBI field office city (more consistent than text headlines)
# We map common slugs to proper city names for readability

city_mapping = {
    'houston': 'Houston',
    'tampa': 'Tampa',
    'saltlakecity': 'Salt Lake City',
    'minneapolis': 'Minneapolis',
    'baltimore': 'Baltimore',
    'sandiego': 'San Diego',
    'jackson': 'Jackson',
    'cincinnati': 'Cincinnati',
    'buffalo': 'Buffalo',
    'pittsburgh': 'Pittsburgh',
    'mobile': 'Mobile',
    'sacramento': 'Sacramento',
    'cleveland': 'Cleveland',
    'miami': 'Miami',
    'neworleans': 'New Orleans',
    'albuquerque': 'Albuquerque',
    'newark': 'Newark',
    'lasvegas': 'Las Vegas',
    'philadelphia': 'Philadelphia',
    'omaha': 'Omaha',
    'stlouis': 'St. Louis',
    'kansascity': 'Kansas City',
    'chicago': 'Chicago',
    'albany': 'Albany',
    'seattle': 'Seattle',
    'anchorage': 'Anchorage',
    'boston': 'Boston',
    'charlotte': 'Charlotte',
    'losangeles': 'Los Angeles',
    'littlerock': 'Little Rock',
    'oklahomacity': 'Oklahoma City',
    'sanantonio': 'San Antonio',
    'sanjuan': 'San Juan'
    # Add more mappings as new field offices appear in your full 3.1k dataset
}

def extract_cities(url):
    if pd.isna(url):
        return []
    url = str(url)
    match = re.search(r'field-offices/([a-zA-Z]+)/', url)
    if match:
        slug = match.group(1).lower()
        proper_name = city_mapping.get(slug, slug.replace('city', ' City').title())
        return [proper_name]
    # For national press releases (no field-offices path), return empty or could flag as 'National'
    return []

df['extracted_cities'] = df['URL'].apply(extract_cities)

# Optional: raw slug version if you need it for grouping
df['field_office_slug'] = df['URL'].apply(lambda x: re.search(r'field-offices/([a-zA-Z]+)/', str(x)).group(1).lower() if re.search(r'field-offices/([a-zA-Z]+)/', str(x)) else None)

# Save enriched dataframe
df.to_csv('enriched_grok_df.csv', index=True)

# Analysis: Top 3 most commonly mentioned apps by victim gender
print("=== TOP 3 MOST COMMONLY MENTIONED APPS BY VICTIM GENDER ===\n")

# Group by victim_gender and sum app columns
app_by_gender = df.groupby('victim_gender')[app_column_names].sum()

# Get top 3 apps for each gender
for gender in app_by_gender.index:
    print(f"VICTIM GENDER: {gender.upper()}")
    print("-" * 40)
    
    # Get the app counts for this gender and sort in descending order
    gender_apps = app_by_gender.loc[gender].sort_values(ascending=False)
    
    # Get top 3 non-zero apps
    top_apps = gender_apps[gender_apps > 0].head(3)
    
    if len(top_apps) > 0:
        for i, (app_col, count) in enumerate(top_apps.items(), 1):
            # Clean up the app name (remove 'app_' prefix and replace underscores)
            app_name = app_col.replace('app_', '').replace('_', ' ').title()
            print(f"{i}. {app_name}: {int(count)} mentions")
    else:
        print("No apps mentioned for this gender category")
    
    print()

# Also show the raw grouped data for reference
print("=== RAW GROUPED DATA (All Apps) ===")
print(app_by_gender.T.sort_values(by=list(app_by_gender.index), ascending=False))

#%%