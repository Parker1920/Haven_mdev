import React, { useState, useContext } from 'react'
import Modal from './Modal'
import AuthContext from '../utils/AuthContext'

export default function AdminLoginModal({ open, onClose }){
  const [password, setPassword] = useState('')
  const [error, setError] = useState('')
  const auth = useContext(AuthContext)

  if (!open) return null

  async function submit(){
    setError('')
    try{
      await auth.login(password)
      onClose()
    }catch(e){
      setError(e.message || 'Login failed')
    }
  }

  return (
    <Modal title="Admin Login" onClose={onClose}>
      <div>
        <label>Enter admin password</label>
        <input value={password} onChange={(e)=>setPassword(e.target.value)} type='password' className='w-full p-2 border rounded' />
        <div className='mt-4'>
          <button className='btn' onClick={submit}>Unlock</button>
          <button className='btn ml-2' onClick={onClose}>Cancel</button>
        </div>
        {error && <div className='text-red-500 mt-2'>{error}</div>}
      </div>
    </Modal>
  )
}
