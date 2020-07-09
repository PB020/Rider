import argparse

import concurrent.futures
import time

import requests
from bs4 import BeautifulSoup, SoupStrainer

PRODUCTS = []
DETAILS = []
MAX_THREADS = 60

def init():
    init_output = open("Rider Output.csv", "w+", encoding = "utf-8")
    init_output.write("Product,Condition,Price\n")
    init_output.close()

    parser = argparse.ArgumentParser(description="Parses Tens of Thousands of eBay Links")
    parser.add_argument('file', action="store", help="File containing eBay links")
    args = parser.parse_args()

    global PRODUCTS
    with open(args.file, "r") as update_links:
        for link in update_links:
            if len(link) > 25:
                PRODUCTS.append(link.strip())

def scrape():
    threads = min(MAX_THREADS, len(PRODUCTS))

    print("Starting eBay Scrape")
    
    with concurrent.futures.ThreadPoolExecutor(max_workers = threads) as executor:
        executor.map(scrape_url, PRODUCTS)

    for detail in DETAILS:
        with open("Rider Output.csv", "a+", encoding = "utf-8") as save:
            save.write(detail)

    print("Finished eBay Scrape")

def scrape_url(product):
    global DETAILS
    session = requests.Session()
    response = session.get(product)

    strainer = SoupStrainer(["div", "h1", "span"])
    soup = BeautifulSoup(response.content, "lxml", parse_only = strainer)

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

    DETAILS.append(f"{product_name},{product_condition},{product_price}\n")

    print(f"\tSaved Details For {product_name}")
    return

def main():
    init()
    t0 = time.time()
    scrape()
    t1 = time.time()
    print(f"\nSaved Details for {len(PRODUCTS)} Products in {t1-t0} Seconds")


if __name__ == "__main__":
    main()