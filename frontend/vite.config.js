import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// Loads the built CSS asynchronously (preload + swap-on-load) instead of as a
// render-blocking <link rel="stylesheet">, with a <noscript> fallback.
const deferCss = () => ({
  name: 'defer-css',
  transformIndexHtml: {
    order: 'post',
    handler(html) {
      return html.replace(
        /<link rel="stylesheet" crossorigin href="([^"]+)">/,
        (_match, href) =>
          `<link rel="preload" as="style" href="${href}" />` +
          `<link rel="stylesheet" href="${href}" media="print" onload="this.media='all'" />` +
          `<noscript><link rel="stylesheet" href="${href}" /></noscript>`
      )
    },
  },
})

// https://vite.dev/config/
export default defineConfig({
  plugins: [react(), deferCss()],
})
