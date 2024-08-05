<!--

TODO:

- without being logged in, the locale is set to default and thus I get czech error messages :(

-->

<i18n lang="yaml" src="@/locales/dialog.yaml" />

<i18n lang="yaml">
en:
  not_logged_in: Login
  not_logged_in_internal_text: Please enter your login credentials and click "Login".
  login: Login
  email: Email
  password: Password
  new_password: Choose a password
  password2: Repeat password
  login_error: There was an error logging you in
  password_reset:
    title: Reset password
    text: Enter a valid email address which was used during registration. We will send you a link for password recovery to this address.
    switch: "Forgotten password? {reset_here}"
    link: Reset it here.
    back_to_login: Back to {login}.
    back_to_login_full: Back to login
    login: login
    error: An error occured during password reset
    success: An email to reset password was sent to {reset_email}.
    button: Send recovery link
  email_required: Please enter a valid email address
  logged_out: You have been logged out
  logged_out_text: You have been logged out - probably because your session has expired. The following button will navigate you to the login page.
  relogin: Login again

cs:
  not_logged_in: Přihlášení
  not_logged_in_internal_text: Zadejte své přihlašovací údaje a stiskněte "Přihlásit".
  login: Přihlásit
  email: Email
  password: Heslo
  new_password: Zvolte si heslo
  password2: Potvrzení hesla
  login_error: Při přihlášování došlo k chybě
  password_reset:
    title: Obnova hesla
    text: Zadejte platnou emailovou adresu, kterou jste použili při registraci. Pošleme vám na ni odkaz, pomocí kterého můžete provést změnu hesla.
    switch: "Zapomenuté heslo? {reset_here}"
    link: Obnovit zde.
    back_to_login: Zpět na {login}.
    back_to_login_full: Zpět na přihlášení
    login: přihlášení
    error: Během resetování hesla došlo k chybě
    success: E-mail pro obnovu hesla byl odeslán na {reset_email}.
    button: Odeslat odkaz pro obnovení
  email_required: Zadejte platnou emailovou adresu
  logged_out: Byli jste odhlášeni
  logged_out_text: Byli jste odhlášeni - pravděpodobně proto, že vaše relace vypršela. Následující tlačítko vás přesměruje na přihlašovací stránku.
  relogin: Přihlásit se znovu
</i18n>

<template>
  <v-dialog v-model="showLoginDialog" persistent :max-width="480">
    <!-- login-->
    <v-card v-if="useShibboleth">
      <v-card-title>{{ $t("logged_out") }}</v-card-title>
      <v-card-text>
        <p>{{ $t("logged_out_text") }}</p>
      </v-card-text>
      <v-card-actions class="pb-4">
        <v-spacer />
        <v-btn :href="$route.fullPath" color="primary">{{
          $t("relogin")
        }}</v-btn>
      </v-card-actions>
    </v-card>
    <v-card v-else-if="currentTab == 'login'">
      <v-card-title class="headline">{{ $t("not_logged_in") }}</v-card-title>
      <v-card-text>
        <div>{{ $t("not_logged_in_internal_text") }}</div>

        <v-divider class="my-3"></v-divider>
        <v-text-field
          v-model="email"
          :label="$t('email')"
          :rules="[rules.required, rules.email]"
        ></v-text-field>
        <v-text-field
          v-on:keyup.enter="triggerLoginOnEnter"
          v-model="password"
          :label="$t('password')"
          :rules="[rules.required, rules.min]"
          :type="showPassword ? 'text' : 'password'"
          :append-icon="showPassword ? 'fa-eye' : 'fa-eye-slash'"
          @click:append="showPassword = !showPassword"
        ></v-text-field>

        <v-alert
          v-if="loginError"
          type="error"
          outlined
          icon="fas fa-exclamation-circle"
        >
          {{ $t("login_error") }}: "<em>{{ loginErrorText }}</em
          >"
        </v-alert>
      </v-card-text>
      <v-card-actions>
        <div class="ml-4" :class="{ small: !loginError }">
          <v-icon color="warning" class="mr-2" v-if="loginError">
            fa fa-caret-right
          </v-icon>

          <i18n
            path="password_reset.switch"
            tag="span"
            :class="loginError ? 'warning--text' : 'secondary--text'"
          >
            <template #reset_here>
              <a
                @click="currentTab = 'reset-password'"
                v-text="$t('password_reset.link')"
              ></a>
            </template>
          </i18n>

          <v-icon color="warning" class="ml-2" v-if="loginError">
            fa fa-caret-left
          </v-icon>
        </div>
        <v-spacer></v-spacer>
        <v-btn
          color="primary"
          class="ma-3"
          @click="doLogin"
          :disabled="!loginValid || requestInProgress"
          v-text="$t('login')"
        ></v-btn>
      </v-card-actions>
    </v-card>
    <!-- reset password -->
    <v-card v-else-if="currentTab == 'reset-password'">
      <v-card-title class="headline">{{
        $t("password_reset.title")
      }}</v-card-title>
      <v-card-text>
        <div>{{ $t("password_reset.text") }}</div>

        <v-text-field
          v-model="email"
          :label="$t('email')"
          :rules="[rules.required, rules.email]"
          class="mt-6"
        ></v-text-field>
        <v-alert
          v-if="resetError"
          type="error"
          outlined
          icon="fas fa-exclamation-circle"
        >
          {{ $t("password_reset.error") }}: "<em>{{ resetError }}</em
          >"
        </v-alert>
        <v-alert v-if="resetSuccess" type="success" outlined>
          <i18n
            path="password_reset.success"
            tag="span"
            class="text--secondary"
          >
            <template #reset_email>
              <a :href="'mailto:' + email" v-text="email"></a>
            </template>
          </i18n>
        </v-alert>
      </v-card-text>
      <v-card-actions>
        <div class="ml-4 small">
          <i18n
            path="password_reset.back_to_login"
            tag="span"
            class="text--secondary"
          >
            <template #login>
              <a
                @click="
                  currentTab = 'login';
                  resetForm();
                "
                v-text="$t('login')"
              ></a>
            </template>
          </i18n>
        </div>
        <v-spacer></v-spacer>
        <v-btn
          color="primary"
          class="ma-3"
          @click="doReset()"
          :disabled="!resetValid || requestInProgress"
          v-if="!resetSuccess"
          v-text="$t('password_reset.button')"
        ></v-btn>
        <v-btn
          v-else
          @click="
            currentTab = 'login';
            resetForm();
          "
          v-text="$t('password_reset.back_to_login_full')"
          class="mr-4 mb-3"
          color="primary"
        ></v-btn>
      </v-card-actions>
    </v-card>
  </v-dialog>
</template>
<script>
import { mapActions, mapGetters, mapState } from "vuex";
import validateEmail from "@/libs/email-validation";

export default {
  name: "LoginDialog",
  props: {
    value: {},
  },
  data() {
    return {
      email: "",
      password: "",
      password2: "",
      currentTab:
        "reset-password" in this.$route.query ? "reset-password" : "login",
      rules: {
        required: (value) => !!value || this.$t("required"),
        min: (v) => v.length >= 8 || this.$t("min_pwd_length"),
        email: (v) => !!validateEmail(v) || this.$t("email_required"),
      },
      resetError: null,
      showPassword: false,
      emailEdited: false, // when email gets edited, we hide associated error message
      passwordEdited: false,
      requestInProgress: false, // if a request was just sent to the backend and is processed
      resetSuccess: false, // reset email was sent
    };
  },
  computed: {
    ...mapState({
      loginError: (state) => state.login.loginError,
    }),
    ...mapGetters({
      loginErrorText: "loginErrorText",
      showLoginDialog: "showLoginDialog",
      useShibboleth: "useShibboleth",
    }),
    loginValid() {
      return (
        this.email !== "" &&
        this.rules.email(this.email) === true &&
        this.password.length >= 8
      );
    },
    resetValid() {
      return this.email !== "" && this.rules.email(this.email) === true;
    },
  },

  methods: {
    ...mapActions({
      login: "login",
      resetPassword: "resetPassword",
      showSnackbar: "showSnackbar",
    }),
    resetForm() {
      this.resetError = null;
      this.resetSuccess = false;
      this.password = "";
      this.showPassword = false;
      this.passwordEdited = false;
      this.requestInProgress = false;
      this.$store.state.login.loginError = null;
    },
    async triggerLoginOnEnter() {
      if (this.loginValid) {
        await this.doLogin();
      }
    },
    async doLogin() {
      this.requestInProgress = true;
      try {
        await this.login({ email: this.email, password: this.password });
      } finally {
        this.requestInProgress = false;
      }
    },
    async doReset() {
      this.requestInProgress = true;
      this.resetError = null;
      this.resetSuccess = false;
      try {
        await this.resetPassword({ email: this.email });
        this.resetSuccess = true;
      } catch (error) {
        console.log(error);
        this.resetError = error;
      } finally {
        this.requestInProgress = false;
      }
    },
  },

  watch: {
    email() {
      this.emailEdited = true;
    },
    password() {
      this.passwordEdited = true;
    },
  },
};
</script>
<style lang="scss">
.v-select.v-text-field.short input {
  max-width: 0;
}

div.small {
  font-size: 80%;
}
</style>
