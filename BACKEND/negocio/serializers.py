from rest_framework import serializers
from django.core.validators import RegexValidator, MaxLengthValidator
from .models import Paciente, Colaborador, Servicio, Tratamiento, Cita, HistoriaClinica, Aperitivo

alpha_re = RegexValidator(
    regex=r'^[A-Za-zÁáÉéÍíÓóÚúÑñ\s]+$',
    message='Solo se permiten letras y espacios'
)
digits_re = RegexValidator(
    regex=r'^\d+$',
    message='Solo se permiten números'
)

class TratamientoSerializer(serializers.ModelSerializer):

    class Meta:
        model = Tratamiento
        fields = '__all__'

class AperitivoSerializer(serializers.ModelSerializer):

    class Meta:
        model = Aperitivo
        fields = '__all__'

class ServicioSerializer(serializers.ModelSerializer):
    tratamientos = TratamientoSerializer(many=True, read_only=True)
    tratamientos_ids = serializers.PrimaryKeyRelatedField(
        many=True,
        write_only=True,
        queryset=Tratamiento.objects.all(),
        source='tratamientos',
    )

    class Meta:
        model = Servicio
        fields = '__all__'

class PacienteSerializer(serializers.ModelSerializer):
    nombres = serializers.CharField(
        validators=[alpha_re, MaxLengthValidator(100)]
    )
    apellidos = serializers.CharField(
        validators=[alpha_re, MaxLengthValidator(100)]
    )
    celular = serializers.CharField(
        validators=[digits_re, MaxLengthValidator(20)]
    )
    numero_documento = serializers.CharField(
        required=False, allow_blank=True, allow_null=True,
        validators=[digits_re, MaxLengthValidator(10)]
    )
    emergencia_number = serializers.CharField(
        required=False, allow_blank=True, allow_null=True,
        validators=[digits_re, MaxLengthValidator(10)]
    )
    fecha_nacimiento = serializers.DateField(required=False, allow_null=True)

    class Meta:
        model = Paciente
        fields = '__all__'

    def validate_fecha_nacimiento(self, value):
        if value and value > value.today():
            raise serializers.ValidationError('La fecha de nacimiento no puede ser futura')
        return value

class ColaboradorSerializer(serializers.ModelSerializer):
    nombres = serializers.CharField(
        validators=[alpha_re, MaxLengthValidator(100)]
    )
    apellidos = serializers.CharField(
        validators=[alpha_re, MaxLengthValidator(100)]
    )
    celular = serializers.CharField(
        validators=[digits_re, MaxLengthValidator(20)]
    )
    numero_documento = serializers.CharField(
        validators=[digits_re, MaxLengthValidator(10)]
    )

    class Meta:
        model = Colaborador
        fields = '__all__'

class CitaSerializer(serializers.ModelSerializer):
    paciente = PacienteSerializer(read_only=True)
    colaborador = ColaboradorSerializer(read_only=True)
    servicio = ServicioSerializer(read_only=True)

    paciente_id = serializers.PrimaryKeyRelatedField(queryset=Paciente.objects.all(), write_only=True)
    colaborador_id = serializers.PrimaryKeyRelatedField(queryset=Colaborador.objects.all(), write_only=True)
    servicio_id = serializers.PrimaryKeyRelatedField(queryset=Servicio.objects.all(), write_only=True)

    aperitivos = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=Aperitivo.objects.all(),
        write_only=True
    )

    aperitivos_info = AperitivoSerializer(many=True, read_only=True, source='aperitivos')

    class Meta:
        model = Cita
        fields = [
            'id',
            'paciente', 'paciente_id',
            'colaborador', 'colaborador_id',
            'servicio', 'servicio_id',
            'aperitivos', 'aperitivos_info',
            'fecha_hora', 'hora',
            'notas', 'estado', 'saldo_pend',
            'created_at'
        ]

    def create(self, validated_data):
        paciente = validated_data.pop('paciente_id')
        colaborador = validated_data.pop('colaborador_id')
        servicio = validated_data.pop('servicio_id')
        aperitivos = validated_data.pop('aperitivos', [])

        cita = Cita.objects.create(
            paciente=paciente,
            colaborador=colaborador,
            servicio=servicio,
            **validated_data
        )

        cita.aperitivos.set(aperitivos)

        total_aperitivos = sum([a.precio for a in aperitivos])
        cita.saldo_pend = servicio.precio + total_aperitivos
        cita.save()

        return cita

    def update(self, instance, validated_data):
        if instance.estado in ('REAL', 'CANC'):
            raise serializers.ValidationError(
                {'estado': 'No se puede modificar una cita que ya fue realizada o cancelada'}
            )

        if 'paciente_id' in validated_data:
            instance.paciente = validated_data.pop('paciente_id')
        if 'colaborador_id' in validated_data:
            instance.colaborador = validated_data.pop('colaborador_id')
        if 'servicio_id' in validated_data:
            instance.servicio = validated_data.pop('servicio_id')
        if 'aperitivos' in validated_data:
            aperitivos = validated_data.pop('aperitivos')
            instance.aperitivos.set(aperitivos)
        else:
            aperitivos = instance.aperitivos.all()

        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        if 'saldo_pend' not in validated_data:
            total = 0
            if instance.servicio:
                total += float(instance.servicio.precio or 0)
            total += sum(float(ap.precio or 0) for ap in aperitivos)
            instance.saldo_pend = total

        instance.save()
        return instance

class HistoriaClinicaSerializer(serializers.ModelSerializer):
    cita = CitaSerializer(read_only=True)

    class Meta:
        model = HistoriaClinica
        fields = '__all__'
