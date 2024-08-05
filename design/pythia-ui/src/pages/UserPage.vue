<i18n lang="yaml">
en:
  is_superuser: Superuser
  logout: Log out
  change_password: Change password

cs:
  is_superuser: Superuživatel
  logout: Odhlásit se
  change_password: Změnit heslo
</i18n>

<template>
  <v-container v-if="loggedIn && user" class="text-center">
    <v-row no-gutters>
      <v-col>
        <v-avatar color="primary" class="mt-10" size="80">
          <v-gravatar :email="user.email" :alt="avatarText" default-img="mp">
          </v-gravatar>
        </v-avatar>
      </v-col>
    </v-row>

    <v-row no-gutters>
      <v-col v-if="user">
        <h3 v-if="user.first_name || user.last_name" class="subdued mt-3">
          {{ user.first_name ? user.first_name : "" }}
          {{ user.last_name ? user.last_name : "" }}
        </h3>
        <h4 v-if="user.email" class="font-weight-light mb-1">
          {{ user.email }}
        </h4>
        <div class="font-weight-black">
          <span v-if="user.is_superuser" v-text="$t('is_superuser')"></span>
        </div>
      </v-col>
    </v-row>

    <v-row class="mb-8" justify="center">
      <v-col v-if="canLogout" cols="auto">
        <v-btn @click="logout" v-text="$t('logout')"></v-btn>
      </v-col>
      <v-col v-if="!useShibboleth" cols="auto">
        <v-btn
          @click="showPasswordChangeDialog = true"
          v-text="$t('change_password')"
        ></v-btn>
        <PasswordChangeDialog v-model="showPasswordChangeDialog" />
      </v-col>
    </v-row>
  </v-container>
</template>

<script>
import { mapActions, mapGetters, mapState } from "vuex";
import VGravatar from "vue-gravatar";
import PasswordChangeDialog from "@/components/account/PasswordChangeDialog";

export default {
  name: "UserPage",
  components: { PasswordChangeDialog, VGravatar },
  data() {
    return {
      showPasswordChangeDialog: false,
    };
  },
  computed: {
    ...mapState({
      user: "user",
    }),
    ...mapGetters({
      loggedIn: "loggedIn",
      avatarText: "avatarText",
      canLogout: "canLogout",
      useShibboleth: "useShibboleth",
    }),
  },

  methods: {
    ...mapActions({
      logout: "logout",
      loadUserData: "loadUserData",
      showSnackbar: "showSnackbar",
    }),
  },

  mounted() {
    // re-download user data on page load to make sure it is up-to-date
    this.loadUserData();
  },
};
</script>

<style scoped></style>
