<i18n src="../locales/common.yaml"></i18n>
<i18n>
en:
  filters: Filters
  subject_schema_select: Subject scheme
  publishers_selected: Publishers selected
  subjects_selected: Subjects selected
cs:
  filters: Filtry
  subject_schema_select: Klasifikační schéma
  publishers_selected: Vybraní vydavatelé
  subjects_selected: Vybraná témata
</i18n>
<template>
  <v-container fluid>
    <v-row>
      <v-col :cols="12">
        <v-expansion-panels>
          <v-expansion-panel>
            <v-expansion-panel-header class="d-flex justify-space-between">
              <template v-slot:default="{ open }">
                <v-row no-gutters>
                  <v-col cols="4">
                    {{ $t("filters") }}
                  </v-col>
                  <v-col cols="4">
                    <v-fade-transition leave-absolute>
                      <span v-if="!open">
                        {{ $t("publishers_selected") }}:
                        {{ selectedPublishers.length }}
                      </span>
                    </v-fade-transition>
                  </v-col>
                  <v-col cols="4">
                    <v-fade-transition leave-absolute>
                      <span v-if="!open">
                        {{ $t("subjects_selected") }}:
                        {{ selectedTopics.length }}
                      </span>
                      <v-select
                        v-else
                        v-model="selectedSubjectSchema"
                        :items="subjectSchemas.map((e) => e.toUpperCase())"
                        :label="$t('subject_schema_select')"
                        @click.stop
                        outlined
                        dense
                        hide-details
                        class="mr-16"
                      ></v-select>
                    </v-fade-transition>
                  </v-col>
                </v-row>
              </template>
            </v-expansion-panel-header>
            <v-expansion-panel-content eager>
              <v-row>
                <v-col :cols="6">
                  <TopicsFilterTable
                    urlArg="publisher"
                    v-model="selectedPublishers"
                    :header="$t('columns.publisher')"
                    score_type="growth"
                  />
                </v-col>
                <v-col :cols="6"
                  ><SubjectTree
                    v-model="selectedTopics"
                    :height="'392px'"
                    :parent_uid="
                      selectedSubjectSchema
                        ? `${selectedSubjectSchema}-ROOT`
                        : 'PSH-ROOT'
                    "
                    score_type="growth"
                /></v-col>
              </v-row>
            </v-expansion-panel-content>
          </v-expansion-panel>
        </v-expansion-panels>
      </v-col>
    </v-row>
    <v-row>
      <v-col cols="12">
        <WorksGrowthTable :filters="filters" />
      </v-col>
    </v-row>
  </v-container>
</template>

<script>
import { mapGetters } from "vuex";
import WorksGrowthTable from "./WorksGrowthTable";
import TopicsFilterTable from "./TopicsFilterTable";
import SubjectTree from "@/components/SubjectTree";
export default {
  name: "WorksGrowthOverview",
  components: { WorksGrowthTable, TopicsFilterTable, SubjectTree },

  data() {
    return {
      selectedPublishers: [],
      selectedTopics: [],
      selectedSubjectSchema: null,
    };
  },

  computed: {
    ...mapGetters({
      subjectSchemas: "subjectSchemas",
    }),
    filters() {
      let out = {};
      if (this.selectedPublishers.length)
        out["publisher"] = [...this.selectedPublishers];
      if (this.selectedTopics.length) out["psh"] = [...this.selectedTopics];
      return out;
    },
  },

  methods: {},

  watch: {
    subjectSchemas: {
      handler() {
        if (!this.subjectSchemas.length) return null;
        if (localStorage.selectedSubjectSchemaFilter) {
          this.selectedSubjectSchema = localStorage.selectedSubjectSchemaFilter;
        }
      },
      immediate: true,
    },
    // filters: {
    //   handler() {
    //     const fltrs = JSON.stringify(this.filters);
    //     if (fltrs !== this.$route.query.filters) {
    //       this.$router.push({
    //         path: this.$router.currentRoute.path,
    //         query: { filters: JSON.stringify(this.filters) },
    //       });
    //     }
    //   },
    //   deep: true,
    // },
  },

  mounted() {
    // if (this.$route.query.filters) {
    //   const filters = JSON.parse(this.$route.query.filters);
    //   this.selectedTopics = filters.psh ?? [];
    // }
  },
};
</script>
