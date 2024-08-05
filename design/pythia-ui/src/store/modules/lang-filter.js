import axios from "axios";

export default {
  state: {
    availableLanguages: [],
    selectedLanguage: null,
  },

  getters: {
    selectedLanguageCode(state) {
      if (state.selectedLanguage) {
        return state.selectedLanguage.name;
      }
      return null;
    },
    workLanguageQueryParams(state) {
      if (state.selectedLanguage) {
        return { lang: state.selectedLanguage.value };
      }
      return {};
    },
  },

  actions: {
    async fetchAvailableLanguages({ commit, dispatch }, { worksetUUID }) {
      try {
        let response = await axios.get(
          `/api/hits/workhit/stats/${worksetUUID}/lang`
        );
        response.data.forEach((item) => {
          item.value = item.name;
          item.name = item.name.toUpperCase() || "-";
        });
        commit("setAvailableLanguages", { languages: response.data });
      } catch (error) {
        dispatch(
          "showSnackbar",
          { content: "Error obtaining list of languages: " + error },
          { root: true }
        );
      }
    },
    changeSelectedLanguage({ commit }, langSpec) {
      commit("setSelectedLanguage", langSpec);
    },
  },

  mutations: {
    setAvailableLanguages(state, { languages }) {
      state.availableLanguages = languages;
    },
    setSelectedLanguage(state, langSpec) {
      state.selectedLanguage = langSpec;
    },
  },
};
