from flask import Blueprint, render_template,session,redirect,url_for,flash, request, current_app, send_from_directory, abort, send_file
from .models import User, Announcement, Files, Folders, Pm, Chat, Useractivity
from website import db, socketio
from sqlalchemy import desc, and_, or_
import os
import shutil
import logging
from werkzeug.security import check_password_hash
from flask_socketio import emit, SocketIO, leave_room, join_room


views = Blueprint('views', __name__)



user_sockets = {}
active_chats = {}
def get_chat_id(user1, user2):
    """Create a unique chat ID for two users."""
    return f"{min(user1, user2)}-{max(user1, user2)}"


uploadpath = 'uploads'
websitefolder = 'website'




@views.route('/')
def home():
    if 'user_id' in session:

        user_id = session['user_id']
        user = User.query.filter_by(id=user_id).first()
        firstname = user.fname
        lastname = user.lname
        recent_announcement = Announcement.query.order_by(desc(Announcement.date_created)).first()
        recent_file = Files.query.filter_by(file_user=user.id).first()
        recent_messages = Pm.query.filter_by(to=user_id).order_by(desc(Pm.date)).first()
        return render_template('home.html', fname=firstname, lname=lastname, recent_announcement=recent_announcement, recent_file=recent_file, recent_messages=recent_messages)
    return redirect(url_for('auth.login'))

@views.route('/profile')
def profile():
    if 'user_id' in session:
        user_id = session['user_id']
        user = User.query.filter_by(id=user_id).first()
        if user:
          firstname = user.fname
          lastname = user.lname
          position = user.position
          advisory = user.advisory
          email = user.email
          action = ' ' + str(user.fname) + ' ' + str(user.lname) + ' Viewed their Profile'
          addtolog = Useractivity(action=action)
          db.session.add(addtolog)
          db.session.commit()
          return render_template('profile.html',user=user, email=email,fname=firstname,lname=lastname,position=position,advisory=advisory)
    return redirect(url_for('auth.login'))



@views.route('/announcement')
def announcement():
    if 'user_id' in session:
          user_id = session['user_id']
          user = User.query.get(user_id)
          announcement = Announcement.query.order_by(desc(Announcement.date_created)).all()
          combined = [(announcement, User.query.get(announcement.user__id)) for announcement in announcement]
          action = ' ' + str(user.fname) + ' ' + str(user.lname) + ' Clicked Announcemnt Page '
          addtolog = Useractivity(action=action)
          db.session.add(addtolog)
          db.session.commit()
          return render_template('announcement.html', announcement=announcement, combined=combined, user=user)
    else:
          return redirect(url_for('auth.login'))


@views.route('/messages/<int:id>')
def messages1(id):
    if 'user_id' in session:
        userid = session['user_id']
        self = User.query.get(userid)
        user = User.query.get(id)
        users = User.query.all()
        messages = Pm.query.filter(
            or_(and_(Pm.to == userid, Pm.fr == id),
                and_(Pm.to == id, Pm.fr == userid))
        ).all()
        action = ' ' + str(self.fname) + ' ' + str(self.lname) + ' Opened their conversation history  with: ' + str(user.fname) + ' ' + str(user.lname)
        addtolog = Useractivity(action=action)
        db.session.add(addtolog)
        db.session.commit()
        return render_template('messages.html', pmid=id, messages=messages, userid=userid, userf=user.fname, userl=user.lname, users=users, position=user.position, user=user)
    return render_template('login.html')


@views.route('/files')
def files():
    if 'user_id' in session: 
        id = session['user_id']
        user = User.query.get(id)
        folders = Folders.query.filter_by(folder_user=id).all()
        action = ' ' + str(user.fname) + ' ' + str(user.lname) + ' Viewed a Files Page'
        addtolog = Useractivity(action=action)
        db.session.add(addtolog)
        db.session.commit()
        return render_template('files.html', folders=folders, user=user)
    else:
         return render_template('login.html')



