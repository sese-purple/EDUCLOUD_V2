import axios from 'axios'

// This creates a custom Axios instance attached to your Django server
const api = axios.create({
  baseURL: 'http://127.0.0.1:8000/api/',
  headers: {
    'Content-Type': 'application/json',
  }
})

// We will add an "interceptor" here later to automatically attach the JWT token!

export default api