from flask import Flask, jsonify, request
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from pymongo import MongoClient
from datetime import datetime
from bson.json_util import dumps
import time

app = Flask(__name__)

# Connect to MongoDB
client = MongoClient('mongodb+srv://aeckhart06:Andrew06@cluster0.ad6vd.mongodb.net/')

# Select database and collection
db = client['ms_ga_contestants']
collection = db['contestants']

# Helper function to convert MongoDB documents to JSON
def serialize_document(document):
    return eval(dumps(document))


def scroll_to_bottom(driver):
    # Get scroll height
    last_height = driver.execute_script("return document.body.scrollHeight")
    
    while True:
        # Scroll down to bottom
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        
        # Wait for new content to load
        time.sleep(2)
        
        # Calculate new scroll height and compare with last scroll height
        new_height = driver.execute_script("return document.body.scrollHeight")
        if new_height == last_height:
            # If heights are the same, we've reached the bottom
            break
        last_height = new_height

def get_elements_by_class(driver, class_name):
    try:
        # Using XPath to find elements with class_name that contain "Georgia" in their text
        xpath_query = f"//div[contains(@class, '{class_name}')][.//text()[contains(., 'Georgia')]]"
        ms_ga_contestants = driver.find_elements(By.XPATH, xpath_query)
        return ms_ga_contestants
    except Exception as e:
        print(f"Error finding elements with class {class_name}: {str(e)}")
        return []

def store_in_mongodb(contestants_data):
    try:
        
        collection.delete_many({})
        
        # Add timestamp to each document
        for contestant in contestants_data:
            contestant['timestamp'] = datetime.now()
            contestant['source_url'] = "https://www.spotfund.com/organization/91c03122-e032-4ff7-aeca-04a717b82fd3"
        
        # Insert all documents
        result = collection.insert_many(contestants_data)
        print(f"Successfully inserted {len(result.inserted_ids)} documents")
        
        # Close the connection
        client.close()
        
    except Exception as e:
        print(f"Error storing data in MongoDB: {str(e)}")

def get_page_content(url, class_name):
    ms_ga_contestants = []
    try:
        # Set up Chrome options
        options = uc.ChromeOptions()
        options.add_argument('--headless')
        
        # Initialize the Chrome driver
        driver = uc.Chrome(options=options)
        
        # Load the page
        driver.get(url)
        
        # Wait for initial content to load
        time.sleep(5)
        
        # Scroll to load all content
        print("Scrolling to load all content...")
        scroll_to_bottom(driver)
        
        # Get the title
        title = driver.title
        print(f"Title: {title}")
        
        # Get all elements with the specified class
        georgia_elements = get_elements_by_class(driver, class_name)
        
        # Print information about each element
        print(f"\nFound {len(georgia_elements)} elements with class '{class_name}':")
        for i, element in enumerate(georgia_elements, 1):
            print(f"\nElement {i}:")
            text = element.text.strip()
            text = text.split("\n")
            print(text)
            name = text[0]
            print("Name: ", name)
            amount_raised = text[2].split("RAISED")[0]
            amount_raised = amount_raised.replace("$", "").replace(",", "")
            amount_raised = int(amount_raised)
            print("Amount Raised: ", amount_raised)
            
            # Add to list (sorted by amount raised)
            if len(ms_ga_contestants) == 0:
                ms_ga_contestants.append({"name": name, "amount_raised": amount_raised})
            else:
                inserted = False
                for index in range(len(ms_ga_contestants)):
                    if ms_ga_contestants[index]["amount_raised"] <= amount_raised:
                        ms_ga_contestants.insert(index, {"name": name, "amount_raised": amount_raised})
                        inserted = True
                        break
                if not inserted:
                    ms_ga_contestants.append({"name": name, "amount_raised": amount_raised})
        
        # Store in MongoDB
        store_in_mongodb(ms_ga_contestants)
        
        driver.quit()
        return ms_ga_contestants
    
    except Exception as e:
        print(f"An error occurred: {str(e)}")
        if 'driver' in locals():
            driver.quit()
        return None

def main():
    url = "https://www.spotfund.com/organization/91c03122-e032-4ff7-aeca-04a717b82fd3"
    class_name = "story-desktop-card-details"
    sorted_contestants = get_page_content(url, class_name)
    # Print the top 10 contestants
    print(sorted_contestants[:10])

if __name__ == "__main__":
#   main() 
    app.run(debug=True)

@app.route("/updatedb", methods=["POST"])
def updatedb():
    main()

@app.route("/contestants", methods=["GET"])
def get_contestants():
    try:
        contestants = collection.find().sort("amount_raised", -1).limit(10)
        # Serialize the documents to JSON format
        return [serialize_document(contestant) for contestant in contestants]
    except Exception as e:
        print(f"Error retrieving contestants: {str(e)}")
        return []