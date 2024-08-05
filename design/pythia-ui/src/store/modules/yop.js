export default {
  state: {
    startYOP: null,
    endYOP: null,
  },

  getters: {
    workYOPQueryParams(state) {
      const output = {};
      if (state.startYOP) {
        output["yop_from"] = state.startYOP;
      }
      if (state.endYOP) {
        output["yop_to"] = state.endYOP;
      }
      return output;
    },
    YOPRange(state) {
      let ret = null;
      if (state.startYOP) {
        if (state.endYOP) {
          ret = `${state.startYOP}-${state.endYOP}`;
        } else {
          ret = `>${state.startYOP}`;
        }
      } else {
        if (state.endYOP) {
          ret = `<${state.endYOP}`;
        }
      }
      return ret;
    },
  },

  actions: {
    changeYOP({ commit }, data) {
      commit("setYOP", data);
    },
  },

  mutations: {
    setYOP(state, data) {
      if ("start" in data) state.startYOP = data.start;
      if ("end" in data) state.endYOP = data.end;
    },
  },
};