@views.route('/new_announcement', methods=['POST','GET'])
def newannouncement():
    if 'user_id' in session:
                user_id = session['user_id']
                user = User.query.filter_by(id=user_id).first()
                if user.position == 'Principal':
                    if request.method == 'POST':
                         title = request.form['title']
                         content = request.form['content']
                         user_id = session['user_id']
                         user = User.query.filter_by(id=user_id).first()
                         if user:
                              id = user.id
                              add_announcement = Announcement(title=title, content=content, user__id=id, status='disallow', fullname=user.fname+" "+user.lname)
                              db.session.add(add_announcement)
                              action = ' ' + str(user.fname) + ' ' + str(user.lname) + ' Announced: ' + str(title)
                              addtolog = Useractivity(action=action)
                              db.session.add(addtolog)
                              db.session.commit()
                              msg = 'Announcement has been created successfully, please wait for the admin to approve.'
                              return render_template('new_announce.html', msg=msg)
                    else:
                         return render_template('new_announce.html')
                else:
                     return redirect(url_for('views.home'))
    else:
        return render_template('new_announce.html')




@views.route('/viewannouncement/<int:id>')
def viewannouncement(id):
    if 'user_id' in session:
          user_id = session['user_id']
          data = Announcement.query.get(id)
          user = User.query.filter_by(id=user_id).first()
          action = ' ' + str(user.fname) + ' ' + str(user.lname) + ' Viewed a announcement page: ' + str(data.title)
          addtolog = Useractivity(action=action)
          db.session.add(addtolog)
          db.session.commit()
          return render_template('viewannouncement.html', data=data, user=user)
    return redirect(url_for('auth.login'))

@views.route('/delete/<int:id>')
def deleteannouncement(id):
     if 'user_id' in session:
          userid = session['user_id']
          user = User.query.get(userid)
          announcement_delete = Announcement.query.filter_by(id=id).first()
          db.session.delete(announcement_delete)
          action = ' ' + str(user.fname) + ' ' + str(user.lname) + ' Deleted a Announcement called: ' + str(announcement_delete.title)
          addtolog = Useractivity(action=action)
          db.session.add(addtolog)
          db.session.commit()
          return redirect(url_for('views.announcement'))
     return render_template('login.html')


@views.route('/create_folder', methods=['POST', 'GET'])
def createfolder():
     if 'user_id' in session:
          id = session['user_id']
          user = User.query.get(id)
          if request.method == 'POST':
               foldername = request.form['foldername']
               currentpath = os.path.join(websitefolder,uploadpath,user.email)
               newpath = os.path.join(currentpath,foldername)
               foldercorrectpath = os.path.join(uploadpath,user.email,foldername)
               try:
                    os.makedirs(newpath)
                    addtodb = Folders(folder_name=foldername, folder_path=foldercorrectpath, folder_user=user.id, fname=user.fname, lname=user.lname)
                    db.session.add(addtodb)
                    action = ' ' + str(user.fname) + ' ' + str(user.lname) + ' Created a folder named: ' + str(foldername)
                    addtolog = Useractivity(action=action)
                    db.session.add(addtolog)
                    db.session.commit()
                    return redirect(url_for('views.files'))
               except:
                    id = session['user_id']
                    user = User.query.get(id)
                    folders = Folders.query.filter_by(folder_user=id).all()
                    msg = 'The folder name already exists, please use different name.'
                    return render_template('files.html', folders=folders, user=user,msg=msg)
     else:
        return render_template('login.html')
     
@views.route('/actionfolder/<int:id>')
def actionfolder(id):
     if 'user_id' in session:
          folders = Folders.query.get(id)
          return render_template('actionfolder.html', folders=folders, id=id)
     else: return render_template('login.html')


@views.route('/deletefolder/<int:id>')
def deletefolder(id):
     if "user_id" in session:
        userid = session['user_id']
        user = User.query.get(userid)
        folder = Folders.query.get(id)
        db.session.delete(folder)
        files = Files.query.filter_by(folderid=id).all()
        for file in files:
             db.session.delete(file)
        db.session.delete(folder)
        action = '' + str(user.fname) + ' ' + str(user.lname) + ' Deleted a folder named: ' + str(folder.folder_name)
        addtolog = Useractivity(action=action)
        db.session.add(addtolog)
        db.session.commit()
        path = folder.folder_path
        correctpath = os.path.join(websitefolder,path)
        shutil.rmtree(correctpath)
     
        
        return redirect(url_for('views.files'))


     else:
          return render_template('login.html')
     

