import pygame #import pygame module for game development
import sys #import sys module to handle system-specific functions (like exiting using sys.exit())
import os #import os module for interacting with the operating system (relative paths)
import random #import random module for random number generation 

pygame.init() #initialize pygame
pygame.mixer.init() #initialize the mixer module for sound effects and music

#relative paths so the game works on all computers once the zip file is extracted
script_dir = os.path.dirname(os.path.abspath(__file__))
base_dir = os.path.dirname(os.path.abspath(__file__))
image_dir = os.path.join(base_dir, "images")
music_dir = os.path.join(base_dir, "music")

#set file paths for all music files
background_music_path = os.path.join(music_dir, "background_music.mp3")
menu_music_path = os.path.join(music_dir, "menu_music.mp3")
win_music_path = os.path.join(music_dir, "win.mp3")
lose_music_path = os.path.join(music_dir, "lose.mp3")

#load click sound effect from music folder (separate from other sounds because it's a sound effect that is only played on button presses)
click_sound_path = os.path.join(music_dir, "click.mp3") #path for click sound effect
try: 
    click_sound = pygame.mixer.Sound(click_sound_path) 
except Exception as e:
    print(f"Could not load click sound: {e}")
    click_sound = None #set click_sound to None if not loaded to avoid errors

#function to load images based on room name
def loc(name):
    global current_image #declare current_image as global variable (because we need to use it outside this function)
    image_path = os.path.join(image_dir, name + ".jpg") #create path to the image file using room name
    current_image = pygame.image.load(image_path) #load the image from file
    if where != "menu":
        current_image = pygame.transform.scale(current_image, (1000, 600))
    else:
        current_image = pygame.transform.scale(current_image, (1000, 700)) #this part exists so the black bar isn't obstructing the visuals of the menu since we don't need to display text down there

#dictionary for choices 'a' with room transitions
#room to the left side of the ':' is the current room, while the room to the right is the next room if 'a' is pressed
a = {
    "basement": "basement_stairs",
    "basement_stairs": "hallway",
    "hallway": "living_room",
    "kitchen": "pantry",
    "bathroom": "hallway",
    "living_room": "front_door",
    "garage": "car",
    "dining_room": "kitchen",
    "upstairs": "bedroom",
    "bedroom": "bedroom_window",
    "office": "living_room",
    "laundry_room": "back_door",
    "back_door": "garden",
    "garden": "front_gate",
    "menu": "basement" #from menu, option a starts game by going to basement
}

#dictionary for choices 'b' with room transitions
#room to the left side of the ':' is the current room, while the room to the right is the next room if 'b' is pressed
b = {
    "basement": "closet",
    "basement_stairs": "kitchen",
    "hallway": "bathroom",
    "kitchen": "dining_room",
    "bathroom": "bathroom_window",
    "living_room": "office",
    "garage": "storage",
    "dining_room": "upstairs",
    "upstairs": "attic",
    "bedroom": "upstairs",
    "office": "laundry_room",
    "laundry_room": "garage",
    "back_door": "laundry_room",
    "garden": "shed",
    "menu": "basement" #from menu, option b starts game by going to basement
}

#separate dictionary for endings and their respective descriptions
endings = {
    "closet": "You couldn't muster the courage to escape and were eventually caught! GAME OVER. Press 'r' to restart.", #lose
    "attic": "The floorboards were too creaky, giving you away! GAME OVER. Press 'r' to restart.", #lose
    "front_door": "The front door is obviously barricaded shut and you were caught. GAME OVER. Press 'r' to restart.", #lose
    "storage": "While looking through the storage, you got a lethal splinter! GAME OVER. Press 'r' to restart.", #lose
    "pantry": "You slipped on a banana peel. GAME OVER. Press 'r' to restart.", #lose
    "car": "You hotwired the car and sped off! YOU WIN! Press 'r' to restart.", #win
    "bathroom_window": "You took a risk, climbed out the window, and ran away! YOU WIN! Press 'r' to restart.", #win
    "bedroom_window": "You jumped from the bedroom window but it was too high up, breaking your leg. GAME OVER. Press 'r' to restart.", #lose
    "shed": "What made you think going into a shed was more important than escaping? You fell into a trap and got caught! GAME OVER. Press 'r' to restart.", #lose
    "front_gate": "You jumped the gate and escaped! YOU WIN! Press 'r' to restart.", #win
    "caught": "You got caught and couldn't escape! GAME OVER. Press 'r' to restart. " #lose, failed to press random key in time
}

