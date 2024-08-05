<i18n>
en:
    work_count: Work count
    all: All languages
    lang_filter: Language filter

cs:
    work_count: Počet děl
    all: Všechny jazyky
    lang_filter: Filtr podle jazyka
</i18n>

<template>
  <v-select
    v-model="selectedLanguage"
    :items="listItems"
    item-text="name"
    item-value="value"
    return-object
    :label="$t('lang_filter')"
  >
    <template v-slot:item="{ item }">
      <v-list-item-content>
        <v-list-item-title v-text="item.name"></v-list-item-title>
        <v-list-item-subtitle v-if="item.count">
          <span class="font-weight-light pr-1">{{ $t("work_count") }}:</span>
          {{ formatInteger(item.count) }}
        </v-list-item-subtitle>
      </v-list-item-content>
    </template>
  </v-select>
</template>

<script>
import { mapActions, mapGetters, mapState } from "vuex";
import { formatInteger } from "@/libs/numbers";

export default {
  name: "WorkLanguageSelector",

  data() {
    return {};
  },

  computed: {
    ...mapState({
      availableItems: (state) => state.langFilter.availableLanguages,
      globalLanguage: (state) => state.langFilter.selectedLanguage,
    }),
    ...mapGetters({
      worksetUUID: "selectedWorksetUUID",
    }),
    listItems() {
      return [{ name: this.$t("all"), value: null }, ...this.availableItems];
    },
    selectedLanguage: {
      get() {
        return this.globalLanguage;
      },
      set(value) {
        this.changeSelectedLanguage(value);
      },
    },
  },

  methods: {
    ...mapActions({
      fetchLanguages: "fetchAvailableLanguages",
      changeSelectedLanguage: "changeSelectedLanguage",
    }),
    formatInteger: formatInteger,
  },

  async created() {
    if (!this.availableItems || this.availableItems.length === 0)
      await this.fetchLanguages({ worksetUUID: this.worksetUUID });
  },
};
</script>

<style scoped></style>
