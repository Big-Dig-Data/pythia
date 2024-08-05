<i18n>
en:
  related_authors: Related authors
  related_publishers: Related publishers
  related_topics: Related topics
  related_langs: Related languages
  related_institutions: Related institutions
  related_work_types: Related work types
  ignore_global_filters: Ignore global filters for related records

cs:
  related_authors: Související autoři
  related_publishers: Související vydavatelé
  related_topics: Související témata
  related_langs: Související jazyky
  related_institutions: Související instituce
  related_work_types: Související typy děl
  ignore_global_filters: Ignoruj globální filtry pro související záznamy
</i18n>

<template>
  <div :class="{ 'concept-card': !standalone }">
    <div class="d-flex" v-if="globalFiltersActive">
      <v-spacer></v-spacer>
      <v-checkbox
        v-model="ignoreGlobalFilters"
        :label="$t('ignore_global_filters')"
        class="small-checkbox"
      />
    </div>
    <v-container fluid class="pa-0">
      <v-row>
        <v-col
          v-for="relType in relatedTopicTypes"
          :key="relType.type"
          :cols="12"
          :lg="standalone ? 6 : 12"
          class="py-0"
        >
          <v-lazy
            min-height="150"
            transition="fade-transition"
            style="height: 100%"
          >
            <OneRelatedTopicWidget
              :extra-filter="extraFilter"
              :title="$t(relType.title)"
              :topic-type="relType.type"
              :ignore-global-filters="ignoreGlobalFilters"
              :standalone="standalone"
            />
          </v-lazy>
        </v-col>
      </v-row>

      <v-row>
        <v-col>
          <CandidatesTable
            v-if="this.includesCandidates.includes(this.topicType)"
            :filters="[{ name: topicType, id: topicId }]"
            :excludeHeaders="['score']"
          />
        </v-col>
      </v-row>
    </v-container>
  </div>
</template>
<script>
import OneRelatedTopicWidget from "./OneRelatedTopicWidget";
import { mapGetters } from "vuex";
import { topicTypeToQueryParam } from "../libs/api";
import CandidatesTable from "./CandidatesTable.vue";

export default {
  name: "ExplicitTopicRelatedTopicsWidget",
  components: {
    CandidatesTable,
    OneRelatedTopicWidget,
    ExplicitTopicRecommendationsWidget: () =>
      import("./ExplicitTopicRecommendationsWidget.vue"),
  },
  props: {
    topicType: { required: true, type: String },
    topicId: { required: true, type: Number },
    standalone: { default: false, type: Boolean },
  },
  data() {
    return {
      includesCandidates: ["author", "publisher", "language", "psh"],
      ignoreGlobalFilters: false,
      relatedTopicTypes: [
        { type: "author", title: "related_authors" },
        { type: "publisher", title: "related_publishers" },
        { type: "psh", title: "related_topics" },
        { type: "language", title: "related_langs" },
        { type: "owner", title: "related_institutions" },
        { type: "work-type", title: "related_work_types" },
      ],
      topicTypeToQueryParam,
    };
  },
  computed: {
    ...mapGetters({
      queryParams: "workQueryParams",
    }),
    extraFilter() {
      let out = {};
      out[this.topicTypeToQueryParam[this.topicType]] = this.topicId;
      return out;
    },
    globalFiltersActive() {
      return Object.values(this.queryParams).some((item) => item);
    },
  },
};
</script>

<style scoped lang="scss">
div.concept-card {
  margin-left: 1.5rem;
  max-height: 85vh;
  overflow-y: scroll;
  width: 100%;
}
</style>
