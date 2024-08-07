# Author: Isuru Kalhara
# Reference : https://pythonspot.com/flask-web-forms/

import os
import sys
import itertools
from jiwer import cer
import pyparsing
import rdflib
from flask import Flask, render_template, flash, request
from wtforms import Form, StringField, validators
from owlready2 import *
from owlready2.sparql.endpoint import *
from query_api import get_book_from_category, get_author_from_book, get_book_from_author, get_book_from_publisher, get_book_from_year, get_book_from_isbn
from owlready2 import *

app = Flask(__name__)
app.config['SECRET_KEY'] = '5791628bb0b13ce0c676dfde280ba245'
global no_query
global anything


class ReusableForm(Form):
    query = StringField('Query:', validators=[validators.data_required()])
    @app.route("/", methods=['GET', 'POST'])
    def hello():
        global graph
        form = ReusableForm(request.form)
        if form.errors:
            print(form.errors)

        base_query = """PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
        PREFIX owl: <http://www.w3.org/2002/07/owl#>
        PREFIX : <http://www.semanticweb.org/huutuongtu/ontologies/2024/3/untitled-ontology-15#>
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
        PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>"""

        output = {}
        query = ''
        # request.form['but1']='AllBook'
        # print(request.form)
        # import pdb; pdb.set_trace()
        if request.method == 'POST':
            if(request.form['but1']=='AllBook'):
                no_query = True
                query = """
                    SELECT ?bookname ?bookauthor ?bookpublisher
                        WHERE {
                            ?book :hasTitle ?bookname .
                            ?book :hasAuthor ?author .
                            ?author :hasName ?bookauthor .
                            ?book :hasPublisher ?publisher .
                            ?publisher :publisherHasName ?bookpublisher .
                        }

            """
            
            else:
                anything = request.form['query']
                no_query = False
                if anything == "":
                    data = []
                else:
                    # print("vao ham")
                    data = []
                    len_dta = len(str(anything))
                    if len_dta < 11 and len_dta > 4:
                        data.extend(get_book_from_isbn(str(anything)))
                    data.extend(get_book_from_author(str(anything)))
                    data.extend(get_book_from_publisher(str(anything)))
                    # data.extend(get_book_from_isbn(str(anything)))
                    if len_dta < 5:
                        data.extend(get_book_from_year(str(anything)))
                    # #get_book_from_category and get_author_from_book work, need fix 2 left
                    if get_book_from_category(anything):
                        data.extend(get_book_from_category(anything))
                    data.extend(get_author_from_book(anything))
                    data.sort()
                    data = list(k for k,_ in itertools.groupby(data))
                    # print(set(data))
                    # data = list(set(data))
                    

                    
            cols = ["Book", "Author", "Publisher"]
            if no_query is False:
                if data==[]:
                    data = ["", "", ""]
            else:
                query = base_query + query
                data = list(default_world.sparql(base_query + query))
                # print(data)

                    

            output = {'columns': cols,
                      'data': data}
            flash('Results ready!')


        return render_template('home.html', form=form, title="Book Search", output=output)


if __name__ == "__main__":

    app.run(port=9000,debug=True)