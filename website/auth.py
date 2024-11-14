from flask import Blueprint,render_template,redirect,url_for,request,session, current_app, jsonify
from website import db, mail
from .models import User, Files, Folders, Loginlog, Loginfailedlog,Signoutlog, Website, Useractivity, Position, Advisory
from werkzeug.security import generate_password_hash, check_password_hash
from .views import uploadpath, websitefolder
from werkzeug.utils import secure_filename
import os
import logging
import random
from datetime import datetime, timedelta
from flask_mail import Message

auth = Blueprint('auth',__name__)

#Email Send
@auth.route('/testingemail')
def test():
    otp = '1234521232'
    name = 'Myko Chan'
    html_path = os.path.join(current_app.root_path,'templates', 'confirmed_email.html')
    with open(html_path, 'r') as file:
        html_content = file.read()

    html_content = html_content.replace('{{ name }}', name)
    msg = Message('Email Successfully Confirmed!', recipients=['sophiagasmen49@gmail.com'])
    msg.html = html_content

    mail.send(msg)
    return 'Email sent successfully!'

@auth.route('/reset-password-teacher', methods=['POST','GET'])
def reset_password_teacher():
    if request.method == 'POST':
        email = request.form['email']
        user = User.query.filter_by(email=email).first()
        if user:
            otp = str(random.randint(100000,999999))
            

            html_path = os.path.join(current_app.root_path,'templates', 'teacher_email_reset_otp_confirmation.html')
            with open(html_path, 'r') as file:
                html_content = file.read()

            html_content = html_content.replace('{{ otp }}', otp)
            msg = Message('Password Reset Request!', recipients=[email])
            msg.html = html_content

            mail.send(msg)
            session['teacher_reset_otp'] = otp
            session['teacher_reset_email_data'] = email
            return render_template('teacherotp.html')
        else:
            msg = 'Email Not Found!'
            return render_template('teacherresetpassword.html', msg=msg)
    return render_template('teacherresetpassword.html')


@auth.route('/teacherotp', methods=['POST','GET'])
def teacherotp():
    if request.method == 'POST':
        otp = request.form['otp']
        otp_session = session.get('teacher_reset_otp')
        if otp == otp_session:
            session.pop('teacher_reset_otp', None)
            print('VErified OTP')
            return render_template('teachernewpassword.html')
        msg = 'Wrong Otp!'
        return render_template('teacherotp.html', msg=msg)
    return redirect(url_for('auth.login'))
    

@auth.route('/teachernewpassword', methods=['POST','GET' ])
def teachernewpassword():
    if request.method == 'POST':
        password = request.form['password']
        confirm = request.form['confirm']
        if password == confirm:
            email = session.get('teacher_reset_email_data')
            teacher = User.query.filter_by(email=email).first()
            hashed = generate_password_hash(password)
            teacher.password = hashed
            db.session.commit()
            session.pop('teacher_reset_email_data', None)
            return redirect(url_for('auth.login'))
        else:
            msg = 'Password Did Not Match!'
            return render_template('teachernewpassword.html', msg=msg)
    return redirect(url_for('auth.login'))




@auth.route('/signup', methods=['POST','GET'])
def signup():
    valididpath = 'website/static/valid_id'
    positions = Position.query.all()
    advisories =  Advisory.query.all()
    otp_expiration_minutes = 5
    
    if request.method == 'POST':
        email = request.form['email']
        fname = request.form['fname']
        lname = request.form['lname']
        password = request.form['password']
        confirm = request.form['confirm']
        position = request.form['position']
        advisory = request.form['advisory']
        valid_id = request.files['valid_id']
        if password == confirm:
            otp = str(random.randint(100000,999999))
            session['otp'] = otp
            session['signup_data'] = {
                'email' : email,
                'fname' : fname,
                'lname' : lname,
                'password' : password,
                'position' : position,
                'advisory' : advisory,
                'valid_id' : valid_id.filename
            }

            # Store the time when the OTP was created as naive
            session['otp_time'] = datetime.now()
            # Store the expiration time for the OTP as naive
            session['otp_expiration'] = (datetime.now() + timedelta(minutes=otp_expiration_minutes))

            #slot for sending otp to email
            
            name = fname + ' ' + lname
            html_path = os.path.join(current_app.root_path,'templates', 'confirmation_email.html')
            with open(html_path, 'r') as file:
                html_content = file.read()

            html_content = html_content.replace('{{ otp }}', otp).replace('{{ name }}', name)
            msg_otp = Message('Email Confirmation!', recipients=[email])
            msg_otp.html = html_content

            mail.send(msg_otp)


            valid_id.save(os.path.join(valididpath,valid_id.filename))
            return render_template('verify_otp.html', email=email, fullname= fname + ' ' + lname)
        else:
            msg = 'Passwords are not identical. Please double-check and retry.'
            return render_template('signup.html', msg=msg)
    return render_template('signup.html', positions=positions, advisories=advisories)


