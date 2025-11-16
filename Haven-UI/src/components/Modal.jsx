import React from 'react'

export default function Modal({title, children, onClose}){
  return (
    <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-40">
      <div className="p-6 rounded shadow max-w-3xl w-full" style={{backgroundColor:'var(--app-card)'}}>
        <div className="flex items-center justify-between mb-3">
          <div className="font-semibold text-lg">{title}</div>
          <button onClick={onClose} className="px-2 py-1 rounded" style={{backgroundColor:'var(--app-accent-3)', color:'#fff'}}>Close</button>
        </div>
        <div>
          {children}
        </div>
      </div>
    </div>
  )
}
