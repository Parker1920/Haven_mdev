import React, { createContext, useEffect } from 'react'

export const ThemeContext = createContext(null)

export default function ThemeProvider({ children }){
  useEffect(()=>{
    // Fetch settings and apply theme CSS variables to :root
    fetch('/api/settings').then(r=>r.json()).then(j=>{
      const theme = (j && j.theme) || j || {}
      const root = document.documentElement
      if(theme){
        Object.entries(theme).forEach(([k,v])=>{
          // Only set CSS variables that look like colors or known keys
          const name = `--${k.replace(/_/g,'-')}`
          try{ root.style.setProperty(name, v) }catch(e){}
        })
      }
    }).catch(()=>{})
  }, [])

  return (
    <ThemeContext.Provider value={null}>
      {children}
    </ThemeContext.Provider>
  )
}
