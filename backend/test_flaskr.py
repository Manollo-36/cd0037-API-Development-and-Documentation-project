from http.client import NETWORK_AUTHENTICATION_REQUIRED
import os
import unittest
import json
from flaskr import create_app
from models import db, Question, Category


class TriviaTestCase(unittest.TestCase):
    """This class represents the trivia test case"""

    def setUp(self):
        """Define test variables and initialize app."""
        self.database_name = "trivia_test"
        self.database_user = "postgres"        
        self.database_password = "password"
        self.database_host = "localhost:5432"
        self.database_path = f"postgresql://{self.database_user}:{self.database_password}@{self.database_host}/{self.database_name}"

        # Create app with the test configuration
        self.app = create_app({
            "SQLALCHEMY_DATABASE_URI": self.database_path,
            "SQLALCHEMY_TRACK_MODIFICATIONS": False,
            "TESTING": True
        })
        self.client = self.app.test_client

        self.new_question ={"question":"Why did the Titanic sink?","answer":"Hit an ice berg", "category": 4,"difficulty":2}
        self.bad_question ={"questions":"Why did the Titanic sink?","answer":"Hit an ice berg", "category": 4,"difficulty":3}
        self.good_search_question = {"searchTerm":"title"}
        self.bad_search_question ={"searchTerm":"Jo"}
        self.good_play_quiz ={"previous_questions": [1],"quiz_category":{ "id":1}}
        self.bad_play_quiz = {"previous_questions": [1],"quiz_category":{ "id":7}}

        # Bind the app to the current context and create all tables
        self.cxt = self.app.app_context()
        self.cxt.push()     
        db.create_all()

        

    def tearDown(self):
        """Executed after each test"""
        with self.app.app_context():
            db.session.remove()
            #db.drop_all()

    """
    TODO
    Write at least one test for each test for successful operation and for expected errors.
    """

    
    #GET Categories

    def test_get_categories(self):
        res = self.client().get("/categories")        
        data = json.loads(res.data)
        print(f'Data:{res.data}')
        self.assertEqual(res.status_code, 200)
        self.assertTrue(data["categories"])
        self.assertTrue(len(data["categories"]))

    def test_404_get_categories(self):
        res = self.client().get("/category")        
        data = json.loads(res.data)
        print(f'Data:{res.data}')
        self.assertEqual(res.status_code, 404)
        self.assertEqual(data["success"], False)
        self.assertEqual(data["message"], "resource not found")

    # GET Questions

    def test_200_get_questions(self):
        res = self.client().get("/questions")    
        print(f'Data:{res.data}')   
        data = json.loads(res.data)
        print(f'Data:{data}')
        self.assertEqual(res.status_code, 200)
        self.assertTrue(data["total_questions"])
        self.assertTrue(data["categories"])
        self.assertTrue(len(data["questions"]))

    def test_404_get_questions(self):
        res = self.client().get("/question")    
        print(f'Data:{res.data}')   
        data = json.loads(res.data)
        print(f'Data:{data}')
        self.assertEqual(res.status_code, 404)
        self.assertEqual(data["success"], False)
        self.assertEqual(data["message"], "resource not found")
    
   
    #GET Question By Category

    def test_200_get_questions_by_category_id(self):
        res = self.client().get("/categories/2/questions")    
        print(f'Data:{res.data}')   
        data = json.loads(res.data)
        print(f'Data:{data}')
        self.assertEqual(res.status_code, 200)
        self.assertTrue(data["total_questions"])
        self.assertTrue(data["current_category"])
        self.assertTrue(len(data["questions"]))

    def test_404_get_questions_by_category_id(self):
        res = self.client().get("/categories/7/questions")    
        print(f'Data:{res.data}')   
        data = json.loads(res.data)
        print(f'Data:{data}')
        self.assertEqual(res.status_code, 404)
        self.assertEqual(data["success"], False)
        self.assertEqual(data["message"], "resource not found")


    #Paging

    def test_200_sent_requesting_valid_page(self):
        res = self.client().get("/questions?page=1")
        #print(f'res_Data:{res.data}')   
        data = json.loads(res.data)
        #print(f'Data:{data}')   
        self.assertEqual(res.status_code, 200)
        self.assertTrue(data["questions"])
        self.assertTrue(data["total_questions"])
        self.assertTrue(data["categories"])
                       

    def test_404_sent_requesting_beyond_valid_page(self):
        res = self.client().get("/questions?page=1000")
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 404)
        self.assertEqual(data["success"], False)
        self.assertEqual(data["message"], "resource not found")

    # Add Question

    def test_200_post_questions_add(self):        
        res = self.client().post("/questions", 
        json=self.new_question)    
        #print(f'Data:{res.data}')   
        data = json.loads(res.data)
        #print(f'Data:{data}')
        self.assertEqual(res.status_code, 200)
        self.assertTrue(data["created"])
        self.assertTrue(data["question"])


    def test_405_post_questions_add(self):
        res = self.client().post("/questions/100", 
        json= self.bad_question)   
        #print(f'Data:{res.data}')   
        data = json.loads(res.data)
        #print(f'Data:{data}')
        self.assertEqual(res.status_code, 405)
        self.assertEqual(data["success"], False)
        self.assertEqual(data["message"], "method not allowed")  

   
    #Search Question

    def test_200_post_questions_search(self):
        res = self.client().post("/questions", 
        json=self.good_search_question)    
        #print(f'Data:{res.data}')   
        data = json.loads(res.data)
        #print(f'Data:{data}')
        self.assertEqual(res.status_code, 200)
        self.assertTrue(data["questions"])

    def test_200_post_questions_search_without_results(self):
        res = self.client().post("/questions", 
        json=self.bad_search_question)    
        #print(f'Data:{res.data}')   
        data = json.loads(res.data)
        #print(f'Data:{data}')
        self.assertEqual(res.status_code, 200)
        self.assertEqual(len(data["questions"]),0)
            

    #Delete Question
    def test_200_delete_questions(self):
        res = self.client().delete("/questions/3")    
        #print(f'Data:{res.data}')   
        data = json.loads(res.data)
        question = Question.query.filter(Question.id == 3).one_or_none()
        #print(f'question:{question}')
        self.assertEqual(res.status_code, 200)
        self.assertTrue(data["success"])
        self.assertTrue(data["deleted"],2)
        self.assertTrue(data["question"])
        self.assertEqual(question, None)

    def test_404_delete_questions(self):
        res = self.client().delete("/questions/100")    
        #print(f'Data:{res.data}')   
        data = json.loads(res.data)
        #print(f'Data:{data}')
        self.assertEqual(res.status_code, 404)
        self.assertEqual(data["success"], False)
        self.assertEqual(data["message"], "resource not found")    


    #POST Quiz

    def test_200_quiz(self):
        res = self.client().post("/quizzes",json=self.good_play_quiz)    
        #print(f'Data:{res.data}')   
        data = json.loads(res.data)
        #print(f'Data:{data}')
        self.assertEqual(res.status_code, 200)
        self.assertTrue(data["question"])
        self.assertTrue(len(data["question"]))

    def test_400_quiz(self):
        res = self.client().post("/quizzes",json=self.bad_play_quiz)    
        #print(f'Data:{res.data}')   
        data = json.loads(res.data)
        #print(f'Data:{data}')
        self.assertEqual(res.status_code, 400)
        self.assertEqual(data["success"], False)
        self.assertEqual(data["message"], "bad request")



# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()
