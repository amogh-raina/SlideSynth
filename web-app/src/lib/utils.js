/**
 * Agent → colour mapping for badges and avatars.
 */
export function getAgentColor(name) {
  if (!name) return '#333'
  const n = name.toLowerCase()
  if (n.includes('research')) return '#34a853'
  if (n.includes('plan'))     return '#7c3aed'
  if (n.includes('verif'))    return '#059669'
  if (n.includes('design'))   return '#ea8600'
  if (n.includes('generat'))  return '#0e7490'
  if (n.includes('edit'))     return '#c2185b'
  return '#1a73e8'
}

/**
 * Agent → Tailwind-friendly badge class.
 */
export function getAgentBadgeClass(name) {
  if (!name) return 'bg-blue-600'
  const n = name.toLowerCase()
  if (n.includes('research')) return 'bg-green-600'
  if (n.includes('plan'))     return 'bg-purple-600'
  if (n.includes('verif'))    return 'bg-emerald-600'
  if (n.includes('design'))   return 'bg-amber-500'
  if (n.includes('generat'))  return 'bg-cyan-700'
  if (n.includes('edit'))     return 'bg-pink-700'
  return 'bg-blue-600'
}

/**
 * File icon styles and symbols based on extension.
 */
export function getFileIcon(name) {
  const extension = name.split('.').pop()?.toLowerCase();
  
  const iconMap = {
    tsx: { color: "text-[oklch(0.65_0.18_220)]", icon: "⚛" },
    ts: { color: "text-[oklch(0.6_0.15_230)]", icon: "◆" },
    jsx: { color: "text-[oklch(0.7_0.2_200)]", icon: "⚛" },
    js: { color: "text-[oklch(0.8_0.18_90)]", icon: "◆" },
    css: { color: "text-[oklch(0.65_0.2_280)]", icon: "◈" },
    json: { color: "text-[oklch(0.75_0.15_85)]", icon: "{}" },
    md: { color: "text-gray-400", icon: "◊" },
    svg: { color: "text-[oklch(0.7_0.15_160)]", icon: "◐" },
    png: { color: "text-[oklch(0.65_0.12_160)]", icon: "◑" },
    jpg: { color: "text-[oklch(0.65_0.12_160)]", icon: "◑" },
    jpeg: { color: "text-[oklch(0.65_0.12_160)]", icon: "◑" },
    html: { color: "text-[oklch(0.65_0.2_25)]", icon: "📄" },
    pdf: { color: "text-red-500", icon: "📕" },
    default: { color: "text-gray-400", icon: "◇" },
  }
  
  return iconMap[extension] || iconMap.default
}

/**
 * File icon emoji based on extension. (Backward compatibility)
 */
export function fileIcon(name) {
  if (/\.(png|jpg|jpeg|gif|svg|webp)$/i.test(name)) return '🖼'
  if (name.endsWith('.json')) return '📋'
  if (name.endsWith('.md'))   return '📝'
  if (name.endsWith('.html')) return '📄'
  if (name.endsWith('.pdf'))  return '📕'
  return '📎'
}

/**
 * Generate a UUID v4.
 */
export function uuid() {
  return ([1e7] + -1e3 + -4e3 + -8e3 + -1e11).replace(/[018]/g, c =>
    (c ^ (crypto.getRandomValues(new Uint8Array(1))[0] & (15 >> (c / 4)))).toString(16),
  )
}
