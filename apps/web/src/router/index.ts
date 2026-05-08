import { createRouter, createWebHistory } from "vue-router";

import { hasAccessToken } from "../lib/auth";
import HomePage from "../pages/HomePage.vue";
import ForgotPasswordPage from "../pages/ForgotPasswordPage.vue";
import SignInPage from "../pages/SignInPage.vue";
import SignOutPage from "../pages/SignOutPage.vue";
import SignUpPage from "../pages/SignUpPage.vue";
import ResetPasswordPage from "../pages/ResetPasswordPage.vue";

export const router = createRouter({
  history: createWebHistory(),
  routes: [
    {
      path: "/",
      name: "home",
      component: HomePage,
      meta: { layout: "dashboard", requiresAuth: true }
    },
    {
      path: "/dashboard",
      name: "dashboard",
      component: HomePage,
      meta: { layout: "dashboard", requiresAuth: true }
    },
    {
      path: "/signin",
      name: "signin",
      component: SignInPage,
      meta: { layout: "auth" }
    },
    {
      path: "/forgot-password",
      name: "forgot-password",
      component: ForgotPasswordPage,
      meta: { layout: "auth" }
    },
    {
      path: "/reset-password",
      name: "reset-password",
      component: ResetPasswordPage,
      meta: { layout: "auth" }
    },
    {
      path: "/signup",
      name: "signup",
      component: SignUpPage,
      meta: { layout: "auth" }
    },
    {
      path: "/signout",
      name: "signout",
      component: SignOutPage,
      meta: { layout: "auth" }
    }
  ]
});

router.beforeEach((to) => {
  if (to.meta.requiresAuth && !hasAccessToken()) {
    return { path: "/signin", query: { next: to.fullPath } };
  }

  return true;
});
