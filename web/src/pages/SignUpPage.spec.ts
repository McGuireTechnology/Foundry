import { mount } from "@vue/test-utils";
import { createMemoryHistory, createRouter } from "vue-router";
import { beforeEach, describe, expect, it, vi } from "vitest";

import SignUpPage from "./SignUpPage.vue";

const apiFetchMock = vi.fn();

vi.mock("../lib/api", () => ({
  apiFetch: (...args: unknown[]) => apiFetchMock(...args)
}));

function makeRouter() {
  return createRouter({
    history: createMemoryHistory(),
    routes: [{ path: "/signup", component: SignUpPage }, { path: "/signin", component: { template: "<div />" } }]
  });
}

describe("SignUpPage", () => {
  beforeEach(() => {
    apiFetchMock.mockReset();
  });

  it("shows friendly duplicate-email message", async () => {
    const router = makeRouter();
    await router.push("/signup");
    await router.isReady();
    apiFetchMock.mockResolvedValue({
      ok: false,
      status: 409
    });

    const wrapper = mount(SignUpPage, { global: { plugins: [router] } });
    await wrapper.find('input[type="email"]').setValue("dup@example.com");
    await wrapper.find('input[autocomplete="new-password"]').setValue("password123");
    await wrapper.find("form").trigger("submit");
    await wrapper.vm.$nextTick();

    expect(wrapper.text()).toContain("An account with this email already exists");
  });
});
