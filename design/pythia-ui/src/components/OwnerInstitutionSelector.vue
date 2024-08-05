<i18n>
en:
    work_count: Work count
    all: All institutions
    inst_filter: Owner institution filter

cs:
    work_count: Počet děl
    all: Všechny instituce
    inst_filter: Filtr podle instituce
</i18n>

<template>
  <v-select
    v-model="selectedInstitution"
    :items="listItems"
    item-text="name"
    item-value="value"
    :label="$t('inst_filter')"
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
  name: "OwnerInstitutionSelector",

  data() {
    return {};
  },

  computed: {
    ...mapState({
      availableItems: (state) => state.ownerFilter.availableInstitutions,
      globalInstitution: (state) => state.ownerFilter.selectedInstitution,
    }),
    ...mapGetters({
      worksetUUID: "selectedWorksetUUID",
    }),
    listItems() {
      return [{ name: this.$t("all"), value: null }, ...this.availableItems];
    },
    selectedInstitution: {
      get() {
        return this.globalInstitution;
      },
      set(value) {
        this.changeSelectedInstitution(value);
      },
    },
  },

  methods: {
    ...mapActions({
      fetchInstitutions: "fetchAvailableInstitutions",
      changeSelectedInstitution: "changeSelectedInstitution",
    }),
    formatInteger: formatInteger,
  },

  created() {
    if (!this.availableItems || this.availableItems.length === 0)
      this.fetchInstitutions({ worksetUUID: this.worksetUUID });
  },
};
</script>

<style scoped></style>
