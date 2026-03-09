import { createRouter, createWebHistory } from 'vue-router'

import Login from '../views/Login.vue'
import Register from '../views/Register.vue'
import AdminDashboard from '../views/AdminDashboard.vue'
import ManageDoctors from '../views/ManageDoctors.vue'
import ManagePatients from '../views/ManagePatients.vue'
import DoctorDashboard from '../views/DoctorDashboard.vue'
import DoctorAvailability from '../views/DocAvailability.vue'
import PatientDashboard from '../views/PatientDashboard.vue'
import DepartmentDetail from '../views/DeptDetail.vue'
import DoctorDetail from '../views/DoctorDetail.vue'
import PatientDoctorAvailability from '../views/PatientCheckAvailability.vue'
import PatientHistory from '../views/PatientHistory.vue'

const router = createRouter({
  history: createWebHistory(),
  routes: [
    { path: '/',                                      component: Login },
    { path: '/register',                              component: Register },
    { path: '/admin/dashboard',                       component: AdminDashboard,            meta: { role: 'admin' } },
    { path: '/admin/doctors',                         component: ManageDoctors,             meta: { role: 'admin' } },
    { path: '/admin/patients',                        component: ManagePatients,            meta: { role: 'admin' } },
    { path: '/doctor/dashboard',                      component: DoctorDashboard,           meta: { role: 'doctor' } },
    { path: '/doctor/availability',                   component: DoctorAvailability,        meta: { role: 'doctor' } },
    { path: '/patient/dashboard',                     component: PatientDashboard,          meta: { role: 'patient' } },
    { path: '/patient/department/:id',                component: DepartmentDetail,          meta: { role: 'patient' } },
    { path: '/patient/doctor/:id',                    component: DoctorDetail,              meta: { role: 'patient' } },
    { path: '/patient/doctor/:id/availability',       component: PatientDoctorAvailability, meta: { role: 'patient' } },
    { path: '/patient/history',                       component: PatientHistory,            meta: { role: 'patient' } },
    { path: '/doctor/patient/:id/history', component: PatientHistory, meta: { role: 'doctor' } },
  ]
})

router.beforeEach((to, from, next) => {
  const token = localStorage.getItem('token')
  const role  = localStorage.getItem('role')

  if (to.path === '/' || to.path === '/register') return next()
  if (!token) return next('/')
  if (to.meta.role && to.meta.role !== role) return next('/')

  next()
})

export default router