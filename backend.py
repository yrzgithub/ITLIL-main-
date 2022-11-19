from flask import Flask,render_template,request,redirect,url_for
from face_recognition import *
import cv2
import numpy
from pickle import dump,load
from os.path import join,isfile
from os import getcwd,listdir
from datetime import datetime
from smtplib import SMTP
from email.message import EmailMessage
from random import randint
from math import pow



class Account:
    name = None
    uname = None
    password = None
    number = None
    gmail = None
    address = None
    id = 0

    def __init__(self,name,username,password,number,gmail,address) -> None:
        self.name = name
        self.uname = username
        self.password = password
        self.number = number
        self.gmail = gmail
        self.address = address

    
    def setID(self,id_no):
        self.id = id_no



class Person:
    name = ""
    username = None
    password = None
    id_no = 0
    face_encodings = None
    age = None
    gender = None
    dob = None
    upolad_date = None
    comments = "N/A"
    lost_location = "Unknown"

    def __init__(self,name):
        self.name = name
        self.upolad_date = datetime.strftime(datetime.now(),format="%d %b %Y")

    def setFaceEncodings(self,encodings):
        self.face_encodings = encodings

    def setId(self,no):
        self.id_no = no

    def setComments(self,comments):
        if isValidData(comments):
            self.comments = comments

    def setAge(self,age):
        self.age = age

    def setGender(self,gender):
        self.gender = gender

    def setDOB(self,dob):
        self.dob = dob

    def setLostLocation(self,location):
        if isValidData(location):
            self.lost_location = location

    def html_path(self):
        return join("static","Images",str(self.id_no)+".jpg")

    def getPath(self):
        return join(images_dir,str(self.id_no)+".jpg")






cwd = getcwd()
images_dir = join(cwd,"static","Images")
saved_image_face_data = join(cwd,"data.pkl")
accouts_data = join(cwd,"accounts.pkl")
admin_email = "seenusanjay20102002@gmail.com"
admin_password = "gamlqrreyphdrxgx"  # app password
v_code = -1

app = Flask(__name__)


def get_page(arg):
    return f"<html><head><font size=\"+5\">{arg}</font></head></html>"


def get_tag_value(name):
    return request.form.get(name)


def get_people_list():
    known_people = []
    if isfile(saved_image_face_data):
        with open(saved_image_face_data,"rb") as file:
            known_people = load(file)
            file.close()
    return known_people


def get_accounts():
    contents = []
    if isfile(accouts_data):
        with open(accouts_data,"rb") as file:
            contents = load(file)
        file.close()
    return contents


@app.route('/')
def home():
    return render_template("login.html")


@app.route('/forget_password.html')
def forget_password():
    return render_template("forget_password.html")


@app.route("/create_account.html")
def create_account():
    return render_template("create_account.html")


@app.route("/forget_password.html",methods=["GET","POST"])
def reset_password():
    global change_password_mail
    clicked_button = get_tag_value("f")
    print(clicked_button)
    if clicked_button=="get":
        change_password_mail = get_tag_value("email")
        print(change_password_mail)
        if not isValidData(change_password_mail):
            return get_page("Invalid email")
        accs = get_accounts()
        for account in accs:
            if account.gmail==change_password_mail:
                send_code(change_password_mail)
                return render_template("reset_password.html")
        return get_page("Email Not Found")

    elif clicked_button=="reset":
        accs = get_accounts()
        code = get_tag_value("vcode")
        if not isValidData(code):
            return get_page("Invalid Verification Code")
        if v_code!=int(code):
            return get_page("Wrong Verification Code")
        new_password = get_tag_value("pass_n")
        re_password = get_tag_value("pass_r")
        if not isValidData(new_password):
            return get_page("Invalid Password")
        if new_password!=re_password:
            return get_page("Passwords didn't match")
        for account in accs:
            if account.gmail==change_password_mail:
                index = accs.index(account)
                account.password = new_password
                accs.pop(index)
                accs.insert(index,account)
                with open(accouts_data,"wb") as file:
                    dump(accs,file)
                    file.close()
                return render_template("password_reseted_successfully.html")

    elif clicked_button=="reseted":
        return redirect(url_for("home"))

    elif clicked_button=="cancel":
        return redirect(url_for("forget_password"))


@app.route("/",methods=["POST","GET"])
def main_page():
    clicked_button = get_tag_value("l")
    print(clicked_button)
    if clicked_button=="login":
        username = get_tag_value("username")
        password = get_tag_value("password")
        if not isValidData(username) or not isValidData(password):
            return get_page("Invalid username or password")
        accs = get_accounts()
        account = None
        for acc in accs:
            if username==acc.uname:
                account = acc
        if account==None:
            return get_page("Username not found")
        elif account.password!=password:
            return get_page("Wrong Password")
        else:
            return render_template("select.html")

    elif clicked_button=="add":
        return render_template("add.html")

    elif clicked_button=="add_acc":
        file_storage = request.files["file"]
        return add(file_storage)
    
    elif clicked_button=="search":
        return render_template("search_img.html")

    elif clicked_button=="upload_search":
        file_storage = request.files["file"]
        return search(file_storage)

    elif clicked_button=="cancel_search":
        return render_template("search_img.html")

    elif clicked_button=="solved":
        return get_page("This feature will be available soon")
    
    elif clicked_button=="v_code":
        code = get_tag_value("verification_code")
        print(code)
        if code==v_code:
            return render_template("acc_added_successfully.html")

    else:
        return redirect(url_for("home"))


