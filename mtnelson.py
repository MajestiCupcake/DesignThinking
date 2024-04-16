try:
    import enchant
    print("pyenchant is installed.")
except ImportError:
    print("pyenchant is not installed.")

### places marked with ? needs attention ###
#Import modules
from psychopy import core, visual, event, gui, monitors, event, sound
from datetime import datetime
#import module for randomization
import random
import pandas as pd
#creates new directory
import os
#scaling images
import text as t #script with text instructions
import enchant

# Initialize the Australian English dictionary
english_dict = enchant.Dict("en_AU")

#Set Variables
#These are not set in stone! Depend on iMotions + COBE ?
SAVE_FOLDER = "nelson_data"
# make sure that there is a logfile directory and otherwise make one
if not os.path.exists(SAVE_FOLDER):
    os.makedirs(SAVE_FOLDER)

#generate ID options
op1 = random.randint(1, 10)
op2 = random.randint(11,20)
op3 = random.randint(100,200)
op4 = random.randint(201, 400)
op5 = random.randint(1000, 5000)

# define dialogue box (important that this happens before you define window)
box = gui.Dlg(title = "Mt Nelson Master Plan")
box.addField("Participant ID: ", choices=[op1,op2,op3,op4,op5]) 
box.addField("Age: ")
box.addField("Gender: ", choices=["Female", "Male", "Other" ])
box.addField("Relation:",choices=["Mt Nelson resident","Hobart resident","Another Aussie","Tourist (overseas)","Other"])
box.show()
if box.OK: # To retrieve data from popup window
    ID = box.data[0]
    AGE = box.data[1]
    GENDER = box.data[2]
    GROUP = box.data[3]
elif box.Cancel: # To cancel the experiment if popup is closed
    core.quit()

# PREPARE LOG FILES
# Get the current date
current_date = datetime.today().date()
now = datetime.now()
utc_time = now.strftime("%H_%M")

# prepare pandas data frame for recorded data
list_of_columns = ['time','id','age','gender','group','task','trial','answer','dic','comment']
logfile = pd.DataFrame(columns=list_of_columns)
logfile_name = "logfile_{}_{}_{}.csv".format(ID, current_date,utc_time)

win = visual.Window(fullscr = True, color = "white")

#initial global variables
task=None
response=None
i=None 
dic=None

#structure
# consent
# task 1 what do you know about the master plan
# task 2: get familiar with inputting words
# task 3: get familiar with inputting stories
# random order
# A: write word you associate with mt nelson area
# B: write words you associate with engaging nature spaces
# C: write a story you remember from the mt nelson area
# D: write a dream you have for the mt nelson area
# E: further comments
# task 4: thank you for participating, contact
'time','id','age','gender','group','task','trial','answer'
def save_data(task,i,response,dic,com):
    global logfile, logfile_name
    logfile = logfile.append({
        'time': datetime.now().strftime("%H_%M_%S"),
        'id':ID,
        'age':AGE,
        'gender': GENDER,
        'group':GROUP,
        'task':task,
        'trial':i,
        'answer': response,
        'dic':dic,
        'comment':com
        }, ignore_index = True)
    path_to_log = os.path.join(SAVE_FOLDER, logfile_name)
    logfile.to_csv(path_to_log)

def save_and_escape(task,i):
    save_data(task,None,'escape',None,None)
    message = visual.TextStim(win, text = t.escape, color="black")
    message.draw()
    win.flip()
    core.wait(2)
    core.quit()
    
# function for getting and evaluyating a key response
def check_words(response):
    if english_dict.check(response)==True:
        dic = 1
        response=response
    else:
        suggest = english_dict.suggest(response)[0:9] 
        choice = "\n\n press the number that suits with correct spelling \n press the letter 'O' for 'Other spelling'"
        suggestions = ['{}: {}'.format(index + 1, item) for index, item in enumerate(suggest)]
        tet1= "Did you mean?: \n {}".format(", ".join(suggestions))
        text= tet1 + choice
        
        dic, response = check_msg(text, suggest)
        
    return dic, response
    

