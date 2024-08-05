<template>
  <v-app>
    <router-view v-if="$route.meta.outsideNormalLayout"> </router-view>
    <LoginDialog v-else-if="showLoginDialog"></LoginDialog>
    <template v-else>
      <SidePanel />

      <v-app-bar app clipped-left dark color="primary darken-1">
        <v-toolbar-title>
          <img
            src="/pythia_logo_horizontal.svg"
            alt="Pythia logo"
            height="42"
            id="logo-image"
          />
        </v-toolbar-title>

        <v-divider class="mx-3" inset vertical></v-divider>

        <div class="workset pl-4">
          <span class="workset"
            ><span class="sc">{{ $t("workset") }}</span
            >: <strong>{{ selectedWorksetName }}</strong></span
          >
        </div>

        <v-divider
          v-if="!$route.meta.hideDateFilter"
          class="mx-8"
          inset
          vertical
        ></v-divider>

        <SelectedDateRangeWidget v-if="!$route.meta.hideDateFilter" />

        <v-divider
          v-if="!$route.meta.hideWorkFilter"
          class="mx-8"
          inset
          vertical
        ></v-divider>

        <WorkFilterWidget v-if="!$route.meta.hideWorkFilter" />
        <v-spacer></v-spacer>
        <v-toolbar-items class="hidden-sm-and-down align-baseline">
          <v-select
            v-model="appLang"
            :items="['cs', 'en']"
            prepend-icon="fa-globe"
            class="short"
          >
          </v-select>
          <v-divider class="mx-3" inset vertical></v-divider>
          <v-avatar size="36px" color="primary" class="mt-2">
            <v-tooltip bottom>
              <template v-slot:activator="{ on }">
                <router-link v-on="on" :to="{ name: 'user-page' }">
                  <img
                    v-if="$store.getters.avatarImg"
                    :src="$store.getters.avatarImg"
                    alt="Avatar"
                  />
                  <span
                    v-else-if="$store.getters.loggedIn"
                    class="white--text headline"
                    >{{ $store.getters.avatarText }}</span
                  >
                  <v-icon v-else dark>fa-user</v-icon>
                </router-link>
              </template>

              <span>{{ $store.getters.usernameText }}</span>
            </v-tooltip>
          </v-avatar>
        </v-toolbar-items>
      </v-app-bar>

      <v-main>
        <v-container fluid>
          <router-view />

          <v-snackbar v-model="snackbarShow" :color="snackbarColor">
            {{ snackbarText }}
            <v-btn dark text @click="hideSnackbar"> Close </v-btn>
          </v-snackbar>
        </v-container>
      </v-main>
    </template>
  </v-app>
</template>

<script>
import SidePanel from "./SidePanel";
import LoginDialog from "@/components/account/LoginDialog";
import SelectedDateRangeWidget from "@/components/SelectedDateRangeWidget";
import WorkFilterWidget from "@/components/WorkFilterWidget";
import { mapActions, mapGetters, mapState } from "vuex";

export default {
  name: "Dashboard",
  components: {
    SidePanel,
    LoginDialog,
    SelectedDateRangeWidget,
    WorkFilterWidget,
  },
  data() {
    return {
      navbarExpanded: false,
      appLang: "cs",
    };
  },

  computed: {
    ...mapState({
      snackbarColor: "snackbarColor",
      snackbarText: "snackbarContent",
    }),
    ...mapGetters({
      showLoginDialog: "showLoginDialog",
    }),
    selectedWorksetName() {
      const selectedWorkset = this.$store.getters.selectedWorkset;
      if (selectedWorkset) return selectedWorkset.name;
      return "-";
    },
    snackbarShow: {
      get() {
        return this.$store.state.snackbarShow;
      },
      set(newValue) {
        if (newValue === false) this.hideSnackbar();
      },
    },
  },

  methods: {
    ...mapActions({
      loadWorksets: "loadWorksets",
      loadUserData: "loadUserData",
      start: "start",
    }),
    toggleNavbar() {
      this.navbarExpanded = !this.navbarExpanded;
    },
    hideSnackbar() {
      this.$store.dispatch("hideSnackbar");
    },
  },
  async created() {
    // this.$store.dispatch('loadWorksets')
    await this.start();
    await Promise.all([this.loadUserData(), this.loadWorksets()]);
  },
  watch: {
    appLang() {
      this.$i18n.locale = this.appLang;
    },
  },
};
</script>

<style lang="scss">
div.workset {
  display: inline-block;

  span.workset {
    display: block;
    font-size: 1.25rem;
  }

  span.model {
  }
}

.sc {
  font-variant: small-caps;
}

.v-select.v-text-field.short input {
  max-width: 0;
}

section.header {
  margin-bottom: 2rem;
}

div.fields {
  margin-top: 1rem;
}

i.v-icon.bl {
  vertical-align: baseline;
}

// this is here to enable creation of checkboxes with removed margins
.v-input.small-checkbox {
  margin-top: 0;

  .v-input__slot {
    margin-bottom: 0 !important;
    margin-right: 0.5rem;

    .v-input--selection-controls__input {
      margin-right: 0;
    }
  }

  label {
    font-size: 0.875rem;
  }
}

#logo-image {
  height: 42px;
  width: auto;
  margin-top: 10px;
}

.cursor-pointer {
  cursor: pointer;
}
</style>
