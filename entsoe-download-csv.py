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
    "https://transparency.entsoe.eu/generation/r2/actualGenerationPerProductionType/show?name=&defaultValue=false&viewType=TABLE&areaType=CTY"
)
bs = BeautifulSoup(r.content, "html.parser")

countryCheckboxes = bs.select(
    "#dv-market-areas-content .dv-filter-hierarchic-wrapper > .dv-filter-checkbox"
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

def download_data(year, countryName, areaCode, cookies):
    print(f"Downloading data for {countryName} ({areaCode}) for year {year}")
    areaCodeUriEncoded = urllib.parse.quote(areaCode)
    url = f"https://transparency.entsoe.eu/generation/r2/actualGenerationPerProductionType" \
          "/export?name=&defaultValue=false&viewType=TABLE&areaType=CTY&atch=false&datepicker-day-offset-select-dv-date-from_input=D" \
          f"&dateTime.dateTime=01.01.{year}+00%3A00%7CUTC%7CDAYTIMERANGE&dateTime.endDateTime=31.12.{year}+00%3A00%7CUTC%7CDAYTIMERANGE" \
          f"&area.values={areaCodeUriEncoded}!{areaCodeUriEncoded}" \
          "&productionType.values=B01&productionType.values=B25&productionType.values=B02&productionType.values=B03&productionType.values=B04" \
          "&productionType.values=B05&productionType.values=B06&productionType.values=B07&productionType.values=B08&productionType.values=B09" \
          "&productionType.values=B10&productionType.values=B11&productionType.values=B12&productionType.values=B13&productionType.values=B14" \
          "&productionType.values=B20&productionType.values=B15&productionType.values=B16&productionType.values=B17&productionType.values=B18" \
          "&productionType.values=B19" \
          "&dateTime.timezone=UTC" \
          "&dateTime.timezone_input=UTC" \
          "&dataItem=ALL" \
          "&timeRange=YEAR" \
          "&exportType=CSV"
    response = requests.get(url, cookies=cookies)
    if response.status_code == 200:
        print(f"Successfully downloaded data for {countryName} ({areaCode}) for year {year}")
        filename = f"./data/{countryName} {year}.csv"
        os.makedirs(os.path.dirname(filename), exist_ok=True)        
        open(filename, "wb").write(response.content)
        print(f"Saved to {os.path.abspath(filename)}")
    else:
        print(f"Failed to download data for {countryName} ({areaCode}) for year {year}")

# Fill your values. You can get them from the browser's developer tools after you login
cookies = {
    "SESSION": "MTgyMDA5MDUtOTZhYy00ZTI4LTg2YzctYWM4OTEzMmU1NmVk",
    "JSESSIONID": "84084094D88A6CAC3579FEB0B13AAA30",
}

with ThreadPoolExecutor(max_workers=10) as executor:
    futures = []
    for year in range(2014, 2023):
        for countryName, areaCode in countryToAreaCode:
            futures.append(executor.submit(download_data, year, countryName, areaCode, cookies))

    for future in futures:
        future.result()  # Wait for all futures to complete
