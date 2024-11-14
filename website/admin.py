from flask import Blueprint, redirect, render_template, request, url_for, current_app, session
from werkzeug.utils import secure_filename
from werkzeug.security import check_password_hash, generate_password_hash
import os
from .models import Website, User, Pm, Folders, Files, Announcement, Loginfailedlog, Loginlog, Signoutlog, Useractivity, Position, Advisory, Admin
from website import db, mail
from flask_mail import Message
import shutil
from werkzeug.security import generate_password_hash
from flask_mail import Message
import random


admin   = Blueprint('admin', __name__)


path = 'website/static/img'

@admin.route('/signoutadmin')
def signoutadmin():
    session.pop('admin', None)
    return render_template('adminlogin.html')

@admin.route('/admin')
def admin1():
    if 'admin' in session:
        return render_template('admin.html')
    return redirect(url_for('admin.adminlogin'))



@admin.route('/update_website', methods=['POST', 'GET'])
def updatewebsite():
    if 'admin' in session:
        website = Website.query.get(1)
        
        if request.method == 'POST':
            name = request.form['name']
            if website != None:
                website.name = name
                img = request.files['file']
                website.logo = img.filename
                db.session.commit()
                secure = secure_filename(img.filename)
                pathjoin = os.path.join(path,secure)
                img.save(pathjoin)
            else:
                img = request.files['file']
                addtodb = Website(name=name, logo=img.filename, id=1)
                db.session.add(addtodb)
                db.session.commit()
                secure = secure_filename(img.filename)
                pathjoin = os.path.join(path,secure)
                img.save(pathjoin)

        return render_template('systeminformation.html',website=website)
    return redirect(url_for('admin.adminlogin'))


@admin.route('/clear_messages', methods=['POST', 'GET'])
def clearmessages():
    if 'admin' in session:
        users = User.query.all()
        if request.method == 'POST':
            teacher = request.form['teacher']
            type = request.form['type']
            if teacher and type == 'all':
                pmall = Pm.query.all()
                for i in pmall:
                    db.session.delete(i)
                    db.session.commit()
            if type == 'all':
                sendpm = Pm.query.filter_by(fr=teacher).all()
                receivedpm = Pm.query.filter_by(to=teacher).all()
                for i in sendpm:
                    db.session.delete(i)
                for i in receivedpm:
                    db.session.delete(i)
                db.session.commit()
            if type == 'sent':
                sendpm = Pm.query.filter_by(fr=teacher).all()
                for i in sendpm:
                    db.session.delete(i)
                    db.session.commit()
                print('Sent messages has been deleted')
            if type == 'received':
                receivedpm = Pm.query.filter_by(to=teacher).all()
                for i in receivedpm:
                    db.session.delete(i)
                    db.session.commit()
                print('will delete received msg')
            
            
        return render_template('clearmessage.html', users=users)
    return redirect(url_for('admin.adminlogin'))

@admin.route('/deleteuser', methods=['POST', 'GET'])
def deleteuser():
    if 'admin' in session:
        path = 'website/uploads/'
        users = User.query.all()
        if request.method == 'POST':
            id = request.form['teacher']
            if id == 'all':
                announcement = Announcement.query.all()
                folders = Folders.query.all()
                files = Files.query.all()
                pm = Pm.query.all()
                teacher = User.query.all()
                for i in folders:
                    db.session.delete(i)
                for i in files:
                    db.session.delete(i)
                for i in teacher:
                    newpath = os.path.join(path,i.email)
                    shutil.rmtree(newpath)
                    db.session.delete(i)
                for i in announcement:
                    db.session.delete(i)
                for i in pm:
                    db.session.delete(i)
                for i in announcement:
                    db.session.delete(i)
                db.session.commit()
                return redirect(url_for('admin.deleteuser'))
            
            folders = Folders.query.filter_by(folder_user=id).all()
            files = Files.query.filter_by(file_user=id).all()
            announcement = Announcement.query.filter_by(user__id=id).all()
            pmreceive = Pm.query.filter_by(to=id).all()
            pmsent = Pm.query.filter_by(fr=id).all()



            

            for i in folders:
                db.session.delete(i)
            for i in files:
                db.session.delete(i)
            for i in announcement:
                db.session.delete(i)
            for i in pmreceive:
                db.session.delete(i)
            for i in pmsent:
                db.session.delete(i)
            teacher = User.query.get(id)
            newpath = os.path.join(path,teacher.email)
            shutil.rmtree(newpath)
            db.session.delete(teacher)
            db.session.commit()
            return redirect(url_for('admin.deleteuser'))
        return render_template('removeuser.html',users=users)
    return redirect(url_for('admin.adminlogin'))

