<i18n src="@/locales/topic-types.yaml"></i18n>
<i18n>
en:
  input:
    search_placeholder: Start typing to search
  no_data: Sorry, but nothing matching was found
  write_something: Write at least 2 letters
  loading: Loading data...
  score: "Score:"
  num_loans: Number of loans
  num_work-type: Number of categories
  num_author: Number of authors
  num_publisher: Number of publishers
  num_language: Number of languages
  num_owner: Number of institutions
  interest_distribution: Interest distribution
  work-type_interest_distribution_info: Distribution of categories based on number of loans
  author_interest_distribution_info: Distribution of authors based on number of loans
  publisher_interest_distribution_info: Distribution of publishers based on number of loans
  language_interest_distribution_info: Distribution of languages based on number of loans
  owner_interest_distribution_info: Distribution of institutions based on number of loans
cs:
  input:
    search_placeholder: Pro vyhledávání začněte psát
  no_data: Je nám to líto, ale nic odpovídajícího jsme nenašli
  write_something: Napište alespoň 2 písmena
  loading: Nahrávám data...
  score: "Skóre:"
</i18n>

<template>
  <v-container fluid>
    <v-row>
      <v-col class="pa-1">
        <v-autocomplete
          v-model="selectedRecord"
          :items="records"
          :loading="isLoading"
          :search-input.sync="queryText"
          color="primary"
          item-text="name"
          item-value="pk"
          :label="$t('topic_type.' + topicType)"
          :placeholder="$t('input.search_placeholder')"
          prepend-inner-icon="fa-search"
          return-object
          clearable
          clear-icon="fa-times"
          :no-filter="true"
        >
          <template #item="{ item }">
            <v-list-item-content>
              <v-list-item-title v-html="item.name"></v-list-item-title>
              <v-list-item-subtitle
                >{{ $t("score") }}
                {{ formatInteger(item.score) }}</v-list-item-subtitle
              >
            </v-list-item-content>
          </template>
          <template #no-data>
            <div v-if="queryTextGoodEnough" class="pa-2">
              <span v-if="isLoading">
                <v-icon>fa-cogs</v-icon>
                {{ $t("loading") }}
              </span>
              <span v-else>
                <v-icon>fa-frown</v-icon>
                {{ $t("no_data") }}
              </span>
            </div>
            <div v-else class="pa-2">{{ $t("write_something") }}</div>
          </template>
        </v-autocomplete>
      </v-col>
    </v-row>

    <v-row v-if="selectedTopicId" no-gutters>
      <v-col>
        <ExplicitTopicDetail
          :topic-type="topicType"
          :topic-id="selectedTopicId"
          :key="selectedTopicId"
        />
      </v-col>
    </v-row>

    <div v-else>
      <v-row>
        <v-col cols="4">
          <TopItemsWidget :topic-type="topicType" order-by="work_count" />
        </v-col>
        <v-col cols="4">
          <TopItemsWidget :topic-type="topicType" order-by="score" />
        </v-col>
        <v-col cols="12" :md="4">
          <BarChartCard
            :url="`/api/hits/workhit/histogram/WORKSET_UID/${topicType}`"
            :dimension="{ name: $t('num_loans'), value: 'name' }"
            :metrics="[
              { name: $t(`num_${topicType}`), value: 'count', type: 'bar' },
            ]"
            :title="$t('interest_distribution')"
            :titleInfo="$t(`${topicType}_interest_distribution_info`)"
            :chartHeight="272"
          />
        </v-col>
      </v-row>
      <v-row>
        <v-col :cols="6">
          <TopItemsWidget
            :topic-type="topicType"
            order-by="absolute_growth"
            :includeInfo="true"
          />
        </v-col>
        <v-col :cols="6">
          <TopItemsWidget
            :topic-type="topicType"
            order-by="relative_growth"
            :includeInfo="true"
          />
        </v-col>
      </v-row>
    </div>
  </v-container>
</template>

<script>
import ExplicitTopicDetail from "../components/ExplicitTopicDetail";
import TopItemsWidget from "../components/TopItemsWidget";
import BarChartCard from "../components/charts/BarChartCard";

import axios from "axios";
import debounce from "lodash/debounce";
import { mapActions, mapGetters } from "vuex";
import { stringify } from "query-string";
import { formatInteger } from "../libs/numbers";

export default {
  name: "ExplicitTopicDetailPage",
  components: {
    ExplicitTopicDetail,
    TopItemsWidget,
    BarChartCard,
  },

  props: {
    topicType: { required: true, type: String },
    topicId: { required: false, type: Number },
  },

  data() {
    return {
      records: [],
      selectedRecord: null,
      isLoading: false,
      queryText: "",
    };
  },

  computed: {
    ...mapGetters({
      selectedWorksetUUID: "selectedWorksetUUID",
    }),
    selectedTopicId() {
      return this.topicId
        ? this.topicId
        : this.selectedRecord
        ? this.selectedRecord.pk
        : null;
    },
    dataUrl() {
      if (this.selectedWorksetUUID) {
        const params = { q: this.queryText };
        return `/api/bookrank/workset/${this.selectedWorksetUUID}/${
          this.topicType
        }/?${stringify(params)}`;
      }
      return null;
    },
    queryTextGoodEnough() {
      return this.queryText && this.queryText.length >= 2;
    },
  },

  methods: {
    ...mapActions({
      showSnackbar: "showSnackbar",
    }),
    formatInteger,
    debouncedLoadMatchingTopics: debounce(function () {
      this.loadMatchingTopics();
    }, 500),
    async loadMatchingTopics() {
      if (this.dataUrl && this.queryTextGoodEnough) {
        this.records = [];
        this.isLoading = true;
        try {
          const response = await axios.get(this.dataUrl);
          this.records = response.data.results.map((el) => {
            if (this.topicType == "psh") el.name += ` (${el.root_node})`;
            return el;
          });
        } catch (error) {
          this.showSnackbar({
            content: "Error fetching data: " + error,
            color: "error",
          });
          console.log("Error fetching data", error);
        } finally {
          this.isLoading = false;
        }
      } else {
        this.records = [];
        this.isLoading = false;
      }
    },
  },

  watch: {
    queryText() {
      this.records = [];
      this.isLoading = true;
      this.debouncedLoadMatchingTopics();
    },
    selectedRecord() {
      if (this.selectedRecord) {
        this.$router.push({
          name: `${this.topicType} detail`,
          params: { topicId: this.selectedRecord.pk },
        });
      } else {
        this.$router.push({ name: "author detail root" });
      }
    },
    topicType() {
      this.records = [];
    },
  },
};
</script>

<style lang="scss">
.item-author {
  font-size: 75%;
  color: #666666;
}
</style>
