from rest_framework.decorators import api_view, permission_classes, throttle_classes
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import viewsets, status
from rest_framework.permissions import AllowAny
from rest_framework.pagination import PageNumberPagination
from django.contrib.auth.models import User
from django.conf import settings
from django.db import models
from django.utils import timezone
from .models import *
from .serializers import *
from .throttles import RegisterAnonThrottle


class SoftDeleteViewSet(viewsets.ModelViewSet):
    def get_queryset(self):
        qs = super().get_queryset()
        if self.request.query_params.get('inactivos') == 'true':
            qs = qs.filter(activo=False)
        elif self.request.query_params.get('todos') == 'true':
            pass
        else:
            qs = qs.filter(activo=True)
        return qs

    def perform_destroy(self, instance):
        if hasattr(instance, 'activo'):
            instance.activo = False
            instance.save(update_fields=['activo'])
        else:
            instance.delete()


class PacienteViewSet(SoftDeleteViewSet):
    queryset = Paciente.objects.all()
    serializer_class = PacienteSerializer


class ColaboradorViewSet(SoftDeleteViewSet):
    queryset = Colaborador.objects.all()
    serializer_class = ColaboradorSerializer


class TratamientoViewSet(SoftDeleteViewSet):
    queryset = Tratamiento.objects.all()
    serializer_class = TratamientoSerializer


class AperitivoViewSet(SoftDeleteViewSet):
    queryset = Aperitivo.objects.all()
    serializer_class = AperitivoSerializer


class ServicioViewSet(SoftDeleteViewSet):
    queryset = Servicio.objects.all()
    serializer_class = ServicioSerializer


class CitaViewSet(viewsets.ModelViewSet):
    queryset = Cita.objects.all().order_by('-fecha_hora')
    serializer_class = CitaSerializer

    def get_queryset(self):
        today = timezone.localdate()
        Cita.objects.filter(fecha_hora__lt=today, estado='PEND').update(estado='RETR')
        qs = super().get_queryset()
        fecha = self.request.query_params.get('fecha')
        if fecha:
            qs = qs.filter(fecha_hora=fecha)
        return qs

    def destroy(self, request, *args, **kwargs):
        return Response(
            {'error': 'Las citas no se pueden eliminar. Puedes cancelarlas cambiando su estado a CANC.'},
            status=status.HTTP_405_METHOD_NOT_ALLOWED
        )


class HistoriasPagination(PageNumberPagination):
    page_size = 20
    page_size_query_param = 'page_size'
    max_page_size = 100


class HistoriaClinicaViewSet(viewsets.ModelViewSet):
    queryset = HistoriaClinica.objects.all().order_by('-created_at')
    serializer_class = HistoriaClinicaSerializer
    pagination_class = HistoriasPagination


@api_view(['GET'])
def historia_clinica_pdf(request, paciente_id):
    from io import BytesIO
    from django.http import HttpResponse
    from reportlab.lib import colors
    from reportlab.lib.pagesizes import letter
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import inch
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable

    try:
        paciente = Paciente.objects.get(id=paciente_id)
    except Paciente.DoesNotExist:
        return Response({'error': 'Paciente no encontrado'}, status=status.HTTP_404_NOT_FOUND)

    historia = getattr(paciente, 'historia_clinica', None)
    citas = Cita.objects.filter(paciente=paciente).select_related('colaborador', 'servicio').order_by('-fecha_hora')

    buf = BytesIO()
    doc = SimpleDocTemplate(buf, pagesize=letter, topMargin=0.5*inch, bottomMargin=0.5*inch)
    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle('Title2', parent=styles['Title'], fontSize=18, spaceAfter=6))
    styles.add(ParagraphStyle('Normal2', parent=styles['Normal'], fontSize=10, spaceAfter=4))
    styles.add(ParagraphStyle('SectionTitle', parent=styles['Normal'], fontSize=12, spaceAfter=6, spaceBefore=12, fontName='Helvetica-Bold'))

    elements = []

    elements.append(Paragraph('Belleza Plena SPA', styles['Title2']))
    elements.append(Paragraph('Historia Clínica', styles['Normal2']))
    elements.append(Spacer(1, 12))
    elements.append(HRFlowable(width='100%', thickness=1, color=colors.HexColor('#059669')))
    elements.append(Spacer(1, 12))

    elements.append(Paragraph('<b>Datos del Paciente</b>', styles['SectionTitle']))
    paciente_data = [
        ['Nombre', f"{paciente.nombres} {paciente.apellidos}"],
        ['Documento', f"{paciente.get_tipo_documento_display() or '—'} {paciente.numero_documento or '—'}"],
        ['Celular', paciente.celular or '—'],
        ['Fecha de Nacimiento', paciente.fecha_nacimiento.strftime('%d/%m/%Y') if paciente.fecha_nacimiento else '—'],
        ['Dirección', paciente.direccion or '—'],
    ]
    t = Table(paciente_data, colWidths=[2*inch, 3.5*inch])
    t.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('ROWBACKGROUNDS', (0, 0), (-1, -1), [colors.white, colors.HexColor('#f0fdf4')]),
    ]))
    elements.append(t)
    elements.append(Spacer(1, 12))

    if paciente.condiciones_medicas:
        elements.append(Paragraph('<b>Condiciones Médicas:</b>', styles['SectionTitle']))
        elements.append(Paragraph(paciente.condiciones_medicas, styles['Normal2']))
        elements.append(Spacer(1, 6))
    if paciente.alergias:
        elements.append(Paragraph('<b>Alergias:</b>', styles['SectionTitle']))
        elements.append(Paragraph(paciente.alergias, styles['Normal2']))
        elements.append(Spacer(1, 6))
    if historia:
        if historia.observaciones:
            elements.append(Paragraph('<b>Observaciones:</b>', styles['SectionTitle']))
            elements.append(Paragraph(historia.observaciones, styles['Normal2']))
            elements.append(Spacer(1, 6))
        if historia.recomendaciones:
            elements.append(Paragraph('<b>Recomendaciones:</b>', styles['SectionTitle']))
            elements.append(Paragraph(historia.recomendaciones, styles['Normal2']))
            elements.append(Spacer(1, 12))

    elements.append(HRFlowable(width='100%', thickness=0.5, color=colors.grey))
    elements.append(Spacer(1, 12))
    elements.append(Paragraph(f'<b>Historial de Citas ({citas.count()})</b>', styles['SectionTitle']))

    if citas.exists():
        cita_data = [['Fecha', 'Hora', 'Servicio', 'Colaborador', 'Estado']]
        for cita in citas:
            cita_data.append([
                cita.fecha_hora.strftime('%d/%m/%Y'),
                str(cita.hora),
                cita.servicio.nombre if cita.servicio else '—',
                f"{cita.colaborador.nombres} {cita.colaborador.apellidos}" if cita.colaborador else '—',
                dict(Cita.ESTADOS_TYPES).get(cita.estado, cita.estado),
            ])
        t = Table(cita_data, colWidths=[1*inch, 0.7*inch, 1.3*inch, 1.5*inch, 1*inch])
        t.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#059669')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 8),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f0fdf4')]),
            ('ALIGN', (1, 1), (1, -1), 'CENTER'),
        ]))
        elements.append(t)
    else:
        elements.append(Paragraph('No tiene citas registradas.', styles['Normal2']))

    elements.append(Spacer(1, 30))
    elements.append(HRFlowable(width='100%', thickness=0.5, color=colors.grey))
    elements.append(Spacer(1, 8))
    elements.append(Paragraph(
        f'Generado el {timezone.now().strftime("%d/%m/%Y %H:%M")} por Belleza Plena SPA',
        ParagraphStyle('Footer', parent=styles['Normal'], fontSize=8, textColor=colors.grey, alignment=1)
    ))

    doc.build(elements)
    buf.seek(0)

    response = HttpResponse(buf, content_type='application/pdf')
    safe_name = f"{paciente.nombres}_{paciente.apellidos}".replace(' ', '_')
    response['Content-Disposition'] = f'attachment; filename="HistoriaClinica_{safe_name}.pdf"'
    return response


