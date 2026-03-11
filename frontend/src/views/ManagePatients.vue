<template>
  <div class="main">

    <div class="page-header">
      <div>
        <h1>Manage Patients</h1>
        <p style="color: var(--text-soft); margin-top: 0.25rem; font-size: 0.9rem;">Edit, blacklist or remove patients</p>
      </div>
      <button class="btn-secondary" @click="$router.push('/admin/dashboard')">Back</button>
    </div>

    <div class="section">
      <div class="section-header">
        <h2>All Patients</h2>
        <span style="color: var(--text-soft); font-size: 0.88rem;">{{ patients.length }} patient(s)</span>
      </div>
      <table>
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
            <td><strong>{{ p.name }}</strong></td>
            <td>{{ p.contact }}</td>
            <td>{{ p.gender }}</td>
            <td>{{ p.age }}</td>
            <td>
              <span :style="{ color: p.is_blacklisted ? 'var(--pink-600)' : '#2eab7a', fontWeight: '700' }">
                {{ p.is_blacklisted ? 'Blacklisted' : 'Active' }}
              </span>
            </td>
            <td>
              <div style="display:flex; gap:0.5rem;">
                <button class="btn-edit" @click="openEdit(p)">Edit</button>
                <button :class="p.is_blacklisted ? 'btn-success' : 'btn-secondary'" @click="toggleBlacklist(p.id, p.is_blacklisted)">
                  {{ p.is_blacklisted ? 'Unblacklist' : 'Blacklist' }}
                </button>
                <button class="btn-danger" @click="deletePatient(p.id)">Delete</button>
              </div>
            </td>
          </tr>
          <tr v-if="patients.length === 0">
            <td colspan="6" class="empty">No patients found.</td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- Edit Modal -->
    <div v-if="showEdit" class="modal-overlay">
      <div class="modal">
        <h3>Edit Patient</h3>
        <input v-model="form.name"    placeholder="Full Name" />
        <input v-model="form.contact" placeholder="Contact Number" />
        <select v-model="form.gender">
          <option disabled value="">Select Gender</option>
          <option value="Male">Male</option>
          <option value="Female">Female</option>
          <option value="Other">Other</option>
        </select>
        <input v-model="form.age" placeholder="Age" />
        <p v-if="error" class="error-msg">{{ error }}</p>
        <div class="modal-actions">
          <button @click="updatePatient">Save</button>
          <button class="btn-secondary" @click="closeForm">Cancel</button>
        </div>
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
      const res     = await fetch('http://127.0.0.1:5000/api/admin/patients', { headers: this.headers })
      const data    = await res.json()
      this.patients = data.result
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
        method: 'PUT', headers: this.headers, body: JSON.stringify(this.form)
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