@views.route('/setpasswordfolder/<int:id>', methods=['POST', 'GET'])
def setpasswordfolder(id):
     if 'user_id' in session:
          folder = Folders.query.get(id)
          userid = session['user_id']
          user = User.query.get(userid)
          if request.method == 'POST':
               password = request.form['password']
               folder.password = password
               action = '' + str(user.fname) + ' ' + str(user.lname) + ' Set a password to Folder: ' + str(folder.folder_name)
               addtolog = Useractivity(action=action)
               db.session.add(addtolog)
               db.session.commit()
               return render_template('foldersetpassword.html', id=id)

          else:
               return render_template('foldersetpassword.html', id=id)
     else:
          return render_template('login.html')
     
@views.route('/renamefolder/<int:id>', methods=['POST','GET'])
def renamefolder(id):
     if 'user_id' in session:
          folder = Folders.query.get(id)
          userid = session['user_id']
          user = User.query.get(userid)
          if request.method == 'POST':
            foldername = request.form['renamefolder']
            
            path = folder.folder_path
            newpath1 = os.path.join(websitefolder,path)
            directory = os.path.dirname(newpath1)
            newpath = os.path.join(directory,foldername)
            if os.path.exists(newpath):
                 return redirect(url_for('views.files'))
            correctpath = os.path.dirname(path)
            correctpath1 = os.path.join(correctpath,foldername)

            os.rename(newpath1, newpath)
            folder.folder_name = foldername
            folder.folder_path = correctpath1
            action = '' + str(user.fname) + ' ' + str(user.lname) + ' Renamed a Folder to: ' + str(foldername)
            addtolog = Useractivity(action=action)
            db.session.add(addtolog)
            db.session.commit()
            return redirect(url_for('views.files'))
          else:
               return render_template('renamefolder.html', folder=folder)
     else:
          return render_template('login.html')
     

@views.route('/folderinfo/<int:id>')
def folderinfo(id):
     if 'user_id' in session:
          folder = Folders.query.get(id)
          user = User.query.filter_by(id=folder.folder_user).first()
          return render_template('folderinfo.html', folder=folder, user=user)
     else: return render_template('login.html')



@views.route('/deleteallfolder', methods=['POST', 'GET'])
def deleteallfolder():
     if 'user_id' in session:
          if request.method == 'POST':
                message = 'Please Confirm Again!!'
                user_id = session['user_id']
                password = request.form['password']
                confirm_password = request.form['confirm_password']
                user = User.query.filter_by(id=user_id).first()
                if password and confirm_password:
                     if password and check_password_hash(user.password, password):
                             folders = Folders.query.filter_by(folder_user=user_id).all()
                             files = Files.query.filter_by(file_user=user_id).all()
                             for i in files:
                                  db.session.delete(i)
                             for i in folders:
                                currentpath = i.folder_path
                                correctpath = os.path.join(websitefolder,currentpath)
                                shutil.rmtree(correctpath)
                                db.session.delete(i)
                             action = '' + str(user.fname) + ' ' + str(user.lname) + ' Deleted All their folders'
                             addtolog = Useractivity(action=action)
                             db.session.add(addtolog)
                             db.session.commit()
                             db.session.commit()
                             return redirect(url_for('views.files')) 
                     else: return render_template('confirmdeleteallfolder.html', messages=message)
                else: return render_template('login.html')
          else:
            return render_template('confirmdeleteallfolder.html')
     else:
          return render_template('login.html')
     


