<template>
  <div class="main">

    <div class="page-header">
      <div>
        <h1>My Availability</h1>
        <p style="color: var(--text-soft); margin-top: 0.25rem; font-size: 0.9rem;">Manage your slots for the next 7 days</p>
      </div>
      <div style="display:flex; gap:0.75rem;">
        <button @click="showForm = true">+ Add Slot</button>
        <button class="btn-secondary" @click="$router.back()">Go Back</button>
      </div>
    </div>

    <div class="section">
      <div class="section-header">
        <h2>Your Slots</h2>
      </div>
      <table>
        <thead>
          <tr><th>Date</th><th>Time</th><th>Action</th></tr>
        </thead>
        <tbody>
          <tr v-for="slot in slots" :key="slot.id">
            <td>{{ slot.date }}</td>
            <td>{{ slot.slot }}</td>
            <td><button class="btn-danger" @click="deleteSlot(slot.id)">Delete</button></td>
          </tr>
          <tr v-if="slots.length === 0">
            <td colspan="3" class="empty">No slots added yet</td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- Add Slot Modal -->
    <div v-if="showForm" class="modal-overlay">
      <div class="modal">
        <h3>Add New Slot</h3>
        <input type="date" v-model="form.date" />
        <input type="text" v-model="form.slot" placeholder="e.g. 08:00 - 12:00" />
        <div class="modal-actions">
          <button @click="addSlot">Save</button>
          <button class="btn-secondary" @click="showForm = false">Cancel</button>
        </div>
      </div>
    </div>

  </div>
</template>

<script>
export default {
  data() {
    return {
      slots: [],
      showForm: false,
      form: { date: '', slot: '' },
      headers: {
        'Authorization': `Bearer ${localStorage.getItem('token')}`,
        'Content-Type': 'application/json'
      }
    }
  },
  mounted() { this.fetchSlots() },
  methods: {
    async fetchSlots() {
      const res  = await fetch('http://127.0.0.1:5000/api/doctor/availability', { headers: this.headers })
      const data = await res.json()
      this.slots = data.slots
    },
    async addSlot() {
      await fetch('http://127.0.0.1:5000/api/doctor/availability', {
        method: 'POST',
        headers: this.headers,
        body: JSON.stringify(this.form)
      })
      this.showForm = false
      this.form = { date: '', slot: '' }
      this.fetchSlots()
    },
    async deleteSlot(id) {
      await fetch(`http://127.0.0.1:5000/api/doctor/availability/${id}`, {
        method: 'DELETE',
        headers: this.headers
      })
      this.fetchSlots()
    }
  }
}
</script>