from flask import Flask, render_template, flash, redirect, url_for, session, logging, request
from flask_mysqldb import MySQL
from wtforms import Form, StringField, TextAreaField, PasswordField, validators,IntegerField, ValidationError, DateField, SubmitField, FileField
from passlib.hash import sha256_crypt
from functools import wraps
import mysql.connector

app = Flask(__name__)

app.config['MYSQL_HOST'] = 'remotemysql.com'
app.config['MYSQL_USER'] = 'hUQBmvI7yy'
app.config['MYSQL_PASSWORD'] = '2cKhthmajX'
app.config['MYSQL_DB'] = 'hUQBmvI7yy'
app.config['MYSQL_CURSORCLASS'] = 'DictCursor'


mysql =MySQL(app)

@app.route('/')
def index():
    return render_template('home.html')

class RegisterCollege(Form):
    College_Name = StringField('College Name', [validators.Length(min = 1, max = 80)])
    Username = StringField('Username', [validators.Length(min= 1, max = 80)])
    College_Email = StringField('College Email', [validators.Length(min =1, max =100)])
    Password = PasswordField('Password', [
        validators.DataRequired(),
        validators.EqualTo('confirm', message='Passwords do not match')
    ])
    confirm = PasswordField('Confirm Password')


@app.route('/RegisterCollege', methods=['GET', 'POST'])
def registercollege():
    form = RegisterCollege(request.form)
    if request.method == 'POST' and form.validate():
        College_Name = form.College_Name.data
        Username = form.Username.data
        College_Email = form.College_Email.data
        Password = sha256_crypt.encrypt(str(form.Password.data))

        cur = mysql.connection.cursor()

        cur.execute("INSERT INTO College_Reg(College_Name, Username, College_Email, Password) VALUES(%s, %s, %s, %s)",
                    (College_Name,Username,College_Email,Password))

        mysql.connection.commit()

        cur.close()

        return redirect(url_for('registercollege'))
    return render_template('RegisterCollege.html', form = form)



@app.route('/LoginCollege', methods=['GET', 'POST'])
def LoginCollege():
    if request.method == 'POST':
        # Get Form Fields
        username = request.form['username']
        password_candidate = request.form['password']

        # Create cursor
        cur = mysql.connection.cursor()

        # Get user by username
        result = cur.execute("SELECT * FROM College_Reg WHERE Username = %s", [username])

        if result > 0:
            # Get stored hash
            data = cur.fetchone()
            password = data['Password']

            # Compare Passwords
            if sha256_crypt.verify(password_candidate, password):
                # Passed
                session['logged_in_college'] = True
                session['username'] = username

                flash('You are now logged in')
                return redirect(url_for('dashboard_college'))
            else:
                error = 'Invalid login'
                return render_template('LoginCollege.html', error=error)
            # Close connection
            cur.close()
        else:
            error = 'Username not found'
            return render_template('loginCollege.html', error=error)

    return render_template('LoginCollege.html')

