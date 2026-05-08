import { mount } from "@vue/test-utils";
import { createMemoryHistory, createRouter } from "vue-router";
import { beforeEach, describe, expect, it, vi } from "vitest";

import SignInPage from "./SignInPage.vue";

const apiFetchMock = vi.fn();
const setAuthBannerMock = vi.fn();
const storeTokensMock = vi.fn();
const setCurrentUserEmailMock = vi.fn();
const rememberEmailMock = vi.fn();
const clearRememberedEmailMock = vi.fn();
const getRememberedEmailMock = vi.fn(() => "");

vi.mock("../lib/api", () => ({
  apiFetch: (...args: unknown[]) => apiFetchMock(...args)
}));

vi.mock("../lib/authBanner", () => ({
  setAuthBanner: (...args: unknown[]) => setAuthBannerMock(...args)
}));

vi.mock("../lib/auth", () => ({
  storeTokens: (...args: unknown[]) => storeTokensMock(...args),
  setCurrentUserEmail: (...args: unknown[]) => setCurrentUserEmailMock(...args),
  rememberEmail: (...args: unknown[]) => rememberEmailMock(...args),
  clearRememberedEmail: (...args: unknown[]) => clearRememberedEmailMock(...args),
  getRememberedEmail: () => getRememberedEmailMock()
}));

function makeRouter(startPath = "/signin") {
  return createRouter({
    history: createMemoryHistory(),
    routes: [
      { path: "/signin", component: SignInPage },
      { path: "/dashboard", component: { template: "<div />" } },
      { path: "/signup", component: { template: "<div />" } },
      { path: "/forgot-password", component: { template: "<div />" } }
    ]
  });
}

describe("SignInPage", () => {
  beforeEach(() => {
    apiFetchMock.mockReset();
    setAuthBannerMock.mockReset();
    storeTokensMock.mockReset();
    setCurrentUserEmailMock.mockReset();
    rememberEmailMock.mockReset();
    clearRememberedEmailMock.mockReset();
    getRememberedEmailMock.mockReturnValue("");
  });

  it("redirects to dashboard on successful sign-in", async () => {
    const router = makeRouter();
    await router.push("/signin");
    await router.isReady();
    apiFetchMock.mockResolvedValue({
      ok: true,
      json: async () => ({ access_token: "a", refresh_token: "r" })
    });

    const wrapper = mount(SignInPage, { global: { plugins: [router] } });
    await wrapper.find('input[type="email"]').setValue("a@example.com");
    await wrapper.find('input[autocomplete="current-password"]').setValue("pw");
    await wrapper.find("form").trigger("submit");
    await wrapper.vm.$nextTick();
    await Promise.resolve();
    await router.isReady();

    expect(storeTokensMock).toHaveBeenCalled();
    expect(setCurrentUserEmailMock).toHaveBeenCalledWith("a@example.com");
    expect(apiFetchMock).toHaveBeenCalledWith(
      "/auth/token",
      expect.objectContaining({ method: "POST" }),
      { redirectOn401: false }
    );
  });

  it("shows lockout message on 429", async () => {
    const router = makeRouter();
    await router.push("/signin");
    await router.isReady();
    apiFetchMock.mockResolvedValue({
      ok: false,
      status: 429,
      json: async () => ({ detail: "Too many failed attempts. Please wait and try again." })
    });

    const wrapper = mount(SignInPage, { global: { plugins: [router] } });
    await wrapper.find('input[type="email"]').setValue("a@example.com");
    await wrapper.find('input[autocomplete="current-password"]').setValue("pw");
    await wrapper.find("form").trigger("submit");
    await wrapper.vm.$nextTick();

    expect(wrapper.text()).toContain("Too many failed attempts");
  });

  it("sets banner when route indicates session expired", async () => {
    const router = makeRouter();
    await router.push("/signin?expired=1");
    await router.isReady();
    mount(SignInPage, { global: { plugins: [router] } });
    expect(setAuthBannerMock).toHaveBeenCalledWith("Your session expired. Please sign in again.");
  });
});
