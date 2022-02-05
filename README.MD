# PyBOT - Pyautogui
## Description
This project is to test the pyautogui library.

## Project Test
Azur Lane - Stage 12 Automation
* Limitation: pyautogui has difficulty with scaled GUI images. Therefore, i wrote a script to create a scaled image. But it is not perfect

###Prep Work - Azur Lane
In Folder @ <u>"pybot\azurlane\GUI"</u>, replace GUI images with full screen images of selected GUI Buttons. A scaler is used to down scale images so that user is able to use pybot even emulator is not full screen mode. Of course it works best if it is full screen.
###Initialize Azur Lane Project
1. Replace pybot\azurlane\GUI images with your own screen shots at full screen.
2. you can only run the script when game is in the main menu. This allows the script to sync with the emulator GUI.
3. run "python pybot -tgi", to generate scaled images of the GUI. This is so that when you make your emulator smaller, we still can use the pybot.