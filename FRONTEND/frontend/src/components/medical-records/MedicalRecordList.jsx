import React, { useEffect, useState } from 'react';
import { Search, Download, FileText } from 'lucide-react';
import { getPatients, getAppointments, downloadHistoriaClinicaPdf } from '../../lib/api';
import { toast } from 'react-toastify';

export default function MedicalRecordList() {
  const [patients, setPatients] = useState([]);
  const [filteredPatients, setFilteredPatients] = useState([]);
  const [selectedPatient, setSelectedPatient] = useState(null);
  const [appointments, setAppointments] = useState([]);

  useEffect(() => {
    getPatients().then((data) => {
      setPatients(data);
      setFilteredPatients(data);
    });
  }, []);

  const handleSearch = (e) => {
    const query = e.target.value.toLowerCase();
    const filtered = patients.filter(
      (p) =>
        p.nombres.toLowerCase().includes(query) ||
        p.apellidos.toLowerCase().includes(query)
    );
    setFilteredPatients(filtered);
  };

  const handleSelectPatient = async (patient) => {
    setSelectedPatient(patient);
    try {
      const allAppointments = await getAppointments();
      const patientAppointments = allAppointments.filter(
        (cita) => cita.paciente?.id === patient.id
      );
      setAppointments(patientAppointments);
    } catch (err) {
      console.error('Error cargando citas:', err);
    }
  };

  const handleDownloadPdf = async () => {
    if (!selectedPatient) return;
    try {
      const blob = await downloadHistoriaClinicaPdf(selectedPatient.id);
      const url = window.URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      link.download = `HistoriaClinica_${selectedPatient.nombres}_${selectedPatient.apellidos}.pdf`;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      window.URL.revokeObjectURL(url);
      toast.success('PDF descargado correctamente');
    } catch (err) {
      toast.error('Error al descargar PDF');
      console.error('Error descargando PDF:', err);
    }
  };

  const estadoLabel = (estado) => {
    const map = { PEND: 'Pendiente', REAL: 'Realizada', CANC: 'Cancelada', RETR: 'Atrasada' };
    return map[estado] || estado;
  };

  return (
    <div className="space-y-6">
      <div className="bg-white p-6 rounded-xl shadow border">
        <h2 className="text-2xl font-bold text-gray-800 mb-4">Historias Clínicas</h2>

        <input
          type="text"
          placeholder="Buscar paciente..."
          onChange={handleSearch}
          className="w-full max-w-sm mb-4 px-3 py-2 border border-gray-300 rounded-lg"
        />

        {selectedPatient && (
          <>
            <div className="flex justify-end mb-4">
              <button
                onClick={handleDownloadPdf}
                className="btn bg-emerald-500 text-white px-4 py-2 rounded hover:bg-emerald-600 flex items-center gap-2"
              >
                <Download className="h-4 w-4" /> Descargar PDF
              </button>
            </div>

            <div className="bg-gray-50 p-4 rounded border mb-6">
              <h3 className="text-lg font-semibold mb-2">Paciente:</h3>
              <p><strong>Nombre:</strong> {selectedPatient.nombres} {selectedPatient.apellidos}</p>
              <p><strong>Documento:</strong> {selectedPatient.tipo_documento} {selectedPatient.numero_documento}</p>
              <p><strong>Celular:</strong> {selectedPatient.celular}</p>
              <p><strong>Email:</strong> {selectedPatient.email}</p>
              <p><strong>Fecha de nacimiento:</strong> {selectedPatient.fecha_nacimiento}</p>
            </div>

            {appointments.length > 0 ? (
              <div className="space-y-4 mb-6">
                {appointments.map((appt) => (
                  <div key={appt.id} className="border border-gray-200 rounded-lg p-4 bg-white">
                    <p><strong>Fecha:</strong> {appt.fecha_hora}</p>
                    <p><strong>Hora:</strong> {appt.hora}</p>
                    <p><strong>Servicio:</strong> {appt.servicio?.nombre || 'N/A'}</p>
                    <p><strong>Colaborador:</strong> {appt.colaborador?.nombres || 'N/A'} {appt.colaborador?.apellidos || ''}</p>
                    <p><strong>Notas:</strong> {appt.notas || 'N/A'}</p>
                    <p><strong>Saldo Pendiente:</strong> ${appt.saldo_pend}</p>
                    <p><strong>Estado:</strong> {estadoLabel(appt.estado)}</p>
                  </div>
                ))}
              </div>
            ) : (
              <p className="text-gray-500 mb-6">Este paciente aún no tiene citas registradas.</p>
            )}
          </>
        )}

        <div className="overflow-y-auto max-h-[500px] grid grid-cols-1 md:grid-cols-2 gap-4 mb-6">
          {filteredPatients.map((p) => (
            <div
              key={p.id}
              className={`cursor-pointer p-4 border rounded hover:border-emerald-500 ${selectedPatient?.id === p.id ? 'border-emerald-500 bg-emerald-50' : ''}`}
              onClick={() => handleSelectPatient(p)}
            >
              <p className="font-semibold text-gray-800">
                {p.nombres} {p.apellidos}
              </p>
              <p className="text-sm text-gray-500">{p.numero_documento}</p>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}