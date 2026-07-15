from rest_framework.decorators import api_view, permission_classes
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import viewsets, status
from rest_framework.permissions import AllowAny
from django.contrib.auth.models import User
from .models import *
from .serializers import *


class PacienteViewSet(viewsets.ModelViewSet):
    queryset = Paciente.objects.all()
    serializer_class = PacienteSerializer

class ColaboradorViewSet(viewsets.ModelViewSet):
    queryset = Colaborador.objects.all()
    serializer_class = ColaboradorSerializer

class TratamientoViewSet(viewsets.ModelViewSet):
    queryset = Tratamiento.objects.all()
    serializer_class = TratamientoSerializer

class AperitivoViewSet(viewsets.ModelViewSet):
    queryset = Aperitivo.objects.all()
    serializer_class = AperitivoSerializer

class ServicioViewSet(viewsets.ModelViewSet):
    queryset = Servicio.objects.all()
    serializer_class = ServicioSerializer

class CitaViewSet(viewsets.ModelViewSet):
    queryset = Cita.objects.all().order_by('-fecha_hora')
    serializer_class = CitaSerializer

class HistoriaClinicaViewSet(viewsets.ModelViewSet):
    queryset = HistoriaClinica.objects.all().order_by('-created_at')
    serializer_class = HistoriaClinicaSerializer

class HistoriasPorPaciente(APIView):
    def get(self, request):
        pacientes_data = []
        pacientes = Paciente.objects.all()

        for paciente in pacientes:
            citas = paciente.cita_set.select_related('colaborador', 'servicio').order_by('-fecha_hora')
            citas_data = []
            for cita in citas:
                if hasattr(cita, 'historiaclinica'):
                    historia = cita.historiaclinica
                    citas_data.append({
                        'id': cita.id,
                        'fecha_hora': cita.fecha_hora,
                        'colaborador_nombre': cita.colaborador.nombres,
                        'servicio_nombre': cita.servicio.nombre,
                        'tratamiento': historia.tratamiento,
                        'observaciones': historia.observaciones,
                        'recomendaciones': historia.recomendaciones,
                    })

            if citas_data:
                pacientes_data.append({
                    'paciente_id': paciente.id,
                    'paciente_nombre': f"{paciente.nombres} {paciente.apellidos}",
                    'citas': citas_data
                })

        return Response(pacientes_data)

class TipoDocumentoChoices(APIView): 
    def get(self, request):
        return Response([
            {'codigo': value, 'nombre': label}
            for value, label in Paciente.DOCUMENT_TYPES
        ])
    
class TipoDocumentoChoices2(APIView): 
    def get(self, request):
        return Response([
            {'codigo': value, 'nombre': label}
            for value, label in Colaborador.DOCUMENT_TYPES
        ])
    
@api_view(['GET'])
def appointment_statuses(request):
    return Response([
        {'value': k, 'label': v}
        for k, v in dict(Cita.ESTADOS_TYPES). items()
    ])


class LabelPatient(APIView): 
    def get(self, request):
        return Response([
            {'codigo': value, 'nombre': label}
            for value, label in Paciente.ETIQUETAS
        ])

@api_view(['POST'])
@permission_classes([AllowAny])
def register(request):
    username = request.data.get('username')
    password = request.data.get('password')
    email = request.data.get('email', '')
    if not username or not password:
        return Response({'error': 'username and password required'}, status=status.HTTP_400_BAD_REQUEST)
    if User.objects.filter(username=username).exists():
        return Response({'error': 'username already exists'}, status=status.HTTP_400_BAD_REQUEST)
    user = User.objects.create_user(username=username, password=password, email=email)
    return Response({'id': user.id, 'username': user.username})
    
