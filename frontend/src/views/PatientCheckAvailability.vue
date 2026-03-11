<template>
  <div class="main">

    <div class="page-header">
      <div>
        <h1>Book Appointment</h1>
        <p style="color: var(--text-soft); margin-top: 0.25rem; font-size: 0.9rem;">Select an available slot to book</p>
      </div>
      <button class="btn-secondary" @click="$router.back()">Go Back</button>
    </div>

    <p v-if="message" :class="message.includes('booked') ? 'success-msg' : 'error-msg'" style="margin-bottom:1rem;">
      {{ message }}
    </p>

    <div class="section">
      <div class="section-header">
        <h2>Available Slots</h2>
        <span v-if="selectedSlot" class="badge booked">1 slot selected</span>
      </div>
      <table>
        <thead>
          <tr><th>Date</th><th>Time</th><th>Select</th></tr>
        </thead>
        <tbody>
          <tr v-for="slot in slots" :key="slot.id">
            <td>{{ slot.date }}</td>
            <td>{{ slot.slot }}</td>
            <td>
              <button
                @click="selectedSlot = slot.id"
                :class="selectedSlot === slot.id ? 'btn-success' : 'btn-secondary'"
              >
                {{ selectedSlot === slot.id ? '✓ Selected' : 'Select' }}
              </button>
            </td>
          </tr>
          <tr v-if="slots.length === 0">
            <td colspan="3" class="empty">No slots available</td>
          </tr>
        </tbody>
      </table>

      <div style="margin-top:1.25rem;">
        <button @click="book" :disabled="!selectedSlot" :style="!selectedSlot ? 'opacity:0.5; cursor:not-allowed;' : ''">
          Confirm Booking
        </button>
      </div>
    </div>

  </div>
</template>

<script>
export default {
  data() {
    return {
      slots:        [],
      selectedSlot: null,
      message:      '',
      headers:      {
        'Authorization': `Bearer ${localStorage.getItem('token')}`,
        'Content-Type': 'application/json'
      }
    }
  },
  mounted() { this.fetchData() },
  methods: {
    async fetchData() {
      const id   = this.$route.params.id
      const res  = await fetch(`http://127.0.0.1:5000/api/patient/doctors/${id}`, { headers: this.headers })
      const data = await res.json()
      this.slots = data.availability
    },
    async book() {
      const res  = await fetch(`http://127.0.0.1:5000/api/patient/book/${this.selectedSlot}`, { method: 'POST', headers: this.headers })
      const data = await res.json()
      this.message      = data.message || data.error
      this.selectedSlot = null
      this.fetchData()
    }
  }
}
</script>