class HistoriasPorPaciente(APIView):
    def get(self, request):
        page = int(request.query_params.get('page', 1))
        page_size = int(request.query_params.get('page_size', 20))
        search = request.query_params.get('search', '').strip()

        pacientes_qs = Paciente.objects.all().order_by('nombres')
        if search:
            pacientes_qs = pacientes_qs.filter(
                models.Q(nombres__icontains=search) | models.Q(apellidos__icontains=search) | models.Q(numero_documento__icontains=search)
            )

        total = pacientes_qs.count()
        start = (page - 1) * page_size
        end = start + page_size
        pacientes_page = pacientes_qs[start:end]

        pacientes_data = []
        for paciente in pacientes_page:
            citas = paciente.cita_set.select_related('colaborador', 'servicio').order_by('-fecha_hora')
            citas_data = []
            for cita in citas:
                historia = getattr(cita.paciente, 'historia_clinica', None)
                if historia:
                    citas_data.append({
                        'id': cita.id,
                        'cita_id': cita.id,
                        'fecha_hora': cita.fecha_hora,
                        'hora': str(cita.hora),
                        'colaborador_nombre': cita.colaborador.nombres,
                        'servicio_nombre': cita.servicio.nombre,
                        'estado': cita.estado,
                        'observaciones': historia.observaciones,
                        'recomendaciones': historia.recomendaciones,
                    })

            pacientes_data.append({
                'paciente_id': paciente.id,
                'paciente_nombre': f"{paciente.nombres} {paciente.apellidos}",
                'paciente_documento': paciente.numero_documento or '',
                'citas': citas_data
            })

        return Response({
            'results': pacientes_data,
            'count': total,
            'page': page,
            'page_size': page_size,
            'total_pages': max(1, -(-total // page_size)),
        })


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
@throttle_classes([RegisterAnonThrottle])
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


@api_view(['POST'])
@permission_classes([AllowAny])
def push_subscribe(request):
    serializer = PushSubscriptionSerializer(data=request.data)
    if serializer.is_valid():
        endpoint = serializer.validated_data['endpoint']
        obj, created = PushSubscription.objects.update_or_create(
            endpoint=endpoint,
            defaults={
                'auth_key': serializer.validated_data['auth_key'],
                'p256dh_key': serializer.validated_data['p256dh_key'],
            }
        )
        return Response({'id': obj.id, 'created': created}, status=status.HTTP_201_CREATED if created else status.HTTP_200_OK)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([AllowAny])
def push_unsubscribe(request):
    endpoint = request.data.get('endpoint')
    if not endpoint:
        return Response({'error': 'endpoint required'}, status=status.HTTP_400_BAD_REQUEST)
    deleted, _ = PushSubscription.objects.filter(endpoint=endpoint).delete()
    return Response({'deleted': deleted}, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([AllowAny])
def push_public_key(request):
    return Response({'publicKey': settings.VAPID_PUBLIC_KEY})
