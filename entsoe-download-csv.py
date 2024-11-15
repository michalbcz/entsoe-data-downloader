import os
import requests
import urllib.parse
from bs4 import BeautifulSoup
from concurrent.futures import ThreadPoolExecutor

# Solution for problem with too many headers
# HTTPException('got more than 100 headers')
import http.client
http.client._MAXHEADERS = 1000

# get all the countries and their ENTSOE area codes
r = requests.get(
    "https://transparency.entsoe.eu/transmission-domain/physicalFlow/show?name=&defaultValue=false&viewType=TABLE&areaType=BORDER_CTY&atch=true&dateTime.dateTime=15.11.2024+00%3A00%7CCET%7CDAY&border.values=CTY%7C10YAL-KESH-----5!BZN_BZN%7C10YAL-KESH-----5_BZN_BZN%7C10YGR-HTSO-----Y&dateTime.timezone=CET_CEST&dateTime.timezone_input=CET+(UTC%2B1)+%2F+CEST+(UTC%2B2)&_=1731685594416"
)
bs = BeautifulSoup(r.content, "html.parser")

countryCheckboxes = bs.select(
    "#dv-market-areas-content .dv-sub-filter-hierarchic-wrapper > .dv-filter-checkbox"
)

# countryToAreaCode sample
# countryToAreaCode = [("Czech Republic", "CTY|10YCZ-CEPS-----N")]

countryToAreaCode = []
for checkbox in countryCheckboxes:
    value = checkbox.find("input")["value"]
    areaCode = value.replace("|SINGLE", "")
    country = (checkbox.text.strip(), areaCode)
    # print(country)
    countryToAreaCode.append(country)

print(countryToAreaCode)

#countryToAreaCode = [('Albania (AL) - Greece (GR)', 'CTY|10YAL-KESH-----5!CTY_CTY|10YAL-KESH-----5_CTY_CTY|10YGR-HTSO-----Y')]
def download_data(year, countryName, areaCode ):
    print(f"Downloading data for {countryName} ({areaCode})")
    # Download link for
    # 'https://transparency.entsoe.eu/generation/r2/actualGenerationPerProductionType/export?name=&defaultValue=false&viewType=TABLE&areaType=CTY&atch=true&datepicker-day-offset-select-dv-date-from_input=D&dateTime.dateTime=06.10.2015+00%3A00%7CCET%7CDAYTIMERANGE&dateTime.endDateTime=06.10.2015+00%3A00%7CCET%7CDAYTIMERANGE&area.values=CTY%7C10Y1001A1001A83F!CTY%7C10Y1001A1001A83F&productionType.values=B01&productionType.values=B25&productionType.values=B02&productionType.values=B03&productionType.values=B04&productionType.values=B05&productionType.values=B06&productionType.values=B07&productionType.values=B08&productionType.values=B09&productionType.values=B10&productionType.values=B11&productionType.values=B12&productionType.values=B13&productionType.values=B14&productionType.values=B20&productionType.values=B15&productionType.values=B16&productionType.values=B17&productionType.values=B18&productionType.values=B19&dateTime.timezone=CET_CEST&dateTime.timezone_input=CET+(UTC%2B1)+%2F+CEST+(UTC%2B2)&dataItem=ALL&timeRange=YEAR&exportType=CSV',

    areaCodeUriEncoded = urllib.parse.quote(areaCode)

    # Fill your values. You can get them from the browser's developer tools after you login
    cookies = {
        "SESSION": "ZDgzZWUzMTMtZjczNy00MTEyLThiYTctMGYwZTc1NDIzZjFi",
        "JSESSIONID": "EFAC76101E3E982D1D09C6E0FF10E2B5",
    }

    # https://transparency.entsoe.eu/transmission-domain/physicalFlow/export
    # ?name=&defaultValue=false&viewType=TABLE
    # &areaType=BORDER_CTY&atch=false
    # &dateTime.dateTime=15.11.2024+00%3A00%7CCET%7CDAY&border.values=CTY%7C10YAL-KESH-----5!CTY_CTY%7C10YAL-KESH-----5_CTY_CTY%7C10YGR-HTSO-----Y
    # &dateTime.timezone=CET_CEST&dateTime.timezone_input=CET+(UTC%2B1)+%2F+CEST+(UTC%2B2)&dataItem=ALL&timeRange=YEAR&exportType=CSV
    
    url = f"https://transparency.entsoe.eu/transmission-domain/physicalFlow" \
    "/export?name=&defaultValue=false&viewType=TABLE&areaType=BORDER_CTY&atch=false&datepicker-day-offset-select-dv-date-from_input=D" \
    f"&dateTime.dateTime=01.01.{year}+00%3A00%7CUTC%7CDAYTIMERANGE&dateTime.endDateTime=31.12.{year}+00%3A00%7CUTC%7CDAYTIMERANGE" \
    f"&border.values={areaCodeUriEncoded}" \
    "&dateTime.timezone=UTC" \
    "&dateTime.timezone_input=UTC" \
    "&dataItem=ALL" \
    "&timeRange=YEAR" \
    "&exportType=CSV"
    # print(url)
    
    print("Downloading data for", countryName)
    r = requests.get(url, cookies=cookies, allow_redirects=True)
    
    filename = f"./data/physicalFlow/{countryName} {year}.csv"
    os.makedirs(os.path.dirname(filename), exist_ok=True)        
    open(filename, "wb").write(r.content)
    print("Saved to", os.path.abspath(filename))

with ThreadPoolExecutor(max_workers=10) as executor:
    futures = []
    for year in range(2023, 2024):
        for countryName, areaCode in countryToAreaCode:
            futures.append(executor.submit(download_data, year, countryName, areaCode))

    for future in futures:
        future.result()  # Wait for all futures to complete