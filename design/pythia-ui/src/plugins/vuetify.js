import Vue from "vue";
import Vuetify from "vuetify/lib";
import colors from "vuetify/es5/util/colors";

Vue.use(Vuetify);

export default new Vuetify({
  icons: {
    iconfont: "fa",
  },
  theme: {
    options: { customProperties: true },
    themes: {
      light: {
        primary: colors.teal.lighten2,
        secondary: colors.grey.lighten3,
        accent: colors.orange.lighten2,
      },
    },
  },
});