@views.route('/viewfiles/<int:id>', methods=['POST','GET'])
def viewfiles(id):
     if 'user_id' in session:

          
          user_id = session['user_id']
          folder = Folders.query.get(id)
          files = Files.query.filter_by(folderid=folder.id).order_by(desc(Files.date)).all()
          user = User.query.get(user_id)

          filesuser = Files.query.filter_by(file_user=user_id).all()
          usedspace = sum(float(file.size) for file in filesuser)
          

          if request.method == 'POST':                    
               if user.mblimit ==  '0':
                    file = request.files['file']
                    filesize = len(file.read())
                    file_size_mb = filesize / (1024 * 1024)
                    filename = file.filename
                    path = folder.folder_path
                    new_path = os.path.join(websitefolder,path, filename)
                    if os.path.exists(new_path):
                         warn = "A File with the same name already exists. Please select a different file or Rename the file then upload it."
                         return render_template('viewfiles.html', warn=warn,folder=folder, files=files, folderid=id)
                    correctfilepath = os.path.join(path,filename)
                    file.seek(0)
                    file.save(new_path)
                    addtodb = Files(file_name=filename , file_path=correctfilepath, file_user=user.id, folderid=folder.id, fname=user.fname, lname=user.lname, position=user.position, size=file_size_mb)
                    db.session.add(addtodb)
                    action = '' + str(user.fname) + ' ' + str(user.lname) + ' Uploaded a File named: ' + str(filename) + ' into folder: ' + str(folder.folder_name)
                    addtolog = Useractivity(action=action)
                    db.session.add(addtolog)
                    db.session.commit()
                    return redirect(url_for('views.viewfiles', id=id,folderid=id))
               else:
                    if usedspace > int(user.mblimit):
                         usedspace2decimal = round(usedspace,2)
                         return render_template('maxed_storage.html',usedspace=usedspace2decimal)
                    file = request.files['file']
                    filesize = len(file.read())
                    file_size_mb = filesize / (1024 * 1024)
                    if file_size_mb > int(user.mblimit):
                         warn = 'You cannot upload a file that exceeds your storage limit!'
                         return render_template('maxed_storage.html',warn=warn)
                    filename = file.filename
                    path = folder.folder_path
                    new_path = os.path.join(websitefolder,path, filename)
                    if os.path.exists(new_path):
                         warn = "A File with the same name already exists. Please select a different file or Rename the file then upload it."
                         return render_template('viewfiles.html', warn=warn,folder=folder, files=files, folderid=id)
                    correctfilepath = os.path.join(path,filename)
                    file.save(new_path)
                    addtodb = Files(file_name=filename , file_path=correctfilepath, file_user=user.id, folderid=folder.id, fname=user.fname, lname=user.lname, position=user.position, size=file_size_mb)
                    db.session.add(addtodb)
                    action = '' + str(user.fname) + ' ' + str(user.lname) + ' Uploaded a File named: ' + str(filename) + ' into folder: ' + str(folder.folder_name)
                    addtolog = Useractivity(action=action)
                    db.session.add(addtolog)
                    db.session.commit()
                    return redirect(url_for('views.viewfiles', id=id,folderid=id))
          return render_template('viewfiles.html', folder=folder, files=files, folderid=id)
     return render_template('login.html')



@views.route('/deleteallfiles/<int:id>', methods=['POST', 'GET'])
def deleteallfiles(id):
     if 'user_id' in session:
          files = Files.query.filter_by(folderid=id).all()
          files_id = Files.query.filter_by(folderid=id).first()
          user = User.query.filter_by(id=files_id.file_user).first()
          folder = Folders.query.get(id)
          messages = 'Please Confirm Again!!'
          if request.method == 'POST':
               password = request.form['password']
               confirm_password = request.form['confirm_password']
               if password and confirm_password:
                    if password and check_password_hash(user.password, password):
                         for i in files:
                              filename = i.file_name
                              path = i.file_path
                              new_path1 = os.path.join(websitefolder,path)
                              directory = os.path.dirname(new_path1)
                              new_path = os.path.join(directory,filename)
                              os.remove(new_path)
                              db.session.delete(i)

                         action = '' + str(user.fname) + ' ' + str(user.lname) + ' Deleted all files in folder: ' + str(folder.folder_name)
                         addtolog = Useractivity(action=action)
                         db.session.add(addtolog)
                         db.session.commit()
                         return redirect(url_for('views.viewfiles', id=id))
                    return render_template('confirmdeleteallfiles.html',messages=messages, id=id)
               return render_template('comfirmdeleteallfiles.html', messages=messages, id=id)
          return render_template('confirmdeleteallfiles.html', id=id)
     return render_template('login.html')


