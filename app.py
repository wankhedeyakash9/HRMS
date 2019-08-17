
from flask import Flask, flash, render_template, request, session, redirect, url_for
import os
import mysql.connector
import fileconvertors
import img_file_functions as img_fun


################################################################################################
# Declaration of some global variables or objects

id_password_post_name = None
side_Btn = list()
myDb = mysql.connector.connect(host="localhost", user='root', passwd='12345', database='hrms')
myCursor = myDb.cursor()
attendance_flag = False

workerOptions = ['Profile', 'My Projects', 'company', 'PunchIn or PunchOut', 'Attendance Report']
workerSideBtn = ['My Profile', 'Attendance', 'Dependents', 'Company Structure', 'My projects', 'Staff Directory']

supervisorOptions = ['Profile', 'People', 'Projects', 'Clients', 'PunchIn or PunchOut', 'Attendance']
supervisorSideBtn = ['Company Structure', 'Client Project Setup', 'Monitor Attendance', 'Employees', 'My Profile',
                     'Attendance', 'My projects', 'Dependents', 'Staff Directory']

##########################################################################################

# An object of Flask
app = Flask(__name__)


#############################################################################################
# This are some methods used for session login


@app.route('/')
def home():
    """This method shows login page until logged in"""

    if not session.get('logged_in'):        # Check if logged in or not
        return render_template('login.html')

    else:
        return loggedIn()                   # if logged in call loggedIn



@app.route('/login', methods=['POST'])
def do_login():
    """The method validate the login id and password"""

    global id_password_post_name

    myCursor.execute("select empId, password, post, concat(Fname,' ',Lname) from Employee where empId = '" +
                     request.form['username']+"'")
    id_password_post_name = myCursor.fetchone()

    if id_password_post_name and (request.form['password'] == id_password_post_name[1] and
                             request.form['username'] == id_password_post_name[0]):
        session['logged_in'] = True

    else:
        flash('Wrong Employee ID or password!', 'info')

    return home()


@app.route('/loggedIn')
def loggedIn():
    """This method determines the type of user and load home page accordingly"""
    session.pop('_flashes', None)
    app.jinja_env.cache = {}

    global options, side_Btn, workerSideBtn, workerOptions, supervisorSideBtn, supervisorOptions, pic
    options = None

    if not img_fun.image_exist():
        myCursor.execute("select image from hrms.employee where EmpId ='"+id_password_post_name[0] + "'")
        pic = myCursor.fetchone()[0]
        fileconvertors.write_file(pic, img_fun.get_random_img_name())

    if id_password_post_name[2] == "worker":
        options = workerOptions
        side_Btn = workerSideBtn

    else:
        options = supervisorOptions
        side_Btn = supervisorSideBtn
        
    return render_template('home.html', buttons=options,  side_Btn=side_Btn,
                           id_password_post_name= id_password_post_name)


@app.route("/logout")
def logout():
    """This method log out the users"""
    os.remove("./static/"+img_fun.get_img_name())
    session['logged_in'] = False
    return home()


########################################################################################################
# This are all the links on home page

@app.route('/Profile')
def profile():
    """this method redirects you to My Profile page """
    return my_profile()


@app.route('/Attendance')
def attendance_report():
    """this method redirects you to Attendance page """
    return attendance()


@app.route("/Company_Structure")
def company():
    """this method redirects you to Company structure page """
    return company_structure()


@app.route('/Client&Project_Setup')
def clients():
    """this method redirects you Clients & Project setup  page """

    return client_project_setup()


@app.route('/My_Projects')
def projects():
    """this method redirects you to My Project page """

    return my_projects()


@app.route('/Employees')
def people():
    """this method redirects you to Employees page """

    return employees()

##############################################################################################

@app.route('/punchinout', methods= ["GET","POST"])
def punchin_or_punchout():
    """This method marks attendance using punch in or punch out """

    user = id_password_post_name[0]

    myCursor.execute( "select PunchOut from attendance where attendance_date= curdate() and EmpId =\"" + user + "\"")
    temp = myCursor.fetchall()

    if request.form["punch"] == "PunchIn" and not temp :
        myCursor.execute("insert into attendance value (\"" + user + "\",curtime(),null,null,curdate())")
    else:
        myCursor.execute("select PunchOut from attendance where attendance_date= curdate() and EmpId =\"" + user + "\"")
        temp = myCursor.fetchall()
        if not temp[0][0]:
            myCursor.execute("update attendance set PunchOut = curtime() where attendance_date= curdate() and EmpId =\"" + user + "\"")

    myDb.commit()

    return attendance()


