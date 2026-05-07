import { defineConfig } from "vitepress";

export default defineConfig({
  title: "Foundry Docs",
  description: "Foundry low-code platform documentation",
  themeConfig: {
    nav: [
      { text: "Guide", link: "/guide/getting-started" },
      { text: "Reference", link: "/reference/architecture" }
    ],
    sidebar: {
      "/guide/": [
        {
          text: "Guide",
          items: [
            { text: "Getting Started", link: "/guide/getting-started" },
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
            { text: "Repository Management", link: "/reference/repository-management" }
          ]
        }
      ]
    }
  }
});