@views.route('/deletefiles/<int:id>/<int:folderid>')
def deletefiles(id,folderid):
     if 'user_id' in session:
          userid = session['user_id']
          user = User.query.get(userid)
          files = Files.query.get(id)
          folder = Folders.query.get(folderid)
          path = files.file_path
          new_path1 = os.path.join(websitefolder,path)
          dir = os.path.dirname(new_path1)
          new_path = os.path.join(dir, files.file_name)
          os.remove(new_path)
          db.session.delete(files)
          action = '' + str(user.fname) + ' ' + str(user.lname) + ' Deleted a File named: ' + str(files.file_name) + ' in folder: ' + str(folder.folder_name)
          addtolog = Useractivity(action=action)
          db.session.add(addtolog)
          db.session.commit()
          return redirect(url_for('views.viewfiles',id=folderid))
     return render_template('login.html')


@views.route('/renamefiles/<int:id>', methods=['POST', 'GET'])
def renamefiles(id):
     if 'user_id' in session:
          file = Files.query.get(id)
          userid = session['user_id']
          user = User.query.get(userid)
          id = file.id
          if request.method == 'POST':
               new_name = request.form['rename'].replace(' ', '_')
               path = file.file_path
               new_path1 = os.path.join(websitefolder,path)
               dir = os.path.dirname(new_path1)
               new_path = os.path.join(dir,new_name)
               if os.path.exists(new_path):
                    warn = "A file with this name already exists. Please select a different file name."
                    return render_template('renamefiles.html', id=id, file=file, warn=warn)
               correctdir = os.path.dirname(path)
               correctpath = os.path.join(correctdir,new_name)
               if new_path:
                    os.rename(new_path1, new_path)
                    file.file_path = correctpath
                    file.file_name = new_name
                    action = '' + str(user.fname) + ' ' + str(user.lname) + ' Renamed a File : ' + str(file.file_name)
                    addtolog = Useractivity(action=action)
                    db.session.add(addtolog)
                    db.session.commit()
                    return redirect(url_for('views.viewfiles', id=file.folderid))
          return render_template('renamefiles.html', id=id, file=file)
     return render_template('login.html')



@views.route('/searchfiles/<int:id>', methods=['POST','GET'])
def searchfiles(id):
     if 'user_id' in session:
          files = Files.query.filter_by(folderid=id).all()
          folder = Folders.query.get(id)
          userid = session['user_id']
          user = User.query.get(userid)
          if request.method == 'POST':
               query = request.form['query']
               results = [file for file in files if query.lower() in file.file_name.lower()]
               action = '' + str(user.fname) + ' ' + str(user.lname) + ' Searched a File : ' + str(query)
               addtolog = Useractivity(action=action)
               db.session.add(addtolog)
               db.session.commit()
               return render_template('searchfilesresults.html', results=results, folder=folder, query=query)
          return redirect(url_for('views.viewfiles', id=id))
     return render_template('login.html')


@views.route('/searchfolders', methods=['POST', 'GET'])
def searchfolder():
     if 'user_id' in session:
          user_id = session['user_id']
          user = User.query.filter_by(id=user_id).first()
          if request.method == 'POST':
               query = request.form['query']
               results = Folders.query.filter(Folders.folder_name.ilike(f'%{ query }%')).all()
               action = '' + str(user.fname) + ' ' + str(user.lname) + ' Searched a Folder: ' + str(query)
               addtolog = Useractivity(action=action)
               db.session.add(addtolog)
               db.session.commit()
               return render_template('searchfolderresult.html', results=results, query=query)

          return render_template('searchfolderresult.html', results=results)

     return render_template('login.html')