### function for showing text and waiting for key press
def msg(txt):
    win.flip()
    message = visual.TextStim(win, text = txt, wrapWidth= 50,color="black")
    message.draw()
    win.flip()
    key = event.waitKeys()
    if 'escape' in key:
        save_and_escape(task, i)

def check_msg(txt, suggest):
    global response, dic
    win.flip()
    message = visual.TextStim(win, text = txt,color="black")
    message.draw()
    win.flip()
    key = event.waitKeys(keyList=['1','2','3','4','5','6','7','8','9','o','escape'])
    if 'escape' in key:
        save_and_escape(task, i)
    if 'O' in key:
        save_and_escape(task,i,response,dic,'OtherSpelling')
        dic=0
        response = response
    else:
        print(key)
        index = int(key[0]) - 1
        response = suggest[index]
        dic=1
    return dic, response

def train_word(where):
    global task
    #setup
    tas="WordsOf"
    task=tas+where
    # Define the prompts
    prompt = "Write a word you associate with " + where
    # Initialize variables
    current_text = ""
    i = 0
    print(f"current task is {task} trial {i}")
    end_trial=False
    prompt_text = visual.TextStim(win, text=prompt, color="black", pos=[0,0.2])
    input_text = visual.TextStim(win, text=current_text, color="grey", pos=[0, -0.2])
    
    #instructions
    msg(t.t1)
    msg(t.t2)
    msg(t.t3)
    msg(t.t4)
    msg(t.t5)
    
    #trials
    while not end_trial:
        prompt_text.text = prompt
        input_text.text = current_text

        prompt_text.draw()
        input_text.draw()
        win.flip()

        keys = event.getKeys()
        if keys:
            if 'backspace' in keys:
                current_text = current_text[:-1]
            elif 'return' in keys:
                current_text = ""
                i += 1
            elif len(keys[0]) == 1:  # Check if a single character key was pressed
                current_text += keys[0]
            elif 'escape' in keys:
                save_and_escape(task,i)
            
        if i==10:
            msg(t.f1)
            end_trial=True  

def test_word(where):
    global task, response, i, dic

    #setup
    tas="WordsOf"
    task=tas+where
    
    prompt = "Write a word you associate with "+where
    current_text = ""
    dic_sum = 0
    i = 0
    print(f"current task is {task} trial {i}")
    end_trial=False
    prompt_text = visual.TextStim(win, text=prompt, color="black", pos=[0, 0.2])
    input_text = visual.TextStim(win, text=current_text, color="grey", pos=[0, -0.2])
    
    #trials
    while not end_trial:
        prompt_text.text = prompt
        input_text.text = current_text

        prompt_text.draw()
        input_text.draw()
        win.flip()

        keys = event.getKeys()
        if keys:
            if 'backspace' in keys:
                current_text = current_text[:-1]
            elif 'return' in keys and current_text!="":
                dic, response =check_words(current_text)
                dic_sum = dic_sum + dic
                save_data(task,i,current_text,dic,None)
                current_text = ""
                i += 1
            elif len(keys[0]) == 1:  # Check if a single character key was pressed
                current_text += keys[0]
            elif 'escape' in keys:
                save_and_escape(task,i)

            
        if i>10: #and dic_sum==10:
            end_trial=True
        if i % 20 == 19:
            msg(t.break_text)

def experiment(ID):
    msg(t.i1)
    msg(t.i2)
    msg(t.i3)
    train_word("CBD (central business district)")
    #instructions
    msg(t.e1)
    msg(t.e2)
    msg(t.e3)
    msg(t.e4)
    if ID % 2:
        test_word("Mt Nelson Oval")
        msg(t.shift_text)
        test_word("engaging outdoor area")
    else:
        test_word("engaging outdoor area")
        msg(t.shift_text)
        test_word("Mt Nelson Oval")

    #experiment is done, save and quit
    message = visual.TextStim(win, text = t.goodbye, color="black")
    message.draw()
    win.flip()
    core.wait(2)
    core.quit()
    
#### run experiment ####
#### 1 means fullblown experiment = 100%, want to only do 50% input 0.5, smallest number is 0.25 = 1 training trial and 20 test trials
experiment(ID)