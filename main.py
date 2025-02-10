from flask import Flask, render_template, redirect, request, make_response, url_for
from werkzeug.security import generate_password_hash, check_password_hash
from data import db_session
from data.Students import Student
from data.FridgeList import FridgeList
from data.DeletedProducts import DelProd
from forms.user_reg import RegisterForm
import os
from flask import Flask, render_template, request
import cv2
import numpy as np
from pyzbar.pyzbar import decode
import datetime


app = Flask(__name__)
app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'
UPLOAD_FOLDER = 'uploads/'
task_n = 0
name = ""
type = ""
cor_ans = 0
real_id = 0
avat_way = "img/logo2.png"
all_list = ["1", "2", "3", "4", "5"]


def main():
    db_session.global_init("db/task.db")
    app.run(host='0.0.0.0', port=5000, debug=True, threaded=False)


def re_id():
    global real_id
    total = 0
    db_sess = db_session.create_session()
    student = db_sess.query(Student)
    for i in student:
        total += 1
    real_id = total


def add_products_in_bd(data):
    data = data[0].split("/")
    data = data[-1]
    data = str(data).split(",")
    print(data)
    db_sess = db_session.create_session()
    ind = (db_sess.query(Student.id).all())[-1]
    ind = str(ind)[1:-2]
    print(ind)
    prod = FridgeList(
        user_id=ind,
        name=data[0],
        type=data[1],
        f_date=data[2],
        l_date=data[3],
        weight=data[4],
        calories=data[5],
        total=data[6]

    )
    db_sess.add(prod)
    db_sess.commit()


@app.route('/MainPage') #Главная страница
def index():
    return render_template('index.html')



@app.route('/products') #страница с продуктами
def product():
    db_sess = db_session.create_session()
    prod = db_sess.query(FridgeList).all()
    ind = (db_sess.query(Student.id).all())[-1]
    ind = str(ind)[1:-2]
    prod_1 = db_sess.query(FridgeList).filter_by(user_id=ind).all()
    if prod_1:
        return render_template('products_html.html', products=prod_1)
    return render_template("upload.html") #если продуктов нет, то перекидывает на страницу где их нужно добавить


@app.route('/del_prod', methods=['POST']) # удаление продукта
def del_prod():
    data = request.form.get('input_data')
    db_sess = db_session.create_session()
    item_to_delete = db_sess.query(FridgeList).filter_by(name=str(data)).first()
    print(item_to_delete)

    # добавить данные в новую БД
    ind = (db_sess.query(Student.id).all())[-1]
    ind = str(ind)[1:-2]

    prod = DelProd(
        user_id=ind,
        name=item_to_delete.name,
        type=item_to_delete.type,
        f_date=item_to_delete.f_date,
        l_date=item_to_delete.l_date,
        weight=item_to_delete.weight,
        calories=item_to_delete.calories,
        total=item_to_delete.total

    )
    db_sess.add(prod)

    db_sess.delete(item_to_delete)
    item_to_delete = db_sess.query(FridgeList).filter_by(name=str(data)).first()
    print(item_to_delete)
    db_sess.commit()



    #подгрузка БД
    db_sess = db_session.create_session()
    ind = (db_sess.query(Student.id).all())[-1]
    ind = str(ind)[1:-2]
    prod_1 = db_sess.query(FridgeList).filter_by(user_id=ind).all()

    if prod_1:
        return render_template('products_html.html', products=prod_1)
    return render_template("upload.html")  # если продуктов нет, то перекидывает на страницу где их нужно добавить


@app.route('/find_prod', methods=['POST']) #доработать
def find_prod():
    data = request.form['find_data']
    db_sess = db_session.create_session()
    ind = (db_sess.query(Student.id).all())[-1]
    ind = str(ind)[1:-2]
    item = db_sess.query(FridgeList).filter_by(name=str(data), user_id=ind).first()

    if item:
        return render_template("search.html", name=item.name)
    else:
        return "Такого продукта нет"


@app.route("/deleted")
def deleted():
    db_sess = db_session.create_session()
    prod = db_sess.query(FridgeList).all()
    ind = (db_sess.query(Student.id).all())[-1]
    ind = str(ind)[1:-2]
    prod_1 = db_sess.query(DelProd).filter_by(user_id=ind).all()
    if prod_1:
        return render_template('deleted.html', products=prod_1)
    else:
        return "Удаленных нет"


@app.route("/spilled")
def spilled():
    db_sess = db_session.create_session()
    ind = (db_sess.query(Student.id).all())[-1]
    ind = str(ind)[1:-2]
    prod = db_sess.query(FridgeList).filter_by(user_id=ind).all()
    product_list = []

    for product in prod:
        product_list.append({'f_date': product.f_date, 'name': product.name, "l_date": product.l_date})

    sp_pr = []
    for i in product_list:
        l_date = i["l_date"].split(":")
        time_now = datetime.date.today()
        if int(str(time_now.year)[2:]) > int(l_date[2]):
            sp_pr.append(i["name"])
        elif int(str(time_now.month)) > int(l_date[1]):
            sp_pr.append(i["name"])
        elif int(str(time_now.day)) > int(l_date[0]):
            sp_pr.append(i["name"])

    if len(sp_pr) > 0:
        return render_template("spilled.html", arr=sp_pr)
    else:
        return "Все в норме"



@app.route('/upload_qr') #загрузки qr кода
def upload_qr():
    return render_template('upload.html')

@app.route('/upload', methods=['POST']) #Загрузка qr кода
def upload_file():
    if 'file' not in request.files:
        return "No file part"

    file = request.files['file']

    if file.filename == '':
        return "No selected file"

    # Считываем изображение из файла
    in_memory_file = np.frombuffer(file.read(), np.uint8)
    image = cv2.imdecode(in_memory_file, cv2.IMREAD_COLOR)

    # Декодируем QR-код
    decoded_objects = decode(image)

    if decoded_objects:
        results = []
        for obj in decoded_objects:
            results.append(obj.data.decode('utf-8'))
        add_products_in_bd(results)
        return render_template("index.html")
    else:
        return "No QR code found"





@app.route('/', methods=['GET', 'POST'])  # регистрация
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        if form.submit1.data:
            if form.password.data != form.password_again.data:
                return render_template('register.html', title='Регистрация',
                                       form=form,
                                       message="Пароли не совпадают")
            db_sess = db_session.create_session()
            if db_sess.query(Student).filter(Student.name.in_([form.name.data])).all():
                return render_template('register.html', title='Регистрация',
                                       form=form,
                                       message="Такой пользователь уже есть")
            user = Student(
                name=form.name.data
            )
            user.set_password(form.password.data)
            db_sess.add(user)
            db_sess.commit()
            return redirect('/MainPage')

        if form.submit2.data:  # пользователь есть в БД
            if form.password.data != form.password_again.data:
                return render_template('register.html', title='Регистрация',
                                       form=form,
                                       message="Пароли не совпадают")
            db_sess = db_session.create_session()
            check = db_sess.query(Student).filter(Student.name.in_([form.name.data])).all()
            if len(check) == 0:
                return render_template('register.html', title='Регистрация',
                                       form=form,
                                       message="Такого пользователя не существует")
            elif len(check) == 1:
                return redirect('/MainPage')

    return render_template('register.html', title='Регистрация', form=form)


if __name__ == '__main__':
    main()