@auth.route('/verify_otp', methods=['POST','GET'])
def verify_otp():

    otp_createdtime = session.get('otp_time')
    expired_time = session.get('otp_expiration')

    if request.method == 'POST':
        otp = request.form['otp']
        stored_otp = session.get('otp')
        stored_data = session.get('signup_data')

        if otp_createdtime:
            expiration_time = expired_time.replace(tzinfo=None)
            if datetime.now() > expiration_time:
                session.pop('otp', None)
                session.pop('signup_data', None)
                session.pop('otp_time', None)
                session.pop('otp_expiration', None)
                return render_template('otp_expired.html')
                    
        if otp == stored_otp:
            hashed_password = generate_password_hash(stored_data['password'])
            mblimit = 0
            status = 'Disallow'
            add_user = User(email=stored_data['email'],fname=stored_data['fname'],
                            lname=stored_data['lname'],password=hashed_password,
                            position=stored_data['position'],advisory=stored_data['advisory'], mblimit=mblimit,status=status, valid_id=stored_data['valid_id'])
            db.session.add(add_user)
            db.session.commit()
            newpath = os.path.join(websitefolder,uploadpath,stored_data['email'])
            os.makedirs(newpath)

            name = stored_data['fname'] + ' ' + stored_data['lname']
            html_path = os.path.join(current_app.root_path,'templates', 'confirmed_email.html')
            with open(html_path, 'r') as file:
                html_content = file.read()

            html_content = html_content.replace('{{ name }}', name)
            msg_confirmed_email = Message('Email Successfully Confirmed!', recipients=[stored_data['email']])
            msg_confirmed_email.html = html_content
            mail.send(msg_confirmed_email)

            session.pop('otp', None)
            session.pop('signup_data', None)
            session.pop('otp_time', None)
            session.pop('otp_expiration', None)
            return render_template('verified_email.html')
        msg = 'Invalid or Expired OTP!'
        return render_template('verify_otp.html', msg=msg,email=stored_data['email'], fullname= stored_data['fname'] + ' ' + stored_data['lname'])
    return redirect(url_for('auth.login'))


@auth.route('/resend_otp', methods=['POST', 'GET'])
def resend_otp():
    data = session.get('otp')
    otp_createdtime = session.get('otp_time')
    expired_time = session.get('otp_expiration')

    if otp_createdtime:
        expiration_time = expired_time.replace(tzinfo=None)
        if datetime.now() > expiration_time:
            session.pop('otp', None)
            session.pop('signup_data', None)
            session.pop('otp_time', None)
            session.pop('otp_expiration', None)
            return render_template('otp_expired.html')
    if data == None:
        return render_template('otp_expired.html')
        
    #slot for sending to email
    print(data)
    stored_data = session.get('signup_data')
    name = stored_data['fname'] + ' ' + stored_data['lname']
    html_path = os.path.join(current_app.root_path,'templates', 'confirmation_email.html')
    with open(html_path, 'r') as file:
        html_content = file.read()

    html_content = html_content.replace('{{ otp }}', data).replace('{{ name }}', name)
    msg_otp = Message('Email Confirmation!', recipients=[stored_data['email']])
    msg_otp.html = html_content
    mail.send(msg_otp)
    
    return jsonify({"message": "OTP sent to your email."}), 200



