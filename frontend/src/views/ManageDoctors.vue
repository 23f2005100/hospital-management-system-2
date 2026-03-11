<template>
  <div class="main">

    <div class="page-header">
      <div>
        <h1>Manage Doctors</h1>
        <p style="color: var(--text-soft); margin-top: 0.25rem; font-size: 0.9rem;">Add, edit, blacklist or remove doctors</p>
      </div>
      <div style="display:flex; gap:0.75rem;">
        <button @click="showForm = true">+ Add Doctor</button>
        <button class="btn-secondary" @click="$router.push('/admin/dashboard')">Back</button>
      </div>
    </div>

    <div class="section">
      <div class="section-header">
        <h2>All Doctors</h2>
        <span style="color: var(--text-soft); font-size: 0.88rem;">{{ doctors.length }} doctor(s)</span>
      </div>
      <table>
        <thead>
          <tr>
            <th>Name</th>
            <th>Specialization</th>
            <th>Qualification</th>
            <th>Experience</th>
            <th>Department</th>
            <th>Status</th>
            <th>Actions</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="d in doctors" :key="d.id">
            <td><strong>{{ d.fullname }}</strong></td>
            <td>{{ d.specialization }}</td>
            <td>{{ d.qualification }}</td>
            <td>{{ d.experience }} yrs</td>
            <td>{{ d.department_name }}</td>
            <td>
              <span :style="{ color: d.is_blacklisted ? 'var(--pink-600)' : '#2eab7a', fontWeight: '700' }">
                {{ d.is_blacklisted ? 'Blacklisted' : 'Active' }}
              </span>
            </td>
            <td>
              <div style="display:flex; gap:0.5rem;">
                <button class="btn-edit" @click="openEdit(d)">Edit</button>
                <button :class="d.is_blacklisted ? 'btn-success' : 'btn-secondary'" @click="toggleBlacklist(d.id, d.is_blacklisted)">
                  {{ d.is_blacklisted ? 'Unblacklist' : 'Blacklist' }}
                </button>
                <button class="btn-danger" @click="deleteDoctor(d.id)">Delete</button>
              </div>
            </td>
          </tr>
          <tr v-if="doctors.length === 0">
            <td colspan="7" class="empty">No doctors found.</td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- Add / Edit Modal -->
    <div v-if="showForm || showEdit" class="modal-overlay">
      <div class="modal" style="width:500px; max-height:90vh; overflow-y:auto;">
        <h3>{{ showEdit ? ' Edit Doctor' : ' Add Doctor' }}</h3>

        <input v-model="form.fullname"       placeholder="Full Name" />

        <template v-if="!showEdit">
          <input v-model="form.email"        placeholder="Email" />
          <input v-model="form.password"     placeholder="Password" type="password" />
        </template>

        <input v-model="form.specialization" placeholder="Specialization" />
        <input v-model="form.qualification"  placeholder="Qualification" />
        <input v-model="form.experience"     placeholder="Experience (years)" />
        <input v-model="form.description"    placeholder="Profile Description" />
        <input v-model="form.contact"        placeholder="Contact Number" />

        <select v-model="form.department_id">
          <option disabled value="">Select Department</option>
          <option v-for="dept in departments" :key="dept.id" :value="dept.id">{{ dept.name }}</option>
        </select>

        <p v-if="error" class="error-msg">{{ error }}</p>

        <div class="modal-actions">
          <button @click="showEdit ? updateDoctor() : addDoctor()">Save</button>
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
      doctors:     [],
      departments: [],
      showForm:    false,
      showEdit:    false,
      editingId:   null,
      error:       '',
      form: { fullname: '', email: '', password: '', specialization: '', qualification: '', experience: '', description: '', contact: '', department_id: '' },
      headers: { 'Authorization': `Bearer ${localStorage.getItem('token')}`, 'Content-Type': 'application/json' }
    }
  },
  mounted() { this.fetchData() },
  methods: {
    async fetchData() {
      const docRes     = await fetch('http://127.0.0.1:5000/api/admin/doctors', { headers: this.headers })
      const data       = await docRes.json()
      this.doctors     = data.result
      const deptRes    = await fetch('http://127.0.0.1:5000/api/admin/departments', { headers: this.headers })
      this.departments = await deptRes.json()
    },

    openEdit(doctor) {
      this.editingId           = doctor.id
      this.form.fullname       = doctor.fullname
      this.form.specialization = doctor.specialization
      this.form.qualification  = doctor.qualification
      this.form.experience     = doctor.experience
      this.form.description    = doctor.description
      this.form.contact        = doctor.contact
      this.form.department_id  = doctor.department_id
      this.showEdit            = true
    },

    closeForm() {
      this.showForm = false
      this.showEdit = false
      this.error    = ''
      this.form     = { fullname: '', email: '', password: '', specialization: '', qualification: '', experience: '', description: '', contact: '', department_id: '' }
    },

    async addDoctor() {
      const res  = await fetch('http://127.0.0.1:5000/api/admin/doctors', { method: 'POST', headers: this.headers, body: JSON.stringify(this.form) })
      const data = await res.json()
      if (data.error) { this.error = data.error; return }
      this.closeForm()
      this.fetchData()
    },

    async updateDoctor() {
      const res  = await fetch(`http://127.0.0.1:5000/api/admin/doctors/${this.editingId}`, { method: 'PUT', headers: this.headers, body: JSON.stringify(this.form) })
      const data = await res.json()
      if (data.error) { this.error = data.error; return }
      this.closeForm()
      this.fetchData()
    },

    async toggleBlacklist(id, isBlacklisted) {
      const action = isBlacklisted ? 'unblacklist' : 'blacklist'
      await fetch(`http://127.0.0.1:5000/api/admin/${action}/doctor/${id}`, { method: 'POST', headers: this.headers })
      this.fetchData()
    },

    async deleteDoctor(id) {
      if (!confirm('Are you sure you want to delete this doctor?')) return
      await fetch(`http://127.0.0.1:5000/api/admin/dashboard/delete/doctor/${id}`, { method: 'DELETE', headers: this.headers })
      this.fetchData()
    }
  }
}
</script>