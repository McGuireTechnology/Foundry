import { defineConfig } from "vitepress";

export default defineConfig({
  title: "Foundry",
  description: "Official documentation for Foundry by McGuire Technology, LLC",
  lang: "en-US",
  cleanUrls: true,
  head: [
    ["link", { rel: "icon", type: "image/svg+xml", href: "/favicon.svg" }]
  ],
  sitemap: {
    hostname: "https://docs.foundry.mcguire.technology"
  },
  themeConfig: {
    footer: {
      message: "Licensed under the MIT License.",
      copyright: "Copyright (c) 2026 McGuire Technology, LLC"
    },
    logo: "/logo.svg",
    nav: [
      { text: "Guide", link: "/guide/getting-started" },
      { text: "Reference", link: "/reference/architecture" }
    ],
    socialLinks: [
      { icon: "github", link: "https://github.com/McGuireTechnology/Foundry" }
    ],
    sidebar: {
      "/guide/": [
        {
          text: "Guide",
          items: [
            { text: "Getting Started", link: "/guide/getting-started" },
            { text: "Authentication", link: "/guide/authentication" },
            { text: "Docker Development", link: "/guide/docker-development" },
            { text: "Local Development", link: "/guide/local-development" }
          ]
        }
      ],
      "/reference/": [
        {
          text: "Reference",
          items: [
            { text: "Architecture", link: "/reference/architecture" },
            { text: "Compose Layout", link: "/reference/compose-layout" },
            { text: "Environment Files", link: "/reference/environment-files" },
            { text: "Repository Management", link: "/reference/repository-management" },
            { text: "Changelog", link: "/reference/changelog" },
            { text: "Backlog", link: "/reference/backlog" }
          ]
        }
      ]
    }
  }
});