def send_code(gmail):
    global v_code
    v_code = randint(pow(10,6),pow(10,7)-1)
    msg = "Your verification code is " + str(v_code)
    server = SMTP(host="smtp.gmail.com",port=587)
    server.starttls()
    server.login(user=admin_email,password=admin_password)
    email = EmailMessage()
    email["From"] = admin_email
    email["To"] = gmail
    email["Subject"] = "Verification Code"  
    email.set_content(msg)  
    server.send_message(email)


@app.route("/create_account.html",methods=["GET","POST"])
def add_account():
    global values
    acc = get_accounts()
    clicked = get_tag_value("create")
    print(clicked)
    if clicked=="sign_in":
        name = get_tag_value("name")
        number = get_tag_value("number")
        address = get_tag_value("address")
        gmail = get_tag_value("gmail")
        username = get_tag_value("username")
        password = get_tag_value("password")
        re_password = get_tag_value("password_re")
        values = [name,number,address,gmail,username,password]
        keys = ["Name","Number","Address","G-Mail","Username","Password"]
        for account in acc:
            if account.uname == username:
                return get_page("This username is already taken")
        if password!=re_password:
            return get_page("Passwords doesn't match")
        for index,value in enumerate(values):
            if not isValidData(value):
                return get_page("Invalid " + keys[index])
        send_code(gmail)
        return render_template("send_code.html")
        
    elif clicked=="v_code":
        code = get_tag_value("code")
        if not isValidData(code):return get_page("Invalid verification code")
        if v_code==int(code):
            acc_list = get_accounts()
            name,number,address,gmail,username,password = values
            acc = Account(name=name,username=username,password=password,number=number,gmail=gmail,address=address)
            acc.setID(len(acc_list)+1)
            acc_list.append(acc)
            with open(accouts_data,"wb") as file:
                dump(obj=acc_list,file=file)
                file.close()
            return render_template("acc_added_successfully.html")
        else:
            return get_page("Wrong verification code")
    
    elif clicked=="login":
        return redirect(url_for("home"))
    
    else:
        return redirect(url_for("create_account"))

    
def isValidData(data):
    return data!=None and data!=""


@app.route("/add")
def add(filestorage): #filestorage->FileStorage
    clicked = get_tag_value("l")
    if clicked=="login":
        return redirect(url_for("main_page"))

    bytes = numpy.fromfile(filestorage,numpy.uint8)
    try:
        img = cv2.imdecode(bytes,cv2.IMREAD_COLOR)
    except cv2.error:
        return get_page("Invalid image")
    locations = face_locations(img)
    if len(locations)!=1:
        print("Invalid image")
        return get_page("Invalid Image")
    a,b,c,d = locations[0]
    cv2.rectangle(img,(d,a),(b,c),color=(255,255,255),thickness=2)
    face_encoding = face_encodings(img,model="large")
    if len(face_encoding)!=1:
        print("Can't detect face properly")
        return get_page("Can't detect face properly")
    face_encodings_data = face_encoding[0]
    known_people = get_people_list()
    name = request.form.get("person_name")
    age = request.form.get("person_age")
    gender = request.form.get("gender")
    dob = request.form.get("dob")
    location = request.form.get("lost_location")
    if not isValidData(name):
        return get_page("Invalid Name")
    if not isValidData(age) or int(age)<=0:
        return get_page("Invalid age")
    if not isValidData(gender):
        return get_page("Gender not selected")
    if not isValidData(dob):
        return get_page("DOB not selected")
    comments = request.form.get("comments")
    print(comments)
    id = len(listdir(images_dir))+1
    person = Person(name)
    person.setId(id)
    person.setFaceEncodings(face_encodings_data)
    person.setAge(age)
    person.setGender(gender)
    person.setDOB(dob)
    person.setLostLocation(location)
    person.setComments(comments)
    known_people.append(person)
    with open(saved_image_face_data,"wb") as file:
        dump(known_people,file)
        file.close()
    current_file_path = person.getPath()
    cv2.imwrite(current_file_path,img)
    return render_template("registration_completed.html")


def search(file_storage):
    bytes = numpy.fromfile(file_storage,numpy.uint8)
    try:
        img = cv2.imdecode(bytes,cv2.IMREAD_COLOR)
    except cv2.error:
        return get_page("Invalid image")
    locations = face_locations(img)
    if len(locations)!=1:
        print("Invalid image")
        return get_page("Invalid Image")
    a,b,c,d = locations[0]
    cv2.rectangle(img,(d,a),(b,c),color=(255,255,255),thickness=2)
    encodings = face_encodings(img,model="large")
    if len(encodings)!=1:
        return get_page("No face found in image")
    current_face_encoding = encodings[0]
    known_persons = []
    if isfile(saved_image_face_data):
        with open(saved_image_face_data,"rb") as file:
            known_persons = load(file)
            file.close()
    known_encodings = []
    for person in known_persons:
        known_encodings.append(person.face_encodings)
    results = compare_faces(known_encodings,current_face_encoding,tolerance=0.6)
    matched = []
    for index,result in enumerate(results):
        if result:
            person = known_persons[index]
            matched.append(person)
    if len(matched)<1:
        return get_page("No Face Matched")
    return render_template("search.html",people=matched)




if __name__=="__main__":
    app.run(debug=True)