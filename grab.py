#!/usr/bin/env python3

#-------------------------------------------------------------------------#
#written by Peter Stenger (@reteps) with support from Ryan Densmore (@rydens)
#If you use this code, please cite us / this page.
#-------------------------------------------------------------------------#
import sys, time
from bs4 import BeautifulSoup
from selenium import webdriver
#-------------------------------------------------------------------------#
def get_page(id, email, passwd):
    speed = 0
    while True:
        driver = webdriver.Chrome()
        driver.get('https://create.kahoot.it/#quiz/' + id);
        time.sleep(0.25 + speed)
        try:
            box = driver.find_element_by_css_selector('#username-input-field__input')
            box.send_keys(email)
            box2 = driver.find_element_by_css_selector('#password-input-field__input')
            box2.send_keys(passwd)
            driver.find_element_by_css_selector('.button--cta-play').click()
            time.sleep(2 + speed)
            #moment of truth#
            driver.find_element_by_css_selector('#quiz-detail-header') #check success
            elem = driver.find_element_by_xpath("//*")
            stuff = elem.get_attribute("innerHTML")
            break
        except Exception:
            driver.quit()
            speed += 2.5
            print('Retrying connection with speed set to {}'.format(speed))
    try:
        driver.find_element_by_css_selector(".create-kahoot-type-selector")
        print("Private kahoot.")
        exit()
    except Exception:
        driver.quit()
        
        
    return stuff
#-------------------------------------------------------------------------#
def start_bot(id,name,answers,speed=0):
    driver = webdriver.Chrome()
    while True:
        try:
            driver.get("https://kahoot.it/#/")
            time.sleep(0.25 + speed)
            box = driver.find_element_by_css_selector('#inputSession')
            box.send_keys(id)
            driver.find_element_by_css_selector('.btn-greyscale').click()
            time.sleep(1.25 + speed)
            box = driver.find_element_by_css_selector('#username')
            box.send_keys(name)
            driver.find_element_by_css_selector('.btn-greyscale').click()
            break
        except Exception:
            speed += 2.5
            print('Retrying bot login with delay set to {} seconds'.format(speed))
    print('connected successfully')
    print("press [1] to start the bot\npress [2] to choose a new name\npress [3] to start on a specific question\n")
    response = input(" > ")
    if response == '3': 
        question = int(input('starting question > ')) - 1
        bot_answer(driver,answers[question:])
    elif response == '2':
        driver.quit()
        name = input('New name > ')
        print('Retrying with name set to {} and delay set to {}'.format(name,speed))
        start_bot(id,name,answers,speed=speed)
    else:
        bot_answer(driver,answers)
#-------------------------------------------------------------------------#
def bot_answer(driver,answers):
    print('bot started.')
    lookuptable = {"0":".answerA", "1":".answerB","2":".answerC","3":".answerD"}
    lookup = {"0":"red","1":"blue","2":"yellow","3":"green"}
    nextQ = False
    answered = False
    for i in range(len(answers)):
        print("Question " ,i+1)
        while True:
            try:
                driver.find_element_by_css_selector(".answer-screen")
                if not answered:
                    try:
                        driver.find_element_by_css_selector(lookuptable[answers[i]]).click()
                        print("Chose " + lookup[answers[i]])
                    except Exception as e:
                        print('Question was skipped before bot could answer.')
                        time.sleep(0.5) #prevent doubles
                        answered, nextQ = False, False
                        break #next question
                        
                    answered = True
            except Exception as e:
                nextQ = True
                if nextQ and answered:
                    nextQ ,answered = False, False
                    break
            time.sleep(0.01)
    driver.quit()
#-------------------------------------------------------------------------#
def getQuestions(soup):
    questions = []
    stuff = soup.findAll("td", {"class":'question-title'})
    for qt in stuff:
        question = qt.find("div").get_text()
        questions.append(question.strip()[:-45])
    return questions
#-------------------------------------------------------------------------#
def getAnswers(soup,hascolor=True):

    questions = soup.findAll("ul", {"class":'answers-list'})
    colors = []
    answers = []
    for i, question in enumerate(questions):
        possibleanswers = question.findAll("li", {"class":"answers-list__item"})
        for possibleanswer in possibleanswers:
            if possibleanswer.find("div",{"class":"answer-label__correct-icon"}) != None:
                num = dict(possibleanswer.find("div",{"class":'answer-label'}).attrs)["class"][1][-1]
                if hascolor:
                    lookuptable = {"0":"red", "1":"blue","2":"yellow","3":"green"}
                    color = lookuptable[num]
                    answers.append(possibleanswer.get_text().strip())
                    colors.append(color)
                else:
                    colors.append(num)
                break
                #only need 1 answer, so break

    return colors, answers
#-------------------------------------------------------------------------#
def printAnswers(url,email,passwd,co,co2,co3):
    html = get_page(url,email,passwd)
    soup = BeautifulSoup(html, 'html.parser')
    questions = getQuestions(soup)
    colors, answers = getAnswers(soup)
    for i in range(len(questions)):
        print('{}{:100s}{}  |  {}{:6s}{} |  {}{:3d}{}  |'.format(co,questions[i],co2,co,colors[i],co2,co,i+1,co2))
        print('{}{:100s}{}  |         |       |'.format(co3,answers[i],co2))
#-------------------------------------------------------------------------#
def scrape(url,email,passwd):
    html = get_page(url,email,passwd)
    soup = BeautifulSoup(html, 'html.parser')
    answers, asd = getAnswers(soup,hascolor=False)
    return answers
#-------------------------------------------------------------------------#
