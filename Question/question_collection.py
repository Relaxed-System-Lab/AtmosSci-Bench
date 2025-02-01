""" This is the question collections file. It contains a list of questions that will be used for evaluation.
"""

from Questions import Question1, Question2, Question3, Question4, Question6, Question7, Question8, Question9, Question10, Question11, Question12, Question13, Question14, Question15, Question16, Question17, Question18, Question19, Question20, Question21, Question22, Question23, Question24, Question25, Question26, Question27, Question28, Question29, Question30, Question31, Question32, Question34

from Questions import Question35, Question36, Question37, Question38, Question39, Question40, Question41, Question42, Question43, Question44, Question45, Question46, Question47, Question48, Question49, Question50, Question51, Question52, Question53, Question55, Question56, Question57, Question59, Question60, Question61, Question62, Question63, Question64, Question65, Question66, Question67, Question68, Question69, Question70, Question71, Question72, Question73, Question74, Question75, Question76, Question77, Question79, Question80


def generate_questions(question_class, base_id, seed_range):
    questions = []
    for i, seed in enumerate(seed_range, start=1):
        unique_id = f"{base_id}_{i}"
        if i==1:    # The first question is the original question
            questions.append(question_class(unique_id=unique_id))
        else:
            questions.append(question_class(unique_id=unique_id, seed=seed))
    return questions

# ========== Settings ==========
# Generate questions with seed range from 999 to 1002, ID pattern is q{id}_{seed}
# INSTANCE_SIZE = 10
# How many instances (INSTANCE_SIZE) of each question to generate
INSTANCE_SIZE = 10
# ===============================


START_SEED = 999
END_SEED = START_SEED + INSTANCE_SIZE
# END_SEED = 1009

# question_collection = generate_questions(Question1, "q1", range(START_SEED, END_SEED))

question_collection = generate_questions(Question1, "q1", range(START_SEED, END_SEED)) + \
                        generate_questions(Question2, "q2", range(START_SEED, END_SEED)) + \
                        generate_questions(Question3, "q3", range(START_SEED, END_SEED)) + \
                        generate_questions(Question4, "q4", range(START_SEED, END_SEED)) + \
                        generate_questions(Question6, "q6", range(START_SEED, END_SEED)) + \
                        generate_questions(Question8, "q8", range(START_SEED, END_SEED)) + \
                        generate_questions(Question9, "q9", range(START_SEED, END_SEED)) + \
                        generate_questions(Question10, "q10", range(START_SEED, END_SEED)) + \
                        generate_questions(Question11, "q11", range(START_SEED, END_SEED)) + \
                        generate_questions(Question12, "q12", range(START_SEED, END_SEED)) + \
                        generate_questions(Question13, "q13", range(START_SEED, END_SEED)) + \
                        generate_questions(Question14, "q14", range(START_SEED, END_SEED)) + \
                        generate_questions(Question15, "q15", range(START_SEED, END_SEED)) + \
                        generate_questions(Question16, "q16", range(START_SEED, END_SEED)) + \
                        generate_questions(Question17, "q17", range(START_SEED, END_SEED)) + \
                        generate_questions(Question18, "q18", range(START_SEED, END_SEED)) + \
                        generate_questions(Question19, "q19", range(START_SEED, END_SEED)) + \
                        generate_questions(Question20, "q20", range(START_SEED, END_SEED)) + \
                        generate_questions(Question21, "q21", range(START_SEED, END_SEED)) + \
                        generate_questions(Question22, "q22", range(START_SEED, END_SEED)) + \
                        generate_questions(Question23, "q23", range(START_SEED, END_SEED)) + \
                        generate_questions(Question24, "q24", range(START_SEED, END_SEED)) + \
                        generate_questions(Question25, "q25", range(START_SEED, END_SEED)) + \
                        generate_questions(Question26, "q26", range(START_SEED, END_SEED)) + \
                        generate_questions(Question27, "q27", range(START_SEED, END_SEED)) + \
                        generate_questions(Question28, "q28", range(START_SEED, END_SEED)) + \
                        generate_questions(Question29, "q29", range(START_SEED, END_SEED)) + \
                        generate_questions(Question30, "q30", range(START_SEED, END_SEED)) + \
                        generate_questions(Question31, "q31", range(START_SEED, END_SEED)) + \
                        generate_questions(Question32, "q32", range(START_SEED, END_SEED)) + \
                        generate_questions(Question34, "q34", range(START_SEED, END_SEED)) + \
                        generate_questions(Question35, "q35", range(START_SEED, END_SEED)) + \
                        generate_questions(Question36, "q36", range(START_SEED, END_SEED)) + \
                        generate_questions(Question37, "q37", range(START_SEED, END_SEED)) + \
                        generate_questions(Question38, "q38", range(START_SEED, END_SEED)) + \
                        generate_questions(Question39, "q39", range(START_SEED, END_SEED)) + \
                        generate_questions(Question40, "q40", range(START_SEED, END_SEED)) + \
                        generate_questions(Question41, "q41", range(START_SEED, END_SEED)) + \
                        generate_questions(Question42, "q42", range(START_SEED, END_SEED)) + \
                        generate_questions(Question45, "q45", range(START_SEED, END_SEED)) + \
                        generate_questions(Question46, "q46", range(START_SEED, END_SEED)) + \
                        generate_questions(Question47, "q47", range(START_SEED, END_SEED)) + \
                        generate_questions(Question48, "q48", range(START_SEED, END_SEED)) + \
                        generate_questions(Question49, "q49", range(START_SEED, END_SEED)) + \
                        generate_questions(Question50, "q50", range(START_SEED, END_SEED)) + \
                        generate_questions(Question51, "q51", range(START_SEED, END_SEED)) + \
                        generate_questions(Question52, "q52", range(START_SEED, END_SEED)) + \
                        generate_questions(Question55, "q55", range(START_SEED, END_SEED)) + \
                        generate_questions(Question56, "q56", range(START_SEED, END_SEED)) + \
                        generate_questions(Question59, "q59", range(START_SEED, END_SEED)) + \
                        generate_questions(Question60, "q60", range(START_SEED, END_SEED)) + \
                        generate_questions(Question61, "q61", range(START_SEED, END_SEED)) + \
                        generate_questions(Question63, "q63", range(START_SEED, END_SEED)) + \
                        generate_questions(Question64, "q64", range(START_SEED, END_SEED)) + \
                        generate_questions(Question65, "q65", range(START_SEED, END_SEED)) + \
                        generate_questions(Question66, "q66", range(START_SEED, END_SEED)) + \
                        generate_questions(Question67, "q67", range(START_SEED, END_SEED)) + \
                        generate_questions(Question69, "q69", range(START_SEED, END_SEED)) + \
                        generate_questions(Question70, "q70", range(START_SEED, END_SEED)) + \
                        generate_questions(Question71, "q71", range(START_SEED, END_SEED)) + \
                        generate_questions(Question72, "q72", range(START_SEED, END_SEED)) + \
                        generate_questions(Question74, "q74", range(START_SEED, END_SEED)) + \
                        generate_questions(Question75, "q75", range(START_SEED, END_SEED)) + \
                        generate_questions(Question76, "q76", range(START_SEED, END_SEED)) + \
                        generate_questions(Question77, "q77", range(START_SEED, END_SEED)) + \
                        generate_questions(Question79, "q79", range(START_SEED, END_SEED)) + \
                        generate_questions(Question80, "q80", range(START_SEED, END_SEED))


# Error Questions: q5, q7, q33, q43, q44, q53, q54, q57, q58, q62, q68, q73, q78