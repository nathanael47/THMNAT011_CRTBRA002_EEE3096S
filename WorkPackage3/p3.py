# Import libraries
import RPi.GPIO as GPIO
import random
import ES2EEPROMUtils
import os
import time

# some global variables that need to change as we run the program
end_of_game = None  # set if the user wins or ends the game

# DEFINE THE PINS USED HERE
LED_value = [11, 13, 15] #definining the pins of the LED to show the guess value 
LED_accuracy = 32  #pin of the LED accuracy 
btn_submit = 16 #defining the pin of the submit button 
btn_increase = 18 #defining the button for the increase LED 
#buzzer = None
#global user_guess, number_of_guesses
#initiating the global variables
value = 0
user_guess = 0
number_of_guesses = 0
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
    global value
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
        value = generate_number()
        while not end_of_game:
            pass
    elif option == "Q":
        print("Come back soon!")
        exit()
    else:
        print("Invalid option. Please select a valid one!")

#function to display the top 3 scores 
def display_scores(count, raw_data):
    # print the scores to the screen in the expected format
    print("There are {} scores. Here are the top 3!".format(count))
    # print out the scores in the required format
    #if there are less than 3 scores stored in the eeprom 
    if count < 3:
        #interate through the values in the values stored 
    	for i in range(0,count):
        	temp = raw_data[i] #temporary array to hold the values through the for loop 
        	position = i+1   #the position either 1, 2 or 3 
        	print(str(position) + " - " + temp[0] + " took " + str(temp[1]) + " guesses")  #formatting to print out the high scores 
    #case is no scores have been stored yet 
    elif count == 0:
    	print("No high scores recorded.")
    #case for when there is more than 3 scores stored in the eeprom 
    else:
        #iterate through the values stored in the eeprom 
    	for i in range(0,3):
        	temp = raw_data[i] #temporary array to store 
        	position = i+1
        	print(str(position) + " - " + temp[0] + " took " + str(temp[1]) + " guesses") #format for the print statement 
    menu() #to prompt the user if they want to play again or quit 
    GPIO.cleanup() #cleanup the GPIOs 
    setup() #to setup the game again 
    pass


