<template>
  <div class="main">

    <!-- Page Header -->
    <div class="page-header">
      <div>
        <h1>🏥 Admin Dashboard</h1>
        <p style="color: var(--text-soft); margin-top: 0.25rem; font-size: 0.9rem;">Hospital overview and management</p>
      </div>
      <div style="display:flex; align-items:center; gap:0.75rem;">
        <input
          v-model="searchQuery"
          @keyup.enter="search"
          placeholder="Search doctors or patients..."
          style="width:220px; margin-bottom:0;"
        />
        <button @click="search">Search</button>
        <button v-if="showResults" class="btn-secondary" @click="clearSearch">✕ Clear</button>
        <button class="btn-danger" @click="logout">Logout</button>
      </div>
    </div>

    <!-- Stat Cards -->
    <div class="stats">
      <div class="stat-card">
        <h3>{{ doctors.length }}</h3>
        <p>Total Doctors</p>
      </div>
      <div class="stat-card">
        <h3>{{ patients.length }}</h3>
        <p>Total Patients</p>
      </div>
      <div class="stat-card">
        <h3>{{ upcoming.length }}</h3>
        <p>Upcoming Appointments</p>
      </div>
      <div class="stat-card">
        <h3>{{ previous.length }}</h3>
        <p>Previous Appointments</p>
      </div>
    </div>

    <!-- Search Results -->
    <div v-if="showResults" class="section">
      <div class="section-header">
        <h2>Results for "{{ searchQuery }}"</h2>
      </div>

      <p style="font-weight:700; margin-bottom:0.5rem; color: var(--text-mid);">Doctors</p>
      <table v-if="searchResults.doctors.length" style="margin-bottom:1.25rem;">
        <thead>
          <tr><th>Name</th><th>Department</th><th>Specialization</th></tr>
        </thead>
        <tbody>
          <tr v-for="d in searchResults.doctors" :key="d.id">
            <td><strong>{{ d.fullname }}</strong></td>
            <td>{{ d.department_name }}</td>
            <td>{{ d.specialization }}</td>
          </tr>
        </tbody>
      </table>
      <p v-else class="empty" style="margin-bottom:1rem;">No doctors found.</p>

      <p style="font-weight:700; margin-bottom:0.5rem; color: var(--text-mid);">Patients</p>
      <table v-if="searchResults.patients.length">
        <thead>
          <tr><th>Name</th><th>Contact</th></tr>
        </thead>
        <tbody>
          <tr v-for="p in searchResults.patients" :key="p.id">
            <td><strong>{{ p.name }}</strong></td>
            <td>{{ p.contact }}</td>
          </tr>
        </tbody>
      </table>
      <p v-else class="empty">No patients found.</p>
    </div>

    <!-- Doctors -->
    <div class="section">
      <div class="section-header">
        <h2>Doctors</h2>
        <button @click="$router.push('/admin/doctors')">Manage Doctors</button>
      </div>
      <table>
        <thead>
          <tr><th>Name</th><th>Department</th><th>Specialization</th><th>Experience</th><th>Status</th></tr>
        </thead>
        <tbody>
          <tr v-for="d in doctors" :key="d.id">
            <td><strong>{{ d.fullname }}</strong></td>
            <td>{{ d.department_name }}</td>
            <td>{{ d.specialization }}</td>
            <td>{{ d.experience }} yrs</td>
            <td>
              <span :style="{ color: d.is_blacklisted ? 'var(--pink-600)' : '#2eab7a', fontWeight: '700' }">
                {{ d.is_blacklisted ? 'Blacklisted' : 'Active' }}
              </span>
            </td>
          </tr>
          <tr v-if="doctors.length === 0">
            <td colspan="5" class="empty">No doctors found</td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- Patients -->
    <div class="section">
      <div class="section-header">
        <h2>Patients</h2>
        <button @click="$router.push('/admin/patients')">Manage Patients</button>
      </div>
      <table>
        <thead>
          <tr><th>Name</th><th>Age</th><th>Gender</th><th>Status</th></tr>
        </thead>
        <tbody>
          <tr v-for="p in patients" :key="p.id">
            <td><strong>{{ p.name }}</strong></td>
            <td>{{ p.age }}</td>
            <td>{{ p.gender }}</td>
            <td>
              <span :style="{ color: p.is_blacklisted ? 'var(--pink-600)' : '#2eab7a', fontWeight: '700' }">
                {{ p.is_blacklisted ? 'Blacklisted' : 'Active' }}
              </span>
            </td>
          </tr>
          <tr v-if="patients.length === 0">
            <td colspan="4" class="empty">No patients found</td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- Upcoming Appointments -->
    <div class="section">
      <div class="section-header">
        <h2>Upcoming Appointments</h2>
        <span style="color: var(--text-soft); font-size: 0.88rem;">{{ upcoming.length }} appointment(s)</span>
      </div>
      <table>
        <thead>
          <tr><th>Patient</th><th>Doctor</th><th>Date</th><th>Time</th></tr>
        </thead>
        <tbody>
          <tr v-for="a in upcoming" :key="a.id">
            <td><strong>{{ a.patient_name }}</strong></td>
            <td>{{ a.doctor_name }}</td>
            <td>{{ a.date }}</td>
            <td>{{ a.time }}</td>
          </tr>
          <tr v-if="upcoming.length === 0">
            <td colspan="4" class="empty">No upcoming appointments</td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- Previous Appointments -->
    <div class="section">
      <div class="section-header">
        <h2>Previous Appointments</h2>
        <span style="color: var(--text-soft); font-size: 0.88rem;">{{ previous.length }} record(s)</span>
      </div>
      <table>
        <thead>
          <tr><th>Patient</th><th>Doctor</th><th>Date</th><th>Time</th></tr>
        </thead>
        <tbody>
          <tr v-for="a in previous" :key="a.id">
            <td><strong>{{ a.patient_name }}</strong></td>
            <td>{{ a.doctor_name }}</td>
            <td>{{ a.date }}</td>
            <td>{{ a.time }}</td>
          </tr>
          <tr v-if="previous.length === 0">
            <td colspan="4" class="empty">No previous appointments</td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- Departments -->
    <div class="section">
      <div class="section-header">
        <h2>Departments</h2>
      </div>
      <table>
        <thead>
          <tr><th>Name</th><th>Description</th></tr>
        </thead>
        <tbody>
          <tr v-for="dept in departments" :key="dept.id">
            <td><strong>{{ dept.name }}</strong></td>
            <td>{{ dept.description }}</td>
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
      doctors:       [],
      patients:      [],
      upcoming:      [],
      previous:      [],
      departments:   [],
      searchQuery:   '',
      searchResults: { doctors: [], patients: [] },
      showResults:   false
    }
  },
  mounted() { this.fetchData() },
  methods: {
    async fetchData() {
      const token   = localStorage.getItem('token')
      const headers = { 'Authorization': `Bearer ${token}` }

      const dash = await fetch('http://127.0.0.1:5000/api/admin/dashboard', { headers })
      const data = await dash.json()
      this.doctors  = data.doctors
      this.patients = data.patients
      this.upcoming = data.upcoming
      this.previous = data.previous

      const dept       = await fetch('http://127.0.0.1:5000/api/admin/departments', { headers })
      this.departments = await dept.json()
    },

    async search() {
      if (!this.searchQuery.trim()) return
      const token = localStorage.getItem('token')
      const res   = await fetch(`http://127.0.0.1:5000/api/admin/search?q=${this.searchQuery}`, {
        headers: { 'Authorization': `Bearer ${token}` }
      })
      this.searchResults = await res.json()
      this.showResults   = true
    },

    clearSearch() {
      this.searchQuery   = ''
      this.searchResults = { doctors: [], patients: [] }
      this.showResults   = false
    },

    logout() {
      localStorage.clear()
      this.$router.push('/')
    }
  }
}
</script>