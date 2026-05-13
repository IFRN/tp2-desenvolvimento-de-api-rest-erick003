from django.db import models
from django.core.validators import MinLengthValidator
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

class Eleitor(models.Model): 
    nome = models.CharField(max_length=150) 
    email = models.EmailField(unique=True)      
    cpf = models.CharField(max_length=14, unique=True, validators=[MinLengthValidator(11)]) 
    data_nascimento = models.DateField()  
    ativo = models.BooleanField(default=True)  
    data_cadastro = models.DateTimeField(auto_now_add=True)

    class Meta: 
        db_table = 'Eleitores'   
        ordering = ['nome']      
  
    def __str__(self): 
        return f'{self.nome} <{self.email}>'

class Eleicao(models.Model): 
    ESTUDANTIL, SINDICAL, ASSOCIACAO, CONDOMINIO, CONSELHO_TIPO = "1", "2", "3", "4", "5"
    RASCUNHO, ABERTA, ENCERRADA, APURADA, CONSELHO_STATUS = "1", "2", "3", "4", "5"

    TIPO_CHOICE = (
        (ESTUDANTIL, "estudantil"),
        (SINDICAL, "sindical"),
        (ASSOCIACAO, "associacao"),
        (CONDOMINIO, "condominio"),
        (CONSELHO_TIPO, "conselho"),
    )

    STATUS_CHOICE = (
        (RASCUNHO, "rascunho"),
        (ABERTA, "aberta"),
        (ENCERRADA, "encerrada"),
        (APURADA, "apurada"),
        (CONSELHO_STATUS, "conselho"),
    )

    STATUS_FLOW = {
        RASCUNHO: ABERTA,
        ABERTA: ENCERRADA,
        ENCERRADA: APURADA,
        APURADA: None, # Fim do fluxo
    }

    titulo = models.CharField(max_length=200) 
    descricao = models.TextField(blank=True)
    tipo = models.CharField(max_length=1, choices=TIPO_CHOICE, default=ESTUDANTIL)
    data_inicio = models.DateTimeField()
    data_fim = models.DateTimeField() 
    status = models.CharField(max_length=1, choices=STATUS_CHOICE, default=RASCUNHO)
    permite_branco = models.BooleanField(default=True)
    criada_por = models.ForeignKey(Eleitor, on_delete=models.PROTECT, related_name='eleicoes_criadas')
 
    def clean(self):
        if self.data_fim and self.data_inicio and self.data_fim < self.data_inicio:
            raise ValidationError('A data de fim deve ser após a data de início.')
        
        if self.pk:
            old_obj = Eleicao.objects.get(pk=self.pk)
            if old_obj.status != self.status:
                allowed_next = self.STATUS_FLOW.get(old_obj.status)
                if self.status != allowed_next:
                    raise ValidationError(f'Fluxo inválido: de "{old_obj.get_status_display()}" o próximo passo deve ser "{dict(self.STATUS_CHOICE).get(allowed_next)}".')

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)
    
    def __str__(self): 
        return self.titulo

    class Meta: 
        db_table = 'Eleicoes'   
        ordering = ['titulo']      

class Candidato(models.Model): 
    eleicao = models.ForeignKey(Eleicao, on_delete=models.CASCADE, related_name='candidatos') 
    numero = models.PositiveIntegerField()  
    nome = models.CharField(max_length=150) 
    nome_urna = models.CharField(max_length=50)
    partido_chapa = models.CharField(max_length=100, blank=True)
    proposta = models.TextField(blank=True)
    foto_url = models.URLField(blank=True)
 
    class Meta: 
        db_table = 'candidatos'   
        ordering = ['nome']   
        unique_together = [('eleicao', 'numero')]   
 
    def __str__(self):  
        return f'{self.nome} ({self.numero})'

class AptidaoLeitor(models.Model): 
    eleitor = models.ForeignKey(Eleitor, on_delete=models.PROTECT, related_name='aptidoes')
    eleicao = models.ForeignKey(Eleicao, on_delete=models.PROTECT, related_name='registros_aptos') 
    data_inclusao = models.DateTimeField(auto_now_add=True)
 
    class Meta: 
        db_table = 'aptidaoleitor'   
        ordering = ['eleitor']    
        unique_together = [('eleitor', 'eleicao')]

    def __str__(self): 
        return f'{self.eleitor} - {self.eleicao}'

class RegistroVotacao(models.Model): 
    eleitor = models.ForeignKey(Eleitor, on_delete=models.PROTECT, related_name='registros_votacao')
    eleicao = models.ForeignKey(Eleicao, on_delete=models.PROTECT, related_name='registros_votacao') 
    data_hora = models.DateTimeField(auto_now_add=True)  
 
    class Meta: 
        db_table = 'registrovotacao'    
 
    def __str__(self): 
        return f'{self.eleitor} votou em {self.eleicao}'

class Voto(models.Model): 
    eleicao = models.ForeignKey(Eleicao, on_delete=models.PROTECT, related_name='votos') 
    candidato = models.ForeignKey(Candidato, on_delete=models.PROTECT, related_name='votos', null=True, blank=True)
    em_branco = models.BooleanField(default=False)
    data_hora = models.DateTimeField(auto_now_add=True)  
    comprovante_hash = models.CharField(max_length=64, unique=True)
 
    def clean(self):
        if self.em_branco and self.candidato is not None:
            raise ValidationError(_('Não pode haver candidato definido se o voto for em branco.'))
        if not self.em_branco and self.candidato is None:
            raise ValidationError(_('Se o voto não for em branco, um candidato deve ser selecionado.'))

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    class Meta: 
        db_table = 'votos'    
        ordering = ['eleicao']       
 
    def __str__(self): 
        return f'Voto na eleição {self.eleicao}'