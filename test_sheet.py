from rest_framework import serializers
from api.models import TestSheetModel, QuestionModel, AnswerModel, TutorialModel, ExerciseModel
from api.serializers.tutorial import TutorialSerializer
from api.serializers.exercise import ExerciseSerializer


class TestSheetSerializer(serializers.ModelSerializer):
    exercise = ExerciseSerializer(many=True, read_only=False)
    tutorial = TutorialSerializer(many=True, read_only=False)

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

        instance.author_id = validated_data.get('author_id', instance.author_id)
        instance.classroom_id = validated_data.get('classroom_id', instance.classroom_id)
        instance.name = validated_data.get('name', instance.name)
        instance.difficulty = validated_data.get('difficulty', instance.difficulty)
        instance.save()

        for tutorial_data in tutorials_data:
            tutorial = TutorialModel.objects.filter(id=tutorial_data['id'])
            tutorial.update(**tutorial_data)

        for exercise_data in exercises_data:
            questions_data = exercise_data.pop('questions')
            exercise = ExerciseModel.objects.filter(id=exercise_data['id'])
            exercise.update(**exercise_data)

            for question_data in questions_data:
                answers_data = question_data.pop('answer')
                question = QuestionModel.objects.filter(id=question_data['id'])
                question.update(**question_data)

                for answer_data in answers_data:
                    answer = AnswerModel.objects.filter(id=answer_data['id'])
                    answer.update(**answer_data)

        return instance

    class Meta:
        model = TestSheetModel
        fields = ['id', 'name', 'author', 'classroom', 'difficulty', 'tutorial', 'exercise']
