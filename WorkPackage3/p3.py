# Import libraries
import RPi.GPIO as GPIO
import random
import ES2EEPROMUtils
import os
import time

# some global variables that need to change as we run the program
end_of_game = None  # set if the user wins or ends the game

# DEFINE THE PINS USED HERE
LED_value = [11, 13, 15]
LED_accuracy = 32
btn_submit = 16
btn_increase = 18
#buzzer = None
user_guess = 0
eeprom = ES2EEPROMUtils.ES2EEPROM()
# Print the game banner
def welcome():
    os.system('clear')
    print("  _   _                 _                  _____ _            __  __ _")
    print("| \ | |               | |                / ____| |          / _|/ _| |")
    print("|  \| |_   _ _ __ ___ | |__   ___ _ __  | (___ | |__  _   _| |_| |_| | ___ ")
    print("| . ` | | | | '_ ` _ \| '_ \ / _ \ '__|  \___ \| '_ \| | | |  _|  _| |/ _ \\")
    print("| |\  | |_| | | | | | | |_) |  __/ |     ____) | | | | |_| | | | | | |  __/")
    print("|_| \_|\__,_|_| |_| |_|_.__/ \___|_|    |_____/|_| |_|\__,_|_| |_| |_|\___|")
    print("")
    print("Guess the number and immortalise your name in the High Score Hall of Fame!")


# Print the game menu
def menu():
    global end_of_game
    option = input("Select an option:   H - View High Scores     P - Play Game       Q - Quit\n")
    option = option.upper()
    if option == "H":
        os.system('clear')
        print("HIGH SCORES!!")
        s_count, ss = fetch_scores()
        display_scores(s_count, ss)
    elif option == "P":
        os.system('clear')
        print("Starting a new round!")
        print("Use the buttons on the Pi to make and submit your guess!")
        print("Press and hold the guess button to cancel your game")
        global value
        value = generate_number()
        while not end_of_game:
            pass
    elif option == "Q":
        print("Come back soon!")
        exit()
    else:
        print("Invalid option. Please select a valid one!")


def display_scores(count, raw_data):
    # print the scores to the screen in the expected format
    print("There are {} scores. Here are the top 3!".format(count))
    # print out the scores in the required format
    if count < 3:
    	for i in range(0,count):
        	temp = raw_data[i]
        	position = i+1
        	print(str(position) + " - " + temp[0] + " took " + str(temp[1]) + " guesses")
    elif count == 0:
    	print("No high scores recorded.")
    else:
    	for i in range(0,3):
        	temp = raw_data[i]
        	position = i+1
        	print(str(position) + " - " + temp[0] + " took " + str(temp[1]) + " guesses")
    menu()
    GPIO.cleanup()
    setup()
    pass


# Setup Pins
def setup():
    global number_of_guesses
    number_of_guesses = 0
    user_guess = 0
    # Setup board mode
    GPIO.setmode(GPIO.BOARD)	#Define the board set up following a GPIO.Board setup
    # Setup regular GPIO
    GPIO.setup(11, GPIO.OUT)	#Setup the 1st LED as an output 
    GPIO.output(11, GPIO.LOW)
    
    GPIO.setup(13, GPIO.OUT)	#Setup the 2nd LED as an output 
    GPIO.output(13, GPIO.LOW)
    
    GPIO.setup(15, GPIO.OUT)	#Setup the 3rd LED as an output 
    GPIO.output(15, GPIO.LOW)
    GPIO.setup(32, GPIO.OUT)	#Setup the accurcy LED as an output 
    GPIO.output(32, GPIO.LOW)
    
    GPIO.setup(33, GPIO.OUT)    #setting the buzzer as an output 
    #GPIO.output(33, GPIO.LOW)
    
    GPIO.setup(16, GPIO.IN)		#Initialised the first button as an input 
    GPIO.setup(18, GPIO.IN)		#setup the second  button as an input 
    #eeprom.clear(2048)
    # Setup PWM channels
    global buzzerPwm
    buzzerPwm = GPIO.PWM(33, 0.5)  #setting up the buzzer as pwm
    buzzerPwm.start(50)
    global LEDPwm
    LEDPwm = GPIO.PWM(32, 1000) #setting up the LED with pwm
    # Setup debouncing and callbacks
    GPIO.setup(16, GPIO.IN, pull_up_down=GPIO.PUD_UP)
    GPIO.add_event_detect(16, GPIO.FALLING, callback=btn_guess_pressed, bouncetime=200)
    GPIO.setup(18, GPIO.IN, pull_up_down=GPIO.PUD_UP)
    GPIO.add_event_detect(18, GPIO.FALLING, callback=btn_increase_pressed, bouncetime=200)
    
    pass


# Load high scores
def fetch_scores():
    
    # get however many scores there are
    score_count = eeprom.read_byte(0)  #reading the first register to get the number of high scores registered.
    # Get the scores
    scores = [] #initiating the array to store the scores 
    j = 7   #Variabe to locate the high score values 
    #For loop to iterate through registers
    for i in range(0, score_count) :
        string = ""
        for k in range((i+1)*4,(i+1)*4+3):
            string = string + chr(eeprom.read_byte(k))
        scores.append([string, eeprom.read_byte(j)]) #reading in the scores and storing in the array 
        j += 4      #incremetation to go to the next register were a score is stored   
        
    # return back the results
    return score_count, scores


# Save high scores
def save_scores():
    # fetch scores
    fetch_scores()
    # include new score
    
    # sort
    # update total amount of scores
    # write new scores
    pass


