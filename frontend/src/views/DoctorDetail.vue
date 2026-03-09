<template>
  <div class="container">
    <div class="card">
      <h1>{{ doctor.fullname }}</h1>
      <p><strong>Qualification:</strong> {{ doctor.qualification }}</p>
      <p><strong>Specialization:</strong> {{ doctor.specialization }}</p>
      <p><strong>Experience:</strong> {{ doctor.experience }}</p>
      <p><strong>About:</strong> {{ doctor.description }}</p>

      <div class="actions">
        <button @click="$router.push(`/patient/doctor/${doctor.id}/availability`)">Check Availability</button>
        <button @click="$router.back()">Go Back</button>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  data() {
    return {
      doctor: {},
      headers: { 'Authorization': `Bearer ${localStorage.getItem('token')}` }
    }
  },
  mounted() { this.fetchData() },
  methods: {
    async fetchData() {
      const id   = this.$route.params.id
      const res  = await fetch(`http://127.0.0.1:5000/api/patient/doctors/${id}`, { headers: this.headers })
      const data = await res.json()
      this.doctor = data.doctor
    }
  }
}
</script>

<style scoped>
.container { display: flex; justify-content: center; padding: 2rem; }
.card      { background: white; border: 1px solid #ddd; border-radius: 8px; padding: 2rem; min-width: 400px; max-width: 600px; }
.card h1   { margin-bottom: 1rem; }
.card p    { margin: 0.5rem 0; }
.actions   { margin-top: 1.5rem; display: flex; gap: 1rem; }
</style>