#############################################################################################
# This are all side buttons links

@app.route('/My_Profile')
def my_profile():
    """This method opens users profile"""
    global side_Btn, id_password_post_name
    app.jinja_env.cache = {}

    labels = ['Employee Id', 'First Name', 'Last Name', 'Date of birth', 'Gender', 'Post', 'Status', 'Department',
              'Supervisor', 'E-mail address', 'Address', 'City', 'State', 'Contact no.(1)', 'Contact no.(2)']
    myCursor.execute("""SELECT e.EmpId,Fname,Lname,DoB,gender,Post,status,DeptName,supervisorId,Email,address,city,state
                    ,contact1,contact2 FROM employee as e left join contactnumbers as c on  e.EmpId= c.empId """ +
                     "where e.EmpId ='" + id_password_post_name[0]+"'")
    values = myCursor.fetchone()

    return render_template('myProfile.html', side_Btn=side_Btn, labels=labels, values=values,
                           id_password_post_name=id_password_post_name)


@app.route('/Attendance')
def attendance():
    """This method shows the atendance of the user"""
    global side_Btn, id_password_post_name

    myCursor.execute("select punchintime  from attendance where attendance_date=current_date and EmpId = '" +
                     id_password_post_name[0]+"'")
    a = myCursor.fetchall()

    btn_tag = ""
    if a:
        btn_tag = "PunchOut"
    else:
        btn_tag = "PunchIn"
    myCursor.execute("Select Attendance_date, PunchInTime,PunchOut,overTimeHrs from attendance where EmpId= '"
                     + id_password_post_name[0]+"'")
    records = myCursor.fetchall()

    return render_template('attendance.html', side_Btn=side_Btn, records=records,
                           myCursor=myCursor, myDb=myDb, btn_tag=btn_tag, app=app,
                           id_password_post_name=id_password_post_name, user = id_password_post_name[0])


@app.route('/Dependents')
def dependents():
    """This method shows the dependents of a user"""
    global side_Btn
    app.jinja_env.cache = {}

    myCursor.execute("select DepName, Relation,age, gender from dependents where EmpId ='"+id_password_post_name[0]+"'")
    records = myCursor.fetchall()
    return render_template('dependents.html', side_Btn=side_Btn, records=records,
                           id_password_post_name=id_password_post_name)


@app.route("/uploadprofilepic", methods=["GET", "POST"])
def upload_img():

    global pic
    app.jinja_env.cache = {}

    session.pop('_flashes', None)
    f = request.files['uploadedImage']
    f.save(f.filename)
    f = str(f)
    f = os.getcwd()+"\\"+f[f.index("'")+1: f.index(" (")-1]
    f = f.replace("\\", "/", 20)
    f = fileconvertors.convertToBinaryData(f)
    tup = (f, id_password_post_name[0])
    myCursor.execute("update employee set hrms.employee.image = %s where hrms.employee.EmpId =%s", tup)
    myDb.commit()
    flash('file uploaded successfully', 'info')
    os.remove("static/"+img_fun.get_img_name())
    myCursor.execute("select image from hrms.employee where EmpId ='" + id_password_post_name[0] + "'")
    pic = myCursor.fetchone()[0]
    fileconvertors.write_file(pic, img_fun.get_random_img_name())
    
    return my_profile()


@app.route('/Company_Structure')
def company_structure():
    """This method shows the compamy structure"""
    global side_Btn
    app.jinja_env.cache = {}
    myCursor.execute("select DepName,concat(address,', ',city,', ',state), contact from hrms.department ")
    records = myCursor.fetchall()
    myCursor.execute("select EmpId from hrms.employee")
    employees = myCursor.fetchall()
    return render_template('compStructure.html', side_Btn=side_Btn, records=records, id_password_post_name=id_password_post_name,
                           employees=employees)


@app.route('/My_Projects')
def my_projects():
    """This functions shows the projects of  a user"""
    global side_Btn, id_password_post_name
    app.jinja_env.cache = {}

    myCursor.execute("select * from hrms.project where Pid in (select Pid from projectassigned where EmpId ='" +
                     id_password_post_name[0] + "')")
    records = myCursor.fetchall()
    return render_template('my_projects.html', side_Btn=side_Btn, records=records,
                            id_password_post_name=id_password_post_name)


