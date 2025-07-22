import random
import HardQuestions as HardQ
import EasyQuestions as EasyQ
import MidQuestions as MidQ


def run_quiz(level, num_questions=20):
    # Randomly select 20 questions (or fewer if not enough are available)
    if level=="easy":
        questions=EasyQ.plant_questions
    elif level=="mid":
        questions=MidQ.plant_questions
    elif level=="hard":
        questions=HardQ.plant_questions
        
    selected_questions = random.sample(questions, min(num_questions, len(questions)))

    score = 0
    results = []

    print("🌱 Welcome to the Plant Quiz! 🌱")
    print(f"🌱 Here is your {level} quiz! 🌱\n")
    
    for i, q in enumerate(selected_questions, 1):
        print(f"Question {i}: {q['question']}")
        for key, value in q['answers'].items():
            print(f"  {key}) {value}")
        
        user_answer = input("Your answer (a/b/c/d): ").strip().lower()
        correct_answer = q['correct_answer']
        is_correct = user_answer == correct_answer
        results.append({
            'question': q['question'],
            'user_answer': user_answer,
            'correct_answer': correct_answer,
            'correct': is_correct,
            'correct_text':q['answers'][q['correct_answer']]
        })

        if is_correct:
            print("✅ Correct!\n")
            score += 1
        else:
            print(f"❌ Incorrect. The correct answer was '{correct_answer}'.\n")

    print("\n📊 Quiz Completed!")
    print(f"You scored {score} out of {len(selected_questions)}.\n")

    print("📝 Detailed Results:")
    for idx, res in enumerate(results, 1):
        status = "✅ Correct" if res['correct'] else f"❌ Wrong Correct: {res['correct_answer']}"
        print(f"{idx}. {res['question']}\n   Your Answer: '{res['user_answer']}' | Status: {status} - {res['correct_text']}\n")

run_quiz("easy")
  