<template>
  <div>
    <h1>Patient History</h1>
    <button @click="$router.back()">Go Back</button>

    <table border="1">
      <thead>
        <tr>
          <th>Doctor</th>
          <th>Date</th>
          <th>Diagnosis</th>
          <th>Prescription</th>
          <th>Medicines</th>
          <th>Status</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="a in history" :key="a.id">
          <td>{{ a.doctor_name }}</td>
          <td>{{ a.date }}</td>
          <td>{{ a.treatment ? a.treatment.diagnosis : '-' }}</td>
          <td>{{ a.treatment ? a.treatment.prescription : '-' }}</td>
          <td>{{ a.treatment ? a.treatment.medicines : '-' }}</td>
          <td>{{ a.status }}</td>
        </tr>
        <tr v-if="history.length === 0">
          <td colspan="6">No history found</td>
        </tr>
      </tbody>
    </table>
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
      const id = this.$route.params.id  // exists for doctor, undefined for patient
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