<template>
  <div>
    <h1>Doctor Dashboard</h1>
    <button @click="logout">Logout</button>
    <button @click="$router.push('/doctor/availability')">+ Add Availability</button>

    <h2>Upcoming Appointments</h2>
    <table>
      <thead>
        <tr>
          <th>Patient</th>
          <th>Date</th>
          <th>Time</th>
          <th>Status</th>
          <th>Actions</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="a in upcoming" :key="a.id">
          <td>{{ a.patient_name }}</td>
          <td>{{ a.date }}</td>
          <td>{{ a.time }}</td>
          <td>{{ a.status }}</td>
          <td>
            <button @click="cancel(a.id)">Cancel</button>
            <button @click="openTreatment(a)">Add Treatment</button>
          </td>
        </tr>
      </tbody>
    </table>

    <h2>Assigned Patients</h2>
    <table>
      <thead>
        <tr>
          <th>Name</th>
          <th>Contact</th>
          <th>Patient History</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="p in assigned" :key="p.id">
          <td>{{ p.name }}</td>
          <td>{{ p.age }}</td>
          <td>
            <button @click="$router.push(`/doctor/patient/${p.id}/history`)">View History</button>
          </td>
        </tr>
        <tr v-if="assigned.length === 0">
          <td colspan="4">No assigned patients</td>
        </tr>
      </tbody>
    </table>

    <h2>Past Appointments</h2>
    <table>
      <thead>
        <tr>
          <th>Patient</th>
          <th>Date</th>
          <th>Time</th>
          <th>Status</th>
          <th>Cancelled By</th>
          <th>Action</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="a in past" :key="a.id">
          <td>{{ a.patient_name }}</td>
          <td>{{ a.date }}</td>
          <td>{{ a.time }}</td>
          <td>{{ a.status }}</td>
          <td>{{ a.cancelled_by ? a.cancelled_by : '-' }}</td>
          <td>
            <button @click="$router.push(`/doctor/patient/${a.patient_id}/history`)">View History</button>
          </td>
        </tr>
        <tr v-if="past.length === 0">
          <td colspan="6">No past appointments</td>
        </tr>
      </tbody>
    </table>


    <!-- Add Treatment Popup -->
    <div v-if="showTreatmentForm" class="overlay">
      <div class="popup">
        <h3>Add Treatment</h3>
        <input v-model="treatment.diagnosis"    placeholder="Diagnosis" /><br />
        <input v-model="treatment.visit_type" placeholder = "Visit_Type"/><br />
        <input v-model="treatment.test_done" placeholder="Tests_Done"/><br />
        <input v-model="treatment.prescription" placeholder="Prescription" /><br />
        <input v-model="treatment.medicines"    placeholder="Medicines" /><br />
        <input v-model="treatment.notes"        placeholder="Notes" /><br />
        <input v-model="treatment.next_visit"   type="date" /><br />
        <p v-if="treatmentError">{{ treatmentError }}</p>
        <button @click="saveTreatment">Save</button>
        <button @click="showTreatmentForm = false">Cancel</button>
      </div>
    </div>

  </div>
</template>

<script>
export default {
  data() {
    return {
      upcoming:          [],
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
  mounted() {
    this.fetchData()
  },
  methods: {
    async fetchData() {
      const res = await fetch('http://127.0.0.1:5000/api/doctor/dashboard', { headers: this.headers })
      if (res.status === 401) { this.$router.push('/'); return }
      const data = await res.json()
      this.upcoming          = data.upcoming || []
      this.assigned = data.assigned || []
      this.past = data.past || []
    },

    async complete(id) {
      await fetch(`http://127.0.0.1:5000/api/doctor/appointments/${id}/complete`, { method: 'POST', headers: this.headers })
      this.fetchData()
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
      this.treatment = { diagnosis: '', prescription: '', medicines: '', notes: '', next_visit: '' }
      this.fetchData()
    },

    logout() {
      localStorage.clear()
      this.$router.push('/')
    }
  }
}
</script>

<style scoped>
.overlay { position: fixed; top: 0; left: 0; width: 100%; height: 100%; background: rgba(0,0,0,0.5); display: flex; justify-content: center; align-items: center; }
.popup   { background: white; padding: 2rem; border-radius: 8px; min-width: 300px; }
</style>