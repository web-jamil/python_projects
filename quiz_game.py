import json
import random
import time
from typing import List, Dict, Optional

class Question:
    def __init__(self, text: str, answer: str, options: List[str] = None, 
                 category: str = "General", difficulty: str = "Medium"):
        self.text = text
        self.answer = answer
        self.options = options if options else []
        self.category = category
        self.difficulty = difficulty
    
    def to_dict(self) -> Dict:
        return {
            "text": self.text,
            "answer": self.answer,
            "options": self.options,
            "category": self.category,
            "difficulty": self.difficulty
        }
    
    @classmethod
    def from_dict(cls, data: Dict):
        return cls(
            text=data["text"],
            answer=data["answer"],
            options=data.get("options", []),
            category=data.get("category", "General"),
            difficulty=data.get("difficulty", "Medium")
        )

class QuizGame:
    def __init__(self):
        self.questions: List[Question] = []
        self.current_question: Optional[Question] = None
        self.score = 0
        self.total_questions = 0
        self.current_index = 0
        self.player_name = ""
        self.quiz_start_time = 0
        self.quiz_end_time = 0
        self.load_questions()
    
    def load_questions(self, filename: str = "questions.json"):
        try:
            with open(filename, "r") as file:
                data = json.load(file)
                self.questions = [Question.from_dict(q) for q in data]
        except FileNotFoundError:
            # Default questions if file doesn't exist
            self.questions = [
                Question(
                    text="What is the capital of France?",
                    answer="Paris",
                    options=["London", "Berlin", "Paris", "Madrid"],
                    category="Geography",
                    difficulty="Easy"
                ),
                Question(
                    text="Is Python an interpreted language?",
                    answer="True",
                    options=["True", "False"],
                    category="Programming",
                    difficulty="Easy"
                ),
                Question(
                    text="What is 2 + 2 * 2?",
                    answer="6",
                    category="Math",
                    difficulty="Medium"
                )
            ]
            self.save_questions()
    
    def save_questions(self, filename: str = "questions.json"):
        with open(filename, "w") as file:
            json.dump([q.to_dict() for q in self.questions], file, indent=2)
    
    def add_question(self, question: Question):
        self.questions.append(question)
        self.save_questions()
    
    def start_quiz(self, player_name: str, num_questions: int = 5, 
                  categories: List[str] = None, difficulty: str = None):
        self.player_name = player_name
        self.score = 0
        self.current_index = 0
        self.quiz_start_time = time.time()
        
        # Filter questions based on criteria
        filtered_questions = self.questions
        if categories:
            filtered_questions = [q for q in filtered_questions if q.category in categories]
        if difficulty:
            filtered_questions = [q for q in filtered_questions if q.difficulty == difficulty]
        
        # Randomly select questions
        self.total_questions = min(num_questions, len(filtered_questions))
        self.quiz_questions = random.sample(filtered_questions, self.total_questions)
        self.next_question()
    
    def next_question(self) -> bool:
        if self.current_index < self.total_questions:
            self.current_question = self.quiz_questions[self.current_index]
            self.current_index += 1
            return True
        else:
            self.quiz_end_time = time.time()
            self.current_question = None
            return False
    
    def check_answer(self, user_answer: str) -> bool:
        if not self.current_question:
            return False
        
        # Normalize answers for comparison
        correct = user_answer.strip().lower() == self.current_question.answer.lower()
        if correct:
            self.score += 1
        return correct
    
    def get_results(self) -> Dict:
        time_taken = self.quiz_end_time - self.quiz_start_time
        return {
            "player": self.player_name,
            "score": self.score,
            "total": self.total_questions,
            "percentage": (self.score / self.total_questions) * 100 if self.total_questions > 0 else 0,
            "time_taken": round(time_taken, 2)
        }
    
    def get_question_with_options(self) -> Dict:
        if not self.current_question:
            return {}
        
        return {
            "text": self.current_question.text,
            "options": self.current_question.options,
            "has_options": len(self.current_question.options) > 0,
            "category": self.current_question.category,
            "difficulty": self.current_question.difficulty,
            "question_number": self.current_index,
            "total_questions": self.total_questions
        }

