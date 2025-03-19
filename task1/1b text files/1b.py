import requests
import re
import os
import nltk
from bs4 import BeautifulSoup
from nltk.corpus import stopwords

# Download stopwords
nltk.download('stopwords')
stop_words = set(stopwords.words('english'))

# 20 Updated Categories
categories = {
    "Astronomy": [
        "https://www.space.com/astronomy",
        "https://astronomy.com/",
        "https://www.skyandtelescope.org/"
    ],
    "Psychology": [
        "https://www.psychologytoday.com/",
        "https://www.verywellmind.com/",
        "https://www.bps.org.uk/"
    ],
    "Climate Change": [
        "https://www.climate.gov/",
        "https://www.un.org/en/climatechange",
        "https://www.carbonbrief.org/"
    ],
    "Robotics": [
        "https://spectrum.ieee.org/robotics",
        "https://www.roboticsbusinessreview.com/",
        "https://www.robotics.org/"
    ],
    "Renewable Energy": [
        "https://www.renewableenergyworld.com/",
        "https://www.irena.org/",
        "https://www.energy.gov/"
    ],
    "Quantum Computing": [
        "https://quantumcomputingreport.com/",
        "https://www.ibm.com/quantum-computing/",
        "https://www.microsoft.com/en-us/quantum/"
    ],
    "Oceanography": [
        "https://ocean.si.edu/",
        "https://www.whoi.edu/",
        "https://www.mbari.org/"
    ],
    "Urban Planning": [
        "https://www.planetizen.com/",
        "https://www.urbandesignforum.org/",
        "https://www.cnu.org/"
    ],
    "Mythology": [
        "https://www.greekmythology.com/",
        "https://mythopedia.com/",
        "https://www.theoi.com/"
    ],
    "Fitness and Wellness": [
        "https://www.shape.com/",
        "https://www.menshealth.com/",
        "https://www.womenshealthmag.com/"
    ],
    "Astrobiology": [
        "https://astrobiology.nasa.gov/",
        "https://www.seti.org/",
        "https://www.astrobio.net/"
    ],
    "Esports": [
        "https://www.dexerto.com/",
        "https://www.esports.net/",
        "https://www.gosugamers.net/"
    ],
    "Music Production": [
        "https://www.soundonsound.com/",
        "https://www.musicradar.com/",
        "https://www.attackmagazine.com/"
    ],
    "Wildlife Conservation": [
        "https://www.worldwildlife.org/",
        "https://www.nationalgeographic.com/animals/",
        "https://www.wcs.org/"
    ],
    "Artificial Intelligence": [
        "https://www.analyticsvidhya.com/",
        "https://www.aitrends.com/",
        "https://deepmind.com/"
    ],
    "Literary Criticism": [
        "https://www.lrb.co.uk/",
        "https://www.nybooks.com/",
        "https://www.newyorker.com/books"
    ],
    "Martial Arts": [
        "https://www.blackbeltmag.com/",
        "https://www.bjjee.com/",
        "https://www.mmamania.com/"
    ],
    "Cryptocurrency": [
        "https://cointelegraph.com/",
        "https://www.coindesk.com/",
        "https://cryptonews.com/"
    ],
    "Architecture": [
        "https://www.archdaily.com/",
        "https://www.designboom.com/architecture/",
        "https://www.dezeen.com/architecture/"
    ],
    "Mental Health": [
        "https://www.mind.org.uk/",
        "https://www.psychcentral.com/",
        "https://www.mentalhealth.org.uk/"
    ]
}

def scrape_website(url):
    headers = {'User-Agent': 'Mozilla/5.0'}
    try:
        response = requests.get(url, headers=headers, timeout=5)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        print(f"Error fetching {url}: {e}")
        return None, None

    soup = BeautifulSoup(response.text, 'html.parser')
    title = soup.title.text if soup.title else "No Title"
    paragraphs = soup.find_all('p')
    content = ' '.join([p.text for p in paragraphs])

    return title, content

def clean_text(text):
    text = re.sub(r'<.*?>', '', text)  
    text = re.sub(r'[^a-zA-Z\s]', '', text)  
    text = text.lower()  
    text = ' '.join([word for word in text.split() if word not in stop_words])  
    return text

def save_to_file(category, text):
    filename = f"{category}.txt"
    with open(filename, "w", encoding="utf-8") as file:
        file.write(text)

if not os.path.exists("WebText-20/raw_files"):
    os.makedirs("WebText-20/raw_files")

for category, urls in categories.items():
    print(f"\nScraping category: {category}")
    all_text = ""

    for url in urls:
        title, content = scrape_website(url)
        if content:
            all_text += f"\nTitle: {title}\nContent: {content}\n"

    raw_file_path = os.path.join("WebText-20/raw_files", f"{category}_raw.txt")
    save_to_file(raw_file_path, all_text)

    cleaned_text = clean_text(all_text)

    cleaned_file_path = os.path.join("WebText-20", f"{category}_cleaned.txt")
    save_to_file(cleaned_file_path, cleaned_text)

    print(f" Saved {category} data ({len(cleaned_text)} characters)")

print("\n Web scraping and text processing complete! Check the 'WebText-20' folder.")