# Generate guess number
def generate_number():
    return random.randint(0, pow(2, 3)-1)


# Increase button pressed
def btn_increase_pressed(channel):
    global user_guess 
    user_guess += 1
    # Increase the value shown on the LEDs
    if user_guess == 1:
        GPIO.output(11, GPIO.LOW)
        GPIO.output(13, GPIO.LOW)
        GPIO.output(15, GPIO.HIGH)
    elif user_guess == 2:
        GPIO.output(11, GPIO.LOW)
        GPIO.output(13, GPIO.HIGH)
        GPIO.output(15, GPIO.LOW)
    elif user_guess == 3:
        GPIO.output(11, GPIO.LOW)
        GPIO.output(13, GPIO.HIGH)
        GPIO.output(15, GPIO.HIGH)
    elif user_guess == 4:
        GPIO.output(11, GPIO.HIGH)
        GPIO.output(13, GPIO.LOW)
        GPIO.output(15, GPIO.LOW)
    elif user_guess == 5:
        GPIO.output(11, GPIO.HIGH)
        GPIO.output(13, GPIO.LOW)
        GPIO.output(15, GPIO.HIGH)
    elif user_guess == 6:
        GPIO.output(11, GPIO.HIGH)
        GPIO.output(13, GPIO.HIGH)
        GPIO.output(15, GPIO.LOW)
    elif user_guess == 7:
        GPIO.output(11, GPIO.HIGH)
        GPIO.output(13, GPIO.HIGH)
        GPIO.output(15, GPIO.HIGH)
    else:
        GPIO.output(11, GPIO.LOW)
        GPIO.output(13, GPIO.LOW)
        GPIO.output(15, GPIO.LOW)
        user_guess = 0;
    
    # You can choose to have a global variable store the user's current guess, 
    # or just pull the value off the LEDs when a user makes a guess
    pass


# Guess button
def btn_guess_pressed(channel):
    
    score_count, scores = fetch_scores()
    startTime = time.time()
    timeButton = time.time() - startTime #check how long the button was pressed for 
    # If they've pressed and held the button, clear up the GPIO and take them back to the menu screen
    if timeButton > 0.2:
        GPIO.cleanup()
        buzzerPwm.stop()
        LEDPwm.stop()
        menu()
        
    # Compare the actual value with the user value displayed on the LEDs
    # Change the PWM LED
    
    else: 
        if user_guess == value:
            number_of_guesses += 1
            buzzerPwm.stop()
            LEDPwm.stop()
            print("Congratulations!!! You guessed the correct number " + str(value))
            name = ""
            #while len(name) != 3:
            name = input("Enter your name. Must be 3 letter:\n")
            score_count += 1
            scores.append([name,number_of_guesses])
            scores.sort(key=lambda x: x[1])
            pop_scores = 7
            eeprom.write_byte(0, score_count)
            for h in range(0, score_count):
                temp = scores[h]
                temp_name = temp[0]
                temp_count = 0;
                for t in range((h+1)*4,(h+1)*4+3):
                    eeprom.write_byte(t, ord(temp_name[temp_count]))
                    temp_count += 1
                eeprom.write_byte(pop_scores, temp[1])
                pop_scores += 4
            GPIO.cleanup()
            setup()
            menu()
        else:
            number_of_guesses += 1
            accuracy_leds()
            trigger_buzzer()
    # if it's close enough, adjust the buzzer
 
    # if it's an exact guess:
    # - Disable LEDs and Buzzer
    # - tell the user and prompt them for a name
    # - fetch all the scores
    # - add the new score
    # - sort the scores
    # - Store the scores back to the EEPROM, being sure to update the score count
  
    pass


# LED Brightness
def accuracy_leds():
    percentage = 0
    
    # Set the brightness of the LED based on how close the guess is to the answer
    # - The % brightness should be directly proportional to the % "closeness"
    # - For example if the answer is 6 and a user guesses 4, the brightness should be at 4/6*100 = 66%
    # - If they guessed 7, the brightness would be at ((8-7)/(8-6)*100 = 50%
    if user_guess < value :
        percentage = ((user_guess/value)*100)
        LEDPwm.start(percentage)
        
    elif user_guess > value:
        percentage =(((8-user_guess)/(8-value))*100)
        LEDPwm.start(percentage)  
    else:
        LEDPwm.start(percentage)
    pass

# Sound Buzzer
def trigger_buzzer():
    # The buzzer operates differently from the LED
    # While we want the brightness of the LED to change(duty cycle), we want the frequency of the buzzer to change
    # The buzzer duty cycle should be left at 50%
    # If the user is off by an absolute value of 3, the buzzer should sound once every second
    # If the user is off by an absolute value of 2, the buzzer should sound twice every second
    # If the user is off by an absolute value of 1, the buzzer should sound 4 times a second
    if abs(user_guess-value) ==  3:
        buzzerPwm.start(50)
        buzzerPwm.ChangeFrequency(1)
    elif abs(user_guess-value) ==  2:
        buzzerPwm.start(50)
        buzzerPwm.ChangeFrequency(2)
    elif abs(user_guess-value) ==  1:
        buzzerPwm.start(50)
        buzzerPwm.ChangeFrequency(4)
    pass


if __name__ == "__main__":
    try:
        # Call setup function
        setup()
        welcome()
        while True:
            menu()
            pass
    except Exception as e:
        print(e)
    finally:
        GPIO.cleanup()