@admin.route('/changepassworduser', methods=['POST','GET'])
def changepassworduser():
    if 'admin' in session:
        users = User.query.all()
        if request.method == 'POST':
            userid = request.form['teacher']
            user = User.query.get(userid)
            password = request.form['password']
            email = request.form['email']
            hashed_password = generate_password_hash(password)
            user.password = hashed_password
            user.email = email
            db.session.commit()

        return render_template('changepassworduser.html',users=users)
    return redirect(url_for('admin.adminlogin'))

@admin.route('/removefolderuser', methods=['POST', 'GET'])
def removefolderuser():
    if 'admin' in session:
        users = User.query.all()
        if request.method == 'POST':
            userid = request.form['teacher']
            teacher = User.query.get(userid)
            email = teacher.email
            folders = Folders.query.filter_by(folder_user=userid).all()
            path = 'website/uploads/' + email
            for i in folders:
                newpath = os.path.join(path, i.folder_name)
                shutil.rmtree(newpath)
                db.session.delete(i)
                db.session.commit()
        return render_template('removefolderuser.html', users=users)
    return redirect(url_for('admin.adminlogin'))


@admin.route('/setuserstorage', methods=['POST', 'GET'])
def setuserstorage():
    if 'admin' in session:
        users = User.query.all()
        if request.method == 'POST':
            teacher = request.form['teacher']
            user = User.query.get(teacher)
            mb = request.form['mb']
            user.mblimit = mb
            db.session.commit()

        return render_template('setuserstorage.html', users=users)
    return redirect(url_for('admin.adminlogin'))


@admin.route('/approveuser', methods=['POST', 'GET'])
def approveuser():
    if 'admin' in session:
        users = User.query.all()
        if request.method == 'POST':
            userid = request.form['teacher']
            action = request.form['action']
            
            if userid == 'All':
                for i in users:
                    i.status = action
                db.session.commit()
                return render_template('aprroveuser.html',users=users)
            user = User.query.get(userid)
            user.status = action
            db.session.commit()
        return render_template('aprroveuser.html',users=users)
    return redirect(url_for('admin.adminlogin'))

@admin.route('/setadminpasssword', methods=['POST', 'GET'])
def setadminpasssword():
    if 'admin' in session:
        admin_id = session.get('admin')
        admin = Admin.query.get(admin_id)
        if request.method == 'POST':
            email = request.form['email']
            password = request.form['password']
            confirm = request.form['confirm']
            if password == confirm:
                hashed = generate_password_hash(password)
                admin_id = session.get('admin')
                admin = Admin.query.get(admin_id)
                admin.password = hashed
                admin.email = email
                db.session.commit()
                msg = 'Successfully Changed!'
                return render_template('setadminpassword.html', email=admin.email, msg=msg)
            msg = 'Password doesnt match!'
            return render_template('setadminpassword.html', msg=msg)
        return render_template('setadminpassword.html', email=admin.email)
    return redirect(url_for('admin.adminlogin'))


@admin.route('/securitylog')
def securitylogs():
    if 'admin' in session:
        loginfailed = Loginfailedlog.query.order_by(Loginfailedlog.id.desc()).all()
        successfullogin = Loginlog.query.order_by(Loginlog.id.desc()).all()
        siguotlog = Signoutlog.query.order_by(Signoutlog.id.desc()).all()
        useractivity = Useractivity.query.order_by(Useractivity.id.desc()).all()
        return render_template('securitylog.html',useractivity=useractivity, loginfailed=loginfailed, successfullogin=successfullogin, siguotlog=siguotlog)
    return redirect(url_for('admin.adminlogin'))




