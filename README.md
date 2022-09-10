# Banana Manga Reader
Banana Manga Reader, also referred to as BMR, is an application designed to read manga on Kobo eReaders, which do not have an inbuilt manga reader for reading manga from online sources. It was designed to be easy to install and use. This also means that there isn't much that a user can configure without modifications to the code. However, Banana Manga Reader (BMR) provides most of the features you would want from a manga reader. You can read online, save a title to a favorites list and download chapters to your library for offline reading. The app was made more for reading manga you already know about rather than for discovering new manga, which is why the search capabilities are limited. (*cough, cough* this is totally by design, yeah.. *cough* not because I have limited knowledge about webscraping in python)

The app was built entirely with python for the back end, since this is the only language that I had any experience with. This meant that the ways I could interact with the device were limited. So, I relied on html for the front end, to provide buttons and images for navigating and viewing. That means that if you are interested, you can experiment with the html files and the python code to customize your BMR app! Even better would be using a similar framework to make more interesting applications for the Kobo ereaders. I will be very interested in seeing what the Kobo community can do with it.

## Features
1. Allows you to read manga from online sources. (currently just mangakakalot)
2. Allows you to add titles to a favorites list for easy access.
3. Allows you to save chapters for offline reading. (Although you will need to be connected to a network for opening the browser, you do not have to be connected to the internet. For example, connecting to a mobile hotspot without internet tethering works well)
4. Manga reading should be a smooth experience. No obstructive elements will be on the screen while reading a manga chapter. Tapping on the left or right side will flip the pages (left turn to go to the next page). Tapping in the center opens up the menu.
5. You can add your own manga to the library. On the microSD card, navigate to KOBOeReader/.BMR/static/library Here, you can create a folder with the manga title as it's name. Inside this folder, add folders with chapter titles, which will have the pages stored in png/jpg image formats. Extracting CBR or CBZ files should give you this structure. [library>manga title> chapter title> images]
6. All of the files and programs remain on the  mnt/onboard partition of the device. No files are placed on the root (/) partition or the /usr partition. This way updating, deleting files and making any changes (backing up files, editing htmls or the python script for personalization or improvement) is safer and easier.

## Installation
1. Make sure you have 300 MB or more space on your Kobo microSD card.
2. Install <a href="https://www.mobileread.com/forums/showthread.php?t=329525">NickelMenu</a>. If you don't have it installed already, click the link and follow the instructions there. NickelMenu will help us create a menu item to launch BMR 
3. To prevent images from showing up as books, perform the following operation by connecting your Kobo to your computer:
    - Navigate to KOBOeReader/.kobo/Kobo and open Kobo eReader.conf in the text editor of your choice
    - Scroll down to find `[FeatureSettings]` , if it doesn't exist, create it! (type it in)
    - Under `[FeatureSettings]`, paste the following:     `ExcludeSyncFolders=\\.(?!kobo|adobe).*?`
4. From the pane on the right, go to the <a href="https://github.com/buxared/BananaMangaReader/releases">Releases</a> page or select the latest release. Download the file named "[Release date]_BMR_v[latest version].zip", for example "220905_BMR_v0.zip".
5. Unzipping the file should give you a folder named ".BMR". Copy this folder to the root of your microSD card. (The root is the KOBOeReader folder. Simply drag ".BMR" to KOBOeReader)
6. Create a menu entry using NickelMenu.
    - From KOBOeReader/.BMR, open "nickelmenuconfig.txt" and copy it's contents.
    - Navigate to KOBOeReader/.adds/nm/
    - If a config file does not exist, create a new text file with any name, for example, "config.txt"
    - Paste the contents from "nickelmenuconfig.txt" into the config file.
7. Safely eject your eReader from your computer.

You are now ready to use Banana Manga Reader!

## Launching and Using BMR
Once you have installed BMR, you can launch the app by performing the following steps:
1. Open NickelMenu on your Kobo eReader and select "Start BMR server". Click "OK".
2. Open NickelMenu on your Kobo eReader and select "Open BMR".
3. Enjoy! More details and instructions for use can be found under "Navigation" from the hamburger menu in the top left corner of the application/browser window.
4. Make sure you always exit the app by navigating to "Close app" from the hamburger menu. Press the "Shut down" button. (Not shutting down this way will keep the BMR server running in the background. You don't want there to be multiple instances using up CPU resources when you start BMR again next time. So, it's best to close the app this way)

### Note:
You will need to be connected to a network to open the application, since it works using the kobo browser. (You do not need an internet connection. Connecting to a network without internet access seems to work) 

## Uninstall BMR
To uninstall BMR, connect your Kobo to your computer and navigate to KOBOeReader/.BMR and create a file (any type) called "uninstall".
Next, run the startup script from your Kobo: go to nickel menu and select Start BMR server.
This will remove BMR and all of the contents of KOBOeReader/.BMR. Any downloaded contents will be lost. Make a backup of the KOBOeReader/.BMR/static/library directory to keep your downloads.
To remove the NickelMenu entries, you will have to open the config file from KOBOeReader/.adds/nm/ and remove the entries manually.

## Obligatory Disclaimer:
I have developed and tested the application on a Kobo Libra 2, which is the only Kobo device I own. I cannot guarantee that it will work as intended on other Kobo devices. Use at your own risk. I am not responsible for any damages/ bricking of your devices.

## Known Bugs and occurances:
1. The first time you open the app using "Open BMR", it may fail, as it needs a couple of seconds for the server to start. Future trials will be faster
2. There is a small image near the hamburger menu icon when the app opens up. This seems to be an artifact of the eink screen. It disappears after clicking/touching anywhere else.
3. Once a chapter link is clicked, loading the first manga page may require about 30 seconds. This is because all of the images are downlaoded to the cache for fast scrolling.
4. Sometimes, when opening a manga chapter, the screen will be blank except for a small box with a "?" in the middle of the screen. Hitting the refresh icon of the browser will solve this problem. This seems to happen because some times the program jumps to the next step without completing the current step (starts to show image without actually fetching it first)

## More
Go to <a href="https://www.mobileread.com/forums/showthread.php?t=348950">mobileread</a> for more details and to ask questions

## Acknowlegements
Many thanks to all the developers of <a href="https://github.com/pgaskin/NickelMenu">NickelMenu</a> for creating a tool that allows us to experiment with our Kobos. 

The idea of using the browser and the startup script were inspired by the <a href="https://www.mobileread.com/forums/showthread.php?t=262353">WebPortal</a> project by <a href="https://github.com/frostschutz">frostschutz</a>

## Leave a Tip!
If you enjoyed using Banana Manga Reader, leave a nice comment on the mobileread page. Better yet, leave me a tip in my tip jar! (paypal: buxared14@gmail.com) As a novice in python, HTML and Linux, it took me many hours and many months to get here. BMR will always remain free, so consider donating. Thanks! 
## I hope you have fun using Banana Manga Reader! Go Bananas !!
