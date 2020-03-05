from rest_framework import serializers
from api.models import TestSheetModel, QuestionModel, AnswerModel, TutorialModel, ExerciseModel
from api.serializers.tutorial import TutorialSerializer
from api.serializers.exercise import ExerciseSerializer


class TestSheetSerializer(serializers.ModelSerializer):
    exercise = ExerciseSerializer(many=True)
    tutorial = TutorialSerializer(many=True)

    def create(self, validated_data):
        tutorial_data = validated_data.pop('tutorial')
        exercise_data = validated_data.pop('exercise')
        test_sheet = TestSheetModel.objects.create(author_id=validated_data['author'].id,
                                                   classroom_id=validated_data['classroom'].id, **validated_data)
        for t in tutorial_data:
            TutorialModel.objects.create(test_sheet_id=test_sheet.id, **t)
        for e in exercise_data:
            question_data = e.pop('questions')
            exercise = ExerciseModel.objects.create(test_sheet_id=test_sheet.id, **e)
            for q in question_data:
                answer_data = q.pop('answer')
                question = QuestionModel.objects.create(exercise_id=exercise.id, **q)
                for a in answer_data:
                    AnswerModel.objects.create(question_id=question.id, **a)
        return test_sheet

    def update(self, instance, validated_data):
        tutorials_data = validated_data.pop('tutorial')
        exercises_data = validated_data.pop('exercise')

        exercises = (instance.exercise).all()
        exercises = list(exercises)
        exercise_instance = ExerciseModel.objects.get(test_sheet_id=instance.id)

        tutorials = (instance.tutorial).all()
        tutorials = list(tutorials)

        instance.author_id = validated_data.get('author_id', instance.author_id)
        instance.classroom_id = validated_data.get('classroom_id', instance.classroom_id)
        instance.name = validated_data.get('name', instance.name)
        instance.difficulty = validated_data.get('difficulty', instance.difficulty)
        instance.save()

        for tutorial_data in tutorials_data:
            tutorial = tutorials.pop(0)
            tutorial.name = tutorial_data.get('name', tutorial.name)
            tutorial.content = tutorial_data.get('content', tutorial.content)
            tutorial.save()

        for exercise_data in exercises_data:
            questions_data = exercise_data.pop('questions')
            questions = exercise_instance.questions.all()
            questions = list(questions)
            question_instance = QuestionModel.objects.get(exercise_id=exercise_instance.id)
            exercise = exercises.pop(0)
            exercise.name = exercise_data.get('name', exercise.name)
            exercise.material_url = exercise_data.get('material_url', exercise.material_url)
            exercise.save()

            for q in questions_data:
                answer_data = q.pop('answer')
                answers = question_instance.answer.all()
                answers = list(answers)

                question = questions.pop(0)
                question.name = q.get('name', question.name)
                question.time_point = q.get('time_point', question.time_point)
                question.max_score = q.get('max_score', question.max_score)
                question.save()

                for a in answer_data:
                    # answers = AnswerModel.objects.filter(question_id=question_instance.id)
                    answer = answers.pop(0)
                    answer.name = a.get('name', answer.name)
                    answer.is_correct = a.get('is_correct', answer.is_correct)
                    answer.save()

        return instance

    class Meta:
        model = TestSheetModel
        fields = ['id', 'name', 'author', 'classroom', 'difficulty', 'tutorial', 'exercise']