@admin.route('/approveannouncement', methods=['POST', 'GET'])
def approveannouncement():
    if 'admin' in session:
        announcement1 = Announcement.query.filter_by(status='disallow').all()
        if request.method == 'POST':
            allow = request.form.get('allow')
            disallow = request.form.get('disallow')
            print(allow)
            print(disallow)
            if allow:
                announcement = Announcement.query.get(allow)
                announcement.status = 'allow'
                db.session.commit()
                return redirect(url_for('admin.approveannouncement'))
            else:
                announcement = Announcement.query.get(disallow)
                db.session.delete(announcement)
                db.session.commit()
            return redirect(url_for('admin.approveannouncement'))
        return render_template('approveannouncement.html',announcement=announcement1)
    return redirect(url_for('admin.adminlogin'))

@admin.route('/viewpendingannouncement/<int:id>')
def viewpendingannouncement(id):
    if 'admin' in session:
        announcement = Announcement.query.get(id)
        return render_template('viewpendingannouncement.html',announcement=announcement)
    return redirect(url_for('admin.adminlogin'))

@admin.route('/addpositionadvisory')
def addpositionadvisory():
    if 'admin' in session:
        positions = Position.query.all()
        advisories = Advisory.query.all()
        return render_template('addpositionadvisory.html', positions=positions, advisories=advisories)
    return redirect(url_for('admin.adminlogin'))

@admin.route('/addposition', methods=['POST', 'GET'])
def addposition():
    if 'admin' in session:
        if request.method == 'POST':
            position = request.form['position']
            addposition = Position(name=position)
            db.session.add(addposition)
            db.session.commit()
            return redirect(url_for('admin.addpositionadvisory'))
        return render_template('addposition.html')
    return redirect(url_for('admin.adminlogin'))

@admin.route('/deleteposition', methods=['POST', 'GET'])
def deleteposition():
    if 'admin' in session:
        positions = Position.query.all()
        if request.method == 'POST':
            id = request.form['id']
            position = Position.query.get(id)
            db.session.delete(position)
            db.session.commit()
            return redirect(url_for('admin.deleteposition'))
        return render_template('deleteposition.html',positions=positions)
    return redirect(url_for('admin.adminlogin'))

@admin.route('/addadvisory', methods=['POST','GET'])
def addadvisory():
    if 'admin' in session:
        if request.method == 'POST':
            advisory = request.form['advisory']
            addtodb = Advisory(name=advisory)
            db.session.add(addtodb)
            db.session.commit()
            return redirect(url_for('admin.addpositionadvisory'))
        return render_template('addadvisory.html')
    return redirect(url_for('admin.adminlogin'))

@admin.route('/deleteadvisory', methods=['POST', 'GET'])
def deleteadvisory():
    if 'admin' in session:
        advisories = Advisory.query.all()
        if request.method == 'POST':
            id = request.form['id']
            advisory = Advisory.query.get(id)
            db.session.delete(advisory)
            db.session.commit()
            return redirect(url_for('admin.deleteadvisory'))
        return render_template('deleteadvisory.html',advisories=advisories)
    return redirect(url_for('admin.adminlogin'))

@admin.route('/deleteallpositionadvisory')
def deleteallpositionadvisory():
    if 'admin' in session:
        positions = Position.query.all()
        advisories = Advisory.query.all()
        for i in positions:
            db.session.delete(i)
        for i in advisories:
            db.session.delete(i)
        db.session.commit()
        return redirect(url_for('admin.addpositionadvisory'))
    return redirect(url_for('admin.adminlogin'))
    


@admin.route('/confirmuser')
def confirmuser():
    if 'admin' in session:
        users = User.query.all()
        return render_template('viewuser.html', users=users)
    return redirect(url_for('admin.adminlogin'))

