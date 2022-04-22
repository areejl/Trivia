import os
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import random

from models import setup_db, Question, Category

QUESTIONS_PER_PAGE = 10

def create_app(test_config=None):
  # create and configure the app
    app = Flask(__name__)
    setup_db(app)
  

  # @TODO: Set up CORS. Allow '*' for origins. Delete the sample route after completing the TODOs

    CORS(app, resources={'/questions': {'origins': '*'},
        '/categories': {'origins': '*'},
        '/categories/<int:id>/questions': {'origins': '*'},
        '/questions/<int:id>': {'origins': '*'},
        '/question/search': {'origins': '*'},
        '/quizzes': {'origins': '*'},

    })
  # '''
  # @TODO: Use the after_request decorator to set Access-Control-Allow
  # '''
    @app.after_request
    def afterRequest(response):
        response.headers.add('Access-Control-Allow-Origin', '*')
        response.headers.add('Access-Control-Allow-Headers',
                             'Content-Type, application/json')
        response.headers.add(
            'Access-Control-Allow-Methods', 'GET, POST, DELETE')
        return response

    def num_questions(questions, request):
        page = request.args.get('page', 1, type=int)
        startingIndex = (page - 1) * QUESTIONS_PER_PAGE
        endingIndex = startingIndex + QUESTIONS_PER_PAGE
        formattedQ = []
        for question in questions:
            formattedQ.append(question.format())
        categories = Category.query.order_by(Category.id).all()

        return jsonify({
            'success': True,
            'questions':
            formattedQ[startingIndex:endingIndex],
            'total_questions':
            len(formattedQ[startingIndex:endingIndex]),
            'categories':
            {category.id: category.type for category in categories},
            'current_category': 'all'}), 200
# '''
#   @TODO: 
#   Create an endpoint to handle GET requests 
#   for all available categories.
# '''
    @ app.route('/categories', methods=['GET'])
    def get_categories():
        categories = Category.query.order_by(Category.id).all()
        formattedCg = {}
        for category in categories:
            formattedCg[int(category.id)] = category.type
        return jsonify(
            {
                'success': True,
                'categories': formattedCg
            }), 200
# '''
#   @TODO: 
#   Create an endpoint to handle GET requests for questions, 
#   including pagination (every 10 questions). 
#   This endpoint should return a list of questions, 
#   number of total questions, current category, categories. 

#   TEST: At this point, when you start the application
#   you should see questions and categories generated,
#   ten questions per page and pagination at the bottom of the screen for three pages.
#   Clicking on the page numbers should update the questions. 
#   '''
    @ app.route('/questions', methods=['GET'])
    def get_Questions():
        questions = Question.query.all()
        questionsJSON = num_questions(questions, request)
        return questionsJSON
# '''
#   @TODO: 
#   Create an endpoint to DELETE question using a question ID. 

#   TEST: When you click the trash icon next to a question, the question will be removed.
#   This removal will persist in the database and when you refresh the page. 
#   '''
    @ app.route('/questions/<int:Q_id>', methods=['DELETE'])
    def delete_Questions(Q_id):
        try:
            question = Question.query.get(Q_id)
            question.delete()
            return jsonify({'success': True}), 200
        except:
            abort(422)
# '''
#   @TODO: 
#   Create an endpoint to POST a new question, 
#   which will require the question and answer text, 
#   category, and difficulty score.

#   TEST: When you submit a question on the "Add" tab, 
#   the form will clear and the question will appear at the end of the last page
#   of the questions list in the "List" tab.  
# '''
    @app.route("/questions", methods=['POST'])
    def add_question():
        try:
            post_req = request.get_json()
            question = post_req['question']
            answer = post_req['answer']
            difficulty = post_req['difficulty']
            category = post_req['category']
            question = Question(
                question=question,
                answer=answer,
                category=category, difficulty=difficulty)
            question.insert()
        except:
            abort(422)
        return jsonify({'success': True,
                        'created': question.id}), 200
# '''
#   @TODO: 
#   Create a POST endpoint to get questions based on a search term. 
#   It should return any questions for whom the search term 
#   is a substring of the question. 

#   TEST: Search by any phrase. The questions list will update to include 
#   only question that include that string within their question. 
#   Try using the word "title" to start. 
# '''
    @app.route('/questions/search', methods=['POST'])
    def search_questions():
        search_req = request.get_json()
        search_Term = search_req.get('searchTerm', None)

        if search_Term:
            search_results = Question.query.filter(Question.question.ilike('%' + search_Term + '%')).all()

        return jsonify({'success': True,
                        'questions': [question.format() for question in search_results],
                        'total_questions': len(search_results),
                        'current_category': None}), 200

# '''
#   @TODO: 
#   Create a GET endpoint to get questions based on category. 

#   TEST: In the "List" tab / main screen, clicking on one of the 
#   categories in the left column will cause only questions of that 
#   category to be shown. 
# '''
    @app.route('/categories/<int:categoryID>/questions', methods=['GET'])
    def questions_ByCateg(categoryID):
        try:
            questions = Question.query.filter(
            Question.category == str(categoryID)).all()

            return jsonify({
                'success': True,
                'questions': [question.format() for question in questions],
                'total_questions': len(questions),
                'current_category': categoryID
            })
        except:
            abort(404)

# '''
#   @TODO: 
#   Create a POST endpoint to get questions to play the quiz. 
#   This endpoint should take category and previous question parameters 
#   and return a random questions within the given category, 
#   if provided, and that is not one of the previous questions. 

#   TEST: In the "Play" tab, after a user selects "All" or a category,
#   one question at a time is displayed, the user is allowed to answer
#   and shown whether they were correct or not. 
# '''
    @app.route('/quizzes', methods=['POST'])
    def play():
        play_req = request.get_json()
        quiz_category = play_req.get('quiz_category')
        previousQ = play_req.get('previous_questions')
        if int(quiz_category['id']) > len(Category.query.all()):
            abort(404)
        questions = None
        if len(Question
               .query
               .filter_by(category=int(quiz_category['id']))
               .all()) == 0:
            questions = Question.query.all()
        else:
            questions = Question.query.filter_by(
                category=int(quiz_category['id']))

        formattedQ = []
        for q in questions:
            if (not(q.id in previousQ)):
                formattedQ.append(q.format())

        if len(formattedQ) == 0:
            return jsonify(
                {'success': True, 'question': False}), 200
        else:
            return jsonify(
                {'success': True, 'question':
                 formattedQ[random.randint(
                     0, len(formattedQ) - 1)],
                 }), 200
# '''
#   @TODO: 
#   Create error handlers for all expected errors 
#   including 404 and 422. 
# ''' 
    @app.errorhandler(400)
    def bad_request(error):
        return jsonify({
            "success": False,
            "status-code": 400,
            "message": "Bad request"}), 400

    @app.errorhandler(404)
    def notfound(error):
        return jsonify({
            "success": False,
            "status-code": 404,
            "message": "resource not found"}), 404
    @app.errorhandler(405)
    def NotAllowed(error):
        return jsonify(
            {"success": False,
             "status-code": 405,
             "message": "Method not allowed"}), 405
    @app.errorhandler(422)
    def unprocessable(error):
        return jsonify({
             "success":False,
             "status-code":422,
             "message":"unprocessable"}),422  

    return app

    