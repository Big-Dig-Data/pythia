import axios from "axios";

export default {
  state: {
    availableInstitutions: [],
    selectedInstitution: null,
  },

  getters: {
    ownerInstitutionQueryParams(state) {
      if (state.selectedInstitution) {
        return {
          owner_inst: state.selectedInstitution,
        };
      }
      return {};
    },
    selectedInstitutionObject(state) {
      if (state.selectedInstitution) {
        return state.availableInstitutions.find(
          (item) => item.pk === state.selectedInstitution
        );
      }
      return null;
    },
  },

  actions: {
    async fetchAvailableInstitutions({ commit, dispatch }, { worksetUUID }) {
      try {
        let response = await axios.get(
          `/api/hits/workhit/stats/${worksetUUID}/owner_institution`
        );
        response.data.forEach((item) => {
          item.value = item.pk;
          item.name = item.name.toUpperCase() || "-";
        });
        commit("setAvailableInstitutions", { institutions: response.data });
      } catch (error) {
        dispatch(
          "showSnackbar",
          { content: "Error obtaining list of institutions: " + error },
          { root: true }
        );
      }
    },
    changeSelectedInstitution({ commit }, institution) {
      commit("setSelectedInstitution", institution);
    },
  },

  mutations: {
    setAvailableInstitutions(state, { institutions }) {
      state.availableInstitutions = institutions;
    },
    setSelectedInstitution(state, institution) {
      state.selectedInstitution = institution;
    },
  },
};
