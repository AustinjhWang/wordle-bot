from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time 
import random

# create list from words.txt
words_file = open("words.txt", "r")
words_string = words_file.read() # a string
words_list = words_string.split("\n") # returns list
words_file.close()

# keep track of correct letters (green), possible letters (yellow), letters that do not exist (grey),
# and letters that are already correct elsewhere (grey with a green of same letter)
Correct_letters = set()
Possible_letters = set()
DNE_letters = set()
Grey_correct_letters = set()

def done(feedback):

      # feedback is initially empty so just return False
      if feedback == []:
            return False

      for item in feedback:
            if item != 'correct':
                  return False
      return True

def create_guess(feedback, previous_guess):
      
      # initially there is no feedback or previous guess
      if feedback == [] and previous_guess == "":
            word = input("Enter a guess or press enter for default: ")
            if word == "":
                  word = "salet"
            print(f"Initial guess is: {word}")
            return word

      index = 0
      for item in feedback:
            if item == "correct":
                  Correct_letters.add((previous_guess[index], index))
            elif item == "present":
                  Possible_letters.add((previous_guess[index], index))
            index = index + 1
      
      # check for absent after adding correct letters to avoid grey green
      index = 0
      for item in feedback:
            if item == "absent":
                  letter = previous_guess[index]
                  
                  # convert list of tuples into list
                  correct_letters_list = [element for tuple in Correct_letters for element in tuple]
                  possible_letters_list = [element for tuple in Possible_letters for element in tuple]

                  # yellow/grey case
                  if letter in possible_letters_list:
                        Possible_letters.add((letter, index))

                  # green/grey, grey/green case
                  elif letter in correct_letters_list:
                        Grey_correct_letters.add(letter)

                  # only add to DNE if letter is not already in correct/possible letters
                  elif letter not in correct_letters_list and letter not in possible_letters_list:
                        DNE_letters.add(letter)               

            index = index + 1
      
      # loop through wordlist and remove all invalid words
      remove_set = set()
      for word in words_list:

            for letter, index in Correct_letters:
                  if word[index] != letter:
                        remove_set.add(word)

            for letter in DNE_letters:
                  if letter in word: 
                        remove_set.add(word)

            for letter, index in Possible_letters:
                  if letter not in word:
                        remove_set.add(word)
                  if word[index] == letter:
                        remove_set.add(word)

            for letter in Grey_correct_letters:
                  # if word contains letter, it has to be in position index
                  if letter in word:
                        indicies = [i for i, char in enumerate(word) if char == letter]
                        index = word.index(letter)
                        if indicies != [index]:
                              remove_set.add(word)

      for word in remove_set:
            words_list.remove(word)
      
      #feedback
      print("Correct Letters")
      print(Correct_letters)
      print("Possible Letters")
      print(Possible_letters)
      print("Not Possible Letters")
      print(DNE_letters)
      print("Grey Correct Letters")
      print(Grey_correct_letters)
      print("Number of possible words left: " + str(len(words_list))) 

      word = random.choice(words_list)
      print(f"New guess: {word}")
      return word

def run(share):
      driver = webdriver.Chrome()
      driver.get("https://www.nytimes.com/games/wordle/index.html")
      webdriver.ActionChains(driver).click().perform()
      
      # get through to the game screen
      continue_button = driver.execute_script("return document.querySelector('.purr-blocker-card__button')")
      webdriver.ActionChains(driver).click(continue_button).perform()
      button_board = driver.execute_script("return document.querySelector('div[class=Welcome-module_buttonContainer__K4GEw]')")
      buttons = button_board.find_elements(By.CLASS_NAME, "Welcome-module_button__ZG0Zh.Welcome-module_gameSaleStyle__duVA4")
      play_button = buttons[3]
      webdriver.ActionChains(driver).click(play_button).perform()
      time.sleep(1)
      webdriver.ActionChains(driver).send_keys(Keys.ENTER).perform()

      guess_number = 0
      previous_guess = ""
      feedback = []

      while not done(feedback) and guess_number < 6:
            guess_number = guess_number + 1
            guess = create_guess(feedback, previous_guess)
            previous_guess = guess

            webdriver.ActionChains(driver).send_keys(guess + Keys.ENTER).perform()

            time.sleep(3)
            row = driver.execute_script(f"return document.querySelector('div[aria-label=\"Row {guess_number}\"]')")
            tiles = row.find_elements(By.CLASS_NAME, "Tile-module_tile__UWEHN")
            feedback = []
            for tile in tiles:
                  print(tile.text + " " + tile.get_dom_attribute("data-state"))
                  feedback.append(tile.get_dom_attribute("data-state"))

      # wait for results to show and click share button
      if share == True:
            time.sleep(3)
            cancel_button = driver.execute_script("return document.querySelector('.Modal-module_closeIconButton__y9b6c')")
            webdriver.ActionChains(driver).click(cancel_button).perform()
            time.sleep(1)
            share_button = driver.execute_script("return document.querySelector('.Footer-module_shareButton__cHprS')")
            webdriver.ActionChains(driver).click(share_button).perform()
            
      driver.quit()
      return guess_number

if __name__ == "__main__":
      run(True)