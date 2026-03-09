<template>
<div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:1rem;">
  
  <!-- Left: title -->
  <h1>Admin Dashboard</h1>

  <!-- Right: search + logout -->
  <div style="display:flex; align-items:center; gap:8px;">
    <input 
      v-model="searchQuery"
      @keyup.enter="search"
      placeholder="Search..."
      style="width:160px; padding:4px 8px; font-size:13px; border:1px solid #ccc; border-radius:4px;"
    />
    <button @click="search">Search</button>
    <button v-if="showResults" @click="clearSearch">✕</button>
    <button @click="logout" style="background:red; color:white; border:none; padding:4px 10px; border-radius:4px; cursor:pointer;">Logout</button>
  </div>

</div>

<!-- Summary Cards -->
<div style="display:flex; gap:1rem; margin-bottom:1.5rem; margin-top:1rem;">
  <div style="border:1px solid #ccc; padding:1rem; border-radius:8px; flex:1; text-align:center;">
    <h2>{{ doctors.length }}</h2>
    <p>Total Doctors</p>
  </div>
  <div style="border:1px solid #ccc; padding:1rem; border-radius:8px; flex:1; text-align:center;">
    <h2>{{ patients.length }}</h2>
    <p>Total Patients</p>
  </div>
  <div style="border:1px solid #ccc; padding:1rem; border-radius:8px; flex:1; text-align:center;">
    <h2>{{ upcoming.length }}</h2>
    <p>Upcoming Appointments</p>
  </div>
  <div style="border:1px solid #ccc; padding:1rem; border-radius:8px; flex:1; text-align:center;">
    <h2>{{ previous.length }}</h2>
    <p>Previous Appointments</p>
  </div>
</div>

    <!-- Search Results -->
    <div v-if="showResults" class="card mb-4">
      <div class="card-body">
        <h5 class="card-title">Results for "{{ searchQuery }}"</h5>

        <p class="fw-bold mt-3">Doctors</p>
        <table class="table table-bordered table-sm" v-if="searchResults.doctors.length">
          <thead class="table-light">
            <tr><th>Name</th><th>Department</th><th>Specialization</th></tr>
          </thead>
          <tbody>
            <tr v-for="d in searchResults.doctors" :key="d.id">
              <td>{{ d.fullname }}</td>
              <td>{{ d.department_name }}</td>
              <td>{{ d.specialization }}</td>
            </tr>
          </tbody>
        </table>
        <p v-else class="text-muted">No doctors found.</p>

        <p class="fw-bold mt-3">Patients</p>
        <table class="table table-bordered table-sm" v-if="searchResults.patients.length">
          <thead class="table-light">
            <tr><th>Name</th><th>Contact</th></tr>
          </thead>
          <tbody>
            <tr v-for="p in searchResults.patients" :key="p.id">
              <td>{{ p.name }}</td>
              <td>{{ p.contact }}</td>
            </tr>
          </tbody>
        </table>
        <p v-else class="text-muted">No patients found.</p>
      </div>
    </div>

    <!-- Doctors -->
    <div class="d-flex justify-content-between align-items-center mb-2">
      <h4>Doctors</h4>
      <button class="btn btn-sm btn-outline-primary" @click="$router.push('/admin/doctors')">Manage Doctors</button>
    </div>
    <table class="table table-bordered table-sm mb-4">
      <tbody>
        <tr v-for="d in doctors" :key="d.id">
          <td>{{ d.fullname }}</td>
          <td>{{ d.department_name }}</td>
        </tr>
      </tbody>
    </table>

    <!-- Patients -->
    <div class="d-flex justify-content-between align-items-center mb-2">
      <h4>Patients</h4>
      <button class="btn btn-sm btn-outline-primary" @click="$router.push('/admin/patients')">Manage Patients</button>
    </div>
    <table class="table table-bordered table-sm mb-4">
      <tbody>
        <tr v-for="p in patients" :key="p.id">
          <td>{{ p.name }}</td>
          <td>{{ p.age  }}</td>
          <td> {{  p.contact }}</td>
        </tr>
      </tbody>
    </table>

    <!-- Upcoming Appointments -->
    <h4 class="mb-2">Upcoming Appointments</h4>
    <table class="table table-bordered table-sm mb-4">
      <thead class="table-light">
        <tr><th>Patient</th><th>Doctor</th><th>Date</th><th>Time</th></tr>
      </thead>
      <tbody>
        <tr v-for="a in upcoming" :key="a.id">
          <td>{{ a.patient_name }}</td>
          <td>{{ a.doctor_name }}</td>
          <td>{{ a.date }}</td>
          <td>{{ a.time }}</td>
        </tr>
        <tr v-if="upcoming.length === 0">
          <td colspan="4" class="text-muted text-center">No upcoming appointments</td>
        </tr>
      </tbody>
    </table>

    <!-- Previous Appointments -->
    <h4 class="mb-2">Previous Appointments</h4>
    <table class="table table-bordered table-sm mb-4">
      <thead class="table-light">
        <tr><th>Patient</th><th>Doctor</th><th>Date</th><th>Time</th></tr>
      </thead>
      <tbody>
        <tr v-for="a in previous" :key="a.id">
          <td>{{ a.patient_name }}</td>
          <td>{{ a.doctor_name }}</td>
          <td>{{ a.date }}</td>
          <td>{{ a.time }}</td>
        </tr>
        <tr v-if="previous.length === 0">
          <td colspan="4" class="text-muted text-center">No previous appointments</td>
        </tr>
      </tbody>
    </table>

    <!-- Departments -->
    <h4 class="mb-2">Departments</h4>
    <table class="table table-bordered table-sm mb-4">
      <tbody>
        <tr v-for="d in departments" :key="d.id">
          <td>{{ d.name }}</td>
          <td>{{ d.description }}</td>
        </tr>
      </tbody>
    </table>
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