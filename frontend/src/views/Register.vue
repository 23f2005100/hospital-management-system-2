<template>
  <div class="auth-container">
    <div class="auth-card">
      <h2>🏥 HMS</h2>
      <h3>Patient Register</h3>

      <div v-if="error"   class="error-msg">{{ error }}</div>
      <div v-if="success" class="success-msg">{{ success }}</div>

      <input v-model="form.name"     placeholder="Full name" />
      <input v-model="form.email"    type="email"    placeholder="Email" />
      <input v-model="form.password" type="password" placeholder="Password" />

      <button @click="register">Register</button>
      <p>Already have an account? <a @click="$router.push('/')">Login here</a></p>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'

const router  = useRouter()
const error   = ref('')
const success = ref('')
const form    = ref({
  name: '', email: '', password: ''})

async function register() {
  error.value = ''
  success.value = ''
  try {
    const res  = await fetch('http://127.0.0.1:5000/api/register', {
      method:  'POST',
      headers: { 'Content-Type': 'application/json' },
      body:    JSON.stringify(form.value)
    })
    const data = await res.json()

    if (!res.ok) {
      error.value = data.error || 'Registration failed'
      return
    }

    // auto login after register
    localStorage.setItem('token',      data.token)
    localStorage.setItem('role',       'patient')
    localStorage.setItem('profile_id', data.profile_id)
    localStorage.setItem('name',       data.name)

    router.push('/patient/dashboard')

  } catch (err) {
    error.value = 'Cannot connect to server'
  }
}
</script>