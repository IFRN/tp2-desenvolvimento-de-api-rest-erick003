from rest_framework import serializers
from .models import Eleitor, Eleicao, Candidato, Voto, AptidaoLeitor, RegistroVotacao

class EleitorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Eleitor
        fields = '__all__'

class EleicaoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Eleicao
        fields = '__all__'

class CandidatoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Candidato
        fields = '__all__'

class VotoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Voto
        fields = '__all__'

class AptidaoLeitorSerializer(serializers.ModelSerializer):
    class Meta:
        model = AptidaoLeitor
        fields = '__all__'

class VotacaoInputSerializer(serializers.Serializer):
    eleicao_id = serializers.IntegerField()
    candidato_id = serializers.IntegerField(required=False, allow_null=True)
    eleitor_cpf = serializers.CharField(max_length=14)
    em_branco = serializers.BooleanField(default=False)