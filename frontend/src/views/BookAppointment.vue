<template>
  <div class="layout">

    <aside class="sidebar">
      <h2>🏥 HMS</h2>
      <p class="welcome">Hi, {{ name }}</p>
      <nav>
        <a @click="$router.push('/patient/dashboard')" :class="{ active: $route.path === '/patient/dashboard' }">🏠 Dashboard</a>
        <a @click="$router.push('/patient/book')"      :class="{ active: $route.path === '/patient/book'      }">📅 Book Appointment</a>
        <a @click="$router.push('/patient/history')"   :class="{ active: $route.path === '/patient/history'   }">📋 History</a>
        <a @click="logout" class="logout">🚪 Logout</a>
      </nav>
    </aside>

    <main class="main">
      <div class="page-header"><h1>Book Appointment</h1></div>

      <!-- Step 1: Search doctors -->
      <div class="section">
        <div class="section-header"><h2>Search Doctors</h2></div>
        <div style="display:flex; gap:0.75rem; margin-bottom:1rem">
          <input v-model="search" class="search-bar" style="margin:0" placeholder="🔍 Search by name or specialization..." />
          <button @click="searchDoctors">Search</button>
        </div>

        <table v-if="doctors.length > 0">
          <thead>
            <tr><th>Name</th><th>Specialization</th><th>Department</th><th>Action</th></tr>
          </thead>
          <tbody>
            <tr v-for="d in doctors" :key="d.id">
              <td>{{ d.fullname }}</td>
              <td>{{ d.specialization }}</td>
              <td>{{ d.department_id }}</td>
              <td><button @click="selectDoctor(d)">View Slots</button></td>
            </tr>
          </tbody>
        </table>
        <div v-else-if="searched" class="empty">No doctors found</div>
      </div>

      <!-- Step 2: View slots for selected doctor -->
      <div class="section" v-if="selectedDoctor">
        <div class="section-header">
          <h2>Available Slots — Dr. {{ selectedDoctor.fullname }}</h2>
        </div>

        <div v-if="slots.length === 0" class="empty">No available slots for this doctor</div>

        <table v-else>
          <thead>
            <tr><th>Date</th><th>Time Slot</th><th>Action</th></tr>
          </thead>
          <tbody>
            <tr v-for="s in slots" :key="s.id">
              <td>{{ s.date }}</td>
              <td>{{ s.slot }}</td>
              <td><button class="btn-success" @click="book(s.id)">📅 Book</button></td>
            </tr>
          </tbody>
        </table>

        <div v-if="bookMsg" class="success-msg" style="margin-top:1rem">{{ bookMsg }}</div>
        <div v-if="bookError" class="error-msg"   style="margin-top:1rem">{{ bookError }}</div>
      </div>

    </main>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'

const router         = useRouter()
const search         = ref('')
const doctors        = ref([])
const searched       = ref(false)
const selectedDoctor = ref(null)
const slots          = ref([])
const bookMsg        = ref('')
const bookError      = ref('')
const name           = localStorage.getItem('name') || 'Patient'

const token   = localStorage.getItem('token')
const headers = { 'Authorization': `Bearer ${token}`, 'Content-Type': 'application/json' }

async function searchDoctors() {
  searched.value = false
  const res    = await fetch(`http://127.0.0.1:5000/api/patient/search?q=${search.value}`, { headers })
  doctors.value  = await res.json()
  searched.value = true
  selectedDoctor.value = null
  slots.value = []
}

async function selectDoctor(doctor) {
  selectedDoctor.value = doctor
  bookMsg.value   = ''
  bookError.value = ''
  const res  = await fetch(`http://127.0.0.1:5000/api/patient/doctors/${doctor.id}`, { headers })
  const data = await res.json()
  slots.value = data.availability || []
}

async function book(slotId) {
  bookMsg.value   = ''
  bookError.value = ''
  const res  = await fetch(`http://127.0.0.1:5000/api/patient/book/${slotId}`, { method: 'POST', headers })
  const data = await res.json()
  if (!res.ok) { bookError.value = data.error || 'Booking failed'; return }
  bookMsg.value = '✅ Appointment booked successfully!'
  // refresh slots
  selectDoctor(selectedDoctor.value)
}

function logout() {
  localStorage.clear()
  router.push('/')
}
</script>