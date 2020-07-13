# CLI Arguments
import argparse

# Web Scraping
import requests
from bs4 import BeautifulSoup, SoupStrainer

# Multi-Threading
import concurrent.futures
import time

PRODUCTS = []
DETAILS = []
PARSED = []
MAX_THREADS = 30

# Rider initializer
def init():
    print("Initializing Rider")

    print("    Parsing Input File")
    parser = argparse.ArgumentParser(description="Parses Tens of Thousands of eBay Links")
    parser.add_argument('file', action="store", help="File containing eBay links")
    args = parser.parse_args()

    global PRODUCTS
    with open(args.file, "r") as update_links:
        for link in update_links:
            if len(link) > 25:
                PRODUCTS.append(link.strip())

    print("    Creating Output File")
    init_output = open("Rider Output.csv", "w+", encoding = "utf-8")
    init_output.write("Product,Condition,Price\n")
    init_output.close()

    print("Finished Initialization")
    print("\n--- --- ---\n")

# "Brain" of the script, initializes multi-threading
def rider():
    print("Starting Rider")

    threads = min(MAX_THREADS, len(PRODUCTS))
    
    print(f"    Starting Download:\n      {len(PRODUCTS)} Product Links on {threads} threads\n")
    with concurrent.futures.ThreadPoolExecutor(max_workers = threads) as executor:
        executor.map(download, PRODUCTS)
    print("    Finished Download")

    print(f"\n    Starting Parsing")
    with concurrent.futures.ThreadPoolExecutor(max_workers = threads) as executor:
        executor.map(parse, DETAILS)
    print("    Finished Parsing")

    print(f"\n    Writing Data")
    with open("Rider Output.csv", "a+", encoding = "utf-8") as save:
        for data in PARSED:
            save.write(data)
    print("    Finished Writing")

    print("Rider Complete")

# Downloads product urls
def download(product):
    global DETAILS
    request = requests.get(product)

    DETAILS.append(request.content)
    
    # Sleep so I don't overwhelm eBay's servers
    # Further implementation should include IP 
    time.sleep(0.25)

# Parses downloaded details
def parse(detail):
    global PARSED
    strainer = SoupStrainer(["div", "h1", "span"])
    soup = BeautifulSoup(detail, "lxml", parse_only = strainer)

    product_name = soup.find(id = "itemTitle").text[16:]
    if "," in product_name:
        product_name = product_name.replace(',', '')

    product_condition = soup.find(id = "vi-itm-cond").text
    if product_condition == "--not specified":
        product_condition = "N/A"
    
    product_price = ""
    try:
        product_price = soup.find(id = "prcIsum").text
        if "," in product_price:
            product_price = product_price.replace(',', '')
    except AttributeError:
        product_price = soup.find(id = "mm-saleDscPrc").text
        if "," in product_price:
            product_price = product_price.replace(',', '')

    PARSED.append(f"{product_name},{product_condition},{product_price}\n")

    print(f"\Parsed Details For {product_name}")

def main():
    init()
    t0 = time.time()
    rider()
    t1 = time.time()
    print(f"\nSaved Details for {len(PRODUCTS)} Products in {t1-t0} Seconds")


if __name__ == "__main__":
    main()
