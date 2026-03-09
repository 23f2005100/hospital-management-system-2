<template>
  <div>
    <h1>{{ department.name }}</h1>
    <p>{{ department.description }}</p>
    <button @click="$router.back()">Go Back</button>

    <h2>Doctors List</h2>
    <table border="1">
      <tr v-for="d in doctors" :key="d.id">
        <td>{{ d.fullname }}</td>
        <td><button @click="$router.push(`/patient/doctor/${d.id}`)">View Details</button></td>
        <td><button @click="$router.push(`/patient/doctor/${d.id}/availability`)">Check Availability</button></td>
      </tr>
    </table>
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
      this.doctors = data.doctors
    }
  }
}
</script>