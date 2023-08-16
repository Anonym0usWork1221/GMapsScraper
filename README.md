GMapsScraper
====
-----------

**_GMapsScraper_** is a command-line tool which is designed to scrape data from Google Maps search results using multiple threads and efficient search algorithms..
If you find any bug or not working function you can contact me. 

 *  Date   : 2023/08/16
 *  Author : **__Abdul Moez__**
 *  Version : 0.1
 *  Study  : UnderGraduate in GCU Lahore, Pakistan
 *  Repository  : https://github.com/Anonym0usWork1221/GMapsScraper
 *  [Documentation](https://github.com/Anonym0usWork1221/GMapsScraper#gmapsscraper-documentation)


 GNU General Public License 

 Copyright (c) 2023 AbdulMoez

-----------

## Requirements
* Python 3.7+
* Google Chrome Stable (also work on chromium on linux headless server)
* Requirements file (as mentioned in installation section in documentation)


## Supported Platform
* Linux
* Windows
* Mac
* Linux Servers (doesn't support `windowed browser`)

## Simple Usage
For just simple execution you don't even need any parameters as all the parameters have default values. Just type (highly recommend to use `-v` tag for verbose. It will only change status tag which keep you up-to-date):
```bash
python3 maps.py
```
After all the parameters here it looks like. I did not add `-d` parameter you need to pass it as in newer version of chrome driver (>=115) are not available direct site so for that you need to pass the driver manually using `-d`. And also the driver which is in `chrome_driver_backup` directory is for latest version (116).
```bash
python maps.py -q ./queries.txt -w 2 -l -1 -u "Not Available" -bw 15 -se contacts -se about -o ./CSV_FILES -v
```

Command line after adding `-d`
```bash
python3 maps.py -q "./queries.txt" -d "./chrome_driver_backup/chromedriver.exe" -v
```

## What this script Scrapes?
1. `Latitude` (lat): The latitude coordinate of a specific place, usually represented as a decimal number. It indicates the north-south position on the Earth's surface.
2. `Longitude` (long): The longitude coordinate of a specific place, also represented as a decimal number. It indicates the east-west position on the Earth's surface.
3. `Map Link` (map_link): A link to the Google Maps page for the specific place. This link can be used to view the location on the map and gather more information.
4. `Cover Image` (cover_image): The URL or source of the cover image associated with the place. This could be an image that represents the establishment, such as its storefront or a logo.
5. `Card Title` (card_title): The title or name of the place, often used as the primary identifier for the establishment.
6. `Rating` (card_rating): The rating of the place, typically represented as a numerical value or a fraction. This indicates the overall customer satisfaction or quality of the establishment.
7. `Privacy Price` (privacy_price): A representation of the price level of the place, indicating how expensive or budget-friendly it is. This might be presented as dollar signs or other symbols.
8. `Category` (card_category): The category or type of the place, which describes what kind of establishment it is (e.g., restaurant, cafe, museum, etc.).
9. `Address` (card_address): The physical address of the place, which includes street name, city, state, and postal code. It helps users locate the establishment.
10. `Working Hours` (card_hours): The operating hours of the place, often provided as a schedule for each day of the week. It specifies when the establishment is open to the public.
11. `Menu Link` (card_menu_link): A link to the menu of the place, if available. This can provide details about the food and drinks offered at a restaurant or cafe.
12. `Website Link` (card_website_link): A link to the official website of the place. This allows users to access more information directly from the establishment's site.
13. `Phone Number` (card_phone_number): The contact phone number for the place. It provides a way for customers to get in touch with the establishment.
14. `Related Images` (card_related_images): A list of URLs or sources for images related to the place. These images might showcase the interior, exterior, or various aspects of the establishment.
15. `About Description` (card_about): A description or summary of the place, often including information about its history, services, offerings, and any unique features.
### Advance Scraping (What this script Scrapes?)
The script is designed to brute force the URLs based on a provided command line parameter (e.g., `-se about`) that appends "about" to the base website URL (https://www.site.com/about). It then navigates to that "about" page and extracts the specified data attributes.

The extracted attributes help gather contact and social media information about the website or establishment. This information is commonly found on the "about" or "contact" pages of websites and can be useful for users who want to connect with the website's social media presence or reach out via email. The script uses Selenium to automate this process and collect the data for further analysis or storage.

Additionally, it scrapes these attributes (if `-se` tag is used in `CLI`):

1. `Site Email` (site_email): The email address associated with the website's contact or support. This could be used for users to reach out with inquiries or feedback.
2. `Facebook Links` (facebook_links): Links to the official Facebook page or profile of the website or establishment. These links can help users connect with the website's social media presence on Facebook.
3. `Twitter Links` (twitter_links): Links to the official Twitter account of the website or establishment. These links enable users to follow the website's updates and announcements on Twitter.
4. `Instagram Links` (instagram_links): Links to the official Instagram account of the website or establishment. These links allow users to access visual content and engage with the website on Instagram.
5. `YouTube Links` (youtube_links): Links to the official YouTube channel of the website or establishment. Users can find videos, tutorials, or other multimedia content related to the website.
6. `LinkedIn Links` (linkedin_links): Links to the official LinkedIn profile or page of the website or establishment. This provides a professional networking platform and business-related updates.

## Visualization
1. **_Script execution_**
  <img src = "README_ASSETS/ss_google_maps.png"/>  

2. **_Visualization of few points of data script scrapes_**.  
<img src = "README_ASSETS/additional_scrape.png"/>


-----

## GMapsScraper Documentation
This command-line tool is designed to scrape data from Google Maps search results using multiple threads and efficient search algorithms. This documentation will provide you with an extensive overview of the tool's features and how to use them effectively.

## Table of Contents

- [Introduction](#introduction)
- [Installation](#installation)
- [Usage](#usage)
   - [Command Line Arguments](#command-line-arguments)
   - [Help for Specific Options](#help-for-specific-options)
- [Input File Format](#input-file-format)
- [Output](#output)
- [Advanced Usage](#advanced-usage)
- [Troubleshooting](#troubleshooting)
- [Conclusion](#conclusion)


## 1. Introduction <a name="introduction"></a>
The `GMapsScraper` tool is a Python script that leverages the power of multiple threads and efficient search algorithms to scrape data from Google Maps search results. It is particularly useful for extracting business or location details for a given set of search queries. This tool aims to provide a user-friendly experience while maximizing scraping efficiency.

## 2. Installation <a name="installation"></a>
To use the `GMapsScraper`, you need to have Python installed on your system. Additionally, you need to install Google Chrome and the required dependencies using the following command:
````
    pip install -r requirements.txt
````

## 3. Usage <a name="usage"></a>
To use the `GMapsScraper`, follow these steps:

Prepare a text file containing the search queries. Each query should be on a separate line in the file.
Open a terminal and navigate to the directory containing the `maps.py` script.
Run the script with the desired command-line arguments.

### Command Line Arguments <a name="command-line-arguments"></a>
The `GMapsScraper` script supports the following command-line arguments:

* `-q` or `--query-file`: Path to the query file. Default: `./queries.txt`
* `-w` or `--threads`: Number of threads to use. Default: `1`
* `-l` or `--limit`: Number of results to scrape. Use `-1` for all results. Default: `-1`
* `-u` or `--unavailable-text`: Replacement text for unavailable information. Default: `Not Available`
* `-bw` or `--browser-wait`: Browser waiting time in seconds. Default: `15`
* `-se` or `--suggested-ext`: Suggested URL extensions to try. Can be specified multiple times.
* `-wb` or `--windowed-browser`: Disable headless mode (display browser window). Default: Headless mode
* `-v` or `--verbose`: Enable verbose mode (additional console output).
* `-o` or `--output-folder`: Output folder to store CSV details. Default: `./CSV_FILES`
* `-d` or `--driver-path`: Path to Chrome driver. If not provided, it will be downloaded.

### Help for Specific Options <a name="help-for-specific-options"></a>
You can use the following command-line options to get help for specific topics:

* `--help-query-file`: Get help for specifying the query file format.
* `--help-limit`: Get help for specifying the result limit.
* `--help-driver-path`: Get help for specifying the Chrome driver path.

## 4. Input File Format <a name="input-file-format"></a>
The query file should contain a list of search queries, with each query on a separate line. For example:

````
Pizza restaurants
Coffee shops
Gas stations
````

## 5. Output <a name="output"></a>
The scraped data will be saved as CSV files in the specified output folder. **_All query's results will be stored in a single CSV file_** named after the query.

## 6. Advanced Usage <a name="advanced-usage"></a>
For advanced users, the script provides options to customize various parameters such as the `number of threads`, `result limit`, `browser behavior`, and more. These options can be adjusted to optimize the scraping process based on your requirements.

## 7. Troubleshooting <a name="troubleshooting"></a>
If you encounter any issues while using the `GMapsScraper` tool, consider the following tips:

* Ensure that you have the required dependencies installed.
* Double-check the path to the query file and ensure it is correct.
*  If you encounter driver-related issues, provide the correct path to the Chrome driver using the `-d` option.

## 8. Conclusion <a name="conclusion"></a>
The `GMapsScraper` tool offers a convenient way to extract data from Google Maps search results using efficient algorithms and multiple threads. By following the instructions in this documentation, you can harness the power of this tool to gather valuable location-based information for your projects.

For additional assistance or inquiries, feel free to reach out to the tool's author, **_Abdul Moez_**.

Thank you for using the `GMapsScraper` tool!

-----------

# Contributor

<a href = "https://github.com/Anonym0usWork1221/GMapsScraper/graphs/contributors">
  <img src = "https://contrib.rocks/image?repo=Anonym0usWork1221/GMapsScraper"/>
</a>

-----------

Assistance
----------
If you need assistance, you can ask for help on my mailing list:

* Email      : abdulmoez123456789@gmail.com

-----------

Buy Me a coffee
--------------
If you would like to support me, you can buy me coffee.

Payoneer: ``abdulmoez123456789@gmail.com``
