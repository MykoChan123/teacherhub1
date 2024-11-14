from flask import Blueprint, session, render_template, current_app
import logging
from .models import User, Files, Pm, Folders, Announcement, Useractivity
import plotly.express as px
import plotly.io as pio
import pandas as pd
from collections import defaultdict
import plotly.graph_objects as go
from website import db


dashboard = Blueprint('dashboard', __name__)

@dashboard.route('/dashboard')
def dashboard_home():
    if 'user_id' in session:
        announcedtotal = Announcement.query.count()
        folderstotal = Folders.query.count()
        pmcount = Pm.query.count()
        userid = session['user_id']
        user = User.query.get(userid)
        files_count = Files.query.filter_by(file_user=userid).count()
        folders_count = Folders.query.filter_by(folder_user=userid).count()
        messages_count = Pm.query.filter_by(fr=userid).count()
        teachers_count = User.query.count()
        
        action = ' ' + str(user.fname) + ' ' + str(user.lname) + ' Viewed Dashboard Page '
        addtolog = Useractivity(action=action)
        db.session.add(addtolog)
        db.session.commit()
        if teachers_count and messages_count and folders_count and files_count:


            messages = Pm.query.with_entities(Pm.fr, Pm.fname, Pm.lname).all()

            fr_count = defaultdict(int)
            if messages:
                for fr_id, fname, lname in messages:
                    if fr_id and fname and lname:
                        name = fname + ' ' + lname
                        fr_count[name] += 1
            
                max_msg = max(fr_count.values())
                teacher_max_msgs = [key for key, value in fr_count.items() if value == max_msg]
                teacher_max_msg = teacher_max_msgs[0]


                min_msg = min(fr_count.values())
                teacher_min_msgs = [key for key, value in fr_count.items() if value == min_msg]
                teacher_min_msg = teacher_min_msgs[0]
            
            
            
            
            data = {
                'Name': list(fr_count.keys()),
                'Message Sent': list(fr_count.values())
            }
            df1 = pd.DataFrame(data)
            fig1 = px.bar(df1, x='Name', y='Message Sent', title='Message Sent by Teacher')

            graph1 = pio.to_html(fig1, full_html=False)

            fig1.update_layout(
                width=1100,
                height=500
            )


            filesbyuser = Files.query.with_entities(Files.fname, Files.lname, Files.file_user).all()
            filesbyusercount = defaultdict(int)
        

            for fname,lname, id in filesbyuser:
                if fname and lname and id:
                    name = fname + ' ' + lname
                    filesbyusercount[name] += 1



            max_upload = max(filesbyusercount.values())
            min_upload = min(filesbyusercount.values())
            total_upload = sum(filesbyusercount.values())

            max_upload_name = list([key for key,value in filesbyusercount.items() if value==max_upload ])
            max_upload_name1 = max_upload_name[0]

            min_upload_name = list([key for key,value in filesbyusercount.items() if value==min_upload ])
            min_upload_name1 = min_upload_name[0]
            


                    

            data = {
                'Name': list(filesbyusercount.keys()),
                'Files' : list(filesbyusercount.values())
            }


            fig2 = px.bar(data, x='Name', y='Files', title='Uploaded files By User')
            
            graph2 = pio.to_html(fig2, full_html=False)
            graph3 = pio.to_html(fig2, full_html=False)

            fig2.update_layout(
                width=1200,
                height=400
            )








            # Query all user positions
            positions = User.query.with_entities(User.position).all()


            # Count occurrences of each position
            position_count = {}
            for position in positions:
                pos = position[0]
                if pos:
                    if pos in position_count:
                        position_count[pos] += 1
                    else:
                        position_count[pos] = 1


            pos_sum = sum(position_count.values())
            pos_percent = {key: (value/pos_sum) * 100 for key, value in position_count.items()}

            sorted_pos_percent = dict(sorted(pos_percent.items(), key=lambda item: item[1], reverse=True))

            min_value_pos = min(position_count.values())

            sorted_keys = list(sorted_pos_percent.keys())
            sorted_values = list(sorted_pos_percent.values())
            sorted_max = round(max(sorted_pos_percent.values()),1)
            sorted_min = round(min(sorted_pos_percent.values()),1)

            pos_min_name = [key for key, value in position_count.items() if value==min_value_pos]
            pos_min_name_list = list(pos_min_name)
            pos_min_name = pos_min_name_list[0]
            



            
            firstkey = sorted_keys[0]
            secondkey = sorted_keys[1]


            secondvalue = round(sorted_values[1],1)
    

            # Prepare data for Plotly
            data = {
                'Position': list(position_count.keys()),  # Positions as categories
                'Teachers': list(position_count.values())   # Counts as values
            }
            df = pd.DataFrame(data)

            # Create a Plotly figure
            fig = px.pie(df, names='Position', values='Teachers', hole=0.3)
            fig.update_traces(
                textinfo='label+percent',  # Display label and percentage
                textposition='inside',     # Place text inside slices
                insidetextorientation='horizontal'  # Ensure text orientation is horizontal for better visibility
            )

            # Update layout to adjust size
            fig.update_layout(
                width=1100,
                height=500,
                title={'text': 'Teacher Positions Distribution', 'x':0.51},
                legend=dict(
                    orientation="v", 
                    xanchor="left",  
                    x=-0.1,  
                    yanchor="top",
                    y=1
                )
            )
            

            # Convert the figure to HTML
            graph_html = pio.to_html(fig, full_html=False,  config={'displayModeBar': False})
            
            

            # Count the message sent by Position
            sent_position = Pm.query.with_entities(Pm.position).all()
            message_sent_position = defaultdict(int)
            for position in sent_position:
                if position and position:
                    message_sent_position[position] += 1

            # Count the Files uploaded by Position
            files_position = Files.query.with_entities(Files.position).all()
            files_position_count = defaultdict(int)

            for position in files_position:
                if position and position:
                    files_position_count[position] += 1

            # Count all the Position
            users_position = User.query.with_entities(User.position).all()
            users_position_list = defaultdict(int)
            users_position_list_keys = users_position_list.keys()

            for position in users_position:
                if position and position:
                    users_position_list[position] += 1


            # Message Sent and files uploaded By Position
            position_message_files = {}
            
            for key in users_position_list_keys:
                message_value = message_sent_position[key] if key in message_sent_position else 0
                files_value = files_position_count[key] if key in files_position_count else 0

                position_message_files[key] = message_value,files_value

            position_message_files_list_keys = list(key[0] for key, value in position_message_files.items())
            position_message_files_list_message = list(value[0] for key, value in position_message_files.items())
            position_message_files_list_file = list(value[1] for key, value in position_message_files.items())

            high_upload_high_message = max(position_message_files, key=lambda k: position_message_files[k][0] * position_message_files[k][1])
            high_upload_high_message_teacher = high_upload_high_message[0]

            low_upload_low_message = min(position_message_files, key=lambda k: position_message_files[k][0] * position_message_files[k][1])
            low_upload_low_message_teacher = low_upload_low_message[0]

            high_upload_low_message = max(position_message_files, key=lambda k: position_message_files[k][1] / max(position_message_files[k][0], 1))
            high_upload_low_message_teacher = high_upload_low_message[0]

            low_upload_high_message = max(position_message_files, key=lambda k: position_message_files[k][0] / max(position_message_files[k][1], 1))
            low_upload_high_message_teacher = low_upload_high_message[0]
            

            

        



            scatter3d_messagesent_position_files = {
                'Message Sent' : position_message_files_list_message,
                'Position' : position_message_files_list_keys,
                'Files uploaded' : position_message_files_list_file
            }
            dfscatter1 = pd.DataFrame(scatter3d_messagesent_position_files)

            figscatter1 = go.Figure(data=[go.Scatter3d(
                z=dfscatter1['Message Sent'],
                y=dfscatter1['Files uploaded'],
                x=dfscatter1['Position'],
                
                mode='markers',
                marker=dict(
                    size=10,
                    color=dfscatter1['Message Sent'],
                    colorscale='Viridis',
                    opacity=0.8
                )
            )])
            figscatter1.update_layout(
                height=500,
            
            scene=dict(
            xaxis=dict(title='Position',
                        tickfont=dict(size=10)),

            yaxis=dict(title='Files Uploaded'),

            zaxis=dict(title='Message Sent'),
                camera=dict(
                    eye=dict(x=1.5, y=1.5, z=1.5)  # Adjust the camera view angle
            )
            ),
            title="Teacher Position: File Uploads & Messages Sent",
            
            
            )

            graph_scatter_test = pio.to_html(figscatter1, full_html=False)









            return render_template('dashboard.html',
                                announcedtotal=announcedtotal,
                                folderstotal=folderstotal,
                                pmcount=pmcount,
                                low_upload_high_message_teacher=low_upload_high_message_teacher,
                                high_upload_high_message_teacher=high_upload_high_message_teacher,
                                low_upload_low_message_teacher=low_upload_low_message_teacher,
                                high_upload_low_message_teacher=high_upload_low_message_teacher,
                                max_msg=max_msg,
                                min_msg=min_msg,
                                teacher_min_msg=teacher_min_msg,
                                teacher_max_msg=teacher_max_msg,
                                graph2=graph2,
                                graph1=graph1,
                                files_count=files_count,
                                teachers_count=teachers_count, 
                                folders_count=folders_count, 
                                messages_count=messages_count, 
                                graph=graph_html,
                                pos_sum=pos_sum,
                                sorted_max=sorted_max,
                                sorted_min=sorted_min,
                                firstkey=firstkey,
                                secondkey=secondkey,
                                secondvalue=secondvalue,
                                pos_min_name=pos_min_name,
                                max_upload=max_upload,
                                min_upload=min_upload,
                                total_upload=total_upload,
                                max_upload_name1=max_upload_name1,
                                min_upload_name1=min_upload_name1,
                                graph_scatter_test=graph_scatter_test,)
        return render_template('nodata.html')

    return render_template('login.html')
