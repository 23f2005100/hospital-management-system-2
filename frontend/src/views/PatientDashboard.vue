<template>
  <div>
    <h1>Welcome {{ patient.name }}</h1>
    <button @click="openProfile">Edit Profile</button>
    <button @click="$router.push('/patient/history')">History</button>
    <button @click="exportHistory">Export Patient History</button>
    <p v-if="exportMsg">{{ exportMsg }}</p>
    <button @click="logout">Logout</button>

    <h2>Departments</h2>
    <table border="1">
      <thead>
        <tr>
          <th>Name</th>
          <th>Action</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="d in departments" :key="d.id">
          <td>{{ d.name }}</td>
          <td><button @click="$router.push(`/patient/department/${d.id}`)">View Details</button></td>
        </tr>
      </tbody>
    </table>

    <h2>Upcoming Appointments</h2>
    <table border="1">
      <thead>
        <tr>
          <th>Doctor</th>
          <th>Dept</th>
          <th>Date</th>
          <th>Time</th>
          <th>Action</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="a in upcoming" :key="a.id">
          <td>{{ a.doctor_name }}</td>
          <td>{{ a.department }}</td>
          <td>{{ a.date }}</td>
          <td>{{ a.time }}</td>
          <td><button @click="cancel(a.id)">Cancel</button></td>
        </tr>
        <tr v-if="upcoming.length === 0">
          <td colspan="5">No upcoming appointments</td>
        </tr>
      </tbody>
    </table>

    <!-- Edit Profile Popup -->
    <div v-if="showProfile" class="overlay">
      <div class="popup">
        <h3>Edit Profile</h3>
        <input v-model="profileForm.name"    placeholder="Name" /><br />
        <input v-model="profileForm.age"     placeholder="Age" /><br />
        <input v-model="profileForm.gender"  placeholder="Gender" /><br />
        <input v-model="profileForm.contact" placeholder="Contact" /><br />
        <button @click="updateProfile">Save</button>
        <button @click="showProfile = false">Cancel</button>
      </div>
    </div>

  </div>
</template>

<script>
export default {
  data() {
    return {
      patient:     {},
      departments: [],
      upcoming:    [],
      showProfile: false,
      profileForm: { name: '', age: '', gender: '', contact: '' },
      exportMsg: '',
      headers:     {
        'Authorization': `Bearer ${localStorage.getItem('token')}`,
        'Content-Type': 'application/json'
      }
    }
  },
  mounted() { this.fetchData() },
  methods: {
    async fetchData() {
      const res  = await fetch('http://127.0.0.1:5000/api/patient/dashboard', { headers: this.headers })
      const data = await res.json()
      this.patient     = data.patient
      this.departments = data.departments
      this.upcoming    = data.upcoming
    },

    async cancel(id) {
      await fetch(`http://127.0.0.1:5000/api/patient/appointments/${id}/cancel`, { method: 'POST', headers: this.headers })
      this.fetchData()
    },

    openProfile() {
      this.profileForm = {
        name:    this.patient.name,
        age:     this.patient.age,
        gender:  this.patient.gender,
        contact: this.patient.contact
      }
      this.showProfile = true
    },

    async updateProfile() {
      await fetch('http://127.0.0.1:5000/api/patient/profile', {
        method: 'PUT',
        headers: this.headers,
        body: JSON.stringify(this.profileForm)
      })
      this.showProfile = false
      this.fetchData()
    },

    async exportHistory() {
      const res  = await fetch('http://127.0.0.1:5000/api/patient/export', { method: 'POST', headers: this.headers })
      const data = await res.json()
      this.exportMsg = data.message
    },

    logout() { localStorage.clear(); this.$router.push('/') }
  }
}
</script>

<style scoped>
.overlay { position: fixed; top: 0; left: 0; width: 100%; height: 100%; background: rgba(0,0,0,0.5); display: flex; justify-content: center; align-items: center; }
.popup   { background: white; padding: 2rem; border-radius: 8px; min-width: 300px; }
</style>