class QuizUI:
    def __init__(self):
        self.game = QuizGame()
        self.running = True
    
    def display_menu(self):
        print("\n==== QUIZ GAME ====")
        print("1. Start New Quiz")
        print("2. Add New Question")
        print("3. View All Questions")
        print("4. Exit")
    
    def start_quiz_flow(self):
        print("\n=== QUIZ SETUP ===")
        player_name = input("Enter your name: ").strip()
        
        print("\nAvailable categories:")
        categories = list(set(q.category for q in self.game.questions))
        for i, cat in enumerate(categories, 1):
            print(f"{i}. {cat}")
        
        selected_categories = []
        cat_input = input("Select categories (comma separated numbers, or leave blank for all): ")
        if cat_input:
            try:
                selected_indices = [int(i.strip()) - 1 for i in cat_input.split(",")]
                selected_categories = [categories[i] for i in selected_indices if 0 <= i < len(categories)]
            except (ValueError, IndexError):
                print("Invalid category selection. Using all categories.")
        
        difficulties = ["Easy", "Medium", "Hard"]
        print("\nDifficulty levels:")
        for i, diff in enumerate(difficulties, 1):
            print(f"{i}. {diff}")
        
        difficulty = None
        diff_input = input("Select difficulty (number, or leave blank for any): ")
        if diff_input:
            try:
                diff_index = int(diff_input) - 1
                if 0 <= diff_index < len(difficulties):
                    difficulty = difficulties[diff_index]
            except ValueError:
                print("Invalid difficulty. Using any difficulty.")
        
        num_questions = 5
        try:
            num_input = input(f"How many questions? (1-{len(self.game.questions)}, default 5): ")
            if num_input:
                num_questions = min(max(1, int(num_input)), len(self.game.questions))
        except ValueError:
            print("Invalid number. Using default 5 questions.")
        
        self.game.start_quiz(player_name, num_questions, selected_categories, difficulty)
        self.run_quiz()
    
    def run_quiz(self):
        while self.game.next_question():
            question_data = self.game.get_question_with_options()
            print(f"\nQuestion {question_data['question_number']}/{question_data['total_questions']}")
            print(f"Category: {question_data['category']} | Difficulty: {question_data['difficulty']}")
            print(f"\n{question_data['text']}")
            
            if question_data['has_options']:
                print("\nOptions:")
                for i, option in enumerate(question_data['options'], 1):
                    print(f"{i}. {option}")
                answer = input("Your answer (number or text): ")
                
                # Convert option number to text if needed
                try:
                    option_num = int(answer) - 1
                    if 0 <= option_num < len(question_data['options']):
                        answer = question_data['options'][option_num]
                except ValueError:
                    pass
            else:
                answer = input("Your answer: ")
            
            if self.game.check_answer(answer):
                print("Correct!")
            else:
                print(f"Wrong! The correct answer is: {self.game.current_question.answer}")
        
        results = self.game.get_results()
        print("\n=== QUIZ RESULTS ===")
        print(f"Player: {results['player']}")
        print(f"Score: {results['score']}/{results['total']}")
        print(f"Percentage: {results['percentage']:.1f}%")
        print(f"Time taken: {results['time_taken']} seconds")
    
    def add_question_flow(self):
        print("\n=== ADD NEW QUESTION ===")
        text = input("Question text: ").strip()
        while not text:
            print("Question text cannot be empty!")
            text = input("Question text: ").strip()
        
        answer = input("Correct answer: ").strip()
        while not answer:
            print("Answer cannot be empty!")
            answer = input("Correct answer: ").strip()
        
        options = []
        print("\nEnter options (leave blank when done):")
        while True:
            option = input(f"Option {len(options) + 1}: ").strip()
            if not option:
                break
            options.append(option)
        
        category = input("Category (default: General): ").strip() or "General"
        difficulty = input("Difficulty (Easy/Medium/Hard, default: Medium): ").strip().capitalize()
        if difficulty not in ["Easy", "Medium", "Hard"]:
            difficulty = "Medium"
        
        new_question = Question(
            text=text,
            answer=answer,
            options=options if options else None,
            category=category,
            difficulty=difficulty
        )
        self.game.add_question(new_question)
        print("Question added successfully!")
    
    def view_questions(self):
        print("\n=== ALL QUESTIONS ===")
        print(f"Total questions: {len(self.game.questions)}")
        for i, question in enumerate(self.game.questions, 1):
            print(f"\nQuestion {i}: {question.text}")
            print(f"Category: {question.category} | Difficulty: {question.difficulty}")
            print(f"Answer: {question.answer}")
            if question.options:
                print("Options:")
                for j, option in enumerate(question.options, 1):
                    print(f"  {j}. {option}")
    
    def run(self):
        while self.running:
            self.display_menu()
            choice = input("Enter your choice: ").strip()
            
            if choice == "1":
                self.start_quiz_flow()
            elif choice == "2":
                self.add_question_flow()
            elif choice == "3":
                self.view_questions()
            elif choice == "4":
                print("Thanks for playing!")
                self.running = False
            else:
                print("Invalid choice. Please try again.")

if __name__ == "__main__":
    ui = QuizUI()
    ui.run()