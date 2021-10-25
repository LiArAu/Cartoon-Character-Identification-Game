from tkinter import ttk, Tk, PhotoImage, RIDGE, END
import random
from PIL import ImageTk, Image
import sqlite3

class DbOperations:
    def __init__(self):
        self.conn = sqlite3.connect('cartoon.db')
        self.curs = self.conn.cursor()

    def load_all_questions(self):
        self.curs.execute('SELECT * FROM questions')
        self.questions = self.curs.fetchall()
        return self.questions

    def insert_question(self, question, path, answer):
        try:
            self.curs.execute(f'INSERT INTO questions (question_content, clue_path, answer) VALUES("{question}","{path}","{answer}")')
            self.conn.commit()
        except Exception as e:
            print(e)

    def load_all_scores(self):
        try:
            self.curs.execute(f'SELECT * from candy_record')
            self.scores = self.curs.fetchall()
            return self.scores
        except Exception as e:
            print(e)

    def create_or_update_score(self, player, score):
        try:
            self.curs.execute(f'INSERT INTO candy_record (username,candy) VALUES ("{player}",{score})')
        except Exception as e:
            self.curs.execute(f'SELECT candy from candy_record WHERE username="{player}"')
            # fetchone, just fetch the first entry.
            self.player_score = self.curs.fetchone()
            if self.player_score[0] < score:
                self.curs.execute(f'UPDATE candy_record SET candy=? WHERE username=?', [score, player])
        self.conn.commit()

    def highest_score(self):
        try:
            self.curs.execute('SELECT MAX(candy),username FROM candy_record')
            print(self.curs.fetchall())
        except Exception as e:
            print(e)


