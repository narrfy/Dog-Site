from flask import *
from flask_sqlalchemy import *
from flask_login import *

app = Flask(__name__, static_url_path='/static')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.sqlite'
app.config['SECRET_KEY'] = 'thisIsAReallyCoolSecretKey'
db = SQLAlchemy(app)

login_manager = LoginManager(app)
login_manager.init_app = 'login'

app.app_context().push()


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True)
    password = db.Column(db.String(100))
    dog = db.relationship('Dog', backref='owner', cascade='all, delete-orphan')

class Dog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(20))
    type = db.Column(db.String(20))
    age = db.Column(db.Integer)
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


@app.route('/')
def home():
    return render_template('home.html')


@app.route('/createAcc', methods=['GET', 'POST'])
def createAcc():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        if User.query.filter_by(username=username).first() is None:
            new_account = User(username=username, password=password)
            db.session.add(new_account)
            db.session.commit()
            login_user(new_account)
            return render_template('home.html')
    return render_template('createAcc.html')


@app.route('/createDog', methods=['GET', 'POST'])
@login_required
def createDog():
    if request.method == 'POST':
        name = request.form['name']
        type = request.form['type']
        age = request.form['age']

        entry = Dog(name=name, type=type, age=age, owner=current_user)
        db.session.add(entry)
        db.session.commit()
        return redirect('/read')
    return render_template('createDog.html')


@app.route('/deleteAcc/<int:id>')
@login_required
def deleteAcc(id):
    user_to_delete = User.query.get(id)
    db.session.delete(user_to_delete)
    db.session.commit()
    logout_user()
    return render_template('home.html')


@app.route('/deleteDog/<int:id>')
@login_required
def deleteDog(id):
    entry = Dog.query.get(id)
    db.session.delete(entry)
    db.session.commit()

    return redirect('/read')


@app.route('/accountSettings/<int:id>', methods=['GET', 'POST'])
@login_required
def updateAcc(id):
    password_update = 'password_submit' in request.form
    username_update = 'username_submit' in request.form

    if request.method == 'POST':
        if password_update:
            current_password = request.form['current_password']
            new_password = request.form['new_password']
            current_user.password = new_password

        if username_update:
            current_username = request.form['current_username']
            new_username = request.form['new_username']
            current_user.username = new_username

        db.session.commit()
        return render_template('home.html')

    return render_template('accountSettings.html', entry=current_user, password_update=password_update, username_update=username_update)


@app.route('/update/<int:id>', methods=['GET', 'POST'])
@login_required
def updateDog(id):
    entry = Dog.query.get(id)

    if request.method == 'POST':
        entry.name = request.form['name']
        entry.type = request.form['type']
        entry.age = request.form['age']

        db.session.commit()
        return redirect('/read')

    return render_template('update.html', entry=entry)


@app.route('/view')
@login_required
def view():
    dog_list = [
        "./static/images/Boxer.jpg",
        "./static/images/Akita.jpg",
        "./static/images/Beagle.jpg",
        "./static/images/Husky.jpg",
        "./static/images/Labrador.jpg",
        "./static/images/Shepherd.jpg"
    ]
    return render_template('view.html', dogList=dog_list)


@app.route('/read')
@login_required
def read():
    entries = Dog.query.all()
    return render_template('read.html', entries=entries)


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username, password=password).first()
        if user:
            login_user(user)
            return render_template('home.html')
    return render_template('login.html')


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return render_template('home.html')


@app.errorhandler(404)
def page_not_found(error):
    return render_template('404.html'), 404

@app.errorhandler(401)
def unauthorized_access(error):
    return render_template('401.html'), 401

if __name__ == '__main__':
    db.create_all()
    app.run()