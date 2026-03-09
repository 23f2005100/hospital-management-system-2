<template>
  <div>
    <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:1rem;">
      <h1>Manage Patients</h1>
      <button @click="$router.push('/admin/dashboard')">Back</button>
    </div>

    <table border="1">
      <thead>
        <tr>
          <th>Name</th>
          <th>Contact</th>
          <th>Gender</th>
          <th>Age</th>
          <th>Status</th>
          <th>Actions</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="p in patients" :key="p.id">
          <td>{{ p.name }}</td>
          <td>{{ p.contact }}</td>
          <td>{{ p.gender }}</td>
          <td>{{ p.age }}</td>
          <td>{{ p.is_blacklisted ? 'Blacklisted' : 'Active' }}</td>
          <td>
            <button @click="openEdit(p)">Edit</button>
            <button @click="toggleBlacklist(p.id, p.is_blacklisted)">{{ p.is_blacklisted ? 'Unblacklist' : 'Blacklist' }}</button>
            <button @click="deletePatient(p.id)">Delete</button>
          </td>
        </tr>
        <tr v-if="patients.length === 0">
          <td colspan="6">No patients found.</td>
        </tr>
      </tbody>
    </table>

    <!-- Edit Popup -->
    <div v-if="showEdit" class="overlay">
      <div class="popup">
        <h3>Edit Patient</h3>

        <label>Name</label><br />
        <input v-model="form.name" placeholder="Full name" /><br /><br />

        <label>Contact</label><br />
        <input v-model="form.contact" placeholder="Phone number" /><br /><br />

        <label>Gender</label><br />
        <select v-model="form.gender">
          <option disabled value="">Select Gender</option>
          <option value="Male">Male</option>
          <option value="Female">Female</option>
          <option value="Other">Other</option>
        </select><br /><br />

        <label>Age</label><br />
        <input v-model="form.age" placeholder="e.g. 30" /><br /><br />

        <p v-if="error" style="color:red">{{ error }}</p>
        <button @click="updatePatient">Save</button>
        <button @click="closeForm">Cancel</button>
      </div>
    </div>

  </div>
</template>

<script>
export default {
  data() {
    return {
      patients:  [],
      showEdit:  false,
      editingId: null,
      error:     '',
      form:      { name: '', contact: '', gender: '', age: '' },
      headers:   { 'Authorization': `Bearer ${localStorage.getItem('token')}`, 'Content-Type': 'application/json' }
    }
  },
  mounted() { this.fetchData() },
  methods: {
    async fetchData() {
      const res      = await fetch('http://127.0.0.1:5000/api/admin/patients', { headers: this.headers })
      const data     = await res.json()
      this.patients  = data.result
    },

    openEdit(patient) {
      this.editingId    = patient.id
      this.form.name    = patient.name
      this.form.contact = patient.contact
      this.form.gender  = patient.gender
      this.form.age     = patient.age
      this.showEdit     = true
    },

    closeForm() {
      this.showEdit = false
      this.error    = ''
      this.form     = { name: '', contact: '', gender: '', age: '' }
    },

    async updatePatient() {
      const res  = await fetch(`http://127.0.0.1:5000/api/admin/patients/${this.editingId}`, {
        method:  'PUT',
        headers: this.headers,
        body:    JSON.stringify(this.form)
      })
      const data = await res.json()
      if (data.error) { this.error = data.error; return }
      this.closeForm()
      this.fetchData()
    },

    async toggleBlacklist(id, isBlacklisted) {
      const action = isBlacklisted ? 'unblacklist' : 'blacklist'
      await fetch(`http://127.0.0.1:5000/api/admin/${action}/patient/${id}`, { method: 'POST', headers: this.headers })
      this.fetchData()
    },

    async deletePatient(id) {
      if (!confirm('Are you sure you want to delete this patient?')) return
      await fetch(`http://127.0.0.1:5000/api/admin/dashboard/delete/patient/${id}`, { method: 'DELETE', headers: this.headers })
      this.fetchData()
    }
  }
}
</script>

<style scoped>
.overlay { position: fixed; top: 0; left: 0; width: 100%; height: 100%; background: rgba(0,0,0,0.5); display: flex; justify-content: center; align-items: center; }
.popup   { background: white; padding: 2rem; border-radius: 8px; min-width: 320px; max-height: 90vh; overflow-y: auto; }
input, select { width: 100%; padding: 6px; box-sizing: border-box; }
</style>