@app.route('/Staff_Directory')
def staff_directory():
    """This method shows the staf directory of all the users of all departments"""
    global side_Btn
    app.jinja_env.cache = {}

    labels = ['Name', 'contact Nos', 'email_ID', 'department']
    myCursor.execute("""select concat(Fname,' ',Lname), concat(contact1,', ',contact2),Email,DeptName 
                         from employee left join contactnumbers on contactnumbers.empId = employee.EmpId""")
    records = myCursor.fetchall()

    return render_template('staff.html', side_Btn=side_Btn, records=records, labels=labels,
                           id_password_post_name=id_password_post_name)


@app.route('/Monitor_Attendance')
def monitor_attendance():
    """This method is used to monitor the attendance of the user by other higher users"""
    global side_Btn, id_password_post_name
    app.jinja_env.cache = {}

    if id_password_post_name[2] == 'supervisor':
        myCursor.execute("""select attendance_date, concat(Fname ,' ',Lname), PunchInTime,PunchOut,overTimeHrs from Employee,
                        attendance where Employee.EmpId in (select EmpId from hrms.employee where supervisorId ='""" +
                         id_password_post_name[0]+"') order by attendance_date ")
    else:
        myCursor.execute("""select attendance_date, concat(Fname ,' ',Lname), PunchInTime,PunchOut,overTimeHrs from Employee,
                        attendance order by attendance_date""")

    records = myCursor.fetchall()

    return render_template('monitorAttendance.html', side_Btn=side_Btn, records=records,
                           id_password_post_name=id_password_post_name)


@app.route('/Employees')
def employees(name=None):
    """This method list the users under a particular user"""
    global side_Btn, id_password_post_name
    app.jinja_env.cache = {}
    records = None
    otherrecords = None

    if id_password_post_name[0]=='Admin':
        myCursor.execute("""select e.EmpId,e.Fname,e.Lname, c.contact1+', '+c.contact2, e.DeptName, e.gender from 
                        employee as e left join contactnumbers as c  on e.EmpId=c.empId where status='active'""" )
        records = myCursor.fetchall()

        myCursor.execute("""select e.EmpId,e.Fname,e.Lname, c.contact1+', '+c.contact2, e.DeptName, e.gender from 
                        employee as e left join contactnumbers as c  on e.EmpId=c.empId where status='terminated'""")
        otherrecords = myCursor.fetchall()

    else:
        myCursor.execute("""select e.EmpId,e.Fname,e.Lname, c.contact1+', '+c.contact2, e.DeptName, e.gender from 
                        employee as e left join contactnumbers as c  on e.EmpId=c.empId where status='active' and
                        supervisorId='"""+ id_password_post_name[0]+"'")
        records = myCursor.fetchall()

        myCursor.execute("""select e.EmpId,e.Fname,e.Lname, c.contact1+', '+c.contact2, e.DeptName, e.gender from employee as e left join 
                                contactnumbers as c  on e.EmpId=c.empId where status='terminated' and supervisorId='""" +
                         id_password_post_name[0] + "'")
        otherrecords = myCursor.fetchall()

    return render_template('employees.html', side_Btn=side_Btn, id_password_post_name=id_password_post_name,
                           records=records, otherrecords=otherrecords, Ename=name)


@app.route('/Client&Project_Setup')
def client_project_setup():
    """This method used to setup the clients and the projects """
    global side_Btn
    app.jinja_env.cache = {}

    pheading = ['Project ID','Name', 'status', 'submission date', 'Client Name']
    cheading =['Client ID', 'Name', 'Contact No','Email address','Address', 'Contract date']

    myCursor.execute("""select Pid, Pname,status,submissionDate, Cname from project left outer join client  on 
                        project.clientId = client.Cid """)
    projectrecords = myCursor.fetchall()

    myCursor.execute("select Cid,Cname, contact,email,concat(address,city,state),contracdate from hrms.client" +
                     " where Cid is not null")
    clientrecords = myCursor.fetchall()

    myCursor.execute("select pid from hrms.project")
    project_list = myCursor.fetchall()

    myCursor.execute("select empid from hrms.employee where status = 'active' and EmpId not in ('Admin','" + id_password_post_name[0]+"')")
    employees_list = myCursor.fetchall()
    return render_template('clientsProjects.html', side_Btn=side_Btn,id_password_post_name=id_password_post_name,
                           projectrecords=projectrecords,
                           clientrecords=clientrecords, pheading=pheading,
                           cheading=cheading, projects=project_list, employees=employees_list)


