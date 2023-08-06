#Packages used to build this project:
import pyttsx3
import datetime
import speech_recognition as sr 
import pyaudio
import webbrowser
import os
import smtplib
import wifi
import channels

#Voice of the assistant used
engine = pyttsx3.init('sapi5')
voices = engine.getProperty('voices')
engine.setProperty('voice',voices[0].id)
#engine.setProperty('voice'voices[1].id)


#Audio function of the assistant
def speak(audio):
    engine.say(audio)
    engine.runAndWait()

#Start point of the assistant
def assistantStart():
    hour = int(datetime.datetime.now().hour)
    if (hour>=5 and hour<12) :
        speak('Good Morning, Boss')
    elif (hour>=12 and hour<18) :
        speak('Good Afternoon, Boss')
    else:
        speak('Good Evening, Boss')
    
    speak('I am Jarvis, How may I help you?')

#It takes microphone input from the user and returns string output
def takeCommand():
    r= sr.Recognizer()
    with sr.Microphone() as source:
        print('Listening...')
        r.pause_threshold = 1
        audio = r.listen(source)
        
    try:
        print('Recognizing...')
        query = r.recognize.google(audio,language='en-in')
        print(f"Boss: {query}\n")
    
    except Exception as e:
        #print(e)
        print("Boss, can you say that again please...")
        speak("Boss, can you say that again please...")
        return 'None'
    
    return query

#Function to send email
def sendEmail(to,content):
    server = smtplib.SMTP('smtp.gmail.com',587)
    server.ehlo()
    server.starttls()
    server.login("iamayushpatel19@gmail.com","Ayushp19@")
    server.sendmail("iamayushpatel19@gmail.com",to,content)
    server.close()

#Function to open a text file or write in the text file
def notepad():
    os.system("Notepad")
    speak("Do you want to open an existing file or a new file?Say either existing file or new file.")
    listen = takeCommand().lower()
    if listen == "existing file":
        speak("Please say the file name")
        cmd = takeCommand()
        open(cmd,'w')
        speak("Do you want to write something?Say yes or no")
        cmd1 = takeCommand().lower
        if cmd1 == 'yes':
            speak("what do you want to write?")
            while(cmd1 == True):
                cmd2 = takeCommand()
                for cmd2 in cm2:  
                    file.write(cmd2)  
                    file.write('\n')
                speak("Do you want write something more?Say yes or no")
        else:
            speak("Okay.")
    else:
        speak("What file name do you wish to give?")
        cmd = takecommand().lower()
        open(cmd,'w')
        speak("Do you want to write something?Say yes or no")
        cmd1 = takeCommand().lower
        if cmd1 == 'yes':
            speak("what do you want to write?")
            while(cmd1 == True):
                cmd2 = takeCommand()
                for cmd2 in cm2:  
                    file.write(cmd2)  
                    file.write('\n')
                speak("Do you want write something more?Say yes or no")
        else:
            speak("Okay.")

def search(cmd1):
    webbrowser.open("www.youtube.com/"+cmd1)

#main function where the program starts
if __name__ == '__main__':
    assistantStart()
    while True:
        query = takeCommand().lower()

        #logic for executing tasks based on query
        #Open Wikipedia and get information about something you want to.
        if 'wikipedia' in query:
            speak('Searching Wikipedia...')
            query = query.replace("wikipedia","")
            results = wikipedia.summary(query, sentences = 5)
            speak("According to Wikipedia")
            speak(results)

        #Open Youtube
        elif "open youtube" in query:
            chrome = "C:\\Users\\ayush\\AppData\\Local\\Google\\Chrome\\Application\\chrome.exe"
            os.startfile(chrome)
            webbrowser.open("www.youtube.com")
            speak("Do you want to open any specific channel?Say yes or no.")
            cmd = takeCommand().lower()
            if cmd == "yes":
                speak("Which channel do you want to open?")
                cmd1 = takeCommand().lower()
                search(cmd1)
        
        #Open Google
        elif "open google" in query:
            webbrowser.open("google.com")
        
        #Open Coursera
        elif "open coursera" in query:
            webbrowser.open("coursera.org")

        #Open Spotify
        elif "open spotify" in query:
            spotify = "C:\\Users\\ayush\AppData\\Roaming\\Spotify\\Spotify.exe"
            os.startfile(spotify)
            #If you want to play songs downloaded in the pc
            '''music_dir = "Write dir name here"
            songs = os.listdir(music_dir)
            print(songs)
            os.startfile(os.path.join(music_dir, songs[0]))'''
        
        #Ask Time
        elif " time" in query:
            strTime = datetiem.datetime.now().strftime("%H:%M")
            if (strTime>=0 and strTime<12):
                t = 'Am'
            else:
                t = 'Pm'
            speak(f"Its {strTime}{t}")
        
        #Open VS Code
        elif "vscode" in query:
            vscode_path = "D:\\Microsoft VS Code\\Code.exe"
            os.startfile(vscode_path)
        
        #Send Email
        elif "send email to me" in query:
            try:
                speak("What should I write?")
                content = takeCommand()
                to = "iamayushpatel19@gmail.com"
                sendEmail(to,content)
                speak("Email sent.")
            except Exception as e:
                #print(e)
                speak("Due to some issue I am not able to complete the command.")

        #ShutDown PC
        elif "shutdown" in query:
            os.system("shutdown /s /t 1")
        
        #Restart PC
        elif "restart" in query:
            os.system("shutdown /r /t 1")
        
        #Logout PC
        elif "logout" in query:
            os.system("shutdown -l")
        
        # elif "laptop password" in query:
        #     if os.system() == 'logout':
        #         os.system("1902")

        #Open MS Word  
        elif "word" in query:
            word = "C:\\Program Files\\Microsoft Office\\root\\Office16\\WINWORD.EXE"
            os.startfile(word)

        #Open MS Power Point
        elif "power point" in query:
            power_point = "C:\\Program Files\\Microsoft Office\\root\\Office16\\POWERPNT.EXE"
            os.startfile(power_point)   
        
        #Open MS Excel
        elif "excel" in query:
            excel = "C:\\Program Files\\Microsoft Office\\root\\Office16\\EXCEL.EXE"
            os.startfile(excel)

        #open Chrome
        elif "chrome" in query:
            chrome = "C:\\Users\\ayush\\AppData\\Local\\Google\\Chrome\\Application\\chrome.exe"
            os.startfile(chrome)
        
        #Open Android Studio
        elif "android studio" in query:
            android_studio = "C:\\Program Files\\Android\\Android Studio\\bin\\studio64.exe"
            os.startfile(android_studio)

        #Open File Explorer
        elif "file" in query:
            file_explorer = "C:\\Program Files\\Android\\Android Studio\\bin\\studio64.exe"
            os.startfile(file_explorer)

        #Connect to wifi
        elif "wifi" in query:
            print("Wifi SSID:")
            ssid = takeCommand()
            print(ssid)
            print("Passwword:")
            password = takeCommand()
            print(password)
            wifi(ssid, password)
        
        # elif "bluetooth" in query:
            
        #Open Notepad and read or write using the assistant
        elif "notepad" in query:
            notepad()

        elif "chatgpt" in query:
            webbrowser.open("chat.openai.com/")
        
        #To stop the assistant
        elif "stop" in query:
            main(False)