#from tkinter import CURRENT
#from unicodedata import category
import sys
from flask import Flask, request, jsonify
from flask_cors import CORS
import random

from models import setup_db, Question, Category, db

QUESTIONS_PER_PAGE = 10

def paginate_questions(request, selection):
    page =  db.paginate(selection,1,QUESTIONS_PER_PAGE,None,True,False)  #request.args.get("page", 1, type=int)
    start = (page - 1) * QUESTIONS_PER_PAGE
    end = start + QUESTIONS_PER_PAGE
   
    questions = [question.format() for question in selection]
    current_questions = questions[start:end]

    return current_questions


def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__)

    if test_config is None:
        setup_db(app)
    else:
        database_path = test_config.get("SQLALCHEMY_DATABASE_URI")
        setup_db(app, database_path=database_path)

    CORS(app)
    with app.app_context():
        db.create_all()

    # CORS Headers
    @app.after_request
    def after_request(response):
        response.headers.add(
            "Access-Control-Allow-Headers", "Content-Type,Authorization,true"
        )
        response.headers.add(
            "Access-Control-Allow-Methods", "GET,PUT,POST,DELETE,OPTIONS"
        )
        return response

    # GET Categories
    @app.route("/categories", methods=["GET"])
    def retrieve_categories():
        try:
            categories = Category.query.order_by(Category.id).all()
            print(f"selection:{categories}")

            formatted_category = {
                category.id: category.type for category in categories
            }
            print(f"formatted_category:{formatted_category}")
            if len(formatted_category) == 0:
                return not_found(404) 

            response = {
                "categories": formatted_category,
            }
            return jsonify(response)
        except Exception as ex:
            print(ex)
            print(sys.exc_info())

    # GET Questions
    @app.route("/questions", methods=["GET"])
    def retrieve_questions():
        
        try:
            all_categories = Category.query.all()
            formatted_cat = {cat.id: cat.type for cat in all_categories}

            selection = (Question.query.all()
            )
            
            current_questions = paginate_questions(request, selection)
            
            if len(current_questions) == 0:
                return not_found(404) 

            response = {
                "questions": current_questions,
                "total_questions": len(Question.query.all()),
                "categories": formatted_cat,
                "current_category": None,
            }

            return jsonify(response)
        except Exception as ex:
           print(ex)
           print(sys.exc_info())

    # DELETE Questions based on Question Id
    @app.route("/questions/<int:question_id>", methods=["DELETE"])
    def delete_question(question_id):
        try:
            question = Question.query.filter(
                Question.id == question_id
            ).one_or_none()
           
            if question is None:               
                return not_found(404)         
      
            question.delete()
            selection = Question.query.order_by(Question.id).all()
            current_question = paginate_questions(request, selection)

            response = {
                "success": True,
                "deleted": question_id,
                "question": current_question,
            }
            return jsonify(response)

        except Exception as ex:
            print(ex)
            print(sys.exc_info())

    # POST Add Question 
    @app.route("/questions", methods=["POST"])
    def create_question():
        body = request.get_json()
        print(f"body:{body}")
        new_question = body.get("question", None)
        new_answer = body.get("answer", None)
        new_category = body.get("category", None)
        new_difficulty = body.get("difficulty", None)
        #new_rating = body.get("rating", None)
        try:
            add_question = Question(
                question=new_question,
                answer=new_answer,
                category=new_category,
                difficulty=new_difficulty,
                #rating=new_rating,
            )
            print(f"add_question:{add_question}")
            if new_question =="" or new_answer =="":
                return method_not_allowed(405) 
            else:
                add_question.insert()

            selection = (
                add_question.query.filter(Question.category == new_category)
                .order_by(Question.id)
                .all()
            )
            current_questions = paginate_questions(request, selection)
            
            response = {
                "created": add_question.id,
                "question": current_questions,
                "success": True
            }
            return jsonify(response),201

        except Exception as ex:
           print(ex)
           print(sys.exc_info())

    #POST Search Question
    @app.route("/questions/search", methods=["POST"])
    def create_search():
        body = request.get_json()
        print(f"body:{body}")
        search = body.get("searchTerm", None)
        
        try:
            if search:
                selection = (
                    Question.query.order_by(Question.id)
                    .filter(Question.question.ilike("%{}%".format(search)))
                    .all()
                )
                print(f'selection:{selection}')
                if len(selection) >= 10:
                    print(f'selection_num:{len(selection)}')
                    current_question = paginate_questions(request, selection)
                else:
                    current_question = [
                        question.format() for question in selection
                    ]
                    print(f'current_question:{current_question}')

                response = {"questions": current_question}
                return jsonify(response)
        except Exception as ex:
           print(ex)
           print(sys.exc_info())

    # GET Questions based on Category Id
    @app.route("/categories/<int:category_id>/questions", methods=["GET"])
    def retrieve_questions_by_category(category_id):
        try:
            all_categories = Category.query.all()
            formatted_cat = {cat.id: cat.type for cat in all_categories}
                    
            if category_id not in formatted_cat:
                return not_found(404) 
            current_category = formatted_cat[category_id]
          
            selection = Question.query.filter(Question.category == category_id).order_by(Question.id).all()
            
            print(f"selection:{selection}")
            if len(selection) == 0:
                return not_found(404) 
            
            questions = paginate_questions(request, selection)

            response = {
                "questions": questions,
                "total_questions": len(selection),
                "current_category": current_category,
            }
            return jsonify(response)
        except Exception as ex:
            print(ex)
            print(sys.exc_info())

    # GET Questions based on current Category and previous questions and randomize next question
    @app.route("/quizzes", methods=["POST"])
    def play_quiz():
        try:
            quiz_request = request.get_json()
         
            previous_questions = quiz_request["previous_questions"]
            current_category_id = quiz_request["quiz_category"]["id"]
          
            if current_category_id == 0:
                questions_in_category = db.session.query(Question.id).all()
            else:
                questions_in_category = (
                    db.session.query(Question.id)
                    .filter(Question.category == current_category_id).filter(~Question.id.in_(previous_questions))
                    .all()
                )
                if len(questions_in_category)==0:
                    return bad_request(400)
               
            flat_question_in_cat = [
                i for sub in questions_in_category for i in sub
            ]         

            if len(flat_question_in_cat) == 0:
                response = {"question": None}
            else:
                new_question_id = random.choice(flat_question_in_cat)
                question = db.session.get(Question, new_question_id)
                response = {"question": question.format()}                
            return jsonify(response)
        except Exception as ex:
            print(ex)            
            print(sys.exc_info())

    # Error Handling
    @app.errorhandler(404)
    def not_found(error):
        return (
            jsonify(
                {
                    "success": False,
                    "error": 404,
                    "message": "resource not found",
                }
            ),
            404,
        )

    @app.errorhandler(422)
    def unprocessable(error):
        return (
            jsonify(
                {"success": False, "error": 422, "message": "unprocessable"}
            ),
            422,
        )

    @app.errorhandler(400)
    def bad_request(error):
        return (
            jsonify({"success": False, "error": 400, "message": "bad request"}),
            400,
        )

    @app.errorhandler(405)
    def method_not_allowed(error):
        return (
            jsonify(
                {
                    "success": False,
                    "error": 405,
                    "message": "method not allowed",
                }
            ),
            405,
        )
    
    @app.errorhandler(500)
    def internal_server_error(error):
        return (
            jsonify(
                {
                    "success": False,
                    "error": 500,
                    "message": "internal server error",
                }
            ),
            500,
        )

    return app
