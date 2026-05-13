import { defineConfig } from "vitepress";

export default defineConfig({
  title: "Vortex",
  description: "Official documentation for Vortex by McGuire Technology, LLC",
  lang: "en-US",
  cleanUrls: true,
  lastUpdated: true,
  head: [["link", { rel: "icon", type: "image/svg+xml", href: "/favicon.svg" }]],
  sitemap: {
    hostname: "https://docs.vortex.mcguire.technology"
  },
  themeConfig: {
    footer: {
      message: "Licensed under the MIT License.",
      copyright: "Copyright (c) 2026 McGuire Technology, LLC"
    },
    logo: "/logo.svg",
    nav: [
      { text: "Users", link: "/users/" },
      { text: "Admins", link: "/admins/" },
      { text: "Developers", link: "/developers/" },
      { text: "Community", link: "/community/" },
      { text: "Changelog", link: "/changelog/" }
    ],
    editLink: {
      pattern: "https://github.com/McGuireTechnology/Vortex/edit/main/apps/docs/docs/:path",
      text: "Edit this page on GitHub"
    },
    lastUpdatedText: "Last updated",
    socialLinks: [{ icon: "github", link: "https://github.com/McGuireTechnology/Vortex" }],
    sidebar: {
      "/users/": [
        {
          text: "Users",
          items: [
            { text: "Overview", link: "/users/" },
            { text: "Authentication", link: "/users/authentication" },
            { text: "Applications", link: "/users/applications" },
            { text: "Databases", link: "/users/databases" }
          ]
        }
      ],
      "/developers/repository-management/": [
        {
          items: [
            { text: "↖ Developers", link: "/developers/" },
            { text: "Overview", link: "/developers/repository-management/" },
            { text: "Branching Strategy", link: "/developers/repository-management/branching-strategy" },
            { text: "Commit Strategy", link: "/developers/repository-management/commit-strategy" },
            { text: "Pull Request Strategy", link: "/developers/repository-management/pull-request-strategy" },
            { text: "Release Strategy", link: "/developers/repository-management/release-strategy" },
            { text: "Ownership and Code Review", link: "/developers/repository-management/ownership-and-code-review" },
            { text: "Dependency and Security Hygiene", link: "/developers/repository-management/dependency-and-security-hygiene" }
          ]
        }
      ],
      "/admins/": [
        {
          text: "Admins",
          items: [
            { text: "Overview", link: "/admins/" },
            { text: "Release Checklist", link: "/admins/release-checklist" },
            { text: "Backlog", link: "/admins/backlog" },
            { text: "Changelog", link: "/changelog/" },
            { text: "Incident Notes", link: "/admins/incident-notes" }
          ]
        }
      ],
      "/developers/": [
        {
          text: "Developers",
          items: [
            { text: "Overview", link: "/developers/" },
            { text: "Getting Started", link: "/developers/getting-started" },
            { text: "Local Development", link: "/developers/local-development" },
            { text: "Docker Development", link: "/developers/docker-development" },
            { text: "Architecture", link: "/developers/architecture" },
            { text: "Compose Layout", link: "/developers/compose-layout" },
            { text: "Environment Files", link: "/developers/environment-files" },
            { text: "Environment Baseline", link: "/developers/environment-baseline" },
            { text: "Testing Strategy", link: "/developers/testing-strategy" },
            { text: "Security Baseline", link: "/developers/security-baseline" },
            { text: "Deprecation Policy", link: "/developers/deprecation-policy" },
            { text: "Definition of Done", link: "/developers/definition-of-done" },
            { text: "Repository Management", link: "/developers/repository-management/" },
            { text: "Docs Information Architecture", link: "/developers/docs-information-architecture" },
            { text: "Changelog", link: "/changelog/" }
          ]
        }
      ],
      "/changelog/": [
        {
          text: "Changelog",
          items: [
            { text: "Overview", link: "/changelog/" },
            { text: "Unreleased", link: "/changelog/unreleased" },
            { text: "v0.1.0 (2026-05-07)", link: "/changelog/v0.1.0" }
          ]
        }
      ],
      "/community/": [
        {
          text: "Community",
          items: [{ text: "Overview", link: "/community/" }]
        }
      ]
    }
  }
});