@auth.route('/login', methods=['POST','GET'])
def login():
    website_detail = Website.query.get(1)
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        user = User.query.filter_by(email=email).first()
        if user and check_password_hash(user.password , password):
            if user.status == 'Disallow':
                msg = 'Please contact the admin to enable your account for login access. Thank you.'
                return render_template('login.html', website_detail=website_detail, msg=msg)
            session['user_id'] = user.id
            userid = session['user_id']
            username = User.query.get(userid)
            addtodb = Loginlog(userid=userid, fname=username.fname, lname=username.lname)
            db.session.add(addtodb)
            db.session.commit()
            return redirect(url_for('views.home'))
        else:
            addtodb = Loginfailedlog(email=email, password=password)
            db.session.add(addtodb)
            db.session.commit()
            return redirect(url_for('auth.error'))
    return render_template('login.html',website_detail=website_detail)

@auth.route('/signout')
def signout():
    
    userid = session['user_id']
    user = User.query.get(userid)
    addtodb = Signoutlog(fname=user.fname, lname=user.lname, userid=userid)
    db.session.add(addtodb)
    db.session.commit()
    session.pop('user_id', None)
    return redirect(url_for('auth.login'))


@auth.route('/error')
def error():
    website_detail = Website.query.get(1)
    return render_template('errorlogin.html', website_detail=website_detail)

@auth.route('/change_password', methods=['POST','GET'])
def changepassword():
    if 'user_id' in session:
        if request.method == 'POST':
            password = request.form['password']
            confirm_password = request.form['confirm_password']
            if password == confirm_password:
                hashed_password = generate_password_hash(password)
                user_id = session['user_id']
                user = User.query.filter_by(id=user_id).first()
                if user:
                    user.password = hashed_password
                    action = ' ' + str(user.fname) + ' ' + str(user.lname) + ' Updated their password info'
                    addtolog = Useractivity(action=action)
                    db.session.add(addtolog)
                    db.session.commit()
                    db.session.commit()
                    return redirect(url_for('views.profile'))
            else:
                return redirect(url_for('auth.changepassword'))
        return render_template('changepassword.html')
        

    return redirect(url_for('auth.login'))


@auth.route('/update_details', methods=['POST', 'GET'])
def updatedetails():
    if 'user_id' in session:
        user_id = session['user_id']
        user = User.query.filter_by(id=user_id).first()
        fname_add = user.fname
        lname_add = user.lname
        email_add = user.email
        position = user.position
        advisory = user.advisory
        pathtoimg = 'website/static/profile'


        
        
        if request.method == 'POST':
            img = request.files['profile']
            email = request.form['email']
            fname = request.form['fname']
            lname = request.form['lname']
            user.email = email
            user.fname = fname
            user.lname = lname
            secure = secure_filename(img.filename)
            path = os.path.join(pathtoimg,secure)
            img.save(path)
            user.img = secure
            action = ' ' + str(user.fname) + ' ' + str(user.lname) + ' Updated their profile info'
            addtolog = Useractivity(action=action)
            db.session.add(addtolog)
            db.session.commit()
            return redirect(url_for('views.profile'))
        else:
            return render_template('update_details.html',advisory=advisory,position=position, fname=fname_add, lname=lname_add,email=email_add )
    return redirect(url_for('auth.login'))

@auth.route('/update_details/change_position', methods=['POST','GET'])
def changeposition():
    if 'user_id' in session:
        user_id = session['user_id']
        user = User.query.filter_by(id=user_id).first()
        positions = Position.query.all()
        if request.method == 'POST':
            position = request.form['position']
            user.position = position
            db.session.commit()
            return redirect(url_for('auth.updatedetails'))
        else:
            return render_template('changeposition.html',positions=positions)
    return redirect(url_for('auth.login'))


@auth.route('/update_details/change_advisory', methods=['POST','GET'])
def changeadvisory():
    if 'user_id' in session:
        user_id = session['user_id']
        user = User.query.filter_by(id=user_id).first()
        advisories = Advisory.query.all()
        if request.method == 'POST':
            advisory = request.form['advisory']
            user.advisory = advisory
            db.session.commit()
            return redirect(url_for('auth.updatedetails'))
        else:
            return render_template('changeadvisory.html', advisories=advisories)
    else:
        return redirect(url_for('auth.login'))