#separate endings for music selection
win_endings = {"car", "bathroom_window", "front_gate"}
lose_endings = {"closet", "attic", "front_door", "storage", "pantry", "bedroom_window", "shed", "caught"}

#ensures that a and b are not continuously triggered
is_a = False
is_b = False

#define colors using rgb color model that we use for text and text background
black = (0, 0, 0)
white = (255, 255, 255)

#set up the display window with specific dimensions
screen_width, screen_height = 1000, 700
screen = pygame.display.set_mode((screen_width, screen_height)) #initialize display window with dimensions
pygame.display.set_caption("Escape") #set window caption

font = pygame.font.SysFont(None, 32) #initialize font with default system font and size 32

#function to handle switching music based on the room in-game
def play_music(music_type):
    pygame.mixer.music.stop() #stop any currently playing music (don't want them to overlap)
    if music_type == "menu":
        file_path = menu_music_path
    elif music_type == "background":
        file_path = background_music_path
    elif music_type == "win":
        file_path = win_music_path
    elif music_type == "lose":
        file_path = lose_music_path
    else:
        print(f"unknown music type: {music_type}")
        return
    try:
        pygame.mixer.music.load(file_path) #load the selected music file
        if music_type in ("menu", "background"):
            pygame.mixer.music.play(-1) #loop continuously for menu and background music
        else:
            pygame.mixer.music.play() #play once in every other case (losing/winning)
    except Exception as e:
        print(f"could not load {music_type} music: {e}")

#function to display text on the screen
def display_text(surface, text, pos, font, color):
    collection = [word.split(' ') for word in text.splitlines()] #split text into lines and words
    space = font.size(' ')[0] #calculate width of a space character
    x, y = pos #initial x and y coordinates for text
    for lines in collection:
        for words in lines:
            word_surface = font.render(words, True, color) #render the word with the specified font and color
            word_width, word_height = word_surface.get_size() #get size of the rendered word
            if x + word_width >= 1000:
                x = pos[0]
                y += word_height
            surface.blit(word_surface, (x, y))
            x += word_width + space #move x to the right for the next word, including space
        x = pos[0] #reset x after finishing a line
        y += word_height - 1 #move y down for the next line

#initialize main game loop variables
running = True #main game loop
random_key_triggered = False #checks if random key event is active
random_key = None #variable to store the randomly selected key for the event
countdown_start_time = 0 #variable to store when the countdown started (in milliseconds)
random_event_decision = None #no random key press event initially
random_key_chance = 20 #percentage chance that the random key-press event occurs (20% when the game starts)
random_key_duration = 3 #seconds the player has to press the random key (default is 3 seconds)
random_event_handled = False #marks that the random event key press was handled
random_event_consumed_time = 0 #timestamp for when the random event key was consumed

#function to trigger a random key event in rooms that are not the menu or the endings
def trigger_random_key_event():
    global random_key_triggered, random_key, countdown_start_time, random_event_decision, random_key_chance #declare globals for modification elsewhere
    if where not in endings and where != "menu" and random_event_decision is None:
        if random.random() < (random_key_chance / 100.0):
            random_key_triggered = True
            countdown_start_time = pygame.time.get_ticks()
            random_key = random.choice("abcdefghijklmnopqrstuvwxyz")
            random_event_decision = True
            print(f"Press the key: {random_key.upper()} (Chance: {random_key_chance}%, Duration: {random_key_duration}s)")
        else:
            random_event_decision = False #if event not triggered, mark decision as false

#function to reset the random key event state after completion or failure
def reset_random_key_event():
    global random_key_triggered, countdown_start_time, random_key
    random_key_triggered = False
    countdown_start_time = 0
    random_key = None #clear the random key so a new one can be selected next time

ending_music_played = False #flag to check if ending music already played

