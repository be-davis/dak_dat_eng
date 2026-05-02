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
#%%
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
        return np.nan
    text = str(text)
    ages = []
    
    # Match patterns like "5-year-old", "12-year-old" but only for reasonable child ages (1-17)
    # Also add context words to avoid matching offender ages
    matches = re.findall(r'(?:victim|child|girl|boy|minor|juvenile).*?(\d{1,2})-year-old|(\d{1,2})-year-old\s+(?:victim|child|girl|boy|minor|juvenile)', text, re.IGNORECASE)
    for match in matches:
        age = int(match[0] if match[0] else match[1])
        if age <= 17:  # Only include ages 17 and under
            ages.append(age)
    
    # Also match standalone X-year-old patterns but limit to 1-17 years
    matches = re.findall(r'(\d{1,2})-year-old', text, re.IGNORECASE)
    for match in matches:
        age = int(match)
        if age <= 17:  # Only include ages 17 and under
            ages.append(age)
    
    # Match "children ages 5 and 8", "child age 12", etc. - more specific context
    matches = re.findall(r'(?:child(?:ren)?\s+age[sd]?\s+|ages?\s+)(\d{1,2})', text, re.IGNORECASE)
    for match in matches:
        age = int(match)
        if age <= 17:
            ages.append(age)
    
    # Match "under the age of X", "child under X"
    matches = re.findall(r'(?:under\s+(?:the\s+)?age\s+of|child\s+under)\s+(\d{1,2})', text, re.IGNORECASE)
    for match in matches:
        age = int(match)
        if age <= 17:
            ages.append(age)
    
    # Match age ranges like "between 5 and 8" - take the midpoint, only if both ages are child ages
    matches = re.findall(r'between\s+(\d{1,2})\s+and\s+(\d{1,2})', text, re.IGNORECASE)
    for low, high in matches:
        low_age, high_age = int(low), int(high)
        if low_age <= 17 and high_age <= 17:  # Only if both ages are child ages
            midpoint = (low_age + high_age) / 2
            ages.append(midpoint)
    
    # Match specific victim age contexts
    matches = re.findall(r'(?:victims?\s+age[sd]?\s+|minors?\s+age[sd]?\s+)(\d{1,2})', text, re.IGNORECASE)
    for match in matches:
        age = int(match)
        if age <= 17:
            ages.append(age)
    
    # Handle toddler/infant/prepubescent - assign reasonable average ages
    if re.search(r'\btoddler\b', text, re.IGNORECASE):
        ages.append(2)  # Average toddler age
    if re.search(r'\binfant\b', text, re.IGNORECASE):
        ages.append(1)  # Average infant age
    if re.search(r'\bprepubescent\b', text, re.IGNORECASE):
        ages.append(8)  # Average prepubescent age
    
    # Return mean of ages or NaN if no ages found
    if ages:
        return np.mean(ages)
    else:
        return np.nan

df['victim_age'] = df['text'].apply(extract_victim_ages)

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
#%%
def analyze_top_apps_by_group(df, app_column_names, group_by_column, top_n=3):
    """
    Analyze and display the top N most commonly mentioned apps grouped by any specified column.
    
    Parameters:
    -----------
    df : pd.DataFrame
        DataFrame containing the case data with the grouping column and app columns
    app_column_names : list
        List of column names that contain app mention data (boolean columns starting with 'app_')
    group_by_column : str
        Name of the column to group by (e.g., 'victim_gender', 'extracted_cities', 'field_office_slug')
    top_n : int, default 3
        Number of top apps to display for each group category
    
    Returns:
    --------
    pd.DataFrame
        Grouped data showing app counts by the specified grouping column
    """
    print(f"=== TOP {top_n} MOST COMMONLY MENTIONED APPS BY {group_by_column.upper()} ===\n")
    
    # Group by specified column and sum app columns
    app_by_group = df.groupby(group_by_column)[app_column_names].sum()
    
    # Get top N apps for each group
    for group_value in app_by_group.index:
        print(f"{group_by_column.upper()}: {str(group_value).upper()}")
        print("-" * 50)
        
        # Get the app counts for this group and sort in descending order
        group_apps = app_by_group.loc[group_value].sort_values(ascending=False)
        
        # Get top N non-zero apps
        top_apps = group_apps[group_apps > 0].head(top_n)
        
        if len(top_apps) > 0:
            for i, (app_col, count) in enumerate(top_apps.items(), 1):
                # Clean up the app name (remove 'app_' prefix and replace underscores)
                app_name = app_col.replace('app_', '').replace('_', ' ').title()
                print(f"{i}. {app_name}: {int(count)} mentions")
        else:
            print(f"No apps mentioned for this {group_by_column} category")
        
        print()
    
    # Also show the raw grouped data for reference
    print("=== RAW GROUPED DATA (All Apps) ===")
    print(app_by_group.T.sort_values(by=list(app_by_group.index), ascending=False))
    
    return app_by_group
#%%
# Run the analysis - group by victim gender
analyze_top_apps_by_group(df, app_column_names, 'victim_age')

#%%  a    x  b2q   a WQNQ3DV 