import axios from "axios";
import Cookies from "js-cookie";
import Vue from "vue";

export default {
  state: {
    loginError: null,
  },

  getters: {
    loginErrorText(state) {
      if (state.loginError) {
        if (state.loginError?.response?.data?.non_field_errors) {
          return state.loginError.response.data.non_field_errors[0];
        }
        return state.loginError;
      }
      return null;
    },
    canLogout(state, getters) {
      return !getters.useShibboleth;
    },
    showLoginDialog(state, getters, rootState) {
      return rootState.user === null;
    },
  },

  actions: {
    async login({ commit, dispatch }, { email, password }) {
      commit("setLoginError", { error: null });

      try {
        await axios.post("/api/rest-auth/login/", {
          email: email,
          password: password,
        });
        await Promise.all([dispatch("loadUserData"), dispatch("loadWorksets")]);
      } catch (error) {
        commit("setLoginError", { error: error });
      }
    },
    async logout({ dispatch }) {
      let csrftoken = Cookies.get("csrftoken");
      try {
        await axios.post(
          "/api/rest-auth/logout/",
          {},
          { headers: { "X-CSRFToken": csrftoken } }
        );
      } catch (error) {
        dispatch("showSnackbar", {
          content: "Error logging out:" + error,
          color: "error",
        });
        return;
      }
      await dispatch("cleanUserData");
    },
    async resetPassword({ commit, dispatch }, { email }) {
      let csrftoken = Cookies.get("csrftoken");
      await axios.post(
        "/api/rest-auth/password/reset/",
        { email: email },
        { headers: { "X-CSRFToken": csrftoken } }
      );
    },
    async changePassword({ commit, dispatch }, { password }) {
      let csrftoken = Cookies.get("csrftoken");
      await axios.post(
        "/api/rest-auth/password/change/",
        { new_password1: password, new_password2: password },
        { headers: { "X-CSRFToken": csrftoken } }
      );
    },
  },

  mutations: {
    setLoginError(state, { error }) {
      state.loginError = error;
    },
  },
};
