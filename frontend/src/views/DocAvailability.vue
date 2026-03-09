<template>
  <div>
    <h2>My Availability (Next 7 Days)</h2>
    <button @click="$router.back()">Go Back</button>

    <table border="1">
      <thead>
        <tr>
          <th>Date</th>
          <th>Time</th>
          <th>Action</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="slot in slots" :key="slot.id">
          <td>{{ slot.date }}</td>
          <td>{{ slot.slot }}</td>
          <td><button @click="deleteSlot(slot.id)">Delete</button></td>
        </tr>
      </tbody>
    </table>

    <button @click="showForm = true">+ Add Slot</button>

    <div v-if="showForm">
      <h3>Add New Slot</h3>
      <input type="date" v-model="form.date" />
      <input type="text" v-model="form.slot" placeholder="e.g. 08:00 - 12:00" />
      <button @click="addSlot">Save</button>
      <button @click="showForm = false">Cancel</button>
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
    },
  }
}
</script>