@views.route('/Teachers')
def teachers():
     if 'user_id' in session:
          users = User.query.all()
          user = User.query.get(session['user_id'])
          action = ' ' + str(user.fname) + ' ' + str(user.lname) + ' Viewed a Teachers Page'
          addtolog = Useractivity(action=action)
          db.session.add(addtolog)
          db.session.commit()
          return render_template('teachers.html', users=users)
     return render_template('login.html')



@views.route('/searchteachers', methods=['POST','GET'])
def searchteacher():
     if 'user_id' in session:
          if request.method == 'POST':
               query = request.form['query']
               users = User.query.filter(User.fname.ilike(f'%{query}%')).all()
               user = User.query.get(session['user_id'])
               action = ' ' + str(user.fname) + ' ' + str(user.lname) + ' Searched a Teacher named: ' + str(query)
               addtolog = Useractivity(action=action)
               db.session.add(addtolog)
               db.session.commit()
               return render_template('searchresultsteacher.html', users=users, query=query)
          pass
     return render_template('login.html')



@views.route('/viewteacher/<int:id>')
def viewteacher(id):
     if 'user_id' in session:
          user = User.query.get(id)
          selfid = User.query.get(session['user_id'])
          folders = Folders.query.filter_by(folder_user=user.id).all()
          action = ' ' + str(selfid.fname) + ' ' + str(selfid.lname) + ' Viewed all the folders of : ' + str(user.fname) + ' ' + str(user.lname)
          addtolog = Useractivity(action=action)
          db.session.add(addtolog)
          db.session.commit()
          return render_template('viewteacher.html', user=user, folders=folders)
     return render_template('login.html')


@views.route('/viewteacherfiles/<int:id>', methods=['POST', 'GET'])
def viewteacherfiles(id):
     if 'user_id' in session:
          user = User.query.get(session['user_id'])
          files = Files.query.filter_by(folderid=id).all()
          folder = Folders.query.get(id)
          folderuser = User.query.get(folder.folder_user)
          password = folder.password
          if password:
               if request.method == 'POST':
                    password = request.form['password']
                    if password == folder.password:
                         return render_template('viewteacherfiles.html', folder=folder, files=files)
                    else:
                         msg = 'WRONG PASSWORD!'  
                         return render_template('protectedfolder.html',id=id,msg=msg)
               return render_template('protectedfolder.html',id=id)
          action = ' ' + str(user.fname) + ' ' + str(user.lname) + ' Viewed '+ str(folderuser.fname) + ' '+ str(folderuser.lname) + "'s" + ' folder named:' + str(folder.folder_name) 
          addtolog = Useractivity(action=action)
          db.session.add(addtolog)
          db.session.commit()
          return render_template('viewteacherfiles.html', folder=folder, files=files, id=id)
     return render_template('login.html')


@views.route('/searchteacherfolders/<int:id>', methods=['POST', 'GET'])
def searchteacherfolders(id):
     if 'user_id' in session:
          if request.method == 'POST':
               query = request.form['query']
               folders = Folders.query.filter_by(folder_user=id).all()
               user = User.query.get(id)
               results = [folder for folder in folders if query.lower() in folder.folder_name.lower()]
               self = User.query.get(session['user_id'])

               action = ' ' + str(self.fname) + ' ' + str(self.lname) + ' Searched a folder named: ' + str(query)
               addtolog = Useractivity(action=action)
               db.session.add(addtolog)
               db.session.commit()
               return render_template('searchteacherfoldersresult.html', results=results, user=user)
          pass
     return render_template('login')

@views.route('/searchteachersfiles/<int:id>', methods=['POST', 'GET'])
def searchteachersfiles(id):
     if 'user_id' in session:
          query = request.form['query']
          files = Files.query.filter_by(folderid=id).all()
          results = [file for file in files if query.lower() in file.file_name.lower()]
          folder = Folders.query.get(id)
          user = User.query.get(session['user_id'])
          action = ' ' + str(user.fname) + ' ' + str(user.lname) + ' Searched a file named: ' + str(query)
          print(action)
          addtolog = Useractivity(action=action)
          db.session.add(addtolog)
          db.session.commit()
          return render_template('searchteachersfiles.html', results=results, folder=folder)
     return render_template('login.html')

