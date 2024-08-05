<i18n src="../locales/common.yaml"></i18n>

<template>
  <v-navigation-drawer
    v-model="drawer"
    :mini-variant.sync="mini"
    clipped
    app
    mobile-breakpoint="900"
  >
    <v-toolbar flat class="transparent">
      <v-list class="pa-0">
        <v-list-item>
          <v-list-item-action>
            <v-icon>fa-th</v-icon>
          </v-list-item-action>

          <v-list-item-content>
            {{ $t("menu") }}
          </v-list-item-content>

          <v-list-item-action>
            <v-btn icon @click.stop="mini = !mini">
              <v-icon>fa-chevron-left</v-icon>
            </v-btn>
          </v-list-item-action>
        </v-list-item>
      </v-list>
    </v-toolbar>

    <div v-if="extraRoutes">
      <v-list
        class="pt-0"
        dense
        v-for="group in groups"
        :key="group.title"
        subheader
      >
        <v-subheader>{{ group.title }}</v-subheader>

        <v-list-item
          v-for="item in group.items"
          :key="item.title"
          :to="{ name: item.linkTo }"
        >
          <!-- exact - use this attr on v-list-item to prevent matching / -->

          <v-list-item-action>
            <v-icon class="fa-fw">{{ item.icon }}</v-icon>
          </v-list-item-action>

          <v-list-item-content>
            <v-list-item-title>{{ item.title }}</v-list-item-title>
          </v-list-item-content>
        </v-list-item>
      </v-list>
    </div>
    <div v-else class="side-loader">
      <span class="fas fa-cog fa-spin fa-3x"></span>
    </div>
  </v-navigation-drawer>
</template>
<script>
import { mapGetters } from "vuex";
import SubjectTreePage from "./SubjectTreePage";
export default {
  name: "SidePanel",
  data() {
    return {
      mini: false,
      drawer: true,
      extraRoutes: false,
    };
  },
  computed: {
    ...mapGetters({ subjectSchemas: "subjectSchemas" }),
    groups() {
      return [
        /*{
            title: this.$i18n.t('pages.settings'),
            items: [
              { title: this.$i18n.t('pages.settings'), icon: 'fa-cog', linkTo: 'home' },
              ]
          },*/
        {
          title: this.$i18n.t("pages.candidates"),
          items: [
            {
              title: this.$i18n.t("pages.candidates"),
              icon: "fa-book",
              linkTo: "candidates table",
            },
            {
              title: this.$i18n.t("pages.acquisitions"),
              icon: "fa-sign-in-alt",
              linkTo: "acquisitions",
            },
          ],
        },
        {
          title: this.$i18n.t("pages.content"),
          items: [
            {
              title: this.$i18n.t("pages.works"),
              icon: "fa-book",
              linkTo: "work detail root",
            },
            {
              title: this.$i18n.t("pages.authors"),
              icon: "fa-user",
              linkTo: "author detail root",
            },
            {
              title: this.$i18n.t("pages.publishers"),
              icon: "fa-print",
              linkTo: "publisher detail root",
            },
            {
              title: this.$i18n.t("pages.languages"),
              icon: "fa-globe",
              linkTo: "language detail root",
            },
            {
              title: this.$i18n.t("pages.work_types"),
              icon: "fa-newspaper",
              linkTo: "work-type detail root",
            },
            {
              title: this.$i18n.t("pages.owner"),
              icon: "fa-university",
              linkTo: "owner detail root",
            },
          ],
        },
        {
          title: this.$i18n.t("pages.recomm"),
          items: [
            //{ title: this.$i18n.t('pages.new_works'), icon: 'fa-book-open', linkTo: 'predictions' },
            {
              title: this.$i18n.t("pages.topic_recomm"),
              icon: "fa-tags",
              linkTo: "psh recommendations",
            },
            {
              title: this.$i18n.t("pages.publisher_recomm"),
              icon: "fa-print",
              linkTo: "publisher recommendations",
            },
            {
              title: this.$i18n.t("pages.author_recomm"),
              icon: "fa-user-friends",
              linkTo: "author recommendations",
            },
          ],
        },
      ];
    },
  },

  watch: {
    subjectSchemas: {
      handler() {
        if (!this.subjectSchemas.length) return null;
        this.subjectSchemas.forEach((tree) => {
          let upperTree = tree.toUpperCase();
          this.$router.addRoute({
            path: `/${tree}`,
            name: `${tree} tree`,
            component: SubjectTreePage,
            props: () => ({
              rootNode: upperTree,
              rootNodeUid: `${upperTree}-ROOT`,
              showCandidates: tree === "thema",
            }),
          });
          this.groups[1].items.push({
            title: this.$i18n.t(`pages.${tree}`),
            icon: "fa-palette",
            linkTo: `${tree} tree`,
          });
        });
        this.extraRoutes = true;
      },
      immediate: true,
    },
  },

  mounted() {
    // in case of the small laptop it collapses side panel
    // but does not hides it completely
    this.mini = this.$vuetify.breakpoint.name == "md";
  },
};
</script>

<style scoped lang="scss">
div.side-loader {
  width: 250px;
  height: 250px;
  text-align: center;
  padding-top: 300px;
  border-radius: 5px;
  color: #aaaaaa;
}
</style>