#####################################################################################################
# This are some internal functions which are not used directly

@app.route("/changePass", methods=['POST'])
def changePass ():
    """This method is used to change the login password of the employee"""
    session.pop("_flashes", None)
    password = request.form["Password"]
    confirm = request.form["ConfirmPassword"]
    if password != confirm:
        flash("Password didn't match with confirm password. Try again!")
    else:
        flash("Password changed successfully")
        myCursor.execute("update employee set password = '"+password + "' where empid = '" + id_password_post_name[0]+"'")
        myDb.commit()
    return my_profile()


@app.route('/deletedemployee', methods=["GET", "POST"])
def deleted_employee():
    """This method is used to terminate an employee"""
    session.pop('_flashes', None)
    app.jinja_env.cache = {}

    if request.form["empid"]:
        myCursor.execute("select concat(Fname,' ',Lname) from employee where EmpId ='" + request.form["empid"] + "'")
        name = myCursor.fetchone()

        myCursor.execute("update employee set status = 'terminated' where EmpId='"+request.form["empid"]+"'")
        if name:
            flash(" Terminated Employee "+str(name), "info")
        else:
            flash(" Employee not found with ID:"+request.form["empid"])
        myDb.commit()
    return redirect(url_for('employees'))


@app.route('/UpdateProfile', methods=['POST'])
def updateProfile():
    """This method is used to Update the profile of the employee"""
    dic = {'Email': request.form["E-mail address"], 'address': request.form["Address"], 'city': request.form["City"],
           'state': request.form["State"]}

    for x, y in dic.items():
        if y != "":
            myCursor.execute("update employee set " + x + " = '" + y + "' where Empid = '"+id_password_post_name[0]+"'")

    dic1 = {'contact1': request.form["Contact no.(1)"], 'contact2': request.form["Contact no.(2)"]}

    for x, y in dic1.items():
        if y != "":
            myCursor.execute("update contactnumbers set " + x + "= " + int(y) + " where empId = '"+id_password_post_name[0]+"'")

    myDb.commit()
    return my_profile()


@app.route("/delete_prompt")
def delete_prompt():
    """This method opens a prompt to terminate employee"""
    app.jinja_env.cache = {}

    return render_template("deleteEmployee.html", side_Btn=side_Btn, id_password_post_name=id_password_post_name)


@app.route('/employeeForm')
def employee_form():
    """This method opens the employee form"""

    myCursor.execute("select DepName from hrms.department")
    departments = myCursor.fetchall()
    return render_template("employeeForm.html", departments=departments, side_Btn=side_Btn,
                           id_password_post_name=id_password_post_name[2])


@app.route('/assignProject', methods=['GET', 'POST'])
def assignProject():
    """This method is used to assign projects to users"""
    employeeid = request.form['EmployeeId']
    projectid = request.form['ProjectId']

    myCursor.execute("select concat(Fname,' ',lname) from employee where Empid = '" + employeeid+"'")
    ename = myCursor.fetchall()[0][0]

    myCursor.execute("select Pname from project where pid ='" + projectid + "'")
    pname = myCursor.fetchall()[0][0]

    myCursor.execute("select EmpId from hrms.projectassigned where EmpId= %s and Pid= %s", (employeeid, projectid))
    exist = myCursor.fetchall()

    if not exist:
        myCursor.execute("insert into hrms.projectassigned value(%s,%s) ",
                         (employeeid, projectid))
        myDb.commit()
        message = 'Assigned employee ' + str(ename) + ' to project ' + str(pname)
    else:
        message = 'Employee ' + str(ename) + ' is already assigned to project ' + str(pname)

    flash(message, 'info')
    return redirect(url_for("client_project_setup"))

################################################################################################



