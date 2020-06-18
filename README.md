# HReader
Interactive data visualization tool for Facebook Messages.
# About
Inspired by r/dataisbeautiful, I decided to make my own data visualisation tool to visualize Facebook Messages using the data You can download.

To make it, I used Python for all the data reading and calculations with Dash library for making the graphs and BeautifulSoup library for parsing HTML files. To create a simple UI, I made a C# program using WPF to display the inputs and the informations, and interact with the Python script that I converted to an exacutable using PyInstaller to work on machines without Python.

The user is presented with an interactive dashboard, which shows many interesing graphs and updates them in real-time after selecting a  timeframe on a main graph. The customization includes: changing colors for each person, enabling/disabling certain features and modifying graph parameters.

This is my first project using Python, and a first one that I'm putting on GitHub, so tips, criticism or any feedback is most welcome.
# How to use
To run this app on Your pc You can:
- download the setup file [hreader-setup.exe](hreader-setup.exe) and install it, 
- clone the repository and use executable file [hreader.exe](hreader/bin/Release/hreader.exe) or 
- run the python script [fdash.py](fdash/fdash.py) with the arguments described in [running_example.txt](fdash/running_example.txt)
# How to download data from Facebook
- Log in to Your account on [facebook](https://Facebook.com/)
- Navigate through Settings -> Your Facebook Information -> Download Your Information
- Media quality doesn't matter for this application
- This program works for both formats, but JSON is way faster and HTML still has some bugs and lacks some features
- After you make a request to create a file, it usually takes ~1-2 days until you can download it
- After downloading the files, unzip them somewhere - this will be Your "Conversation directory"