def is_logged_in_college(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if 'logged_in_college' in session:
            return f(*args, **kwargs)
        else:
            flash('Unauthorized, Please login', 'danger')
            return redirect(url_for('index'))
    return wrap

@app.route('/logoutcollege')
@is_logged_in_college
def logout_college():
    session.clear()
    flash('You are now logged out', 'success')
    return redirect(url_for('index'))
# , [validators.Length(min=1, max=10)]
# , [validators.Length(min = 1, max =200)]
class CollegeDtails(Form):
    College_Name = StringField('College Name', [validators.Length(min=1, max=80)])
    Location = StringField('Location', [validators.Length(min=1, max=80)])
    Fees = StringField('Fees', [validators.Length(min=1, max=100)])
    Courses = StringField('Courses')
    Application_Link = StringField('Application Link', [validators.Length(min=1, max =300)])
    Contact = IntegerField('Contact Number')
    Nirf_Rank = IntegerField('Nirf Rank')
    Average_CTC = StringField('Average CTC', [validators.Length(min=1, max=100)])
    Notable_Companies = StringField('Notable Companies that visit', [validators.Length(min=1, max =1000)])
    JEE_MAINS_Rank_Criteria = StringField('JEE MAINS RANK CRITERIA', [validators.Length(min=1,max=80)])
    About = TextAreaField("About US")
    Website_Link = StringField('Website Link', [validators.Length(min=1,max=90)])

@app.route('/dashboardcollege',methods=['GET', 'POST'])
def dashboard_college():
        ct = mysql.connection.cursor()
        result = ct.execute("SELECT * FROM  College_Details WHERE Username LIKE %s", (session['username'],))
        get = ct.fetchall()
        if(result == 0):
            at = True
            form = CollegeDtails(request.form)
            if request.method =='POST' and form.validate():
                College_Name = form.College_Name.data
                Location = form.Location.data
                Fees = form.Fees.data
                Courses = form.Courses.data
                Application_Link = form.Application_Link.data
                Contact = form.Contact.data
                Nirf_Rank = form.Nirf_Rank.data
                Average_CTC = form.Average_CTC.data
                Notable_Companies = form.Notable_Companies.data
                JEE_MAINS_Rank_Criteria =form.JEE_MAINS_Rank_Criteria.data
                About =form.About.data
                Webite_Link = form.Website_Link.data

                cur = mysql.connection.cursor()
                cur.execute("INSERT INTO College_Details(Username, College_Name, Location, Fees, Courses, Application_Link, Contact, Nirf_Rank, Average_CTC, Notable_Companies, JEE_MAINS_RANK_Criteria, About, Website_Link) VALUES(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)",
                            (session['username'], College_Name, Location, Fees, Courses, Application_Link, Contact,
                             Nirf_Rank, Average_CTC, Notable_Companies, JEE_MAINS_Rank_Criteria, About, Webite_Link))
                mysql.connection.commit()
                cur.close()
                return redirect((url_for('index')))
            return render_template('dashboard_college.html', form = form, at =at)
        return render_template('dashboard_college.html',get = get)
        ct.close()

class UpdateDetails(Form):
    Fees = StringField('Fees', [validators.Length(min=1, max=100)])
    Courses = StringField('Courses')
    Application_Link = StringField('Application Link', [validators.Length(min=1, max =300)])
    Contact = IntegerField('Contact Number')
    Nirf_Rank = IntegerField('Nirf Rank')
    Average_CTC = StringField('Average CTC', [validators.Length(min=1, max=100)])
    Notable_Companies = StringField('Notable Companies that visit', [validators.Length(min=1, max =1000)])
    JEE_MAINS_Rank_Criteria = StringField('JEE MAINS RANK CRITERIA', [validators.Length(min=1,max=80)])
    About = TextAreaField("About US")
    Website_Link = StringField('Website Link', [validators.Length(min=1,max=90)])


# #################### until this point it was college################################
#######################################
########################################
########################################

class RegisterStudent(Form):
    Username = StringField('Username', [validators.Length(min=1, max=80)])
    Student_Name = StringField('Student Name', [validators.Length(min = 1, max = 80)])
    email = StringField('Student Email', [validators.Length(min =1, max =100)])
    Contact = IntegerField('Contact')
    Password = PasswordField('Password', [
        validators.DataRequired(),
        validators.EqualTo('confirm', message='Passwords do not match')
    ])
    confirm = PasswordField('Confirm Password')

@app.route('/registerstudent', methods=['GET', 'POST'])
def registerstudent():
    form = RegisterStudent(request.form)
    if request.method == 'POST' and form.validate():
        Username = form.Username.data
        Student_Name = form.Student_Name.data
        email = form.email.data
        Contact = form.Contact.data
        Password = sha256_crypt.encrypt(str(form.Password.data))

        cur = mysql.connection.cursor()

        cur.execute("INSERT INTO Student(Username, Student_Name, email, Contact, Password) VALUES(%s, %s, %s, %s, %s)",
                    (Username, Student_Name, email, Contact, Password))

        mysql.connection.commit()

        cur.close()

        return redirect(url_for('registerstudent'))
    return render_template('Registerstudentt.html', form = form)

@app.route('/LoginStudent', methods=['GET', 'POST'])
def LoginStudent():
    if request.method == 'POST':
        # Get Form Fields
        username = request.form['username']
        password_candidate = request.form['password']

        # Create cursor
        cur = mysql.connection.cursor()

        # Get user by username
        result = cur.execute("SELECT * FROM Student WHERE Username = %s", [username])

        if result > 0:
            # Get stored hash
            data = cur.fetchone()
            password = data['Password']

            # Compare Passwords
            if sha256_crypt.verify(password_candidate, password):
                # Passed
                session['logged_in_student'] = True
                session['username'] = username

                flash('You are now logged in')
                return redirect(url_for('dashboard_student'))
            else:
                error = 'Invalid login'
                return render_template('LoginStudent.html', error=error)
            # Close connection
            cur.close()
        else:
            error = 'Username not found'
            return render_template('LoginStudent.html', error=error)

    return render_template('LoginStudent.html')

def is_logged_in_student(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if 'logged_in_student' in session:
            return f(*args, **kwargs)
        else:
            flash('Unauthorized, Please login', 'danger')
            return redirect(url_for('index'))
    return wrap

@app.route('/logoutstudent')
@is_logged_in_student
def logout_student():
    session.clear()
    flash('You are now logged out', 'success')
    return redirect(url_for('index'))

@app.route('/dashboardstudent',methods=['GET', 'POST'])
def dashboard_student():
    cur = mysql.connection.cursor()
    result =cur.execute("SELECT * FROM College_Details")
    myproblems = cur.fetchall()
    if result>0:
        return render_template('dashboard_student.html',myproblems =myproblems)
    else:
        msg = 'No problems posted'
        return render_template('dashboard_student.html', msg =msg)
    cur.close()
    return render_template('dashboard_student.html')


@app.route('/sort',methods = ['GET', 'POST'])
def sort():
    if request.method == 'POST':
        Fees = request.form['Fees']
        Courses = request.form['Courses']
        Nirf_Rank = request.form['Nirf_Rank']
        Average_CTC = request.form['Average_CTC']
        JEE_MAINS_Criteria = request.form['JEE_MAINS_Criteria']
        cur =mysql.connection.cursor()
        result = cur.execute("SELECT * FROM College_Details WHERE Fees = %s OR Courses = %s OR Nirf_Rank =%s OR Average_CTC =%s OR JEE_MAINS_Rank_Criteria =%s",[Fees,
            Courses, Nirf_Rank, Average_CTC, JEE_MAINS_Criteria])
        myproblems = cur.fetchall()
        if result > 0:
            return render_template('sort.html', myproblems =myproblems)
        else:
           error = 'Username not found'
           return render_template('sort.html', error=error)
        cur.close()
    return render_template('sort.html')

class ReportForm(Form):
    College_Name = StringField('College Name', [validators.Length(min=1, max=200)])
    Complain = TextAreaField('Comlain')

@app.route('/report', methods=['GET', 'POST'])
def report():
    form = ReportForm(request.form)
    if request.method == 'POST' and form.validate():
        College_Name = form.College_Name.data
        Complain = form.Complain.data

        cur = mysql.connection.cursor()

        cur.execute("INSERT INTO Report(College_Name, Complain) VALUES(%s, %s)",
                    (College_Name, Complain))

        mysql.connection.commit()

        cur.close()

        return redirect(url_for('report'))
    return render_template('report.html', form = form)


    
######################################ADMIN##############################
@app.route('/KanteKeAlaawahKoiBhi', methods=['GET', 'POST'])
def login_admin():
    if request.method == 'POST':
        # Get Form Fields
        username = request.form['username']
        password_candidate = request.form['password']

        # Create cursor
        cur = mysql.connection.cursor()

        # Get user by username
        result = cur.execute("SELECT * FROM admin WHERE admin_id = %s", [username])

        if result > 0:
            # Get stored hash
            data = cur.fetchone()
            password = data['password']

            # Compare Passwords
            if (password_candidate == password):

                session['logged_in'] = True
                session['username'] = username

                flash('You are now logged in')
                return redirect(url_for('dashboard_admin'))
            else:
                error = 'Invalid login'
                return render_template('login_admin.html', error=error)
            # Close connection
            cur.close()
        else:
            error = 'Username not found'
            return render_template('login_admin.html', error=error)

    return render_template('login_admin.html')

@app.route('/dashboard_admin')
def dashboard_admin():
    return render_template('dashboard_admin.html')


def is_logged_in(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if 'logged_in' in session:
            return f(*args, **kwargs)
        else:
            flash('Unauthorized, Please login', 'danger')
            return redirect(url_for('index'))
    return wrap

@app.route('/logout_admin')
@is_logged_in
def logout():
    session.clear()
    flash('You are now logged out', 'success')
    return redirect(url_for('index'))

@app.route('/viewreport')
@is_logged_in
def viewreports():
    cur = mysql.connection.cursor()
    result = cur.execute("SELECT * FROM Report")
    myproblems = cur.fetchall()

    if result > 0:
        return render_template('viewreport.html', myproblems=myproblems)
    else:
        msg = 'No reports posted'
        return render_template('viewreport.html', msg=msg)
    cur.close()
    return render_template('viewreport.html')

@app.route('/viewstudent')
@is_logged_in
def viewet():
    cur = mysql.connection.cursor()
    result = cur.execute("SELECT * FROM Student")
    myproblems = cur.fetchall()

    if result > 0:
        return render_template('viewstudent.html', myproblems=myproblems)
    else:
        msg = 'No problems posted'
        return render_template('viewstudent.html', msg=msg)
    cur.close()
    return render_template('viewstudent.html')

@app.route('/viewcollege')
@is_logged_in
def viewcollege():
    cur = mysql.connection.cursor()
    result = cur.execute("SELECT * FROM College_Reg")
    myproblems = cur.fetchall()

    if result > 0:
        return render_template('viewcollege.html', myproblems=myproblems)
    else:
        msg = 'No problems posted'
        return render_template('viewcollege.html', msg=msg)
    cur.close()
    return render_template('viewcollege.html')

@app.route('/delete_college/<string:College_Name>', methods=['POST'])
@is_logged_in
def delete_college(College_Name):
    # Create cursor
    cur = mysql.connection.cursor()

    # Execute
    cur.execute("DELETE FROM College_Reg WHERE College_Name = %s", [College_Name])
    # Commit to DB
    mysql.connection.commit()

    #Close connection
    cur.close()

    flash('Article Deleted', 'success')
    # cat = mysql.connection.cursor()
    # cat.execute("DELETE FROM College_Details WHERE College_Name = %s", [College_Name])
    # mysql.connection.commit()
    # cat.close()

    return redirect(url_for('dashboard_admin'))

@app.route('/update/<string:College_Name>', methods=['GET', 'POST'])

def updatebio(College_Name):
    # Create cursor
    cur = mysql.connection.cursor()

    # Get article by id
    result = cur.execute("SELECT * FROM College_Details WHERE Username = %s", [College_Name])

    art = cur.fetchone()
    # cur.close()
    # Get form
    form = CollegeDtails(request.form)
    form.Fees.data = art['Fees']
    form.Courses.data = art['Courses']
    form.Application_Link.data = art['Application_Link']
    form.Contact.data = art['Contact']
    form.Nirf_Rank.data = art['Nirf_Rank']
    form.Average_CTC.data = art['Average_CTC']
    form.Notable_Companies.data = art['Notable_Companies']
    form.JEE_MAINS_Rank_Criteria.data = art['JEE_MAINS_Rank_Criteria']
    form.About.data = art['About']
    form.Website_Link.data =art['Website_Link']

    if request.method == 'POST' and form.validate():
        Fees = request.form['Fees']
        Courses = request.form['Courses']
        Application_Link = request.form['Aplication Link']
        Contact = request.form['Contact']
        Nirf_Rank = request.form['Nirf Rank']
        Average_CTC = request.form['Average CTC']
        Notable_Companies = request.form['Notable Companies']
        JEE_MAINS_Rank_Criteria = request.form['JEE MAINS Rank Criteria']
        About = request.form['About']
        Website_Link = request.form['Website Link']


        # Create Cursor
        # cur = mysql.connection.cursor()
        app.logger.info(About)
        stmt ="UPDATE College_Details SET Fees=%s, Courses=%s, Application_Link=%s, Contact=%s, Nirf_Rank=%s, Average_CTC=%s, Notable_Companies=%s, JEE_MAINS_Rank_Criteria =%s, About = %s, Website_Link = %s, WHERE College_Name=%s"
        # Execute
        cur.execute(stmt,(Fees, Courses, Application_Link, Contact, Nirf_Rank, Average_CTC, Notable_Companies, JEE_MAINS_Rank_Criteria, About, Website_Link, [College_Name]))
        # Commit to DB
        mysql.connection.commit()

        #Close connection
        cur.close()

        flash('Article Updated', 'success')

        return redirect(url_for('index'))

    return render_template('update.html', form=form)


if __name__ == '__main__':
    app.secret_key='secret123'
    app.run(debug=True)