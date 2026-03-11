<template>
  <div class="main">

    <div class="page-header">
      <div>
        <h1>{{ department.name }}</h1>
        <p style="color: var(--text-soft); margin-top: 0.25rem; font-size: 0.9rem;">{{ department.description }}</p>
      </div>
      <button class="btn-secondary" @click="$router.back()">Go Back</button>
    </div>

    <div class="section">
      <div class="section-header">
        <h2>Doctors in this Department</h2>
        <span style="color: var(--text-soft); font-size: 0.88rem;">{{ doctors.length }} doctor(s)</span>
      </div>
      <table>
        <thead>
          <tr><th>Doctor</th><th>Specialization</th><th>Status</th><th>Actions</th></tr>
        </thead>
        <tbody>
          <tr v-for="d in doctors" :key="d.id">
            <td><strong>{{ d.fullname }}</strong></td>
            <td>{{ d.specialization }}</td>
            <td>
              <span v-if="d.is_blacklisted" style="color: var(--pink-600); font-weight: 600;">
                Currently Unavailable
              </span>
              <span v-else class="badge completed">Available</span>
            </td>
            <td>
              <template v-if="!d.is_blacklisted">
                <div style="display:flex; gap:0.5rem;">
                  <button @click="$router.push(`/patient/doctor/${d.id}`)">View Details</button>
                  <button class="btn-success" @click="$router.push(`/patient/doctor/${d.id}/availability`)">Book</button>
                </div>
              </template>
              <span v-else style="color: var(--text-soft); font-size: 0.85rem;">—</span>
            </td>
          </tr>
          <tr v-if="doctors.length === 0">
            <td colspan="4" class="empty">No doctors in this department</td>
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
      department: {},
      doctors: [],
      headers: { 'Authorization': `Bearer ${localStorage.getItem('token')}` }
    }
  },
  mounted() { this.fetchData() },
  methods: {
    async fetchData() {
      const id = this.$route.params.id
      const res = await fetch(`http://127.0.0.1:5000/api/patient/departments/${id}`, { headers: this.headers })
      const data = await res.json()
      this.department = data.department
      this.doctors    = data.doctors
    }
  }
}
</script>