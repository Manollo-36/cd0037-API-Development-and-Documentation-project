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
        self.database_user = "Emmanuel"        
        self.database_password = "Manos"
        self.database_host = "localhost:5432"
        self.database_path = f"postgresql://{self.database_user}:{self.database_password}@{self.database_host}/{self.database_name}"

        # Create app with the test configuration
        self.app = create_app({
            "SQLALCHEMY_DATABASE_URI": self.database_path,
            "SQLALCHEMY_TRACK_MODIFICATIONS": False,
            "TESTING": True
        })
        self.client = self.app.test_client

        # Bind the app to the current context and create all tables
        with self.app.app_context():
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
    # def test_get_categories(self):
    #     res = self.client().get("/categories")        
    #     data = json.loads(res.data)
    #     print(f'Data:{res.data}')
    #     self.assertEqual(res.status_code, 200)
    #     self.assertTrue(data["categories"])
    #     self.assertTrue(len(data["categories"]))

    # def test_404_get_categories(self):
    #     res = self.client().get("/category",json={"id":1})        
    #     data = json.loads(res.data)
    #     print(f'Data:{res.data}')
    #     self.assertEqual(res.status_code, 404)
    #     self.assertEqual(data["success"], False)
    #     self.assertEqual(data["message"], "resource not found")

    # def test_200_sent_requesting_valid_page(self):
    #     res = self.client().get("/questions?page=1")
    #     print(f'res_Data:{res.data}')   
    #     data = json.loads(res.data)
    #     print(f'Data:{data}')   
    #     self.assertEqual(res.status_code, 200)
    #     self.assertTrue(data["questions"])
    #     self.assertTrue(data["total_questions"])
    #     self.assertTrue(data["categories"])
    #     self.assertTrue(data["current_category"])
                

    def test_500_sent_requesting_beyond_valid_page(self):
        res = self.client().get("/questions?page=1000")
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 500)
        self.assertEqual(data["success"], False)
        self.assertEqual(data["message"], "internal server error")

    # def test_get_questions(self):
    #     res = self.client().get("/questions")    
    #     print(f'Data:{res.data}')   
    #     data = json.loads(res.data)
    #     print(f'Data:{data}')
    #     self.assertEqual(res.status_code, 200)
    #     self.assertTrue(data["total_questions"])
    #     self.assertTrue(data["current_category"])
    #     self.assertTrue(len(data["questions"]))

    # def test_404_get_questions(self):
    #     res = self.client().get("/question", json={"category": 1})    
    #     print(f'Data:{res.data}')   
    #     data = json.loads(res.data)
    #     print(f'Data:{data}')
    #     self.assertEqual(res.status_code, 404)
    #     self.assertEqual(data["success"], False)
    #     self.assertEqual(data["message"], "resource not found")
    
    # def test_200_get_questions_by_category_id(self):
    #     res = self.client().get("/category/2/questions", json={"category": 1})    
    #     print(f'Data:{res.data}')   
    #     data = json.loads(res.data)
    #     print(f'Data:{data}')
    #     self.assertEqual(res.status_code, 200)
    #     self.assertTrue(data["total_questions"])
    #     self.assertTrue(data["current_category"])
    #     self.assertTrue(len(data["questions"]))

    # def test_404_get_questions_by_category_id(self):
    #     res = self.client().get("/category/2/questions", json={"category": 1})    
    #     print(f'Data:{res.data}')   
    #     data = json.loads(res.data)
    #     print(f'Data:{data}')
    #     self.assertEqual(res.status_code, 404)
    #     self.assertEqual(data["success"], False)
    #     self.assertEqual(data["message"], "resource not found")

    def test_200_delete_questions(self):
        res = self.client().delete("/questions/25")    
        print(f'Data:{res.data}')   
        data = json.loads(res.data)
        print(f'Data:{data}')
        self.assertEqual(res.status_code, 200)
        self.assertTrue(data["success"])
        self.assertTrue(data["deleted"])
        self.assertTrue(data["question"])

    def test_500_delete_questions(self):
        res = self.client().delete("/questions/100")    
        print(f'Data:{res.data}')   
        data = json.loads(res.data)
        print(f'Data:{data}')
        self.assertEqual(res.status_code, 500)
        self.assertEqual(data["success"], False)
        self.assertEqual(data["message"], "internal server error")

    # def test_200_post_questions(self):
    #     res = self.client().post("/questions", 
    #     json={"question":"Why did the Titanic sink?","answer":"Hit an ice berg", "category": 4,"difficulty":2})    
    #     print(f'Data:{res.data}')   
    #     data = json.loads(res.data)
    #     print(f'Data:{data}')
    #     self.assertEqual(res.status_code, 200)
    #     self.assertTrue(data["created"])
    #     self.assertTrue(data["question"])

    # def test_404_post_questions(self):
    #     res = self.client().post("/question", 
    #     json={"question":"Why did the Titanic sink?","answer":"Hit an ice berg", "category": 4,"difficulty":''})    
    #     print(f'Data:{res.data}')   
    #     data = json.loads(res.data)
    #     print(f'Data:{data}')
    #     self.assertEqual(res.status_code, 404)
    #     self.assertEqual(data["success"], False)
    #     self.assertEqual(data["message"], "resource not found")  
   
    # def test_post_questions_search(self):
    #     res = self.client().post("/questions", 
    #     json={"searchTerm":"title"})    
    #     print(f'Data:{res.data}')   
    #     data = json.loads(res.data)
    #     print(f'Data:{data}')
    #     self.assertEqual(res.status_code, 200)
    #     self.assertTrue(data["created"])
    #     self.assertTrue(data["question"])

    # def test_post_questions_search(self):
    #     res = self.client().post("/question", 
    #     json={"searchTerm":"Jo"})    
    #     print(f'Data:{res.data}')   
    #     data = json.loads(res.data)
    #     print(f'Data:{data}')
    #     self.assertEqual(res.status_code, 404)
    #     self.assertTrue(data["created"])
    #     self.assertTrue(data["question"])
    
    # def test_quiz(self):
    #     res = self.client().post("/quizzes",json={"previous_questions": [1],"quiz_category":{ "id":1}})    
    #     print(f'Data:{res.data}')   
    #     data = json.loads(res.data)
    #     print(f'Data:{data}')
    #     self.assertEqual(res.status_code, 200)
    #     self.assertTrue(data["question"])
    #     self.assertTrue(len(data["question"]))

    # def test_quiz(self):
    #     res = self.client().post("/quizzes",json={"previous_questions": [1],"quiz_category":{ "id":7}})    
    #     print(f'Data:{res.data}')   
    #     data = json.loads(res.data)
    #     print(f'Data:{data}')
    #     self.assertEqual(res.status_code, 404)
    #     self.assertEqual(data["success"], False)
    #     self.assertEqual(data["message"], "resource not found")

# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()
