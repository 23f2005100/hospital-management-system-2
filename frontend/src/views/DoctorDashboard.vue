<template>
  <div class="main">

    <div class="page-header">
      <div>
        <h1>🩺 Dr. {{ doctor.fullname }}</h1>
        <p style="color: var(--text-soft); margin-top: 0.25rem; font-size: 0.9rem;">Manage your appointments and patients</p>
      </div>
      <div style="display:flex; gap:0.75rem;">
        <button @click="$router.push('/doctor/availability')">+ Add Availability</button>
        <button class="btn-danger" @click="logout">Logout</button>
      </div>
    </div>

    <!-- Upcoming Appointments -->
    <div class="section">
      <div class="section-header">
        <h2>Upcoming Appointments</h2>
        <span style="color: var(--text-soft); font-size: 0.88rem;">{{ upcoming.length }} appointment(s)</span>
      </div>
      <table>
        <thead>
          <tr><th>Patient</th><th>Date</th><th>Time</th><th>Status</th><th>Actions</th></tr>
        </thead>
        <tbody>
          <tr v-for="a in upcoming" :key="a.id">
            <td><strong>{{ a.patient_name }}</strong></td>
            <td>{{ a.date }}</td>
            <td>{{ a.time }}</td>
            <td><span :class="['badge', a.status.toLowerCase()]">{{ a.status }}</span></td>
            <td>
              <div style="display:flex; gap:0.5rem;">
                <button class="btn-danger" @click="cancel(a.id)">Cancel</button>
                <button class="btn-success" @click="openTreatment(a)">Add Treatment</button>
              </div>
            </td>
          </tr>
          <tr v-if="upcoming.length === 0">
            <td colspan="5" class="empty">No upcoming appointments</td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- Assigned Patients -->
    <div class="section">
      <div class="section-header">
        <h2>Assigned Patients</h2>
        <span style="color: var(--text-soft); font-size: 0.88rem;">{{ assigned.length }} patient(s)</span>
      </div>
      <table>
        <thead>
          <tr><th>Name</th><th>Age</th><th>Action</th></tr>
        </thead>
        <tbody>
          <tr v-for="p in assigned" :key="p.id">
            <td><strong>{{ p.name }}</strong></td>
            <td>{{ p.age }}</td>
            <td>
              <button @click="$router.push(`/doctor/patient/${p.id}/history`)">View History</button>
            </td>
          </tr>
          <tr v-if="assigned.length === 0">
            <td colspan="3" class="empty">No assigned patients</td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- Past Appointments -->
    <div class="section">
      <div class="section-header">
        <h2>Past Appointments</h2>
        <span style="color: var(--text-soft); font-size: 0.88rem;">{{ past.length }} record(s)</span>
      </div>
      <table>
        <thead>
          <tr><th>Patient</th><th>Date</th><th>Time</th><th>Status</th><th>Cancelled By</th><th>Action</th></tr>
        </thead>
        <tbody>
          <tr v-for="a in past" :key="a.id">
            <td><strong>{{ a.patient_name }}</strong></td>
            <td>{{ a.date }}</td>
            <td>{{ a.time }}</td>
            <td><span :class="['badge', a.status.toLowerCase()]">{{ a.status }}</span></td>
            <td>{{ a.cancelled_by || '—' }}</td>
            <td>
              <button @click="$router.push(`/doctor/patient/${a.patient_id}/history`)">View History</button>
            </td>
          </tr>
          <tr v-if="past.length === 0">
            <td colspan="6" class="empty">No past appointments</td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- Treatment Modal -->
    <div v-if="showTreatmentForm" class="modal-overlay">
      <div class="modal">
        <h3>Add Treatment</h3>
        <input v-model="treatment.visit_type"   placeholder="Visit Type" />
        <input v-model="treatment.test_done"    placeholder="Tests Done" />
        <input v-model="treatment.diagnosis"    placeholder="Diagnosis" />
        <input v-model="treatment.prescription" placeholder="Prescription" />
        <input v-model="treatment.medicines"    placeholder="Medicines" />
        <input v-model="treatment.notes"        placeholder="Notes" />
        <input v-model="treatment.next_visit"   type="date" placeholder="Next Visit" />
        <p v-if="treatmentError" class="error-msg">{{ treatmentError }}</p>
        <div class="modal-actions">
          <button @click="saveTreatment">Save</button>
          <button class="btn-secondary" @click="showTreatmentForm = false">Cancel</button>
        </div>
      </div>
    </div>

  </div>
</template>

<script>
export default {
  data() {
    return {
      doctor: [],
      upcoming: [],
      assigned: [],
      past: [],
      showTreatmentForm: false,
      selectedAppointmentId: null,
      treatmentError: '',
      treatment: { diagnosis: '', visit_type: '', test_done: '', prescription: '', medicines: '', notes: '', next_visit: '' },
      headers: {
        'Authorization': `Bearer ${localStorage.getItem('token')}`,
        'Content-Type': 'application/json'
      }
    }
  },
  mounted() { this.fetchData() },
  methods: {
    async fetchData() {
      const res = await fetch('http://127.0.0.1:5000/api/doctor/dashboard', { headers: this.headers })
      if (res.status === 401) { this.$router.push('/'); return }
      const data = await res.json()
      this.doctor = data.doctor
      this.upcoming = data.upcoming || []
      this.assigned = data.assigned || []
      this.past     = data.past     || []
    },

    async cancel(id) {
      await fetch(`http://127.0.0.1:5000/api/doctor/appointments/${id}/cancel`, { method: 'POST', headers: this.headers })
      this.fetchData()
    },

    openTreatment(appointment) {
      this.selectedAppointmentId = appointment.id
      this.showTreatmentForm     = true
      this.treatmentError        = ''
    },

    async saveTreatment() {
      const res = await fetch(`http://127.0.0.1:5000/api/doctor/appointments/${this.selectedAppointmentId}/treatment`, {
        method: 'POST', headers: this.headers, body: JSON.stringify(this.treatment)
      })
      if (!res.ok) { this.treatmentError = 'Failed to save'; return }
      this.showTreatmentForm = false
      this.treatment = { diagnosis: '', visit_type: '', test_done: '', prescription: '', medicines: '', notes: '', next_visit: '' }
      this.fetchData()
    },

    logout() { localStorage.clear(); this.$router.push('/') }
  }
}
</script>