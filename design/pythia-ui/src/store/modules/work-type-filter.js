import axios from "axios";

export default {
  state: {
    availableWorkTypes: [],
    selectedWorkType: null,
  },

  getters: {
    ownerWorkTypeQueryParams(state) {
      if (state.selectedWorkType) {
        return {
          work_category: state.selectedWorkType,
        };
      }
      return {};
    },
    selectedWorkTypeObject(state) {
      if (state.selectedWorkType) {
        return state.availableWorkTypes.find(
          (item) => item.pk === state.selectedWorkType
        );
      }
      return null;
    },
  },

  actions: {
    async fetchAvailableWorkTypes({ commit, dispatch }, { worksetUUID }) {
      try {
        let response = await axios.get(
          `/api/hits/workhit/stats/${worksetUUID}/work_category`
        );
        response.data.forEach((item) => {
          item.value = item.pk;
          item.name = item.name || "-";
        });
        commit("setAvailableWorkTypes", { workTypes: response.data });
      } catch (error) {
        dispatch(
          "showSnackbar",
          { content: "Error obtaining list of work types: " + error },
          { root: true }
        );
      }
    },
    changeSelectedWorkType({ commit }, workType) {
      commit("setSelectedWorkType", workType);
    },
  },

  mutations: {
    setAvailableWorkTypes(state, { workTypes }) {
      state.availableWorkTypes = workTypes;
    },
    setSelectedWorkType(state, workType) {
      state.selectedWorkType = workType;
    },
  },
};
