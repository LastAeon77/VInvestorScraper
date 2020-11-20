# plan: scrape using selenium
#       Use Beautiful Soup Raw html
#       integrate into postgre/mysql, whatever kekw

from selenium import webdriver
from bs4 import BeautifulSoup
import aiohttp
from SoupAnalysis.SoupAnalyze import analyzeAndInsert
import asyncio

#    soup = await BeautifulSoup(page.text.encode("ISO-8859-1"), "lxml")


async def get_site_content(currUrl):
    async with aiohttp.ClientSession() as session:
        async with session.get(currUrl) as resp:
            page = await resp.read()
    soup = BeautifulSoup(page, "lxml")
    return soup


if __name__ == "__main__":
    browser = webdriver.Chrome()
    count = 0
    i = 1
    while count < 1000:
        browser.get(
            "http://property.treasury.go.th/pvmwebsite/search_data/s_land1_price.asp"
        )  # open website
        browser.find_element_by_name("chanode_no").send_keys(i)
        browser.find_element_by_name("selChangwat").send_keys("กระบี่")
        browser.find_element_by_name("Submit2").click()
        browser.switch_to.window(browser.window_handles[-1])  # switch tabs
        SELECTED_URL = browser.page_source
        # loop = asyncio.get_event_loop()
        # sites_soup = loop.run_until_complete(get_site_content(SELECTED_URL))
        # #sites_soup = sites_soup.find_all('a')
        # # print(sites_soup)

        # loop.close()
        soup = BeautifulSoup(SELECTED_URL, "lxml")
        links = soup.find_all("a")
        for link in links:
            temp = link.get("onclick")
            temp = temp.replace("LandReport(", "")
            temp = temp.replace(");", "")
            temp = temp.split(",")
            temp[2] = temp[2].replace("'", "")
            templateLink = f"http://property.treasury.go.th/pvmwebsite/search_data/r_land_price.asp?landid={temp[0]}&changwat={temp[1]}&amphur={temp[2]}"
            analyzeAndInsert(templateLink)
        if not links:
            count += 1
        else:
            count = 0
        i += 1
    browser.quit()
