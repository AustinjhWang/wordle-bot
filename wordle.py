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

# keep track of correct letters (green), possible letters (yellow), and letters that do not exist (grey)
Correct_letters = []
Possible_letters = set()
DNE_letters = set()

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
                  Correct_letters.append((previous_guess[index], index))
            elif item == "present":
                  Possible_letters.add((previous_guess[index], index))
            index = index + 1
      
      # check for absent after adding correct letters to avoid grey green
      # only add to DNE if letter is not already in correct/possible letters
      index = 0
      for item in feedback:
            if item == "absent":
                  letter = previous_guess[index]
                  
                  # convert list of tuples into list
                  correct_letters_list = [element for tuple in Correct_letters for element in tuple]
                  possible_letters_list = [element for tuple in Possible_letters for element in tuple]

                  if letter not in correct_letters_list and letter not in possible_letters_list:
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

      for word in remove_set:
            words_list.remove(word)
      
      #feedback
      print("Correct Letters")
      print(Correct_letters)
      print("Possible Letters")
      print(Possible_letters)
      print("Not Possible Letters")
      print(DNE_letters)
      print("Number of possible words left: " + str(len(words_list))) 

      word = random.choice(words_list)
      print(f"New guess: {word}")
      return word

def run(share):
      driver = webdriver.Chrome()
      driver.get("https://www.nytimes.com/games/wordle/index.html")
      #driver.get("https://wordle.berknation.com/")
      webdriver.ActionChains(driver).click().perform()

      guess_number = 0
      previous_guess = ""
      feedback = []

      while not done(feedback) and guess_number < 6:
            if guess_number != 0:
                  time.sleep(2)

            guess_number = guess_number + 1
            guess = create_guess(feedback, previous_guess)
            previous_guess = guess

            webdriver.ActionChains(driver).send_keys(guess + Keys.ENTER).perform()

            row = driver.execute_script(f"return document.querySelector('game-app').shadowRoot.querySelector('game-row:nth-child({guess_number})').shadowRoot.querySelectorAll('game-tile')")
            feedback = []
            for tile in row:
                  feedback.append(tile.get_attribute("evaluation"))
                  print(tile.get_attribute("evaluation"))

      # wait for results to show and click share button
      if share == True:
            time.sleep(5)
            share_button = driver.execute_script("return document.querySelector('game-app').shadowRoot.querySelector('game-stats').shadowRoot.querySelector('button')")
            webdriver.ActionChains(driver).click(share_button).perform()
            
      driver.quit()
      return guess_number

if __name__ == "__main__":
      run(True)