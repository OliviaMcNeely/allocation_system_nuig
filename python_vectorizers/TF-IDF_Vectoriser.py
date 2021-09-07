from flask import Flask
from flask import request
from mysql.connector import connect, Error
import pandas
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import linear_kernel

application = Flask(__name__)

# Function to convert all strings to lower case and sepearate words
def clean_skills(x):
    token_list = []
    if isinstance(x, list):
        for string in x:
            i = 0
            start = 0
            string = string.replace(".", "").replace(",", "")
            for x in range(0, len(string)):
                if " " == string[i:i+1]:
                    token_list.append(str.lower(string[start:i]))
                    start = i + 1
                i += 1
            token_list.append(str.lower(string[start:i]))
        return token_list
    else:
        if isinstance(x, str):
            x = x.replace(".", "")
            return [str.lower(x.replace(" ", ", "))]
        else:
            return ['']


# Function to convert description string to an array and strip of spaces
def clean_description(string):
    start = 0
    i = 0
    token_list = []
    if isinstance(string, str):
        for x in range(0, len(string)):
            if " " == string[i:i+1]:
                token_list.append(str.lower(string[start:i]))
                start = i + 1
            i += 1
        token_list.append(str.lower(string[start:i]))
        return token_list
    else:
        return ''


def clean_experience(x):
    token_list = []
    if isinstance(x, list):
        for string in x:
            i = 0
            start = 0
            string = string.replace(".", "").replace(",", "")
            for x in range(0, len(string)):
                if " " == string[i:i+1]:
                    token_list.append(str.lower(string[start:i]))
                    start = i + 1
                i += 1
            token_list.append(str.lower(string[start:i]))
        return token_list
    else:
        #Check if exists. If not, return empty string
        if isinstance(x, str):
            x = x.replace(".", "")
            return [str.lower(x.replace(" ", ", "))]
        else:
            return ['']


def create_soup(x):
        return ' '.join(x['description']) + ' ' + ' '.join(x['skills']) + ' ' + ' '.join(x['experience'])
    

@application.route("/recommend")
def hello_world():

    ids_list = []
    des_list = []
    skills_list = []
    exp_list = []
    metadata = []

    if 'id' in request.args:
        position_id = int(request.args['id'])
    else:
        return "Error: No id field provided. Please specify an id."
    
    try:
        with connect(
            host="mysql1.it.nuigalway.ie",
            user="mydb6146mo",
            password="zo4gah",
            database="mydb6146",
        ) as connection:

            with connection.cursor() as cursor:

                #Get student ids
                cursor.execute("SELECT user_id FROM students")
                ids = cursor.fetchall()
                for i in ids:
                    ids_list.append(i[0])

                #Get student bio
                cursor.execute("SELECT bio FROM students")
                bio = cursor.fetchall()
                for i in bio:
                    des_list.append(i[0])

                #Get student skills
                for student_id in ids_list:
                    cursor.execute("SELECT skill FROM skills WHERE skill_id IN (SELECT skill_id FROM students_skills WHERE user_id = " 
                    + str(student_id) + ")")
                    stu_skills = cursor.fetchall()
                    skills_list.append([i[0] for i in stu_skills])

                #Get student experience
                for student_id in ids_list:
                    cursor.execute("SELECT description FROM experience WHERE student_id = " + str(student_id))
                    exp_des = cursor.fetchall()
                    exp_list.append([i[0] for i in exp_des])

                #Append position id
                ids_list.append(position_id)

                #Append position description
                cursor.execute("SELECT position_description FROM positions WHERE position_id = " + str(position_id))
                pos_description = cursor.fetchall()
                for i in pos_description:
                    des_list.append(i[0])
                
                #Append position skills
                cursor.execute("SELECT skill FROM skills WHERE skill_id IN (SELECT skill_id FROM position_skills WHERE position_id = " 
                + str(position_id) + ")")
                pos_skills = cursor.fetchall()
                skills_list.append([i[0] for i in pos_skills])

                exp_list.append([])

                #Combine data
                data = {
                    "id": ids_list,
                    "description": des_list,
                    "skills": skills_list,
                    "experience": exp_list
                }

                #load data into a DataFrame object:
                metadata = pandas.DataFrame(data)

                # Apply clean_skills function to the skills.
                metadata['skills'] = metadata['skills'].apply(clean_skills)

                # Apply clean_description function to the skills.
                metadata['description'] = metadata['description'].apply(clean_description)

                # Apply clean_description function to the experience.
                metadata['experience'] = metadata['experience'].apply(clean_experience)

                # Create a new soup feature with the description and the skills
                metadata['soup'] = metadata.apply(create_soup, axis=1)

                #Define a TF-IDF Vectorizer Object. Remove all english stop words such as 'the', 'a'
                tfidf = TfidfVectorizer(stop_words='english')

                #Construct the required TF-IDF matrix by fitting and transforming the data
                tfidf_matrix = tfidf.fit_transform(metadata['soup'])

                # Compute the Cosine Similarity matrix
                cosine_sim = linear_kernel(tfidf_matrix, tfidf_matrix)

                # Reset index of your main DataFrame and construct reverse mapping as before
                metadata = metadata.reset_index()
                indices = pandas.Series(metadata.index, index=metadata['id'])

                # Function that takes in position id as input and outputs most similar students
                def get_recommendations(id, cosine_sim=cosine_sim):
                    # Get the index of the position that matches the id
                    idx = indices[id]

                    # Get the pairwise similarity scores of all students with that position
                    sim_scores = list(enumerate(cosine_sim[idx]))

                    # Sort the students based on the similarity scores
                    sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)

                    # Get the scores of the 10 most similar students
                    sim_scores = sim_scores[1:11]

                    # Return the top 10 most similar students
                    return sim_scores

                #Call function passing in the id and the matrix
                scores = get_recommendations(position_id, cosine_sim)

                for i in scores:
                    student_id = metadata['id'].iloc[i[0]]
                    score = round((i[1] * 100),2)
                    rec_id = str(student_id) + "" + str(position_id)
                    with connection.cursor() as cursor:
                        cursor.execute("SELECT * FROM recommendations WHERE recommendation_id = " + rec_id)
                        data=cursor.fetchall()
                        if len(data)==0:
                            cursor.execute("INSERT INTO recommendations (recommendation_id, score, position_id, student_id) VALUES (" + rec_id + ", " + str(score) + ", " + str(position_id) + ", " + str(student_id) + ")")
                            connection.commit()
                        else:
                            cursor.execute("UPDATE recommendations SET score = " + str(score) + " WHERE recommendation_id = " + rec_id)
                            connection.commit()
 
                return "created"

    except Error as e:
        return str(e)
