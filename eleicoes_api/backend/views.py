from rest_framework import viewsets, filters, status
from rest_framework.views import APIView
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from django.shortcuts import get_object_or_404
import hashlib
import uuid

from .models import Eleitor, Eleicao, Candidato, Voto, RegistroVotacao
from .serializers import (
    EleitorSerializer, EleicaoSerializer, CandidatoSerializer, 
    VotoSerializer, VotacaoInputSerializer
)

class EleitorViewSet(viewsets.ModelViewSet):
    queryset = Eleitor.objects.all()
    serializer_class = EleitorSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['ativo']
    search_fields = ['nome', 'cpf']

class EleicaoViewSet(viewsets.ModelViewSet):
    queryset = Eleicao.objects.all()
    serializer_class = EleicaoSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['status', 'tipo']
    search_fields = ['titulo']

class CandidatoViewSet(viewsets.ModelViewSet):
    queryset = Candidato.objects.all()
    serializer_class = CandidatoSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['eleicao']

class VotoViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Voto.objects.all()
    serializer_class = VotoSerializer

class VotarView(APIView):
    def post(self, request):
        serializer = VotacaoInputSerializer(data=request.data)
        if serializer.is_valid():
            data = serializer.validated_data
            eleitor = get_object_or_404(Eleitor, cpf=data['eleitor_cpf'])
            eleicao = get_object_or_404(Eleicao, id=data['eleicao_id'])
            
    
            if eleicao.status != 'Aberta':
                return Response({"erro": "Esta eleição não está aberta."}, status=status.HTTP_400_BAD_REQUEST)

            if RegistroVotacao.objects.filter(eleitor=eleitor, eleicao=eleicao).exists():
                return Response({"erro": "Você já votou nesta eleição!"}, status=status.HTTP_400_BAD_REQUEST)

            RegistroVotacao.objects.create(eleitor=eleitor, eleicao=eleicao)

           
            candidato = None
            if not data['em_branco']:
                candidato = get_object_or_404(Candidato, id=data['candidato_id'], eleicao=eleicao)

            salt = uuid.uuid4().hex
            comprovante = hashlib.sha256(f"{eleitor.cpf}{salt}".encode()).hexdigest()[:12].upper()

            Voto.objects.create(
                eleicao=eleicao,
                candidato=candidato,
                em_branco=data['em_branco'],
                comprovante_hash=comprovante
            )

            return Response({
                "mensagem": "Voto computado com sucesso!",
                "comprovante": comprovante,
                "instrucao": "Use o código acima para gerar seu QR Code de autenticidade."
            }, status=status.HTTP_201_CREATED)
            
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)