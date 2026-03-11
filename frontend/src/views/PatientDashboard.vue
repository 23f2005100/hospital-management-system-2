<template>
  <div class="main">

    <!-- Page Header -->
    <div class="page-header">
      <div>
        <h1>👋 Welcome, {{ patient.name }}</h1>
        <p style="color: var(--text-soft); margin-top: 0.25rem; font-size: 0.9rem;">Manage your appointments and health records</p>
      </div>
      <div style="display:flex; gap:0.75rem; align-items:center;">
        <button class="btn-secondary" @click="openProfile">Edit Profile</button>
        <button class="btn-secondary" @click="$router.push('/patient/history')">History</button>
        <button class="btn-secondary" @click="exportHistory">Export History</button>
        <button class="btn-danger" @click="logout">Logout</button>
      </div>
    </div>

    <p v-if="exportMsg" class="success-msg" style="margin-bottom:1rem;">{{ exportMsg }}</p>

    <!-- Search -->
    <div class="section" style="margin-bottom:1.5rem;">
      <div style="display:flex; gap:0.75rem; align-items:center;">
        <input
          v-model="searchQuery"
          @keyup.enter="search"
          placeholder="Search doctor by name, specialization or department..."
          style="margin-bottom:0;"
        />
        <button @click="search" style="white-space:nowrap;">Search</button>
        <button v-if="showResults" class="btn-secondary" @click="clearSearch">✕ Clear</button>
      </div>

      <!-- Search Results -->
      <div v-if="showResults" style="margin-top:1.25rem;">
        <h2 style="margin-bottom:0.75rem;">Results for "{{ searchQuery }}"</h2>
        <table v-if="searchResults.doctors.length">
          <thead>
            <tr><th>Name</th><th>Department</th><th>Specialization</th><th>Actions</th></tr>
          </thead>
          <tbody>
            <tr v-for="d in searchResults.doctors" :key="d.id">
              <td>{{ d.fullname }}</td>
              <td>{{ d.department_name }}</td>
              <td>{{ d.specialization }}</td>
              <td style="display:flex; gap:0.5rem;">
                <button @click="$router.push(`/patient/doctor/${d.id}`)">View</button>
                <button class="btn-success" @click="$router.push(`/patient/doctor/${d.id}/availability`)">Book</button>
              </td>
            </tr>
          </tbody>
        </table>
        <p class="empty" v-else>No doctors found.</p>
      </div>
    </div>

    <!-- Departments -->
    <div class="section">
      <div class="section-header">
        <h2>Departments</h2>
      </div>
      <table>
        <thead>
          <tr><th>Department</th><th>Doctors</th><th>Action</th></tr>
        </thead>
        <tbody>
          <tr v-for="d in departments" :key="d.id">
            <td><strong>{{ d.name }}</strong></td>
            <td>{{ d.doctor_count }} doctor(s)</td>
            <td><button @click="$router.push(`/patient/department/${d.id}`)">View Details</button></td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- Upcoming Appointments -->
    <div class="section">
      <div class="section-header">
        <h2>Upcoming Appointments</h2>
      </div>
      <table>
        <thead>
          <tr><th>Doctor</th><th>Department</th><th>Date</th><th>Time</th><th>Action</th></tr>
        </thead>
        <tbody>
          <tr v-for="a in upcoming" :key="a.id">
            <td><strong>{{ a.doctor_name }}</strong></td>
            <td>{{ a.department }}</td>
            <td>{{ a.date }}</td>
            <td>{{ a.time }}</td>
            <td><button class="btn-danger" @click="cancel(a.id)">Cancel</button></td>
          </tr>
          <tr v-if="upcoming.length === 0">
            <td colspan="5" class="empty">No upcoming appointments</td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- Edit Profile Modal -->
    <div v-if="showProfile" class="modal-overlay">
      <div class="modal">
        <h3>Edit Profile</h3>
        <input v-model="profileForm.name"     placeholder="Full Name" />
        <input v-model="profileForm.email"    placeholder="Email" />
        <input v-model="profileForm.password" placeholder="New Password (leave blank to keep)" type="password" />
        <input v-model="profileForm.age"      placeholder="Age" />
        <input v-model="profileForm.gender"   placeholder="Gender" />
        <input v-model="profileForm.contact"  placeholder="Contact" />
        <div class="modal-actions">
          <button @click="updateProfile">Save Changes</button>
          <button class="btn-secondary" @click="showProfile = false">Cancel</button>
        </div>
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
      profileForm: { name: '', email: '', password:'', age: '', gender: '', contact: '' },
      exportMsg: '',
      searchQuery:   '',
      searchResults: { doctors: [] },
      showResults:   false,
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

    async search() {
    if (!this.searchQuery.trim()) return
    const res  = await fetch(`http://127.0.0.1:5000/api/patient/search?q=${this.searchQuery}`, { headers: this.headers })
    const data = await res.json()
    this.searchResults = data
    this.showResults   = true
    },

    clearSearch() {
        this.searchQuery   = ''
        this.searchResults = { doctors: [] }
        this.showResults   = false
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