@admin.route('/approveuser/<int:id>')
def confirmuseraccount(id):
    if 'admin' in session:
        user = User.query.get(id)
        email = user.email
        name = user.fname + ' ' + user.lname
        user.status = 'Allow'
        db.session.commit()

        html_path = os.path.join(current_app.root_path,'templates', 'valid_id_confirmed.html')
        with open(html_path, 'r') as file:
            html_content = file.read()

        html_content = html_content.replace('{{ name }}', name)
        msg = Message('Government ID Successfully Confirmed!', recipients=[email])
        msg.html = html_content

        mail.send(msg)
        return redirect(url_for('admin.confirmuser'))
    return redirect(url_for('admin.adminlogin'))

@admin.route('/adminlogin', methods=['POST', 'GET'])
def adminlogin():
    admin = Admin.query.get(1)
    if admin == None:
        email = 'admin@email.com'
        password = 'admin'
        hashed = generate_password_hash(password)
        addtodb = Admin(email=email, password=hashed)
        db.session.add(addtodb)
        db.session.commit()
        return render_template('adminlogin.html')
    else:
        if request.method == 'POST':
            email = request.form['email']
            password = request.form['password']
            admin = Admin.query.filter_by(email=email).first()
            if admin:
                if check_password_hash(admin.password, password) and email == admin.email:
                    session['admin'] = admin.id
                    return redirect(url_for('admin.admin1'))
                return render_template('adminlogin.html', msg='Wrong Password Or No Account!')
            return render_template('adminlogin.html', msg='Wrong Password Or No Account!')
    return render_template('adminlogin.html')


@admin.route('/deleteuser/<int:id>')
def deleteuseraccount(id):
    if 'admin' in session:
        user = User.query.get(id)
        db.session.delete(user)
        db.session.commit()\
        
        email = user.email
        name = user.fname + ' ' + user.lname

        html_path = os.path.join(current_app.root_path,'templates', 'valid_id_failed.html')
        with open(html_path, 'r') as file:
            html_content = file.read()

        html_content = html_content.replace('{{ name }}', name)
        msg = Message('ID Verification Failed', recipients=[email])
        msg.html = html_content

        mail.send(msg)
        return redirect(url_for('admin.confirmuser'))
    return redirect(url_for('admin.adminlogin'))

@admin.route("/test")
def test():
    return render_template('reset_email_admin_otp.html')

@admin.route('/reset_email_admin', methods=['POST','GET'])
def reset_email_admin():
   
    if request.method == 'POST':
        email = request.form['email']
        admin = Admin.query.filter_by(email=email).first()
        if admin:
            otp = str(random.randint(100000, 999999))
            html_path = os.path.join(current_app.root_path,'templates', 'reset_email_admin_otp.html')
            with open(html_path, 'r') as file:
                html_content = file.read()

            html_content = html_content.replace('{{ otp }}', otp)
            msg = Message('Reset Admin Password OTP!', recipients=[admin.email])
            msg.html = html_content

            mail.send(msg)
            print(otp)
            session['otp_admin'] = otp
            session['admin_reset_email'] = email
            return render_template('adminpasswordotp.html')
        msg = 'Account Not Found!'
        return render_template('forgetadmin.html', msg=msg)
    return render_template('forgetadmin.html')

@admin.route('/otp_verify_admin', methods=['POST', 'GET'])
def otp_verify_admin():
    otp = request.form['otp']
    stored_otp = session.get('otp_admin')
    if otp == stored_otp:
        session.pop('otp_admin', None)
        return render_template('admin_reset_password.html')
    else:
        print('otp_wrong')
        return render_template('adminpasswordotp.html')


@admin.route('/admin_reset_password', methods=['POST', 'GET'])
def admin_reset_password():
    stored_email = session.get('admin_reset_email')
    admin = Admin.query.filter_by(email=stored_email).first()
    password = request.form['password']
    confirm = request.form['confirm']
    hashed = generate_password_hash(password)
    if password == confirm:
        admin.password = hashed
        session.pop('admin_reset_email', None)
        db.session.commit()
        return render_template('adminlogin.html')
    return render_template('admin_reset_password.html', msg='Password Dont match!')

