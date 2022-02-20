from walmart import Walmart
import datetime
def main(url):
    url = url
    w_scrape = Walmart(url=url)
    print("Walmart scraper created")
    output_df = w_scrape.scrape()
    print("Scrape complete!")
    print(output_df.head())
    output_df.to_csv(f"../output/walmart_product_{datetime.datetime.today().strftime('%d-%m-%y')}.csv")

if __name__ == "__main__":
    main(url = "https://www.walmart.com/browse/electronics/touchscreen-laptops/3944_3951_1089430_1230091_1101633")