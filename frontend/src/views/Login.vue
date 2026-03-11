<template>
  <div class="auth-container">
    <div class="auth-card">
      <h2>🏥 HMS</h2>
      <h3>Login</h3>

      <div v-if="error" class="error-msg">{{ error }}</div>

      <input v-model="email"    type="email"    placeholder="Email" />
      <input v-model="password" type="password" placeholder="Password" />

      <button @click="login">Login</button>
      <p>New patient? <a @click="$router.push('/register')">Register here</a></p>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'

const router   = useRouter()
const email    = ref('')
const password = ref('')
const error    = ref('')

async function login() {
  error.value = ''
  try {
    const res  = await fetch('http://127.0.0.1:5000/api/login', {
      method:  'POST',
      headers: { 'Content-Type': 'application/json' },
      body:    JSON.stringify({ email: email.value, password: password.value })
    })
    const data = await res.json()

    if (data.error) {
      error.value = data.error || 'Login failed'
      return
    }

    localStorage.setItem('token',      data.token)
    localStorage.setItem('role',       data.role)
    localStorage.setItem('profile_id', data.profile_id)
    localStorage.setItem('name',       data.name)

    if (data.role === 'admin')       router.push('/admin/dashboard')
    else if (data.role === 'doctor') router.push('/doctor/dashboard')
    else                             router.push('/patient/dashboard')

  } catch (err) {
    error.value = 'Cannot connect to server'
  }
}
</script>