class Character:
    def __init__(self,master):
        self.master = master
        self.master.geometry('800x600+250+10')
        self.master.title('Cartoon Character Identification Game')
        self.prev_color = 'black'

        self.db = DbOperations()
        self.questions = {}
        for q in self.db.load_all_questions():
            self.questions[q[1]] = (q[2],q[3])

        self.header = ttk.Frame(self.master)
        self.header.pack()
        self.logo = PhotoImage(file = 'images/mylogo.png').subsample(3,3)
        ttk.Label(self.header,image = self.logo).grid(row=0,column=0)
        ttk.Label(self.header,text = 'Let\'s play a game!').grid(row=0,column=1)
        # learning:
        # let's play a game row make column 1 very long, we use sticky = 'ne' to make next row of column 1 closer to column 2.
        ttk.Button(self.header, text = 'Start to Play', command = self.home).grid(row = 1,column = 1,sticky = 'ne')
        ttk.Button(self.header, text = 'About the Game', command = self.info).grid(row = 1,column = 2)
        ttk.Button(self.header, text = 'Settings', command = self.setting).grid(row = 1,column = 3)
        ttk.Button(self.header, text = 'Candy Rank', command = self.rank).grid(row = 1,column = 4)

    # Frame Body should change when you choose home/info/settings/rank
    def create_frame_body(self,frame_style = None):
        try:
            self.frame_body.forget()
        except:
            pass
        self.frame_body = ttk.Frame(self.master,style = frame_style)
        self.frame_body.pack()
        self.frame_body.config(relief=RIDGE,padding = (50,15))

    # ----------------------------- All functions in the home page -----------------------------
    def home(self):
        self.create_frame_body()
        self.candy = 0
        ttk.Button(self.frame_body, text = 'Start', command = self.get_username).grid(row=0,column=0)

    def get_username(self):
        self.create_frame_body()
        ttk.Label(self.frame_body,text = 'Enter your name').grid(row=0,column = 0)
        self.username_obj = ttk.Entry(self.frame_body)
        self.username_obj.grid(row=1,column=0)
        ttk.Button(self.frame_body,text = 'Enter the game', command = self.play_action).grid(row=2,column=0)

    def play_action(self):
        self.create_frame_body()
        if self.questions:
            question = random.choice(list(self.questions.keys()))
            ttk.Label(self.frame_body, text = question).grid(row=0,column=0,columnspan=2)
            self.user_answer_obj = ttk.Entry(self.frame_body)
            self.user_answer_obj.grid(row=2,column=0,columnspan=2)
            self.clue_button = ttk.Button(self.frame_body,text = 'Clue', command = lambda: self.clue_action(question))
            self.clue_button.grid(row=3,column=0)
            ttk.Button(self.frame_body,text = 'Next', command = lambda: self.next_action(question)).grid(row=3,column=1)
        else:
            self.candy = max(0,self.candy)
            self.username = self.username_obj.get()
            ttk.Label(self.frame_body, text = f"Congrats, {self.username}. You have completed all of the questions.").grid(row=0,column=0)
            ttk.Label(self.frame_body, text = f"You have {self.candy} candies now!").grid(row=1,column=0)
            self.db.create_or_update_score(self.username,self.candy)
            self.db.load_all_scores()
            ttk.Button(self.frame_body, text = 'Play Again', command = self.home).grid(row=2,column=0)

    def clue_action(self,question):
        self.candy -= 5
        image = Image.open(self.questions[question][0])
        image = image.resize((80,80))
        self.image = ImageTk.PhotoImage(image)
        self.clue_button['state'] = 'disabled'
        ttk.Label(self.frame_body, image = self.image).grid(row=1,column=0,columnspan=2)

    def next_action(self,question):
        self.user_answer = self.user_answer_obj.get()
        self.user_answer_obj.delete(0,END)
        if self.user_answer.strip().lower() == self.questions[question][1]:
            self.candy += 10
        self.questions.pop(question)
        self.play_action()
    # ----------------------------- End All functions in the home page -----------------------------

    def info(self):
        self.create_frame_body()
        ttk.Label(self.frame_body,text = 'This is a game designed for kids and also adults with childlike innocence.').pack()
        ttk.Label(self.frame_body,text = 'Hope this game could remind you of the cartoon characters that have brought you so much laughter and life lessons.').pack()
        ttk.Label(self.frame_body,text = 'In this game, the more characters you know, the more candies you will get.').pack()
        ttk.Label(self.frame_body,text = '-------------------------------').pack()
        ttk.Label(self.frame_body,text = 'If you want to be a contributor, ').pack()
        ttk.Label(self.frame_body,text ='please click \'Add New Question\' button below. Thanks!').pack()
        ttk.Button(self.frame_body, text = 'Add New Question',command=self.add_question).pack()

    def add_question(self):
        self.create_frame_body()
        ttk.Label(self.frame_body,text = 'Enter the description of your new character. (No more than 25 words)').grid(row=0,column=0)
        self.content = ttk.Entry(self.frame_body)
        self.content.grid(row=1,column=0)

        ttk.Label(self.frame_body,text = 'Enter the path to the image for clue. (Eg. images/tomandjerry_clue.png)').grid(row=2,column=0)
        self.clue_path= ttk.Entry(self.frame_body)
        self.clue_path.grid(row=3,column=0)

        ttk.Label(self.frame_body,text = 'Enter your character\'s name. Eg. Tom and Jerry)').grid(row=4,column=0)
        self.newch = ttk.Entry(self.frame_body)
        self.newch.grid(row=5,column=0)

        ttk.Button(self.frame_body,text = 'Confirm and Add',command = self.save_question).grid(row=6,column=0)

    def save_question(self):
        self.db.insert_question(self.content.get(), self.clue_path.get(),self.newch.get().strip().lower())
        self.info()

    def setting(self):
        self.create_frame_body()
        ttk.Label(self.frame_body,text = 'Settings').grid(row=0,column=0)
        ttk.Button(self.frame_body,text = 'Change color',command = self.redefine).grid(row=1,column=0)

    def redefine(self):
        self.s = ttk.Style()
        self.s.configure('TFrame',background = self.prev_color)
        self.create_frame_body()
        self.color = ttk.Entry(self.frame_body)
        self.color.grid(row=2,column=0)
        ttk.Button(self.frame_body, text = 'Try it on', command = self.try_color).grid(row=3,column=0)

    def try_color(self):
        self.s.configure('TFrame',background = self.color.get())
        self.create_frame_body(frame_style='TFrame')
        ttk.Button(self.frame_body, text = 'Confirm', command = self.confirm_color).grid(row=0,column=0)
        ttk.Button(self.frame_body, text = 'Revert the change', command = self.redefine).grid(row=1,column=0)

    def confirm_color(self):
        self.setting()
        self.prev_color = self.color.get()

    def rank(self):
        self.create_frame_body()
        scores = self.db.load_all_scores()
        if not scores:
            ttk.Label(self.frame_body,text = 'No players yet. Be the first one!').grid(row=0,column=0)
            return
        ttk.Label(self.frame_body,text = 'Name').grid(row=0,column=0)
        ttk.Label(self.frame_body,text = 'Candy').grid(row=0,column=1)
        scores = sorted(scores,key = lambda score: score[1],reverse = True)
        for i,score in enumerate(scores):
            ttk.Label(self.frame_body,text = score[0]).grid(row=1+i,column=0)
            ttk.Label(self.frame_body,text = score[1]).grid(row=1+i,column=1)

root = Tk()
Character(root)
root.mainloop()
