<template>
  <div>
    <h2>Doctor's Availability</h2>
    <button @click="$router.back()">Go Back</button>

    <table border="1">
      <thead>
        <tr>
          <th>Date</th>
          <th>Time</th>
          <th>Select</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="slot in slots" :key="slot.id">
          <td>{{ slot.date }}</td>
          <td>{{ slot.slot }}</td>
          <td>
            <button
              @click="selectedSlot = slot.id"
              :style="selectedSlot === slot.id ? 'background:green; color:white' : ''"
            >
              {{ selectedSlot === slot.id ? 'Selected' : 'Select' }}
            </button>
          </td>
        </tr>
        <tr v-if="slots.length === 0">
          <td colspan="3">No slots available</td>
        </tr>
      </tbody>
    </table>

    <br />
    <button @click="book" :disabled="!selectedSlot">Book</button>
    <p v-if="message">{{ message }}</p>
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