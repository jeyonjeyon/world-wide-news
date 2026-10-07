import json
import urllib.request
import xml.etree.ElementTree as ET

# Define RSS feeds mapped to your dashboard categories
FEEDS = {
    "globalOverview": [
        "https://news.un.org/feed/subscribe/en/news/all/rss.xml",
        "https://www.reuters.com/arc/outboundfeeds/rss/?outputType=xml"
    ],
    "north-america": [
        "https://moxie.foxnews.com/google-publisher/latest.xml",
        "https://rss.cbc.ca/lineup/topstories.xml"
    ],
    "latin-america": [
        "https://mercopress.com/rss/"
    ],
    "east-asia": [
        "http://www.xinhuanet.com/english/rss/worldrss.xml"
    ],
    "south-asia": [
        "https://www.thehindu.com/news/national/feeder/default.rss",
        "https://www.dawn.com/feed"
    ],
    "europe": [
        "https://feeds.bbci.co.uk/news/world/europe/rss.xml",
        "https://www.france24.com/en/rss"
    ],
    "middle-east": [
        "https://www.aljazeera.com/xml/rss/all.xml"
    ],
    "africa": [
        "https://allafrica.com/tools/headlines/rdf/latest/headlines.rdf"
    ],
    "oceania": [
        "https://www.rnz.co.nz/rss/world.xml"
    ]
}

def parse_rss(url):
    articles = []
    try:
        req = urllib.request.Request(
            url, 
            headers={'User-Agent': 'Mozilla/5.0'}
        )
        with urllib.request.urlopen(req, timeout=10) as response:
            xml_data = response.read()
            root = ET.fromstring(xml_data)
            
            # Handle standard RSS and Atom feeds
            item_tag = 'item' if root.findall('.//item') else '{http://www.w3.org/2005/Atom}entry'
            
            for item in root.findall(f'.//{item_tag}')[:15]: # Grab up to 15 per feed
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
                
                # Basic HTML tag stripping for summaries
                import re
                summary_text = re.sub('<.*?>', '', summary_text)

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
            category_articles.extend(parse_rss(url))
        
        # Limit to 10-30 items per region for a rich scrollable list
        dashboard_data[category] = category_articles[:20]

    with open('news.json', 'w', encoding='utf-8') as f:
        json.dump(dashboard_data, f, ensure_ascii=False, indent=4)
    print("news.json updated successfully!")

if __name__ == "__main__":
    main()
