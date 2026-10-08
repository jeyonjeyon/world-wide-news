import json
import urllib.request
import xml.etree.ElementTree as ET
import re

# Tighter RSS feeds
FEEDS = {
    "globalOverview": [
        "https://news.un.org/feed/subscribe/en/news/all/rss.xml",
        "https://feeds.bbci.co.uk/news/world/rss.xml"
    ],
    "north-america": [
        "https://moxie.foxnews.com/google-publisher/latest.xml",
        "https://rss.cbc.ca/lineup/topstories.xml"
    ],
    "latin-america": [
        "https://mercopress.com/rss/"
    ],
    "east-asia": [
        "https://feeds.bbci.co.uk/news/world/asia/rss.xml",
        "https://english.news.cn/world/index.htm"
    ],
    "south-asia": [
        "https://www.thehindu.com/news/national/feeder/default.rss",
        "https://www.dawn.com/feed"
    ],
    "europe": [
        "https://feeds.bbci.co.uk/news/world/europe/rss.xml",
        "https://www.france24.com/en/europe/rss"
    ],
    "middle-east": [
        "https://feeds.bbci.co.uk/news/world/middle_east/rss.xml",
        "https://www.aljazeera.com/xml/rss/all.xml"
    ],
    "africa": [
        "https://feeds.bbci.co.uk/news/world/africa/rss.xml",
        "https://allafrica.com/tools/headlines/rdf/latest/headlines.rdf"
    ],
    "oceania": [
        "https://feeds.bbci.co.uk/news/world/australia/rss.xml",
        "https://www.rnz.co.nz/rss/world.xml"
    ]
}

# Strict keyword guardrails for each region
REGION_KEYWORDS = {
    "globalOverview": ["world", "global", "un", "international", "united nations"],
    "north-america": ["america", "us", "usa", "united states", "canada", "washington", "ottawa", "trump", "biden", "congress", "white house", "mexico"],
    "latin-america": ["latin america", "brazil", "argentina", "chile", "colombia", "peru", "mexico", "venezuela", "caribbean", "santiago", "buenos aires", "brasilia"],
    "east-asia": ["asia", "china", "japan", "korea", "taiwan", "beijing", "tokyo", "seoul", "taipei", "pyongyang", "hong kong", "shanghai"],
    "south-asia": ["india", "pakistan", "bangladesh", "sri lanka", "nepal", "delhi", "islamabad", "new delhi", "mumbai", "karachi", "dhaka"],
    "europe": ["europe", "eu", "uk", "britain", "france", "germany", "italy", "ukraine", "russia", "london", "paris", "berlin", "brussels", "mowcow"],
    "middle-east": ["middle east", "israel", "gaza", "iran", "saudi", "dubai", "syria", "iraq", "lebanon", "jerusalem", "tehran", "riyadh", "tel aviv"],
    "africa": ["africa", "nigeria", "south africa", "kenya", "egypt", "ethiopia", "ghana", "nairobi", "lagos", "cairo", "johannesburg"],
    "oceania": ["oceania", "australia", "new zealand", "fiji", "sydney", "melbourne", "canberra", "wellington", "auckland", "pacific"]
}

def matches_region(text, category):
    """Checks if the text contains any of the required keywords for the category."""
    if category not in REGION_KEYWORDS:
        return True # Fallback if a category isn't mapped
    
    text_lower = text.lower()
    keywords = REGION_KEYWORDS[category]
    return any(kw in text_lower for kw in keywords)

def parse_rss(url, category):
    articles = []
    try:
        req = urllib.request.Request(
            url, 
            headers={'User-Agent': 'Mozilla/5.0'}
        )
        with urllib.request.urlopen(req, timeout=10) as response:
            xml_data = response.read()
            root = ET.fromstring(xml_data)
            
            item_tag = 'item' if root.findall('.//item') else '{http://www.w3.org/2005/Atom}entry'
            
            # Grab a larger pool (e.g., 30) so we have enough items left after filtering out misses
            for item in root.findall(f'.//{item_tag}')[:30]:
                if item_tag == 'item':
                    title = item.find('title')
                    link = item.find('link')
                    desc = item.find('description')
                else:
                    title = item.find('{http://www.w3.org/2005/Atom}title')
                    link = item.find('{http://www.w3.org/2005/Atom}link')
                    desc = item.find('{http://www.w3.org/2005/Atom}summary')

                title_text = title.text.strip() if title is not None and title.text else "No title"
                link_text = link.text.strip() if link is not None and link.text else (link.attrib.get('href') if link is not None else "#")
                summary_text = desc.text.strip() if desc is not None and desc.text else "No summary available."
                
                summary_text = re.sub('<.*?>', '', summary_text)
                
                # Combine title and summary to check for regional relevance
                combined_content = f"{title_text} {summary_text}"
                
                # Apply keyword filter guardrail
                if matches_region(combined_content, category):
                    articles.append({
                        "headline": title_text,
                        "summary": summary_text[:180] + "..." if len(summary_text) > 180 else summary_text,
                        "sources": [url.split('/')[2].replace('www.', '')],
                        "url": link_text
                    })
    except Exception as e:
        print(f"Error fetching {url}: {e}")
    return articles

def main():
    dashboard_data = {}
    
    for category, feed_urls in FEEDS.items():
        category_articles = []
        for url in feed_urls:
            category_articles.extend(parse_rss(url, category))
        
        # Remove duplicate articles based on headline
        seen_headlines = set()
        unique_articles = []
        for article in category_articles:
            if article["headline"] not in seen_headlines:
                seen_headlines.add(article["headline"])
                unique_articles.append(article)

        # Limit to 20 items per region
        dashboard_data[category] = unique_articles[:20]

    with open('news.json', 'w', encoding='utf-8') as f:
        json.dump(dashboard_data, f, ensure_ascii=False, indent=4)
    print("news.json updated successfully with keyword filtering!")

if __name__ == "__main__":
    main()
