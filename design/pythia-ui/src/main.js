import Vue from "vue";
import App from "./pages/Main";
import store from "./store";
import router from "./router";
import vuetify from "./plugins/vuetify";
import i18n from "./i18n";

Vue.config.productionTip = false;

// suppress warning about selection type from vuetify treeview in dev env
Vue.config.warnHandler = function (msg, vm, trace) {
  if (
    msg !==
    'Invalid prop: custom validator check failed for prop "selectionType".'
  ) {
    const hasConsole = typeof console !== "undefined";
    if (hasConsole && !Vue.config.silent) {
      console.error(`[Vue warn]: ${msg}${trace}`);
    }
  }
};

const titleBase = "Pythia";
router.afterEach((to, from) => {
  document.title = titleBase;
  if (to.meta && to.meta.title) {
    document.title += ": " + i18n.t(to.meta.title);
  }
});

Vue.prototype.$numRowsOpts = [10, 20, 50, 100];

new Vue({
  el: "#app",
  render: (h) => h(App),
  store,
  i18n,
  router,
  vuetify,
});
