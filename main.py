# Degrees website
# Made by Kush Desai
# From 3/5/2021 - 29/10/2021
# License: MIT License

'''
Git
Repo: https://github.com/KushDesai04/13DTP-Project
user.name = 'Kush Desai'
user.email = '17522@burnside.school.nz
'''


import models
from flask import Flask, render_template, request, url_for
from flask_sqlalchemy import SQLAlchemy
from config import Config
from forms import FilterForm
import json


app = Flask(__name__)
app.config.from_object(Config)
db = SQLAlchemy(app)


# Sends uni to every page but is used in nav

@app.context_processor
def context_processor():
    unis = models.University.query.all()
    return dict(unis=unis)


# Reroute when a 404 error is found
@app.errorhandler(404)
def page_not_found(error):
    return render_template('404.html'), 404


# Home page
@app.route('/')
def home():
    universities = models.University.query.all()
    return render_template('home.html', universities=universities)


@app.route('/like', methods=['POST'])
def like():
    degree = json.loads(request.get_data())
    deg = models.Degree.query.filter_by(name=degree['degree']).first()
    deg.likes += 1 if degree['positive'] else - 1
    db.session.merge(deg)
    db.session.commit()
    return str(deg.likes)


# Indiviudual uni page
@app.route('/university/<int:id>')
def university(id):
    university = models.University.query.filter_by(id=id).first_or_404()
    return render_template('university.html', university=university)


# All unis page
@app.route('/universities')
def universities():
    university = models.University.query.all()
    print(university)
    return render_template('university.html', university=university)


# Indiviudual degree page
@app.route('/degree/<int:id>')
def degree(id):
    degree = models.Degree.query.filter_by(id=id).first_or_404()
    universities = degree.universities
    prereq = degree.prerequisites
    prereq_uni = [req.uid for req in prereq]
    return render_template('degree.html', degree=degree,
                           universities=universities,
                           prereq=prereq,
                           prereq_uni=prereq_uni)


# All degrees page
@app.route('/degrees', methods=['GET', 'POST'])
def degrees():
    form = FilterForm()
    degrees = models.Degree.query.all()
    subjects = models.Subject.query.all()
    prerequisites = models.Prerequisites.query.all()
    for p in prerequisites:
        print(p.sid)
    sort_by = 'alphabet'

    if form.validate_on_submit():
        # Empty list to store degrees filtered by university
        uni_degrees = []

        if form.uni_data.data:
            # Get uni id from form
            university_filter = (form.uni_data.data)

            # Filter degrees by uni using set
            for degree in degrees:
                unis = [university.id for university in degree.universities]
                for uni in unis:
                    if str(uni) in university_filter:
                        uni_degrees.append(degree)

        else:
            uni_degrees = set(degrees)

        if form.subject_data.data:
            # Get subject ids from form
            subject_filter = (form.subject_data.data)
            # Get subjects where id in filter or degrees with no prerequisites
            subjects = models.Prerequisites.query.filter(models.Prerequisites.sid.in_(
                subject_filter) | models.Prerequisites.sid.is_(None)).all()

            # Get degree id for every subject filtered
            subjects = [subject.did for subject in subjects]
            sub_degrees = models.Degree.query.filter(
                models.Degree.id.in_(subjects)).all()

            # Get degrees that are in both sets
            degrees = list(set(uni_degrees) & set(sub_degrees))

        # If no subject filters:
        else:
            degrees = uni_degrees

        sort_by = form.radio.data

    else:
        print(form.errors)

    # Sort degrees by name
    if sort_by == 'alphabet':
        degrees = sorted(degrees, key=lambda degree: degree.name)
    elif sort_by == 'likes':
        degrees = sorted(
            degrees,
            key=lambda degree: degree.likes,
            reverse=True)

    return render_template('degrees.html', degrees=degrees, form=form)


if __name__ == '__main__':
    app.run(debug=app.config['DEBUG'])
