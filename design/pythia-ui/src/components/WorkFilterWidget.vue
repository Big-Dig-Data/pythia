<i18n>
en:
    work_filter: Work filter
    all: All
    language_work_filter: Language work filter
    owner_work_filter: Owner organization work filter
    date_work_filter: Year of publication filter
    work_type_filter: Work type filter
cs:
    work_filter: Filtr děl
    all: Vše
    language_work_filter: Jazykový filtr děl
    owner_work_filter: Filtr děl podle vlastnické organizace
    date_work_filter: Filtr děl podle roku vydání
    work_type_filter: Filter podle typu díla
</i18n>

<template>
  <div
    class="d-inline-flex flex-column cursor-pointer"
    @click="showDialog = true"
  >
    <div class="sc">{{ $t("work_filter") }}</div>
    <div>
      <v-tooltip bottom>
        <template v-slot:activator="{ on }">
          <span v-on="on">
            <v-icon small class="bl inactive">fa-language</v-icon>
            <span :class="{ highlight: lang !== null }">
              {{ langDisplay }}
            </span>
          </span>
        </template>
        {{ $t("language_work_filter") }}
      </v-tooltip>

      <v-tooltip bottom>
        <template v-slot:activator="{ on }">
          <span v-on="on">
            <v-icon small class="bl inactive separated">fa-university</v-icon>
            <span :class="{ highlight: selectedInstitutionObject !== null }">
              {{ institutionDisplay }}
            </span>
          </span>
        </template>
        {{ $t("owner_work_filter") }}
      </v-tooltip>

      <v-tooltip bottom>
        <template v-slot:activator="{ on }">
          <span v-on="on">
            <v-icon small class="bl inactive separated">fa-calendar</v-icon>
            <span :class="{ highlight: YOPRange !== null }">
              {{ YOPRange ? YOPRange : $t("all") }}
            </span>
          </span>
        </template>
        {{ $t("date_work_filter") }}
      </v-tooltip>

      <v-tooltip bottom>
        <template v-slot:activator="{ on }">
          <span v-on="on">
            <v-icon small class="bl inactive separated">fa-book</v-icon>
            <span :class="{ highlight: selectedWorkTypeObject !== null }">
              {{ workTypeDisplay }}
            </span>
          </span>
        </template>
        {{ $t("work_type_filter") }}
      </v-tooltip>
    </div>
    <v-dialog v-model="showDialog" max-width="640px">
      <WorkFilterDialog @close="showDialog = false" />
    </v-dialog>
  </div>
</template>

<script>
import { mapGetters } from "vuex";
import WorkFilterDialog from "./WorkFilterDialog";

export default {
  name: "WorkFilterWidget",

  components: {
    WorkFilterDialog,
  },

  data() {
    return {
      showDialog: false,
    };
  },

  computed: {
    ...mapGetters({
      lang: "selectedLanguageCode",
      YOPRange: "YOPRange",
      selectedInstitutionObject: "selectedInstitutionObject",
      selectedWorkTypeObject: "selectedWorkTypeObject",
    }),
    langDisplay() {
      return this.lang !== null
        ? this.lang
          ? this.lang.toUpperCase()
          : "-"
        : this.$t("all");
    },
    institutionDisplay() {
      return this.selectedInstitutionObject
        ? this.selectedInstitutionObject.name
        : this.$t("all");
    },
    workTypeDisplay() {
      return this.selectedWorkTypeObject
        ? this.selectedWorkTypeObject.name
        : this.$t("all");
    },
  },
};
</script>

<style scoped lang="scss">
.separated {
  border-left: solid 1px var(--v-primary-lighten2);
  padding-left: 0.5rem;
  margin-left: 0.3rem;
}

.inactive {
  color: var(--v-primary-lighten2);
}

.highlight {
  color: yellow;
  text-shadow: 0 0 8px yellow;
}
</style>