@app.route('/addEmployee', methods=['GET', 'POST'])
def addEmployee():
    """This method is used to add new user(employee) to the organization"""
    session.pop('_flashes', None)
    app.jinja_env.cache = {}
    dep = request.form['dep']
    vals = {"fname": request.form['fname'].capitalize(), "lname": request.form["lname"].capitalize(),
            "doB": request.form["DoB"], "gender": request.form["gender"], "post": request.form["post"],
            "doJ": request.form["DoJ"], "email": request.form["email"],
            "address": request.form["address"], "city": request.form["city"], "state": request.form["state"],
            "password": request.form["password"]}

    if dep == 'None':
        dep = 'null'

    generated_id = (vals["fname"])[:3]+(vals["doJ"][2:]).replace('-', '', 2)
    myCursor.execute("""insert into hrms.employee(EmpId,Fname,Lname,DoB,gender,Post,Doj,DeptName,Email,address,city,state,
                    password)  values('"""+generated_id+"',%s,%s,%s,%s,%s,%s,"+dep+",%s,%s,%s,%s,%s)", tuple(vals.values()))
    myDb.commit()
    myCursor.execute("insert into contactnumbers value('" + request.form['contact1'] + "','" + request.form['contact2'] +
                     "','" + generated_id + "')")
    myDb.commit()

    flash("Employee added successfully", 'info')
    return employees()


@app.route("/addClient", methods=["GET", "POST"])
def add_client():
    """This method is used to add new client to the organization"""
    session.pop('_flashes', None)
    app.jinja_env.cache = {}

    lst = dict()
    lst["cid"] = ""
    lst["Cname"] = str(request.form["Cname"])
    lst["contact"] = request.form["contact"]
    lst["email"] = request.form["email"]
    lst["address"] = request.form["address"]
    lst["city"] = request.form["city"]
    lst["state"] = request.form['state']
    lst["Cdate"] = str(request.form['Cdate'])
    lst["cid"] = lst["Cname"][:4]+lst["Cdate"][2:].replace("-", '', 2)
    tup = tuple(lst.values())
    myCursor.execute("insert into client value(%s,%s,%s,%s,%s,%s,%s,%s) ", tup)
    myDb.commit()
    flash("Client add successfully", "info")
    return client_project_setup()


@app.route("/add_project", methods=["GET", "POST"])
def add_project():
    """This method is used to add new project to the organization"""
    session.pop("_flashes", None)
    app.jinja_env.cache = {}

    lst = list()
    lst.append(request.form['Pname'])
    lst.append(request.form["Pdate"])
    lst.insert(0, lst[0][:4]+(lst[1][2:]).replace("-", "", 2))
    tup = tuple(lst)
    cid = request.form['Cname']
    if cid == 'None':
        cid = 'null'
    else:
        cid = "'"+cid+"'"

    myCursor.execute("insert into project values (%s,%s,'active',%s,"+cid+")", tup)

    myDb.commit()
    flash('Project added successfully', 'info')
    return client_project_setup()


@app.route('/add_dependent', methods=['GET', 'POST'])
def add_dependent():
    """This method is used to add dependents of an employee"""
    depName = request.form['dep_name']
    age = request.form['age']
    gender = request.form['gender']
    empId = request.form['empId']
    relation = request.form['rel']

    myCursor.execute("select concat(Fname,' ',Lname) from employee where EmpId ='" + empId + "'")
    name = myCursor.fetchone()

    if not name:
        flash(" Employee not found with ID:" + empId)
        return redirect(url_for('employees'))

    else:
        flash(" Added dependent of employee " + str(name[0]), "info")

    myCursor.execute("insert into dependents value(%s,%s,%s,%s,%s)",
                     (depName, age, gender, empId, relation))
    myDb.commit()
    return redirect(url_for('employees'))


@app.route('/add_depart', methods=['GET','POST'])
def add_department():
    """This method is used to add department in the organization"""

    Dep_Name = request.form['dep_name']
    address = request.form['address']
    city = request.form['city']
    state = request.form['state']
    contact = request.form['contact']
    MgrId = request.form['mgr_id']
    if request.form["mgr_id"] == 'None':
        MgrId = None
    myCursor.execute("insert into department(DepName,address,city,state,contact,MgrId) values (%s,%s,%s,%s,%s,%s)",
                     (Dep_Name,address,city,state,contact,MgrId))
    myDb.commit()
    return company_structure()


##################################################################################################

app.jinja_env.cache = {}
app.jinja_env.globals.update(get_img_name=img_fun.get_img_name)


app.secret_key = os.urandom(12)
app.config["TEMPLATES_AUTO_RELOAD"] = True

if __name__ == "__main__":
    app.run(debug=True, host='localhost', port=5000)