@socketio.on('txtdata')
def txtdata(data):
    user_id = session['user_id']
    if user_id:
        user = User.query.get(user_id)
        if user:
            addtodb = Chat(msg=data['msg'], user_id=user.id, user_email=user.email)
            db.session.add(addtodb)
            db.session.commit()
            emit('txtdata', {'msg': data['msg'], 'user_id': user.id}, broadcast=True)



@views.route('/pm/<int:id>')
def pm(id):
    if 'user_id' in session:
        userid = session['user_id']
        self = User.query.get(userid)
        user = User.query.get(id)
        messages = Pm.query.filter(
            or_(and_(Pm.to == userid, Pm.fr == id),
                and_(Pm.to == id, Pm.fr == userid))
        ).all()
        action = ' ' + str(self.fname) + ' ' + str(self.lname) + ' Viewed their conversation with : ' + str(user.fname) + ' ' + str(user.lname)
        addtolog = Useractivity(action=action)
        db.session.add(addtolog)
        db.session.commit()
        return render_template('pm.html', pmid=id, messages=messages, userid=userid, userf=user.fname, userl=user.lname)
    return render_template('login.html')


@socketio.on('pm')
def pmtext(data):
    user_id = session['user_id']
    user = User.query.get(user_id)
    msg = data['msg']
    to = data['to']
    recepientuser = User.query.get(to)

    if user_id and to:
        room_id = f"room_{min(user_id, to)}_{max(user_id, to)}"
        addtodb = Pm(msg=msg, fr=user_id, to=to, fname=user.fname, lname=user.lname, position=user.position)
        db.session.add(addtodb)
        action = ' ' + str(user.fname) + ' ' + str(user.lname) + ' Sent a message to: : ' + str(recepientuser.fname) + ' ' + str(recepientuser.lname)
        addtolog = Useractivity(action=action)
        db.session.add(addtolog)
        db.session.commit()
        emit('pm', {'msg': msg, 'from': user_id, 'fname': user.fname, 'lname': user.lname }, room=room_id)

@socketio.on('connect')
def handle_conect():
    user_id = session['user_id']
    if user_id:
        user_sockets[user_id] = request.sid


@socketio.on('disconnect')
def handle_disconnect():
    user_id = session.get('user_id')
    if user_id and user_id in user_sockets:
        del user_sockets[user_id]


@socketio.on('start_chat')
def start_chat(data):
    user_id = session.get('user_id')
    chat_with = data.get('chat_with')
    if user_id and chat_with:
        room_id = f"room_{min(user_id, chat_with)}_{max(user_id, chat_with)}"
        join_room(room_id)
        if user_id not in active_chats:
            active_chats[user_id] = []
        if room_id not in active_chats[user_id]:
            active_chats[user_id].append(room_id)


@views.route('/pmsearch/<int:id>', methods=['POST', 'GET'])
def pmsearch(id):
    if 'user_id' in session:
        userid = session['user_id']
        user = User.query.get(userid)
        if request.method == 'POST':
          query = request.form['query']
          pm = Pm.query.filter(or_(Pm.to == userid, Pm.fr == userid)).filter(Pm.msg.ilike(f'%{query}%')).all()

          action = ' ' + str(user.fname) + ' ' + str(user.lname) + ' Searched a message: ' + str(query) 
          addtolog = Useractivity(action=action)
          db.session.add(addtolog)
          db.session.commit()

          return render_template('pmsearch.html', pmresults=pm, pmid=id, query=query)
        pass
    return render_template('login.html')

@views.route('/removefolderpassword/<int:id>')
def removefolderpassword(id):
     if 'user_id' in session:
          folder = Folders.query.get(id)
          userid = session['user_id']
          user = User.query.get(userid)
          if folder.password:
               folder.password = None
               action = '' + str(user.fname) + ' ' + str(user.lname) + ' Removed a password to Folder: ' + str(folder.folder_name)
               addtolog = Useractivity(action=action)
               db.session.add(addtolog)
               db.session.commit()
               return redirect(url_for('views.files'))
          else:
               return redirect(url_for('views.files'))
     return render_template('login.html')




