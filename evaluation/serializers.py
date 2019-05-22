from rest_framework import serializers
import evaluation.models


class TajweedEvaluationSerializer(serializers.ModelSerializer):
    class Meta:
        model = evaluation.models.TajweedEvaluation
        fields = '__all__'


class EvaluationSerializer(serializers.ModelSerializer):
    class Meta:
        model = evaluation.models.Evaluation
        fields = '__all__'

    def validate_session_id(self, value):
        """Field level validation for session ID string."""
        if value is None or value == '':
            raise serializers.ValidationError("Session ID cannot be null/empty string.")
        return value

    def create(self, validated_data):
        defaults = {'session_id': validated_data.get('session_id', None),
                    'platform': validated_data.get('platform', None),
                    'evaluation': validated_data.get('evaluation', None),
                    'associated_recording': validated_data.get('associated_recording', None)}
        eval_obj, created = evaluation.models.Evaluation.objects.update_or_create(
                associated_recording=validated_data.get('associated_recording', None),
                defaults=defaults
        )
        print("Evaluation created: {}".format(created))
        return eval_obj
