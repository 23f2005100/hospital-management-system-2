<template>
  <div class="main">

    <div class="page-header">
      <div>
        <h1>📋 Patient History</h1>
        <p style="color: var(--text-soft); margin-top: 0.25rem; font-size: 0.9rem;">Past appointments, diagnoses and prescriptions</p>
      </div>
      <button class="btn-secondary" @click="$router.back()">Go Back</button>
    </div>

    <div class="section">
      <div class="section-header">
        <h2>Appointment Records</h2>
        <span style="color: var(--text-soft); font-size: 0.88rem;">{{ history.length }} record(s)</span>
      </div>
      <table>
        <thead>
          <tr>
            <th>Doctor</th>
            <th>Date</th>
            <th>Visit Type</th>
            <th>Tests Done</th>
            <th>Diagnosis</th>
            <th>Prescription</th>
            <th>Medicines</th>
            <th>Notes</th>
            <th>Next Visit</th>
            <th>Status</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="a in history" :key="a.id">
            <td><strong>{{ a.doctor_name }}</strong></td>
            <td>{{ a.date }}</td>
            <td>{{ a.treatment ? a.treatment.visit_type   : '—' }}</td>
            <td>{{ a.treatment ? a.treatment.test_done    : '—' }}</td>
            <td>{{ a.treatment ? a.treatment.diagnosis    : '—' }}</td>
            <td>{{ a.treatment ? a.treatment.prescription : '—' }}</td>
            <td>{{ a.treatment ? a.treatment.medicines    : '—' }}</td>
            <td>{{ a.treatment ? a.treatment.notes        : '—' }}</td>
            <td>{{ a.treatment ? a.treatment.next_visit   : '—' }}</td>
            <td>
              <span :class="['badge', a.status.toLowerCase()]">{{ a.status }}</span>
            </td>
          </tr>
          <tr v-if="history.length === 0">
            <td colspan="10" class="empty">No history found</td>
          </tr>
        </tbody>
      </table>
    </div>

  </div>
</template>

<script>
export default {
  data() {
    return {
      history: [],
      headers: { 'Authorization': `Bearer ${localStorage.getItem('token')}` }
    }
  },
  mounted() { this.fetchData() },
  methods: {
    async fetchData() {
      const id  = this.$route.params.id
      const url = id
        ? `http://127.0.0.1:5000/api/doctor/patient/${id}/history`
        : `http://127.0.0.1:5000/api/patient/history`

      const res  = await fetch(url, { headers: this.headers })
      const data = await res.json()
      this.history = id ? data.appointments : data
    }
  }
}
</script>