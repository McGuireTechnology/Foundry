import DefaultTheme from "vitepress/theme";
import type { Theme } from "vitepress";
import { h } from "vue";
import ReportIssueLink from "./ReportIssueLink.vue";
import "./custom.css";

const theme: Theme = {
  ...DefaultTheme,
  Layout: () => {
    return h(DefaultTheme.Layout, null, {
      "doc-footer-before": () => h(ReportIssueLink)
    });
  }
};

export default theme;
