<template>
  <div>
    <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:1rem;">
      <h1>Manage Doctors</h1>
      <div style="display:flex; gap:8px;">
        <button @click="showForm = true">+ Add Doctor</button>
        <button @click="$router.push('/admin/dashboard')">Back</button>
      </div>
    </div>

    <table border="1">
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
          <td>{{ d.fullname }}</td>
          <td>{{ d.specialization }}</td>
          <td>{{ d.qualification }}</td>
          <td>{{ d.experience }} yrs</td>
          <td>{{ d.department_name }}</td>
          <td>{{ d.is_blacklisted ? 'Blacklisted' : 'Active' }}</td>
          <td>
            <button @click="openEdit(d)">Edit</button>
            <button @click="toggleBlacklist(d.id, d.is_blacklisted)">{{ d.is_blacklisted ? 'Unblacklist' : 'Blacklist' }}</button>
            <button @click="deleteDoctor(d.id)">Delete</button>
          </td>
        </tr>
        <tr v-if="doctors.length === 0">
          <td colspan="7">No doctors found.</td>
        </tr>
      </tbody>
    </table>

    <!-- Add / Edit Popup -->
    <div v-if="showForm || showEdit" class="overlay">
      <div class="popup">
        <h3>{{ showEdit ? 'Edit Doctor' : 'Add Doctor' }}</h3>

        <label>Full Name</label><br />
        <input v-model="form.fullname" placeholder="e.g. Dr. John Smith" /><br /><br />

        <template v-if="!showEdit">
          <label>Email</label><br />
          <input v-model="form.email" placeholder="doctor@email.com" /><br /><br />

          <label>Password</label><br />
          <input v-model="form.password" type="password" placeholder="Password" /><br /><br />
        </template>

        <label>Specialization</label><br />
        <input v-model="form.specialization" placeholder="e.g. Cardiologist" /><br /><br />

        <label>Qualification</label><br />
        <input v-model="form.qualification" placeholder="e.g. MBBS, MD" /><br /><br />

        <label>Experience (years)</label><br />
        <input v-model="form.experience" placeholder="e.g. 5" /><br /><br />

        <label>Description</label><br />
        <input v-model="form.description" placeholder="Brief profile description" /><br /><br />

        <label>Contact</label><br />
        <input v-model="form.contact" placeholder="Phone number" /><br /><br />

        <label>Department</label><br />
        <select v-model="form.department_id">
          <option disabled value="">Select Department</option>
          <option v-for="dept in departments" :key="dept.id" :value="dept.id">{{ dept.name }}</option>
        </select><br /><br />

        <p v-if="error" style="color:red">{{ error }}</p>
        <button @click="showEdit ? updateDoctor() : addDoctor()">Save</button>
        <button @click="closeForm">Cancel</button>
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
      headers:     { 'Authorization': `Bearer ${localStorage.getItem('token')}`, 'Content-Type': 'application/json' }
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

<style scoped>
.overlay { position: fixed; top: 0; left: 0; width: 100%; height: 100%; background: rgba(0,0,0,0.5); display: flex; justify-content: center; align-items: center; }
.popup   { background: white; padding: 2rem; border-radius: 8px; min-width: 320px; max-height: 90vh; overflow-y: auto; }
input, select { width: 100%; padding: 6px; box-sizing: border-box; }
</style>