import Vue from "vue";
import Vuex from "vuex";
import axios from "axios";
import dateRange from "./modules/date-range";
import langFilter from "./modules/lang-filter";
import YOP from "./modules/yop";
import ownerFilter from "./modules/owner-filter";
import login from "./modules/login";
import workTypeFilter from "./modules/work-type-filter";
import { ConcurrencyManager } from "axios-concurrency";
import { CHART_COLORS } from "@/libs/colors";

Vue.use(Vuex);

const MAX_CONCURRENT_REQUESTS_DEFAULT = 2;
let concurrencyManager = null;

export default new Vuex.Store({
  modules: {
    dateRange,
    langFilter,
    YOP,
    ownerFilter,
    workTypeFilter,
    login,
  },

  state: {
    worksets: [],
    selectedWorkset: null,
    loadingWorksets: false,
    snackbarShow: false,
    snackbarContent: null,
    snackbarColor: null,
    user: null,
    serverSettings: {},
  },

  getters: {
    selectedWorkset: (state) => state.selectedWorkset,
    loadingWorksets: (state) => state.loadingWorksets,
    selectedWorksetUUID: (state) => {
      if (state.selectedWorkset) return state.selectedWorkset.uuid;
      return null;
    },
    loggedIn: (state) => state.user !== null,
    avatarImg: (state) => {
      return null;
    },
    avatarText: (state) => {
      if (state.user?.email) {
        return state.user.email[0].toUpperCase();
      }
      return "A";
    },
    usernameText: (state) => {
      return state.user?.email ?? "not logged in";
    },
    workQueryParams: (state, getters) => {
      return {
        ...getters.workLanguageQueryParams,
        ...getters.dateRangeQueryParams,
        ...getters.workYOPQueryParams,
        ...getters.ownerInstitutionQueryParams,
        ...getters.ownerWorkTypeQueryParams,
      };
    },
    chartColors() {
      return CHART_COLORS;
    },
    vufindUrl(state) {
      return state.serverSettings.VUFIND_URL ?? "";
    },
    subjectSchemas(state) {
      return state.serverSettings.SUBJECT_SCHEMAS || [];
    },
    useShibboleth(state) {
      return state.serverSettings.USE_SHIBBOLETH ?? false;
    },
  },

  actions: {
    async start({ dispatch, commit }) {
      axios.defaults.xsrfCookieName = "csrftoken";
      axios.defaults.xsrfHeaderName = "X-CSRFToken";
      axios.interceptors.response.use(
        function (response) {
          // Do something with response data
          return response;
        },
        function (error) {
          // Do something with response error
          if (
            error.response &&
            error.response.status >= 400 &&
            error.response.status !== 404 &&
            error.response.status < 500
          ) {
            // if there is 40x error, try to reauthenticate
            console.log("reauthenticating", error.request);
            commit("setUserData", null);
          }
          return Promise.reject(error);
        }
      );
      let max_concurrent_requests = parseInt(
        localStorage.getItem("max_concurrent_requests")
      );
      if (!max_concurrent_requests) {
        max_concurrent_requests = MAX_CONCURRENT_REQUESTS_DEFAULT;
      }
      concurrencyManager = ConcurrencyManager(axios, max_concurrent_requests);
      await dispatch("loadServerSettings");
    },
    async loadWorksets(context) {
      context.commit("setLoadingWorksets", { yes: true });
      axios.get(`/api/bookrank/workset/`).then(
        (response) => {
          context.commit("setLoadingWorksets", { yes: false });
          const oldSelectedWS = this.state.selectedWorkset;
          context.commit("replaceWorksets", { worksets: response.data });
          // find the records that matches the last selected record
          if (oldSelectedWS) {
            let matchingWS = null;
            for (let ws of this.state.worksets) {
              if (ws.uuid === oldSelectedWS.uuid) {
                matchingWS = ws;
                break;
              }
            }
            if (matchingWS) {
              context.commit("setSelectedWorkset", { workset: matchingWS });
            } else {
              context.commit("setSelectedWorkset", { workset: null });
              this.dispatch("selectFirstUsableWorkset");
            }
          } else {
            this.dispatch("selectFirstUsableWorkset");
          }
        },
        (error) => {
          console.log("Error fetching data", error);
          context.commit("setLoadingWorksets", { yes: false });
        }
      );
    },
    selectFirstUsableWorkset({ state }) {
      let success = false;
      if (state.worksets) {
        for (let ws of state.worksets) {
          if (ws.mi_count > 0) {
            this.dispatch("setSelectedWorkset", { workset: ws });
            success = true;
            break;
          }
        }
        if (!success) {
          this.dispatch("setSelectedWorkset", { workset: state.worksets[0] });
        }
      }
    },
    setSelectedWorkset(context, { workset }) {
      context.commit("setSelectedWorkset", { workset: workset });
    },
    showSnackbar(context, { content, color }) {
      context.commit("setSnackbarContent", { content: content });
      context.commit("setSnackbarShow", { show: true, color: color });
    },
    hideSnackbar(context) {
      context.commit("setSnackbarShow", { show: false });
    },
    async loadUserData({ commit }) {
      axios
        .get("/api/rest-auth/user/")
        .then((response) => {
          commit("setUserData", response.data);
        })
        .catch((error) => {
          console.log("Error: " + error);
        });
    },
    async cleanUserData({ commit, dispatch }) {
      commit("setUserData", null);
    },
    async loadServerSettings({ commit, dispatch }) {
      try {
        let resp = await axios.get("/api/info/");
        commit("setServerSettings", { settings: resp.data });
      } catch (error) {
        dispatch("showSnackbar", {
          content: "Error loading basic server info: " + error,
        });
      }
    },
  },
  mutations: {
    replaceWorksets(state, { worksets }) {
      Vue.set(state, "worksets", worksets);
    },
    setSelectedWorkset(state, { workset }) {
      Vue.set(state, "selectedWorkset", workset);
    },
    setLoadingWorksets(state, { yes }) {
      Vue.set(state, "loadingWorksets", yes);
    },
    setSnackbarShow(state, { show, color }) {
      Vue.set(state, "snackbarShow", show);
      Vue.set(state, "snackbarColor", color);
    },
    setSnackbarContent(state, { content }) {
      Vue.set(state, "snackbarContent", content);
    },
    setUserData(state, user) {
      Vue.set(state, "user", user);
    },
    setServerSettings(state, { settings }) {
      state.serverSettings = settings;
    },
  },
});
