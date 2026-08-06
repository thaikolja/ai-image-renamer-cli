import { defineConfig } from 'vitepress'

export default defineConfig({
  title: 'AI Image Renamer',
  description: 'Rename images using AI-generated descriptions',
  lang: 'en-US',
  base: '/ai-image-renamer/',

  head: [
    ['meta', { name: 'theme-color', content: '#3eaf7c' }],
  ],

  lastUpdated: true,

  themeConfig: {
    logo: '/ai-image-renamer-cli-logo.png',
    nav: [
      { text: 'Guide', link: '/guide/getting-started' },
      { text: 'Reference', link: '/reference/cli' },
      { text: 'Contributing', link: '/contributing' },
      { text: 'Changelog', link: '/changelog' },
    ],

    sidebar: {
      '/guide/': [
        {
          text: 'Guide',
          items: [
            { text: 'Getting Started', link: '/guide/getting-started' },
            { text: 'Installation', link: '/guide/installation' },
            { text: 'Configuration', link: '/guide/configuration' },
            { text: 'Providers', link: '/guide/providers' },
          ],
        },
      ],
      '/reference/': [
        {
          text: 'Reference',
          items: [
            { text: 'CLI Reference', link: '/reference/cli' },
            { text: 'Config Keys', link: '/reference/config-keys' },
            { text: 'API Reference', link: '/reference/api' },
          ],
        },
      ],
    },

    outline: { level: [2, 3] },

    search: {
      provider: 'local',
    },

    footer: {
      message: 'Released under the MIT License',
      copyright: 'Copyright © 2025-present Kolja Nolte',
    },

    editLink: {
      pattern: 'https://github.com/thaikolja/ai-image-renamer/edit/main/docs/:path',
      text: 'Edit this page on GitHub',
    },

    socialLinks: [
      { icon: 'github', link: 'https://github.com/thaikolja/ai-image-renamer' },
    ],
  },
})
