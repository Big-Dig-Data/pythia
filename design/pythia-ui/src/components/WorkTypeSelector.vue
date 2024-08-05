<i18n>
en:
    work_count: Work count
    all: All types
    work_type_filter: Work type filter

cs:
    work_count: Počet děl
    all: Všechny typy
    work_type_filter: Filtr podle typu díla
</i18n>

<template>
  <v-select
    v-model="selectedWorkType"
    :items="listItems"
    item-text="name"
    item-value="value"
    :label="$t('work_type_filter')"
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
  name: "WorkTypeSelector",

  data() {
    return {};
  },

  computed: {
    ...mapState({
      availableItems: (state) => state.workTypeFilter.availableWorkTypes,
      globalWorkType: (state) => state.workTypeFilter.selectedWorkType,
    }),
    ...mapGetters({
      worksetUUID: "selectedWorksetUUID",
    }),
    listItems() {
      return [{ name: this.$t("all"), value: null }, ...this.availableItems];
    },
    selectedWorkType: {
      get() {
        return this.globalWorkType;
      },
      set(value) {
        this.changeSelectedWorkType(value);
      },
    },
  },

  methods: {
    ...mapActions({
      fetchWorkTypes: "fetchAvailableWorkTypes",
      changeSelectedWorkType: "changeSelectedWorkType",
    }),
    formatInteger: formatInteger,
  },

  created() {
    if (!this.availableItems || this.availableItems.length === 0)
      this.fetchWorkTypes({ worksetUUID: this.worksetUUID });
  },
};
</script>

<style scoped></style>