# Setup Pins
def setup():
 
    # Setup board mode
    GPIO.setmode(GPIO.BOARD)	#Define the board set up following a GPIO.Board setup
    # Setup regular GPIO
    GPIO.setup(11, GPIO.OUT)	#Setup the 1st LED as an output 
    GPIO.output(11, GPIO.LOW)   #set up the lED to initial value of low/ off 
    
    GPIO.setup(13, GPIO.OUT)	#Setup the 2nd LED as an output 
    GPIO.output(13, GPIO.LOW)   #set up the lED to initial value of low/ off
    
    GPIO.setup(15, GPIO.OUT)	#Setup the 3rd LED as an output 
    GPIO.output(15, GPIO.LOW)   #set up the lED to initial value of low/ off
    GPIO.setup(32, GPIO.OUT)	#Setup the accurcy LED as an output 
    GPIO.output(32, GPIO.LOW)   #set up the lED to initial value of low/ off
    
    GPIO.setup(33, GPIO.OUT)    #setting the buzzer as an output 
    #GPIO.output(33, GPIO.LOW)
    
    GPIO.setup(16, GPIO.IN)		#Initialised the first button as an input 
    GPIO.setup(18, GPIO.IN)		#setup the second  button as an input 
   # eeprom.clear(2048)
    # Setup PWM channels
    global buzzerPwm
    buzzerPwm = GPIO.PWM(33, 1)  #setting up the buzzer as pwm
    buzzerPwm.stop()  #to make sure the buzzer if off unless it is intiated 
    #buzzerPwm.start(50)
    global LEDPwm
    LEDPwm = GPIO.PWM(32, 1000) #setting up the LED with pwm
    # Setup debouncing and callbacks
    #setting up the submitting button 
    GPIO.setup(16, GPIO.IN, pull_up_down=GPIO.PUD_UP)  #setting up the initial                    
    GPIO.add_event_detect(16, GPIO.FALLING, callback=btn_guess_pressed, bouncetime=200) #setting the callback 
    # Setup of the user increment button 
    GPIO.setup(18, GPIO.IN, pull_up_down=GPIO.PUD_UP) #intial setup 
    GPIO.add_event_detect(18, GPIO.FALLING, callback=btn_increase_pressed, bouncetime=200) #setup trigger 
    
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
        string = "" #place holder to hold the name 
        #used to retrieve the name of the highscore holder 
        for k in range((i+1)*4,(i+1)*4+3): 
            string = string + chr(eeprom.read_byte(k)) #appending to an empty string and forming the name 
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
    #setting up the binary for the number 1(001)
    if user_guess == 1:
        GPIO.output(11, GPIO.LOW) #LED off 
        GPIO.output(13, GPIO.LOW) #LED off 
        GPIO.output(15, GPIO.HIGH) #LED on 
    #setting up the binary for the number 2(010)
    elif user_guess == 2:
        GPIO.output(11, GPIO.LOW) #LED off 
        GPIO.output(13, GPIO.HIGH) #LED on
        GPIO.output(15, GPIO.LOW) #LED off 
    #setting up the binary for the number 3(011)
    elif user_guess == 3:
        GPIO.output(11, GPIO.LOW) #LED off 
        GPIO.output(13, GPIO.HIGH) #LED on
        GPIO.output(15, GPIO.HIGH) #LED on
    #setting up the binary for the number 4(100)
    elif user_guess == 4:
        GPIO.output(11, GPIO.HIGH) #LED on
        GPIO.output(13, GPIO.LOW) #LED off 
        GPIO.output(15, GPIO.LOW) #LED off 
    #setting up the binary for the number 5(101)
    elif user_guess == 5:
        GPIO.output(11, GPIO.HIGH) #LED on
        GPIO.output(13, GPIO.LOW) #LED off 
        GPIO.output(15, GPIO.HIGH) #LED on
    #setting up the binary for the number 6(110)
    elif user_guess == 6:
        GPIO.output(11, GPIO.HIGH) #LED on
        GPIO.output(13, GPIO.HIGH) #LED on
        GPIO.output(15, GPIO.LOW) #LED off 
    #setting up the binary for the number 7(111)
    elif user_guess == 7:
        GPIO.output(11, GPIO.HIGH) #LED on
        GPIO.output(13, GPIO.HIGH) #LED on
        GPIO.output(15, GPIO.HIGH) #LED on
    #setting up the binary for the number 0(000)
    else:
        GPIO.output(11, GPIO.LOW) #LED off 
        GPIO.output(13, GPIO.LOW) #LED off 
        GPIO.output(15, GPIO.LOW) #LED off 
        user_guess = 0
    
    # You can choose to have a global variable store the user's current guess, 
    # or just pull the value off the LEDs when a user makes a guess
    pass


