import api from './axiosClient'

export const getPatients = (showInactivos) => api.get(`pacientes/${showInactivos ? '?inactivos=true' : ''}`).then(res => res.data);
export const getPatient = (id) => api.get(`pacientes/${id}/`).then(res => res.data);
export const createPatient = (data) => api.post('pacientes/', data);
export const updatePatient = (id, data) => api.put(`pacientes/${id}/`, data);
export const deletePatient = (id) => api.delete(`pacientes/${id}/`);
export const restorePatient = (id) => api.patch(`pacientes/${id}/?inactivos=true`, { activo: true });

// ---------------------- CITAS ----------------------
export const getAppointments = () => api.get('citas/').then(res => res.data);
export const getAppointment = (id) => api.get(`citas/${id}/`).then(res => res.data);
export const createAppointment = (data) => api.post('citas/', data);
export const updateAppointment = (id, data) => api.put(`citas/${id}/`, data);

// ---------------------- HISTORIAS CLÍNICAS ----------------------
export async function getMedicalRecords() {
  const response = await axios.get('/api/historias-clinicas/');
  return response.data;
}
export const updateMedicalRecord = (id, data) =>
  axios.put(`/api/historias/${id}/`, data).then(res => res.data);

// ---------------------- TRATAMIENTOS ----------------------
export const getTreatments = (showInactivos) => api.get(`tratamientos/${showInactivos ? '?inactivos=true' : ''}`).then(res => res.data);
export const getTreatment = (id) => api.get(`tratamientos/${id}/`).then(res => res.data);
export const createTreatment = (data) => api.post('tratamientos/', data);
export const updateTreatment = (id, data) => api.put(`tratamientos/${id}/`, data);
export const deleteTreatment = (id) => api.delete(`tratamientos/${id}/`);
export const restoreTreatment = (id) => api.patch(`tratamientos/${id}/?inactivos=true`, { activo: true });

// ---------------------- APERITIVOS ----------------------
export const getSnacks = (showInactivos) => api.get(`aperitivos/${showInactivos ? '?inactivos=true' : ''}`).then(res => res.data);
export const getSnack = (id) => api.get(`aperitivos/${id}/`).then(res => res.data);
export const createSnack = (data) => api.post('aperitivos/', data);
export const updateSnack = (id, data) => api.put(`aperitivos/${id}/`, data);
export const deleteSnack = (id) => api.delete(`aperitivos/${id}/`);
export const restoreSnack = (id) => api.patch(`aperitivos/${id}/?inactivos=true`, { activo: true });

// ---------------------- SERVICIOS ----------------------
export const getServices = (showInactivos) => api.get(`servicios/${showInactivos ? '?inactivos=true' : ''}`).then(res => res.data);
export const getService = (id) => api.get(`servicios/${id}/`).then(res => res.data);
export const createService = (data) => api.post('servicios/', data);
export const updateService = (id, data) => api.put(`servicios/${id}/`, data);
export const deleteService = (id) => api.delete(`servicios/${id}/`);
export const restoreService = (id) => api.patch(`servicios/${id}/?inactivos=true`, { activo: true });

// ---------------------- TRABAJADORES ----------------------
export const getWorkers = (showInactivos) => api.get(`trabajadores/${showInactivos ? '?inactivos=true' : ''}`).then(res => res.data);
export const getWorker = (id) => api.get(`trabajadores/${id}/`).then(res => res.data);
export const createWorker = (data) => api.post('trabajadores/', data);
export const updateWorker = (id, data) => api.put(`trabajadores/${id}/`, data);
export const deleteWorker = (id) => api.delete(`trabajadores/${id}/`);
export const restoreWorker = (id) => api.patch(`trabajadores/${id}/?inactivos=true`, { activo: true });

//------------------------TIPO DE DOCUMENTOS(PACIENTE)------------------
export const getDocumentTypes = () => api.get('tipos-documento/').then(res => res.data);

//------------------------ESTADOS DE LAS CITAS------------------
export const getAppointmentStatuses = () => api.get('estados-cita/').then(res => res.data);

//------------------------TIPO DE DOCUMENTOS(COLABORADOR)------------------
export const getDocumentTypes2 = () => api.get('tipos-documento2/').then(res => res.data);

//------------------------ETIQUETAS PACIENTE------------------
export const getLabelPat = () => api.get('etiquetas-pac/').then(res => res.data);

// ---------------------- REPORTES ----------------------
export const getReportMonths = () => api.get('reportes/meses/').then(res => res.data);
export const getMonthReport = (mes) => api.get(`reportes/meses/${mes}/`).then(res => res.data);
export const getReportsList = () => api.get('reportes/').then(res => res.data);
export const downloadMonthPdf = (mes) =>
  api.get(`reportes/meses/${mes}/pdf/`, { responseType: 'blob' }).then(res => res.data);
