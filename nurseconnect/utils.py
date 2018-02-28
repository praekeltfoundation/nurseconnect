import datetime


def get_period_date_format():
    """
    Returns the current year and month concatenated into a string

    e.g.
    datetime.date(2018, 2, 1) -> 201802
    datetime.date(2012, 11, 29) -> 201211
    """
    return datetime.date.today().strftime('%Y%m')


def convert_string_to_boolean_list(string):
    '''
    Return a list of boolean values from a string of 'true'
    and 'false', separated by commas.
    '''
    values = []
    for answer in string.split(","):
        ans = answer.strip().lower()
        if(ans == "true"):
            values.append(True)
        elif(ans == "false"):
            values.append(False)
        else:
            pass

    return values


def get_survey_results_for_user(survey, user):
    '''
    Return a list of survey results for a user in the following format:
    [
        {
            question": question_text,
            "user_answer": True/False,
            "correct_answer": True/False,
        },
        { ... },
    ]

    Return None if the user has not submitted a survey

    NOTE: This currently only works for Radio Buttons with True/False
    and uses a hack where data stored in the survey thank you text will
    store true, false string values seperated by commas.
    '''
    try:
        submission = (survey.get_submission_class()
                            .objects.get(page=survey, user=user))

        # This is a hack, that uses answers of "true" or "false"
        # seperated by commas in the thank you text field of a survey
        clean_answer_key = convert_string_to_boolean_list(
            survey.thank_you_text)

        questions = [(field.clean_name, field.label)
                     for field in survey.get_form_fields()]
        if (len(clean_answer_key) != len(questions)):
            raise Exception("Incorrectly configured survey, check thank"
                            " you text and number of questions asked")

        user_answers = submission.get_data()

        answers = []
        for question_info, correct_answer in zip(questions, clean_answer_key):
            key, question_text = question_info
            actual_user_answer = user_answers[key]
            answers.append({
                "question": question_text,
                "user_answer": (True
                                if actual_user_answer.lower() == "true"
                                else False),
                "correct_answer": correct_answer,
            })
        return answers
    except survey.get_submission_class().DoesNotExist:
        return None
