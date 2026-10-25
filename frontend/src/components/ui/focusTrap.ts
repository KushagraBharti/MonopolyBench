const FOCUSABLE = 'a[href], button:not([disabled]), input:not([disabled]), select:not([disabled]), textarea:not([disabled]), summary, [tabindex]:not([tabindex="-1"])'

/** Keeps Tab and Shift+Tab inside a modal container. Call from a keydown handler. */
export function trapTab(event: KeyboardEvent, container: HTMLElement | null) {
  if (event.key !== 'Tab' || !container) return
  const items = Array.from(container.querySelectorAll<HTMLElement>(FOCUSABLE)).filter(el => !el.closest('[inert]') && el.getClientRects().length > 0)
  if (items.length === 0) { event.preventDefault(); container.focus(); return }
  const first = items[0]
  const last = items[items.length - 1]
  const current = document.activeElement
  if (event.shiftKey && (current === first || !container.contains(current))) { event.preventDefault(); last.focus() }
  else if (!event.shiftKey && (current === last || !container.contains(current))) { event.preventDefault(); first.focus() }
}