#function to restart the game, used initially and when player restarts after an ending
#everything resets to default when the player is in the menu (so menu images is loaded, random key press event is reset, ending music stops playing, etc.)
def reset_game():
    global where, random_event_decision, ending_music_played, random_key_chance, random_key_duration
    where = "menu"
    random_event_decision = None
    loc(where)
    random_key_chance = 20
    random_key_duration = 3
    ending_music_played = False
    play_music("menu")

#start the game by calling reset_game() function
reset_game()

#main game loop
while running:
    #event handling loop
    for event in pygame.event.get():
        if event.type == pygame.QUIT: #exits the game loop if python is quit
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE: #esc quits the game window which therefore stops the game loop
                running = False
            elif where in endings and event.key == pygame.K_r: #click sound for when player restarts game with 'r'
                if click_sound:
                    click_sound.play()
                reset_game()
            elif event.key == pygame.K_TAB: #if 'tab' key is pressed to change random key chance
                random_key_chance += 20
                if random_key_chance > 100:
                    random_key_chance = 0
                print(f"Random key chance set to {random_key_chance}%")
                if click_sound:
                    click_sound.play()
            elif event.key == pygame.K_BACKQUOTE: #if '`' key is pressed to change random key duration
                random_key_duration += 1
                if random_key_duration > 5:
                    random_key_duration = 1
                print(f"Random key duration set to {random_key_duration}s")
                if click_sound:
                    click_sound.play()
            elif random_key_triggered: #if random key event is active
                if event.key == getattr(pygame, f'K_{random_key}'): #if the pressed key matches the random key
                    if click_sound:
                        click_sound.play() 
                    reset_random_key_event()
                    random_event_handled = True #random key press was handled
                    random_event_consumed_time = pygame.time.get_ticks() #record time when the key was pressed
                    if random_key == 'a': #if the random key is 'a', mark it as pressed for the movement between rooms situation
                        is_a = True
                    elif random_key == 'b': #if the random key is 'b', mark it as pressed for movement movement between rooms situation
                        is_b = True
    keys = pygame.key.get_pressed() #get state of all keyboard keys

    if where not in endings and not random_key_triggered:
        trigger_random_key_event() #attempt to trigger a random key event

    #if a random key event is active, check if time has run out
    if random_key_triggered:
        elapsed_time = (pygame.time.get_ticks() - countdown_start_time) / 1000 #calculate elapsed time in seconds
        remaining_time = max(0, random_key_duration - elapsed_time) #calculate remaining time
        if remaining_time <= 0:
            where = "caught"
            loc(where) #load image for caught ending
            reset_random_key_event() #reset random key event state
            random_event_decision = None #reset event decision for new room

    #if in an ending room and ending music hasn't been played, load appropriate music
    if where in endings and not ending_music_played:
        if where in win_endings: #if player escapes (wins)
            play_music("win")
        else: #if it is a losing ending
            play_music("lose")
        ending_music_played = True #mark that ending music has been played as to not overlap

    #set the caption text based on the current room
    if where not in endings:
        if where == "basement":
            current_caption = ("You wake up to find yourself in a basement, what do you do? \n\n"
                               " a. Go up the basement stairs \n b. Hide in a closet")
        elif where == "basement_stairs":
            current_caption = ("As you arrive at the top of the stairs, you see a kitchen to the left and a hallway to the right, where do you go? \n\n"
                               " a. Hallway \n b. Kitchen")
        elif where == "hallway":
            current_caption = ("As you're walking down the hallway, you can either go to the bathroom or continue to the living room: \n\n"
                               " a. Living room \n b. Bathroom")
        elif where == "kitchen":
            current_caption = ("You're now in the kitchen. From here, you can head into the pantry or go to the dining room: \n\n"
                               " a. Pantry \n b. Dining room")
        elif where == "bathroom":
            current_caption = ("You're in the bathroom. Do you return to the hallway or risk climbing out the window? \n\n"
                               " a. Return to the hallway \n b. Climb out the window")
        elif where == "living_room":
            current_caption = ("You're in the living room. You can try escaping through the front door or go to the office: \n\n"
                               " a. Try front door \n b. Go to the office")
        elif where == "garage":
            current_caption = ("You're in the garage. You can attempt to hotwire the car or go to the storage room: \n\n"
                               " a. Hotwire car \n b. Go to storage room")
        elif where == "dining_room":
            current_caption = ("You're in the dining room. You can either return to the kitchern or go up the stairs to the second floor: \n\n"
                               " a. Return to the kitchen \n b. Go upstairs")
        elif where == "upstairs":
            current_caption = ("As you head up the stairs, you see an open bedroom door, and a ladder leading to the attic. Where do you go? \n\n"
                               " a. Bedroom \n b. Attic")
        elif where == "bedroom":
            current_caption = ("After entering the bedroom, you see that you can open the window. Do you take the risk to climb out? \n\n"
                               " a. Climb out the window \n b. Go back to the stairs")
        elif where == "office":
            current_caption = ("As you enter the office, you notice the laundry room. You can either turn back or proceed forward: \n\n"
                               " a. Go back into the living room \n b. Go to laundry room")
        elif where == "laundry_room":
            current_caption = ("You're in the laundry room. From here, you can go to the back door or into the garage: \n\n"
                               " a. Back door \n b. Garage")
        elif where == "back_door":
            current_caption = ("You're at the back door. You can go outside to the garden or go back into the laundry room: \n\n"
                               " a. Garden \n b. Laundry room")
        elif where == "garden":
            current_caption = ("You step into the freakiest garden you have ever seen. Do you go to the front gate or garden shed?: \n\n"
                               " a. Front gate \n b. Shed")
        elif where == "menu":
            current_caption = ("") #no caption for menu
    else:
        current_caption = endings[where] #if in an ending, display the corresponding ending message in the ending dictionary

    current_time = pygame.time.get_ticks() #get current time
    if not random_key_triggered and (current_time - random_event_consumed_time > 200): #only allow movement if not in random event or cooldown passed (prevents unwanted presses when random key event selects either 'a' or 'b')
        previous_room = where #store the current room before moving (we need this to know if we're leaving the menu later, in order to play the correct music)
        if keys[pygame.K_a] and where in a and not is_a: #if 'a' is pressed and valid in current room and not already pressed
            where = a[where]
            loc(where)
            reset_random_key_event()
            random_event_decision = None
            is_a = True #mark 'a' as pressed
            if click_sound:
                click_sound.play()
            if previous_room == "menu" and where != "menu": #if leaving menu, switch music
                play_music("background")
        if not keys[pygame.K_a]:
            is_a = False #reset a key flag if key not pressed
        if keys[pygame.K_b] and where in b and not is_b: #if 'b' is pressed and valid in current room and not already pressed
            previous_room = where #store the current room before moving (we need this to know if we're leaving the menu later, in order to play the correct music)
            where = b[where]
            loc(where)
            reset_random_key_event()
            random_event_decision = None
            is_b = True #mark 'b' as pressed 
            if click_sound:
                click_sound.play()
            if previous_room == "menu" and where != "menu": #if leaving menu, switch music to background music (menu can only lead to the game starting)
                play_music("background")
        if not keys[pygame.K_b]:
            is_b = False #reset to false if not pressed

    #reset random_event_handled if neither 'a' nor 'b' are pressed
    if not keys[pygame.K_a] and not keys[pygame.K_b]:
        random_event_handled = False

    #display the current room image on the screen at specified position
    screen.blit(current_image, (0, 0))
    if where != "menu": #draw black rectangle for text background if not in menu
        pygame.draw.rect(screen, black, (0, 580, 1000, 120))

    #display caption text with specified position, font, and color
    display_text(screen, current_caption, (20, 590), font, white)

    #if random key event is active, display the countdown and prompt
    if random_key_triggered:
        elapsed_time = (pygame.time.get_ticks() - countdown_start_time) / 1000 #calculate elapsed time in seconds
        remaining_time = max(0, (random_key_duration - elapsed_time) + 1) #calculate remaining time (+1 to more accurately display amount of time left [e.g. 3, 2, 1, lose, instead of 2, 1, 0, lose])
        countdown_text = f"You have been caught! Press key: {random_key.upper()} to escape! | Time: {int(remaining_time)}s" 
        display_text(screen, countdown_text, (20, 530), font, white) #display countdown text on screen

    pygame.display.update() #update the display repeatedly with all drawn elements

pygame.quit() #quit pygame modules
sys.exit() #exit the system