# Guess button
def btn_guess_pressed(channel):
    #getting the global variables 
    global number_of_guesses
    global user_guess
    global value
    score_count, scores = fetch_scores() #getting the scores
    startTime = time.time() #intiating a start time 
    #while the button is not pressed 
    while GPIO.input(16) == 0:
    	pass
    timeButton = time.time() - startTime #check how long the button was pressed for 
    # If they've pressed and held the button, clear up the GPIO and take them back to the menu screen
    #if the buzzer is pressed for two long
    if timeButton > 0.2:
        GPIO.cleanup() #cleaning up the GPIO pins 
        buzzerPwm.stop() #stopping the buzzer 
        LEDPwm.stop() #stopping the LEDPWM 
        menu() #going back to the menu page 
        
    # Compare the actual value with the user value displayed on the LEDs
    # Change the PWM LED
    
    else: 
        #case if the guess value and the randomly generated number 
        if user_guess == value: 
            number_of_guesses += 1 #incrementing the users guess 
            buzzerPwm.stop() #stopping the buzzer 
            print("Congratulations!!! You guessed the correct number " + str(value)) #Congratulation message 
            name = "" #empty string to store the users name 
            #while len(name) != 3:
            name = input("Enter your name. Must be 3 letter:\n") #prompting the user to insert their name 
            score_count += 1 #increasing the number of high scores stored 
            scores.append([name,number_of_guesses]) #appending to an array list 
            scores.sort(key=lambda x: x[1]) #sorting out the array list from highest to lowest 
            pop_scores = 7 #position of were the number of guesses should be stored 
            eeprom.write_byte(0, score_count) #writing to the eeprom for the number of highscrores that need to be stored 
            #Writing to the eeprom 
            for h in range(0, score_count):
                temp = scores[h] #temporary array 
                temp_name = temp[0]
                temp_count = 0;
                #inserting to the registers within the eeprom 
                for t in range((h+1)*4,(h+1)*4+3):
                    eeprom.write_byte(t, ord(temp_name[temp_count]))
                    temp_count += 1
                eeprom.write_byte(pop_scores, temp[1])
                pop_scores += 4
            GPIO.cleanup() #cleanup GPIOs
            user_guess = 0 #reset user guess 
            LEDPwm.stop() #stop LED 
            setup() #setup again 
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
    global value
    global user_guess
    percentage = 0
    
    # Set the brightness of the LED based on how close the guess is to the answer
    # - The % brightness should be directly proportional to the % "closeness"
    # - For example if the answer is 6 and a user guesses 4, the brightness should be at 4/6*100 = 66%
    # - If they guessed 7, the brightness would be at ((8-7)/(8-6)*100 = 50%
    #case were the guessed value is less than the generated number but not eqaul zero 
    if user_guess < value and user_guess != 0 :
    	percentage = ((user_guess/value)*100) #obtaining a percetange of how close it is to the value 
    	LEDPwm.start(percentage) #starting the LED 
    #case where the guessed value is greater than the actual value 
    elif user_guess > value:
    	percentage =(((8-user_guess)/(8-value))*100) #obtaining a percetange of how close it is to the value
    	LEDPwm.start(percentage) #starting the LED 
    #case where the guessed value is less than the actual value and equal to zero 
    elif user_guess < value and user_guess == 0:
    	percentage = ((user_guess+1)/(value+1))*100 #obtaining a percetange of how close it is to the value
    	LEDPwm.start(percentage) #starting the LED 
    # when the guess value is exactly the randomly generated value 
    elif user_guess == value:
    	LEDPwm.start(100) #starting the LED 
    else:
    	LEDPwm.start(percentage) #starting the LED 
    pass

# Sound Buzzer
def trigger_buzzer():
    global user_guess
    global value
    # The buzzer operates differently from the LED
    # While we want the brightness of the LED to change(duty cycle), we want the frequency of the buzzer to change
    # The buzzer duty cycle should be left at 50%
    # If the user is off by an absolute value of 3, the buzzer should sound once every second
    if abs(user_guess-value) ==  3:
    	#GPIO.output(33, GPIO.HIGH)
    	buzzerPwm.start(50) #start the buzzer 
    	buzzerPwm.ChangeFrequency(1) #change the frequency so it buzzes once every second 
    # If the user is off by an absolute value of 2, the buzzer should sound twice every second
    elif abs(user_guess-value) ==  2:
    	#GPIO.output(33, GPIO.HIGH)
    	buzzerPwm.start(50) #start the buzzer 
    	buzzerPwm.ChangeFrequency(2) #change the frequency so it buzzes twice  every second 
    # If the user is off by an absolute value of 1, the buzzer should sound 4 times a second
    elif abs(user_guess-value) ==  1:
    	#GPIO.output(33, GPIO.HIGH)
    	buzzerPwm.start(50) #start the buzzer 
    	buzzerPwm.ChangeFrequency(4) #change the frequency so it buzzes four times every second 
    else:
    	pass
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
